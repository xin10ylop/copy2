# Our copy of wallet 4's 3-hop buys since the stop (skipped_groups.py -> SPD/toolong.json), as if the bot could route
# 3 hops: the coins' paths (31 minutes, model.py's fetcher on Triton) and the live rule (tp 2.4, 30 min, no stop,
# holding through its sale), with one more pool hop each way than model.py charges (another 0.3% in and out).
# 1 SOL, every copy (no slot limit) and 2 open with the routable ones; landings 4 / 8 / one block late; raw and
# without the best 2.
#   python3 -I hops3_copy.py SPD
import sys, os, io, contextlib, json, gzip
SPD = sys.argv[1]
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv = ["x", SPD]; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import exit_search as E
M = E.M
rows = json.load(open(f"{SPD}/toolong.json"))
p3 = f"{SPD}/paths_3hop.json.gz"
P3 = json.load(gzip.open(p3)) if os.path.exists(p3) else {}
for r in rows:
    k = f"{r['slot']}_{r['mint8']}"
    if k not in P3:
        try:
            res = M.path(r)
            if res: P3[k] = res
        except Exception as e: print("path failed", r["mint8"], str(e)[:60])
json.dump(P3, gzip.open(p3, "wt"))
E.G.P.update(P3)
H = 0.997 * 0.997                                     # one more pool hop in and out
rows = [r for r in rows if f"{r['slot']}_{r['mint8']}" in P3]
print(f"{len(rows)} 3-hop buys with a path")
LIVE = dict(tp=2.4, sl=None, hold=1790, follow=None, pmax=1.25, trail=None)
for n in E.LAND:
    v = []
    for r in rows:
        o = E.model(r, n, **LIVE)
        if o and o[1] != "refused": v.append(((o[0] + 1.0026) * H - 1.0026, o[1]))
    s = sorted((x[0] for x in v), reverse=True)
    print(f"  landing {str(n):6s}: {len(v)} copies, net {sum(s):+.2f} SOL ({100*sum(s)/max(1,len(v)):+.1f}% a copy), without the best 2 {sum(s[2:]):+.2f}; "
          f"tp {sum(1 for x in v if x[1]=='tp')}, won {sum(1 for x in s if x > 0)}")
# with the routable ones, 2 open, as the bot would run (raw, mean of landings)
both = sorted([r for r in E.A + E.B] + rows, key=lambda r: r["t"]); h3 = {id(r) for r in rows}
def sim(rs, n):
    out, open_ = [], []
    for r in rs:
        open_ = [x for x in open_ if x > r["t"]]
        if len(open_) >= 2: continue
        o = E.model(r, n, **LIVE)
        if o is None: continue
        net = (o[0] + 1.0026) * H - 1.0026 if id(r) in h3 and o[1] != "refused" else o[0]
        if o[1] != "refused": open_.append(r["t"] + o[2])
        out.append(net)
    return sum(out), sum(sorted(out, reverse=True)[2:])
for name, rs in (("routable only (live)", E.A + E.B), ("routable + 3-hop", both)):
    x = [sim(sorted(rs, key=lambda r: r["t"]), n) for n in E.LAND]
    print(f"  2 open, two weeks, {name:22s}: {sum(a for a, _ in x)/3:+.2f} SOL (without the best 2 {sum(b for _, b in x)/3:+.2f}), mean of 3 landings")
