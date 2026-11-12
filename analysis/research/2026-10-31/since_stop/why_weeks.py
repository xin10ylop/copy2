# Why the live rule made +10.6 SOL (raw model) on Oct 29-Nov 5 and +0.1 on Nov 5-12: wallet 4's own result each week,
# and our copies split by exit. Hold, tp 2.5, no stop, 30 min, limit 1.25, 1 SOL, 2 open, landing 4.
#   python3 -I why_weeks.py SPD
import sys, os, io, contextlib, json, statistics
SPD = sys.argv[1]; here = os.path.dirname(os.path.abspath(__file__))
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv = ["x", SPD]; sys.path.insert(0, here); import exit_search as E
W4 = E.M.W4; WSOL = "So11111111111111111111111111111111111111112"; WB = "3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh"
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
    if list(mv) == [WB] and abs(sol) > 0.05: rates.append((t["blockTime"], abs(sol * 1e9 / mv[WB])))
    txs.append((t["blockTime"], sol, mv))
for nm, rs in (("week 1 (Oct 29 14:02 - Nov 5 08:49)", E.A), ("week 2 (Nov 5 08:49 - Nov 12 08:49)", E.B)):
    t0, t1 = min(r["t"] for r in rs), max(r["t"] for r in rs) + 1; mints = {r["mint8"] for r in rs}
    R = statistics.median(x for t, x in rates if t0 - 86400 <= t <= t1 + 86400) / 1e9
    his = {}
    for t, sol, mv in txs:
        cs = [k for k in mv if k != WB]
        if len(cs) != 1 or cs[0][:8] not in mints: continue
        c = his.setdefault(cs[0][:8], [0.0, 0.0]); v = sol + mv.get(WB, 0) * R; c[0] += v
        if mv[cs[0]] > 0: c[1] += -v
    hv = [c for c in his.values() if c[1] > 0]; hs = sorted((c[0] for c in hv), reverse=True)
    print(f"{nm}: {len(rs)} buys")
    print(f"  wallet 4 real: {len(hv)} coins, spent {sum(c[1] for c in hv):.1f} SOL, net {sum(hs):+.2f} ({100*sum(hs)/sum(c[1] for c in hv):+.1f}%), "
          f"without its best 2 {sum(hs[2:]):+.2f}, won {sum(1 for x in hs if x > 0)}")
    out, open_, pk = [], [], []
    for r in rs:
        open_ = [x for x in open_ if x > r["t"]]
        if len(open_) >= 2: continue
        o = E.model(r, 4, tp=2.5, sl=None, hold=1790, follow=None, pmax=1.25, trail=None)
        if o is None: continue
        if o[1] != "refused": open_.append(r["t"] + o[2])
        out.append(o)
    v = sorted((o[0] for o in out), reverse=True)
    print(f"  us, raw model: {len(out)} copies, net {sum(v):+.2f}, without the best 2 {sum(v[2:]):+.2f}; best two {v[0]:+.2f} {v[1]:+.2f}")
    for ex in ("tp", "time", "refused", "graduated"):
        x = [o[0] for o in out if o[1] == ex]
        if x: print(f"    {ex:9s} {len(x):3d} copies, {sum(x):+6.2f} SOL, {sum(x)/len(x):+.3f} each")
    print(f"    reached take profit: {100*sum(1 for o in out if o[1]=='tp')/len([o for o in out if o[1]!='refused']):.0f}% of copies")
