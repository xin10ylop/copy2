# Wallet 4's last two weeks (Oct 29 12:02 - Nov 12 06:49 UTC) copied with the bot as it runs on Nov 13: 0.5 SOL,
# 2 open, tp 2.4, 30 min, no stop, its sale followed only at 30-180 s under 1.5x, 3-hop routes (one more pool hop
# each way charged on them). Raw model at 0.5 SOL (model.py's quotes, stake 0.5), mean over landing 4 / 8 / one
# block late, and corrected with the gap measured on wallet 4 itself (lookalikes copyscore: +7.4 points a copy in
# week 1, +8.5 in week 2).
#   python3 -I live_rule_05.py SPD
import sys, os, io, contextlib, json, gzip
SPD = sys.argv[1]
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv = ["x", SPD]; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import exit_search as E
M = E.M; G = E.G
P3 = json.load(gzip.open(f"{SPD}/paths_3hop.json.gz")); G.P.update(P3)
H3 = {k for k in P3}
STAKE = float(os.environ.get("STAKE", "0.5")); GAP = {"w1": 0.074, "w2": 0.085}
def model(r, n, tp=2.4, hold=1790, a=30, b=180, below=1.5, pmax=1.25):
    m, tr = G.P[f"{r['slot']}_{r['mint8']}"]
    k = next((i for i, e in enumerate(tr) if e["user"] == M.W4 and e["buy"] and e["slot"] == r["slot"]), None)
    if k is None: return None
    its = tr[k]; vta = its["vt"]; t0 = its["t"]; rate = r["sol"] * 1e9 / (its["q"] * (1 + its["bps"] / 1e4))
    j = k + len([e for e in tr[k + 1:] if e["slot"] <= its["slot"] + 1]) if n == "slot+1" else min(k + n, len(tr) - 1)
    ent = tr[j]; px_in = (vta / ent["vt"]) ** 2
    if px_in > pmax: return (-0.0004, "refused", 0)
    hops = 0.997 if f"{r['slot']}_{r['mint8']}" in H3 else 1.0
    Q = STAKE * 1e9 * (1 - 0.003) * hops / rate; net_in = Q * 1e4 / (1e4 + ent["bps"])
    tok = ent["vt"] - ent["vt"] * ent["vq"] / (ent["vq"] + net_in)
    ex, why = None, "time"
    for i in range(j + 1, len(tr)):
        e = tr[i]; px = (vta / e["vt"]) ** 2; age = e["t"] - t0
        if e.get("real") == 0: why, ex = "graduated", i; break
        if e["user"] == M.W4 and not e["buy"] and a <= age < b and px < below: why, ex = "its_sell", min(i + 1, len(tr) - 1); break
        if px >= tp: why, ex = "tp", min(i + 1, len(tr) - 1); break
        if age >= hold: why, ex = "time", i; break
    if ex is None: ex = len(tr) - 1
    x = tr[ex]; vq_r = x["vq"] + net_in; vt_r = x["vt"] * x["vq"] / vq_r
    out = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - x["bps"] / 1e4)
    return (out * rate * (1 - 0.003) * hops / 1e9 - STAKE - 0.0026, why, x["t"] - t0)
rows3 = [r for r in json.load(open(f"{SPD}/toolong.json")) if f"{r['slot']}_{r['mint8']}" in P3]
END = max(r["t"] for r in G.trips); MID = END - 7 * 86400
allr = sorted(G.trips + rows3, key=lambda r: r["t"])
W = {"w1": [r for r in allr if r["t"] < MID], "w2": [r for r in allr if MID <= r["t"] <= END]}
def sim(rs, n):
    out, open_ = [], []
    for r in rs:
        open_ = [x for x in open_ if x > r["t"]]
        if len(open_) >= 2: continue
        o = model(r, n)
        if o is None: continue
        if o[1] != "refused": open_.append(r["t"] + o[2])
        out.append(o)
    v = sorted((o[0] for o in out), reverse=True); c = sum(1 for o in out if o[1] != "refused")
    return sum(v), sum(v[2:]), c
print(f"wallet 4 copied as the bot runs on Nov 13, {STAKE} SOL, 2 open; mean of landings 4 / 8 / one block late")
tot = [0, 0, 0]
for w in ("w1", "w2"):
    x = [sim(W[w], n) for n in E.LAND]; raw = sum(a for a, _, _ in x) / 3; r2 = sum(b for _, b, _ in x) / 3; c = sum(z for _, _, z in x) / 3
    corr = raw + GAP[w] * STAKE * c
    tot = [tot[0] + raw, tot[1] + r2, tot[2] + corr]
    print(f"  {w}: {c:.0f} copies, raw {raw:+.2f} SOL (without the best 2 {r2:+.2f}), corrected {corr:+.2f}")
print(f"  both: raw {tot[0]:+.2f} (without the best 2s {tot[1]:+.2f}), corrected {tot[2]:+.2f}")
