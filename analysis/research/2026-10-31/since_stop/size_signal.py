# Does wallet 4's bet size say anything? Oct 29 14:02 to Nov 12 08:49 Beirut, its 1.45+ SOL buys we can copy. By size
# band: its own real result (SOL in and out, WBTC at its own swap rate), and our copy (live rule, raw model, 1 SOL,
# every coin, landing 4). Then two ways to use it, picked on week 1 and scored on week 2 (2 open, 1 SOL base):
# only copy buys of S+ SOL; and a stake that grows with its size.
#   python3 -I size_signal.py SPD
import sys, os, io, contextlib, json, statistics
SPD = sys.argv[1]; here = os.path.dirname(os.path.abspath(__file__))
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv = ["x", SPD]; sys.path.insert(0, here); import exit_search as E
W4 = E.M.W4; WSOL = "So11111111111111111111111111111111111111112"; WB = "3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh"
ALL = E.A + E.B; mints = {r["mint8"]: r for r in ALL}
txs, rates = [], []
for f in os.listdir(f"{SPD}/w4tx"):
    t = json.load(open(f"{SPD}/w4tx/{f}")); m = t["meta"]
    if m.get("err"): continue
    ks = t["transaction"]["message"]["accountKeys"] + sum(((m.get("loadedAddresses") or {}).get(x, []) for x in ("writable", "readonly")), [])
    if W4 not in ks: continue
    i = ks.index(W4)
    def tb(w):
        d = {}
        for b in m.get(w) or []:
            if b.get("owner") == W4: d[b["mint"]] = d.get(b["mint"], 0) + int(b["uiTokenAmount"]["amount"])
        return d
    pre, post = tb("preTokenBalances"), tb("postTokenBalances")
    sol = (m["postBalances"][i] - m["preBalances"][i]) / 1e9 + (post.get(WSOL, 0) - pre.get(WSOL, 0)) / 1e9
    mv = {k: post.get(k, 0) - pre.get(k, 0) for k in set(pre) | set(post) if k != WSOL and post.get(k, 0) != pre.get(k, 0)}
    if list(mv) == [WB] and abs(sol) > 0.05: rates.append(abs(sol * 1e9 / mv[WB]))
    txs.append((sol, mv))
R = statistics.median(rates) / 1e9; his = {}
for sol, mv in txs:
    cs = [k for k in mv if k != WB]
    if len(cs) != 1 or cs[0][:8] not in mints: continue
    c = his.setdefault(cs[0][:8], [0.0, 0.0]); v = sol + mv.get(WB, 0) * R; c[0] += v
    if mv[cs[0]] > 0: c[1] += -v
LIVE = dict(tp=2.5, sl=None, hold=1790, follow=None, pmax=1.25, trail=None)
ours = {r["mint8"]: E.model(r, 4, **LIVE) for r in ALL}
print(f"{len(ALL)} buys, sizes: median {statistics.median(r['sol'] for r in ALL):.2f} SOL, "
      f"quartiles {[round(x, 2) for x in statistics.quantiles([r['sol'] for r in ALL], n=4)]}")
BANDS = ((1.45, 1.6), (1.6, 1.8), (1.8, 2.0), (2.0, 2.5), (2.5, 99))
print(f"\n{'its size':10s} {'buys':>5s} | {'its real %':>10s} {'won':>5s} | {'our copy: net/copy':>18s} {'tp hit':>7s} {'w/o best 2':>10s} | week 1 / week 2 (our net/copy)")
for lo, hi in BANDS:
    rs = [r for r in ALL if lo <= r["sol"] < hi]
    h = [his[r["mint8"]] for r in rs if r["mint8"] in his and his[r["mint8"]][1] > 0]
    o = [ours[r["mint8"]] for r in rs if ours[r["mint8"]] and ours[r["mint8"]][1] != "refused"]
    v = sorted((x[0] for x in o), reverse=True)
    w = [[ours[r["mint8"]][0] for r in rs if r in W and ours[r["mint8"]] and ours[r["mint8"]][1] != "refused"] for W in (E.A, E.B)]
    print(f"{lo:.2f}-{hi if hi < 99 else '':<5} {len(rs):5d} | {100*sum(x[0] for x in h)/sum(x[1] for x in h):+9.1f}% {sum(1 for x in h if x[0] > 0):2d}/{len(h):<2d} | "
          f"{sum(v)/len(v):+17.3f} {100*sum(1 for x in o if x[1]=='tp')/len(o):6.0f}% {sum(v[2:])/len(v):+10.3f} | "
          + " / ".join(f"{sum(x)/len(x):+.3f} ({len(x)})" if x else "-" for x in w))
def sim(rs, n, stake_of, keep=lambda r: True):
    out, open_ = [], []
    for r in rs:
        if not keep(r): continue
        open_ = [x for x in open_ if x > r["t"]]
        if len(open_) >= 2: continue
        o = E.model(r, n, **LIVE)
        if o is None: continue
        if o[1] != "refused": open_.append(r["t"] + o[2])
        out.append((o[0] * stake_of(r), o[1]))
    v = sorted((x[0] for x in out), reverse=True); took = sum(1 for x in out if x[1] != "refused")
    return took, sum(v), sum(v[2:])
print("\nRules, 2 open, raw model, mean over landing 4 / 8 / one block late: copies, net (w/o best 2); and with the 9.1-point yardstick")
print(f"   {'rule':40s} | week 1                       | week 2")
rules = [("live: every 1.45+ buy, 1 SOL", lambda r: 1.0, lambda r: True)]
for s in (1.6, 1.8, 2.0): rules.append((f"only its buys of {s}+ SOL", lambda r: 1.0, lambda r, s=s: r["sol"] >= s))
rules.append(("stake = its size / 1.8 (0.8-1.4 SOL)", lambda r: min(max(r["sol"] / 1.8, 0.8), 1.4), lambda r: True))
rules.append(("1.5 SOL on its 2.0+ buys, 1 below", lambda r: 1.5 if r["sol"] >= 2.0 else 1.0, lambda r: True))
for name, st, keep in rules:
    cells = []
    for W in (E.A, E.B):
        x = [sim(W, n, st, keep) for n in E.LAND]; c = sum(a[0] for a in x) / 3; s = sum(a[1] for a in x) / 3; s2 = sum(a[2] for a in x) / 3
        stake = sum(st(r) for r in W if keep(r)) / max(1, sum(1 for r in W if keep(r)))
        cells.append(f"{c:5.1f} {s:+6.2f} ({s2:+6.2f}) yard {s + 0.091 * c * stake:+6.2f}")
    print(f"   {name:40s} | " + " | ".join(cells))
