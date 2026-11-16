# Is something wrong live? (the owner, Nov 16: "until now I'm not seeing the whole thing working, something is wrong
# somewhere"). The 24 copies of the frozen setup (#38-#62) whose coin paths after_exit.py fetched: for each, the backtest
# model on that very coin and wallet 4's own buy, with the live rule, at the backtest's landings (4 / 8 trades after its
# buy / the next slot) and at the exact place our buy landed; against our real result (% of the stake, the journal,
# equal to the chain) and wallet 4's own result on the coin (the status's "its pct"). If the model at our real landing
# says what really happened, the bot does what the backtest assumes and the losses are the coins'.
#   python3 -I live_vs_model.py LIVE_PATHS > out/live_vs_model.txt
import sys, os, json, gzip, re
import numpy as np
PATHS = sys.argv[1]
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-14/float_exits"); import lib as L
ME = "Eao8T2Pk2aDzPWUFCA8si7oWd5ndFKfnX3HjYMpERst6"; W4 = L.W4; OURS = {W4, ME}
# from the status and the journal: #, coin, its SOL, hops (copied = 2 assumed when not printed), real %, its own %, exit
T = [(38, "Dyc9zPSt", 1.541, 1, 58.1, 101.5, "sell_pressure"), (39, "E3c6RqFX", 1.715, 1, -53.7, -36.5, "sell_pressure"),
     (41, "GqAzs7Pb", 1.889, 2, 14.5, -35.9, "sell_pressure"), (42, "3DCv33mL", 1.953, 1, -10.8, -14.2, "sell_pressure"),
     (43, "DAnPxZ7s", 1.592, 1, -5.0, -12.9, "sell_pressure"), (44, "Z3kN3Xpm", 2.017, 1, 42.4, 31.1, "sell_pressure"),
     (45, "GkJDPnXR", 1.301, 1, -6.1, 7.0, "its_sell"), (46, "Dy1ZHNtB", 1.530, 1, -25.7, -16.7, "its_sell"),
     (47, "wQPAb4FH", 1.308, 1, -20.3, -14.9, "its_sell"), (48, "AUtnQZej", 1.349, 1, -16.4, -10.1, "sell_pressure"),
     (49, "CcV84RDz", 1.384, 1, -4.2, -8.9, "sell_pressure"), (50, "BUddYo5u", 1.693, 1, -22.5, -24.1, "sell_pressure"),
     (51, "CdM8ufFW", 1.832, 2, -59.8, -66.0, "stall"), (52, "3Pad5Fm3", 1.619, 1, -3.1, None, "sell_pressure"),
     (53, "DqyALnyB", 2.233, 2, -2.4, -74.9, "sell_pressure"), (54, "76ZkaX1B", 1.878, 1, 5.2, -2.6, "sell_pressure"),
     (55, "4zGubjNG", 1.596, 1, -22.3, -22.7, "sell_pressure"), (56, "ScqzaRCp", 1.580, 2, 16.1, 31.7, "its_sell"),
     (57, "4NahCr5e", 1.900, 1, 45.4, 64.9, "sell_pressure"), (58, "GTA7n7Lx", 1.694, 1, -7.0, 5.6, "its_sell"),
     (59, "CFUwRZgT", 1.455, 1, -26.0, -28.2, "its_sell"), (60, "5pRtNCGM", 1.662, 2, 1.4, 27.4, "sell_pressure"),
     (61, "8nUF7NLv", 1.546, 2, -31.1, 1.4, "its_sell"), (62, "8izPeTka", 1.817, 2, -29.2, -31.4, "sell_pressure")]
files = {f.split("_")[1][:8]: f for f in os.listdir(PATHS) if f.endswith(".json.gz")}
def trig(p, x, sig):
    age = p["age"]
    if not len(age): return None
    if sig[0] == "stall":
        px = p["px"] / x["pin"]; pk = np.maximum.accumulate(px); newhi = np.concatenate([[True], pk[1:] > pk[:-1]])
        last = np.maximum.accumulate(np.where(newhi, age, -1e9)); return L.first((pk >= 1.0) & (age - last >= 180))
    lo = np.searchsorted(age, age - 60, side="left"); s = np.concatenate([[0], np.cumsum(x["sell"])]); b = np.concatenate([[0], np.cumsum(x["buy"])])
    return L.first(((s[1:] - s[lo]) - (b[1:] - b[lo]) >= 5) & (age >= 30))
def model(p, x, stake=0.5):
    if p["refused"]: return (-0.0004, "refused", 0)
    base = L.model(p, stake, 4.0, 600, (30, 290, 1.5), None)
    t = [(i, nm) for i, nm in ((trig(p, x, ("press",)), "sell_pressure"), (trig(p, x, ("stall",)), "stall")) if i is not None]
    if not t: return base
    i, why = min(t)
    if p["age"][i] >= 600: return base
    ex = min(i + 1, len(p["px"]) - 1)
    if p["age"][ex] > base[2] or (p["age"][ex] == base[2] and base[1] != "time"): return base
    vt0, vq0, bps0 = p["ent"]; Q = stake * 1e9 * p["hopf"] / p["rate"]; net_in = Q * 1e4 / (1e4 + bps0); tok = vt0 - vt0 * vq0 / (vq0 + net_in)
    vq_r = p["vq"][ex] + net_in; vt_r = p["vt"][ex] * p["vq"][ex] / vq_r; out = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - p["bps"][ex] / 1e4)
    return (out * p["rate"] * p["hopf"] / 1e9 - stake - 0.0026, why, int(p["age"][ex]))
print(f"{'#':>3} {'coin':8s} | {'real':>7s} {'model at our landing':>22s} | {'model 4 / 8 / slot+1 (backtest)':>32s} | {'wallet 4':>8s} | our landing (trades after its buy) | exits real / model")
rows = []
for num, c, sol, hops, real, its, rexit in T:
    if c not in files: print(f"{num:3d} {c} no path"); continue
    slot, mint = files[c].split(".")[0].split("_"); tr = json.load(gzip.open(f"{PATHS}/{files[c]}"))
    k = next((i for i, e in enumerate(tr) if e["user"] == W4 and e["buy"]), None); o = next((i for i, e in enumerate(tr) if e["user"] == ME and e["buy"]), None)
    if k is None or o is None: print(f"{num:3d} {c} its buy or ours not found"); continue
    r = dict(slot=tr[k]["slot"], sol=sol, hops=hops, key=c); P = {c: (mint, [e for e in tr if e["user"] != ME])}
    land = len([e for e in tr[k + 1:o] if e["user"] != ME])           # trades by others between its buy and ours
    out = {}
    for n in (land if land > 0 else 1, 4, 8, "slot+1"):
        p = L.prep(r, P, n)
        if p is None: continue
        q = P[c][1]; rest = q[len(q) - len(p["px"]):]; j = len(q) - len(p["px"]) - 1
        other = np.array([e["user"] not in OURS for e in rest], dtype=bool); sell = np.array([not e["buy"] for e in rest], dtype=bool) & other
        x = dict(sell=sell, buy=other & ~sell, pin=(q[k]["vt"] / q[j]["vt"]) ** 2)
        out[n] = model(p, x)
    m0 = out.get(land if land > 0 else 1); ms = [out[n] for n in (4, 8, "slot+1") if n in out]
    pc = lambda v: 100 * v[0] / 0.5
    rows.append((real, pc(m0), np.mean([pc(v) for v in ms]), its))
    print(f"{num:3d} {c} | {real:+6.1f}% {pc(m0):+21.1f}% | " + " / ".join(f"{pc(v):+6.1f}%" for v in ms) + f" | {'' if its is None else f'{its:+6.1f}%':>8s} | {land:3d} | {rexit} / {m0[1]}")
a = np.array([(r[0], r[1], r[2]) for r in rows])
print(f"\n{len(rows)} copies, the mean a copy: real {a[:, 0].mean():+.1f}% | model at our landing {a[:, 1].mean():+.1f}% | model at the backtest's landings {a[:, 2].mean():+.1f}%"
      f" | wallet 4 on the same coins {np.mean([r[3] for r in rows if r[3] is not None]):+.1f}%")
print(f"real minus model at our landing: {np.mean(a[:, 0] - a[:, 1]):+.1f} points a copy (median {np.median(a[:, 0] - a[:, 1]):+.1f})")
