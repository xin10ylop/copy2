# Wallet 4's 1.45+ SOL buys since the stop (Oct 29 12:02 UTC) that the bot skips, by the scan's verdict (scan.out):
# no route because the route needs 3 hops ("TooLong"), or no pool reaches the quote ("NoAnchor"); against the routable
# ones we copy. Its own real result on each group (its SOL in and out per coin, WBTC at its own swap rate, coins it
# sold into another token left out), and the quote tokens. Also writes SPD/toolong.json for the path fetch.
#   python3 -I skipped_groups.py SPD
import sys, os, re, json, statistics, collections
SPD = sys.argv[1]; W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
WSOL = "So11111111111111111111111111111111111111112"; WB = "3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh"
T0 = 1793274720 + 600
txs, rates, bt, full = [], [], {}, {}
for f in os.listdir(f"{SPD}/w4tx"):
    t = json.load(open(f"{SPD}/w4tx/{f}")); m = t["meta"]; bt[t["slot"]] = t["blockTime"]
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
    for k in post: full.setdefault((t["slot"], k[:8]), k)
    sol = (m["postBalances"][i] - m["preBalances"][i]) / 1e9 + (post.get(WSOL, 0) - pre.get(WSOL, 0)) / 1e9
    mv = {k: post.get(k, 0) - pre.get(k, 0) for k in set(pre) | set(post) if k != WSOL and post.get(k, 0) != pre.get(k, 0)}
    if list(mv) == [WB] and abs(sol) > 0.05: rates.append(abs(sol * 1e9 / mv[WB]))
    txs.append((sol, mv))
R = statistics.median(rates) / 1e9
groups = collections.defaultdict(list); toolong = []
for l in open(f"{SPD}/scan.out"):
    m = re.match(r"(\d+) (\S{8}) ([\d.]+) SOL from (\S+) quote (\S+) jupiter (\S+): (ROUTABLE|no route)(.*)", l)
    if not m or bt.get(int(m.group(1)), 0) < T0: continue
    g = "routable" if m.group(7) == "ROUTABLE" else ("3 hops" if "TooLong" in m.group(8) else "no pool")
    groups[g].append((m.group(2), m.group(5), m.group(4)))
    if g == "3 hops":
        toolong.append(dict(slot=int(m.group(1)), t=bt[int(m.group(1))], mint8=m.group(2), sol=float(m.group(3)), frm=m.group(4), quote=m.group(5), ok=True))
json.dump(toolong, open(f"{SPD}/toolong.json", "w"))
his = {}
for sol, mv in txs:
    cs = [k for k in mv if k != WB]
    if len(cs) != 1: 
        for k in cs: his.setdefault(k[:8], [0, 0, True])[2] = True
        continue
    c = his.setdefault(cs[0][:8], [0.0, 0.0, False]); v = sol + mv.get(WB, 0) * R; c[0] += v
    if mv[cs[0]] > 0: c[1] += -v
print(f"since Oct 29 12:02 UTC; WBTC at {R*1e9:.0f} lamports a unit")
print(f"{'group':10s} {'buys':>5s} | its real: coins, spent, net, %, won, without its best 2 | quotes")
for g in ("routable", "3 hops", "no pool"):
    c = [his[m8] for m8, _, _ in groups[g] if m8 in his and not his[m8][2] and his[m8][1] > 0]
    v = sorted((x[0] for x in c), reverse=True); sp = sum(x[1] for x in c)
    q = collections.Counter(x[1][:8] for x in groups[g]).most_common(5)
    print(f"{g:10s} {len(groups[g]):5d} | {len(c):3d} {sp:7.1f} {sum(v):+7.2f} {100*sum(v)/sp if sp else 0:+6.1f}% {sum(1 for x in v if x > 0):3d} {sum(v[2:]):+7.2f} | {q}")
