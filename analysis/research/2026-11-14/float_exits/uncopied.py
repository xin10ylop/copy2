# What the bot still does not copy (the owner, Nov 14), since Oct 29 12:02 UTC: wallet 4's 1.45+ SOL buys with no
# route by the token it paid with, its own result on them (its SOL and tokens in and out per coin, tokens at
# prices.json; coins still held or traded with another coin in one transaction left out), and its buys left
# unpriced (paid in a token prices.json does not have).
#   python3 -I uncopied.py SPD
import sys, os, re, json, collections, datetime
SPD = sys.argv[1]; W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"; WSOL = "So11111111111111111111111111111111111111112"
T0 = 1793274720 + 600; px = json.load(open(f"{SPD}/prices.json"))
bt, trips, mixed, last = {}, collections.defaultdict(lambda: dict(spent=0.0, back=0.0, held=0)), set(), 0
for f in os.listdir(f"{SPD}/w4tx"):
    t = json.load(open(f"{SPD}/w4tx/{f}")); m = t["meta"]; bt[t["slot"]] = t["blockTime"]; last = max(last, t["blockTime"])
    if m.get("err") or t["blockTime"] < T0 - 3600: continue
    ks = t["transaction"]["message"]["accountKeys"] + sum(((m.get("loadedAddresses") or {}).get(x, []) for x in ("writable", "readonly")), [])
    if W4 not in ks: continue
    i = ks.index(W4); d = collections.defaultdict(int)
    for k, s in (("preTokenBalances", -1), ("postTokenBalances", 1)):
        for b in m.get(k) or []:
            if b.get("owner") == W4: d[b["mint"]] += s * int(b["uiTokenAmount"]["amount"])
    d = {k: v for k, v in d.items() if v}; sol = m["postBalances"][i] - m["preBalances"][i] + d.pop(WSOL, 0)
    coins = [k for k in d if k not in px]
    if len(coins) != 1: mixed.update(coins); continue
    c = coins[0]; tr = trips[c]; v = sol + sum(a * px[k] for k, a in d.items() if k != c); tr["held"] += d[c]
    if d[c] > 0: tr["spent"] += -v
    else: tr["back"] += v
by8 = {}
for c in trips: by8.setdefault(c[:8], c)
days = (last - T0) / 86400
G = collections.defaultdict(list); unp = collections.Counter(); n_ok = 0
for l in open(f"{SPD}/scan_hops.out"):
    u = re.match(r"(\d+) (\S{8}) unpriced: paid in (\S+)", l)
    if u:
        if bt.get(int(u.group(1)), 0) >= T0: unp[u.group(3)] += 1
        continue
    g = re.match(r"(\d+) (\S{8}) ([\d.]+) SOL from (\S+) quote (\S+) jupiter (\S+): (ROUTABLE|no route)(.*)", l)
    if not g or bt.get(int(g.group(1)), 0) < T0: continue
    if g.group(7) == "ROUTABLE": n_ok += 1; continue
    G[g.group(4)[:8]].append(g.group(2))
print(f"since Oct 29 14:02 Beirut ({days:.1f} days): {n_ok} buys of 1.45+ SOL have a route ({n_ok / days:.1f} a day); {sum(len(v) for v in G.values())} have none ({sum(len(v) for v in G.values()) / days:.1f} a day)")
print(f"   {'paid with':9s} {'buys':>4s} {'a day':>5s} | its own result: coins, spent SOL, net SOL, %, won")
tot = [0, 0.0, 0.0, 0]
for k, v in sorted(G.items(), key=lambda kv: -len(kv[1])):
    c = [trips[by8[m]] for m in dict.fromkeys(v) if m in by8 and by8[m] not in mixed and trips[by8[m]]["held"] == 0 and trips[by8[m]]["spent"] > 0]
    sp = sum(x["spent"] for x in c) / 1e9; net = sum(x["back"] - x["spent"] for x in c) / 1e9; won = sum(1 for x in c if x["back"] > x["spent"])
    tot[0] += len(c); tot[1] += sp; tot[2] += net; tot[3] += won
    if len(v) >= 4: print(f"   {k:9s} {len(v):4d} {len(v) / days:5.1f} | {len(c):3d} {sp:6.1f} {net:+6.2f} {100 * net / sp if sp else 0:+6.1f}% {won:3d}")
print(f"   {'all':9s} {sum(len(v) for v in G.values()):4d} {sum(len(v) for v in G.values()) / days:5.1f} | {tot[0]:3d} {tot[1]:6.1f} {tot[2]:+6.2f} {100 * tot[2] / tot[1]:+6.1f}% {tot[3]:3d}   ({len(G)} tokens; those with under 4 buys not listed)")
print(f"its buys left unpriced (any size; paid in a token not in prices.json): {sum(unp.values())} ({sum(unp.values()) / days:.1f} a day): {unp.most_common(8)}")
