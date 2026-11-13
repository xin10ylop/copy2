# PUMP's price in SOL by day, from wallet 4's own swaps of SOL for PUMP and back (0.2+ SOL, only SOL and PUMP moved).
#   python3 -I pump_rate.py SPD/tx
import os, sys, json, collections, datetime, statistics
W = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"; WS = "So11111111111111111111111111111111111111112"
TX = sys.argv[1]; out = collections.defaultdict(list)
for f in os.listdir(TX):
    t = json.load(open(f"{TX}/{f}")); m = t["meta"]
    if m.get("err"): continue
    ks = t["transaction"]["message"]["accountKeys"] + sum(((m.get("loadedAddresses") or {}).get(x, []) for x in ("writable", "readonly")), [])
    if W not in ks: continue
    i = ks.index(W); d = collections.defaultdict(int)
    for k, s in (("preTokenBalances", -1), ("postTokenBalances", 1)):
        for b in m.get(k) or []:
            if b.get("owner") == W: d[b["mint"]] += s * int(b["uiTokenAmount"]["amount"])
    d = {k: v for k, v in d.items() if v}; sol = m["postBalances"][i] - m["preBalances"][i] + d.pop(WS, 0)
    if len(d) == 1 and list(d)[0].startswith("pumpCmXq") and abs(sol) > 2e8 and (sol > 0) != (list(d.values())[0] > 0):
        day = datetime.datetime.fromtimestamp(t["blockTime"], datetime.timezone.utc).strftime("%m-%d")
        out[day].append(abs(sol) / 1e9 / (abs(list(d.values())[0]) / 1e6))
for day in sorted(out):
    r = out[day]
    print(day, f"{len(r):3d} swaps  median {statistics.median(r) * 1e6:.1f} SOL a million PUMP  (min {min(r) * 1e6:.1f}, max {max(r) * 1e6:.1f})")
