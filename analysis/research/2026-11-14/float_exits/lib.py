# Shared by the float studies: wallet 4's copyable 1.45+ SOL buys since the stop with PUMP and SPCX held as floats
# (examples/scan.rs with FLOATS=..., its "hops N how X" verdicts), each coin's 31-minute path (model.py's fetcher), and
# the copy model of since_stop/exit_final.py made fast (numpy): our buy N trades after its own, refused past 1.25x,
# exits tp / timer / the early-sale rule / a stop, the sell on the trade after the trigger, the cautious price model
# (our quote stays in the curve). Costs: 0.3% a pool hop each way (a float's own curve route has none), 0.0026 SOL a
# round trip, 0.0004 a refused buy. A quote token is valued at wallet 4's own rate at its buy.
import os, re, json, gzip
import numpy as np
W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
T_STOP = 1793274720 + 600                                   # Oct 29 12:02 UTC
NAMES = {"So111111": "SOL", "3NZ9JMVB": "WBTC", "pumpCmXq": "PUMP", "SPCXxcqX": "SPCX"}
LAND = (4, 8, "slot+1")
CAL = {"tp": 0.189, "time": 0.093, "graduated": 0.093, "its_sell": 0.039, "stop": 0.039, "refused": 0.0}   # since_stop README: the model's miss on our real trades, points of the stake
def load(SPD):
    t_of = {(r["slot"], r["mint8"]): r["t"] for r in json.load(open(f"{SPD}/routable.json"))}
    P = json.load(gzip.open(f"{SPD}/paths.json.gz"))
    rows = []
    for l in open(f"{SPD}/scan_hops.out"):
        m = re.match(r"(\d+) (\S{8}) ([\d.]+) SOL from (\S+) quote (\S+) jupiter (\S+): ROUTABLE hops (\d+) how (\S+) .*?input: (\w{8})", l)
        if not m: continue
        slot, m8 = int(m.group(1)), m.group(2)
        if (slot, m8) not in t_of or t_of[slot, m8] < T_STOP: continue
        rows.append(dict(slot=slot, mint8=m8, t=t_of[slot, m8], sol=float(m.group(3)), frm=m.group(4), quote=m.group(5), hops=int(m.group(7)),
                         how=m.group(8), anchor=NAMES.get(m.group(9), m.group(9)), key=f"{slot}_{m8}"))
    rows.sort(key=lambda r: r["t"])
    last, out, nopath, rebuy = {}, [], 0, 0
    for r in rows:                                           # the bot skips a coin it bought within the hour
        again = r["mint8"] in last and r["t"] - last[r["mint8"]] < 3600; last[r["mint8"]] = r["t"]
        if again: rebuy += 1; continue
        if r["key"] not in P or not P[r["key"]]: nopath += 1; continue
        out.append(r)
    return out, P, dict(rows=len(rows), rebuy=rebuy, nopath=nopath)
def prep(r, P, n, pmax=1.25):
    """The path after our entry as arrays, for landing n; None when its buy is not in the path."""
    m, tr = P[r["key"]]
    k = next((i for i, e in enumerate(tr) if e["user"] == W4 and e["buy"] and e["slot"] == r["slot"]), None)
    if k is None: return None
    its = tr[k]; vta = its["vt"]; t0 = its["t"]; rate = r["sol"] * 1e9 / (its["q"] * (1 + its["bps"] / 1e4))
    j = k + len([e for e in tr[k + 1:] if e["slot"] <= its["slot"] + 1]) if n == "slot+1" else min(k + n, len(tr) - 1)
    ent = tr[j]; px_in = (vta / ent["vt"]) ** 2
    rest = tr[j + 1:]
    return dict(refused=px_in > pmax, rate=rate, ent=(ent["vt"], ent["vq"], ent["bps"]), hopf=0.997 ** (r["hops"] - 1), t0=t0,
                px=np.array([(vta / e["vt"]) ** 2 for e in rest]), age=np.array([e["t"] - t0 for e in rest]),
                sell=np.array([e["user"] == W4 and not e["buy"] for e in rest], dtype=bool), grad=np.array([e.get("real") == 0 for e in rest], dtype=bool),
                vt=np.array([float(e["vt"]) for e in rest]), vq=np.array([float(e["vq"]) for e in rest]), bps=np.array([float(e["bps"]) for e in rest]),
                last=(ent["t"] - t0))
def first(c):
    i = int(np.argmax(c)) if len(c) else 0
    return i if len(c) and c[i] else None
def model(p, stake, tp, hold, early, sl):
    """(net SOL, why, seconds held) for one prepared copy."""
    if p["refused"]: return (-0.0004, "refused", 0)
    vt0, vq0, bps0 = p["ent"]
    Q = stake * 1e9 * p["hopf"] / p["rate"]; net_in = Q * 1e4 / (1e4 + bps0); tok = vt0 - vt0 * vq0 / (vq0 + net_in)
    n = len(p["px"])
    if n == 0:                                               # no trade after ours: sold at the state we bought at
        vq_r = vq0 + net_in; vt_r = vt0 * vq0 / vq_r
        return ((vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - bps0 / 1e4) * p["rate"] * p["hopf"] / 1e9 - stake - 0.0026, "time", int(p["last"]))
    c = []                                                   # (trigger index, priority, why, exit one trade later)
    i = first(p["grad"]);                                    c += [(i, 0, "graduated", 0)] if i is not None else []
    if early:
        i = first(p["sell"] & (p["age"] >= early[0]) & (p["age"] < early[1]) & (p["px"] < early[2])); c += [(i, 1, "its_sell", 1)] if i is not None else []
    if tp: i = first(p["px"] >= tp);                         c += [(i, 2, "tp", 1)] if i is not None else []
    if sl: i = first(p["px"] <= sl);                         c += [(i, 3, "stop", 1)] if i is not None else []
    i = first(p["age"] >= hold);                             c += [(i, 4, "time", 0)] if i is not None else []
    if c:
        i, _, why, d = min(c); ex = min(i + d, n - 1)
    else:
        why, ex = "time", n - 1
    vq_r = p["vq"][ex] + net_in; vt_r = p["vt"][ex] * p["vq"][ex] / vq_r
    out = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - p["bps"][ex] / 1e4)
    return (out * p["rate"] * p["hopf"] / 1e9 - stake - 0.0026, why, int(p["age"][ex]))
