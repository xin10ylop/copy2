# Every token wallet 4 paid with for a coin since Oct 21 (one token out, one coin in), priced at Jupiter's price now
# (lamports per raw unit), so the scan can value every buy. Writes SPD/prices_full.json and SPD/paid_tokens.json.
#   python3 -I price_tokens.py SPD
import sys, json, os, collections, urllib.request, time
SPD = sys.argv[1]; W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"; WSOL = "So11111111111111111111111111111111111111112"
paid, dec = collections.Counter(), {}
for f in os.listdir(f"{SPD}/w4tx"):
    if int(f.split("_")[0]) < 461000000: continue
    t = json.load(open(f"{SPD}/w4tx/{f}")); m = t["meta"]
    if m.get("err"): continue
    d = collections.defaultdict(int)
    for k, s in (("preTokenBalances", -1), ("postTokenBalances", 1)):
        for b in m.get(k) or []:
            dec[b["mint"]] = b["uiTokenAmount"]["decimals"]
            if b.get("owner") == W4: d[b["mint"]] += s * int(b["uiTokenAmount"]["amount"])
    ups = [k for k, v in d.items() if v > 0]; downs = [k for k, v in d.items() if v < 0 and k != WSOL]
    if len(ups) == 1 and len(downs) == 1: paid[downs[0]] += 1
mints = [m for m, n in paid.most_common() if n >= 3]
px = {}
for i in range(0, len(mints), 30):
    for k in range(6):
        try:
            px.update(json.load(urllib.request.urlopen("https://lite-api.jup.ag/price/v3?ids=" + ",".join(mints[i:i + 30] + [WSOL]), timeout=30))); break
        except Exception: time.sleep(5 * (k + 1))
    time.sleep(2)
sol = px[WSOL]["usdPrice"]
out = {m: px[m]["usdPrice"] / sol * 1e9 / 10 ** dec[m] for m in mints if m in px and px[m].get("usdPrice")}
json.dump(out, open(f"{SPD}/prices_full.json", "w")); json.dump(dict(paid.most_common()), open(f"{SPD}/paid_tokens.json", "w"))
print(f"{len(paid)} tokens it paid with since Oct 21, {len(mints)} used 3+ times, {len(out)} priced (SOL ${sol:.2f})")
