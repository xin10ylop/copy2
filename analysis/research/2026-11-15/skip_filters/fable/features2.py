# Step 1b: more of wallet 4's own state at each buy, from its transactions alone (no model): seconds since its last
# buy of any size and of any coin (gap_any), its buys of any size in the last 5 / 30 / 60 min, its position in a
# "session" (buys less than 30 min apart), how many coins it holds at that moment, seconds since its last sale, and
# its result on the last 3 and 10 coins it sold out of. Adds them to SKIPQ/features.json.
#   python3 -I features2.py SPD SKIPQ
import sys, os, json, collections, bisect
SPD, SKIPQ = sys.argv[1], sys.argv[2]; W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"; WSOL = "So11111111111111111111111111111111111111112"
px = json.load(open(f"{SPD}/prices.json")); ev = []          # (time, coin, +1 buy / -1 sell, SOL value)
trips = collections.defaultdict(lambda: dict(spent=0.0, back=0.0, held=0, first=None, last=None))
for f in os.listdir(f"{SPD}/w4tx"):
    t = json.load(open(f"{SPD}/w4tx/{f}")); m = t["meta"]
    if m.get("err"): continue
    ks = t["transaction"]["message"]["accountKeys"] + sum(((m.get("loadedAddresses") or {}).get(x, []) for x in ("writable", "readonly")), [])
    if W4 not in ks: continue
    i = ks.index(W4); d = collections.defaultdict(int)
    for k, s in (("preTokenBalances", -1), ("postTokenBalances", 1)):
        for b in m.get(k) or []:
            if b.get("owner") == W4: d[b["mint"]] += s * int(b["uiTokenAmount"]["amount"])
    d = {k: v for k, v in d.items() if v}; sol = m["postBalances"][i] - m["preBalances"][i] + d.pop(WSOL, 0)
    coins = [k for k in d if k not in px]
    if len(coins) != 1: continue
    c = coins[0]; v = sol + sum(a * px[k] for k, a in d.items() if k != c); bt = t["blockTime"]; tr = trips[c]; tr["held"] += d[c]
    if d[c] > 0: ev.append((bt, c, 1, -v / 1e9)); tr["spent"] += -v; tr["first"] = min(tr["first"] or bt, bt)
    else: ev.append((bt, c, -1, v / 1e9)); tr["back"] += v; tr["last"] = max(tr["last"] or bt, bt)
ev.sort(); buys = [e[0] for e in ev if e[2] == 1]; sells = [e[0] for e in ev if e[2] == -1]
closed = sorted((tr["last"], (tr["back"] - tr["spent"]) / tr["spent"]) for tr in trips.values() if tr["held"] == 0 and tr["spent"] > 0 and tr["last"])
ct = [c[0] for c in closed]
spans = sorted((tr["first"], tr["last"] or 1e18) for tr in trips.values() if tr["first"])
D = json.load(open(f"{SKIPQ}/features.json"))
for f in D:
    t = f["t"]; i = bisect.bisect_left(buys, t)                 # buys strictly before t
    f["gap_any"] = t - buys[i - 1] if i else None
    for w, name in ((300, "any_5m"), (1800, "any_30m"), (3600, "any_60m")): f[name] = i - bisect.bisect_left(buys, t - w)
    j = bisect.bisect_left(sells, t); f["since_sell"] = t - sells[j - 1] if j else None
    n = 1; k = i - 1; prev = t
    while k >= 0 and prev - buys[k] < 1800: n += 1; prev = buys[k]; k -= 1
    f["session_pos"] = n; f["session_age"] = t - prev
    f["holding"] = sum(1 for a, b in spans if a < t < b)
    c = bisect.bisect_left(ct, t)
    for w, name in ((3, "w4_last3"), (10, "w4_last10")):
        x = [closed[q][1] for q in range(max(0, c - w), c)]; f[name] = sum(x) / len(x) if x else None
json.dump(D, open(f"{SKIPQ}/features.json", "w"))
print(len(D), "rows;", len(buys), "buys of any size,", len(sells), "sales")
