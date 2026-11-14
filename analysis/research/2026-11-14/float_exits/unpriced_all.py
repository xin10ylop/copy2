# The buys the scan leaves "unpriced" since Oct 29 12:02 UTC (paid in a token prices.json lacks): valued at Jupiter's
# price today, how many are 1.45+ SOL, by token, and wallet 4's own result on those coins. Writes SPD/prices_all.json.
#   python3 -I unpriced_all.py SPD
import sys, os, re, json, collections, urllib.request
SPD = sys.argv[1]; W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"; WSOL = "So11111111111111111111111111111111111111112"
T0 = 1793274720 + 600; px = json.load(open(f"{SPD}/prices.json"))
want = {}
for l in open(f"{SPD}/scan_hops.out"):
    u = re.match(r"(\d+) (\S{8}) unpriced: paid in (\S+)", l)
    if u: want[int(u.group(1)), u.group(2)] = u.group(3)[:8]
txs, full, dec, last = [], {}, {}, 0
for f in os.listdir(f"{SPD}/w4tx"):
    t = json.load(open(f"{SPD}/w4tx/{f}")); m = t["meta"]; last = max(last, t["blockTime"])
    if m.get("err") or t["blockTime"] < T0 - 3600: continue
    ks = t["transaction"]["message"]["accountKeys"] + sum(((m.get("loadedAddresses") or {}).get(x, []) for x in ("writable", "readonly")), [])
    if W4 not in ks: continue
    i = ks.index(W4); d = collections.defaultdict(int)
    for k, s in (("preTokenBalances", -1), ("postTokenBalances", 1)):
        for b in m.get(k) or []:
            dec[b["mint"]] = b["uiTokenAmount"]["decimals"]
            if b.get("owner") == W4: d[b["mint"]] += s * int(b["uiTokenAmount"]["amount"])
    d = {k: v for k, v in d.items() if v}; sol = m["postBalances"][i] - m["preBalances"][i] + d.pop(WSOL, 0)
    txs.append((t["slot"], t["blockTime"], sol, d))
    for k in d: full.setdefault(k[:8], k)
pay = sorted({full[p] for p in set(want.values()) if p in full})
jp = {}
for i in range(0, len(pay), 40):
    jp.update(json.load(urllib.request.urlopen("https://lite-api.jup.ag/price/v3?ids=" + ",".join(pay[i:i + 40] + [WSOL]), timeout=30)))
solusd = jp[WSOL]["usdPrice"]
for m in pay:
    if m in jp and jp[m].get("usdPrice"): px[m] = jp[m]["usdPrice"] / solusd * 1e9 / 10 ** dec[m]
json.dump(px, open(f"{SPD}/prices_all.json", "w"))
trips, mixed, big = collections.defaultdict(lambda: dict(spent=0.0, back=0.0, held=0)), set(), collections.defaultdict(list)
for slot, bt, sol, d in txs:
    coins = [k for k in d if k not in px]
    if len(coins) != 1: mixed.update(coins); continue
    c = coins[0]; tr = trips[c]; v = sol + sum(a * px[k] for k, a in d.items() if k != c); tr["held"] += d[c]
    if d[c] > 0:
        tr["spent"] += -v
        if (slot, c[:8]) in want and bt >= T0 and -v >= 1.45e9: big[want[slot, c[:8]]].append(c)
    else: tr["back"] += v
days = (last - T0) / 86400; n = sum(len(v) for v in big.values())
print(f"{sum(1 for (s, c), p in want.items())} unpriced buys in the scan (all dates); priced now {len([m for m in pay if m in px])} of {len(pay)} tokens (SOL ${solusd:.2f})")
print(f"since Oct 29 14:02 Beirut: {n} of them are 1.45+ SOL at today's price ({n / days:.1f} a day)")
print(f"   {'paid with':9s} {'buys':>4s} {'a day':>5s} | its own result: coins, spent SOL, net SOL, %, won")
tot = [0, 0.0, 0.0, 0]
for k, v in sorted(big.items(), key=lambda kv: -len(kv[1])):
    c = [trips[m] for m in dict.fromkeys(v) if m not in mixed and trips[m]["held"] == 0 and trips[m]["spent"] > 0]
    sp = sum(x["spent"] for x in c) / 1e9; net = sum(x["back"] - x["spent"] for x in c) / 1e9; won = sum(1 for x in c if x["back"] > x["spent"])
    tot[0] += len(c); tot[1] += sp; tot[2] += net; tot[3] += won
    if len(v) >= 3: print(f"   {k:9s} {len(v):4d} {len(v) / days:5.1f} | {len(c):3d} {sp:6.1f} {net:+6.2f} {100 * net / sp if sp else 0:+6.1f}% {won:3d}")
print(f"   {'all':9s} {n:4d} {n / days:5.1f} | {tot[0]:3d} {tot[1]:6.1f} {tot[2]:+6.2f} {100 * tot[2] / max(tot[1], 1e-9):+6.1f}% {tot[3]:3d}")
