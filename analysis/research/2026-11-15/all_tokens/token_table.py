# With every token wallet 4 pays with held as a float (scan_all.out): its 1.45+ SOL buys since Oct 29 12:02 UTC by
# the token we would pay with, a day, and its own result on them (SOL and tokens in and out per coin at
# prices_full2.json; coins still held or traded with another coin in one transaction left out).
#   python3 -I token_table.py SPD
import sys, os, re, json, collections
SPD = sys.argv[1]; W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"; WSOL = "So11111111111111111111111111111111111111112"
T0 = 1793274720 + 600; px = json.load(open(f"{SPD}/prices_full2.json"))
bt, trips, mixed, last = {}, collections.defaultdict(lambda: dict(spent=0.0, back=0.0, held=0)), set(), 0
for f in os.listdir(f"{SPD}/w4tx"):
    s = int(f.split("_")[0])
    if s < 463000000: continue
    t = json.load(open(f"{SPD}/w4tx/{f}")); m = t["meta"]; bt[t["slot"]] = t["blockTime"]; last = max(last, t["blockTime"])
    if m.get("err"): continue
    ks = t["transaction"]["message"]["accountKeys"] + sum(((m.get("loadedAddresses") or {}).get(x, []) for x in ("writable", "readonly")), [])
    if W4 not in ks: continue
    i = ks.index(W4); d = collections.defaultdict(int)
    for k, sg in (("preTokenBalances", -1), ("postTokenBalances", 1)):
        for b in m.get(k) or []:
            if b.get("owner") == W4: d[b["mint"]] += sg * int(b["uiTokenAmount"]["amount"])
    d = {k: v for k, v in d.items() if v}; sol = m["postBalances"][i] - m["preBalances"][i] + d.pop(WSOL, 0)
    coins = [k for k in d if k not in px]
    if len(coins) != 1: mixed.update(coins); continue
    c = coins[0]; tr = trips[c]; v = sol + sum(a * px[k] for k, a in d.items() if k != c); tr["held"] += d[c]
    if d[c] > 0: tr["spent"] += -v
    else: tr["back"] += v
by8 = {}
for c in trips: by8.setdefault(c[:8], c)
days = (last - T0) / 86400; G = collections.defaultdict(list); full = {k[:8]: k for k in px}
for l in open(f"{SPD}/scan_all.out"):
    g = re.match(r"(\d+) (\S{8}) ([\d.]+) SOL from (\S+) quote (\S+) jupiter (\S+): ROUTABLE hops (\d+) how (\S+) .*?input: (\w{8})", l)
    if not g or bt.get(int(g.group(1)), 0) < T0: continue
    G[g.group(9)].append(g.group(2))
rows = []
for k, v in G.items():
    c = [trips[by8[m]] for m in dict.fromkeys(v) if m in by8 and by8[m] not in mixed and trips[by8[m]]["held"] == 0 and trips[by8[m]]["spent"] > 0]
    sp = sum(x["spent"] for x in c) / 1e9; net = sum(x["back"] - x["spent"] for x in c) / 1e9
    rows.append((k, len(v), len(c), sp, net, sum(1 for x in c if x["back"] > x["spent"]), sorted((x["back"] - x["spent"]) / 1e9 for x in c)))
rows.sort(key=lambda r: -r[1])
print(f"since Oct 29 14:02 Beirut ({days:.1f} days); its 1.45+ SOL buys by what we would pay with, every paying token a float")
print(f"   {'pays with':9s} {'buys':>4s} {'a day':>5s} | its own: coins, spent, net SOL, %, won, net without its best 2")
json.dump({full.get(k, k): n for k, n, *_ in rows}, open(f"{SPD}/route_tokens.json", "w"))
for k, n, nc, sp, net, won, v in rows:
    if n >= 5: print(f"   {k:9s} {n:4d} {n / days:5.1f} | {nc:3d} {sp:6.1f} {net:+6.2f} {100 * net / sp if sp else 0:+6.1f}% {won:3d} {sum(v[:-2]):+6.2f}")
print(f"   all       {sum(r[1] for r in rows):4d} {sum(r[1] for r in rows) / days:5.1f}; tokens with under 5 buys: {sum(1 for r in rows if r[1] < 5)} ({sum(r[1] for r in rows if r[1] < 5)} buys)")
