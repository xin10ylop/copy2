import json, os, sys, re, urllib.request, collections
SPD = sys.argv[1]; W = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
lines = [l for l in open(f"{SPD}/scan.out") if "unpriced" in l]
want = {(int(l.split()[0]), l.split()[1], l.split()[-1]) for l in lines}
files = {}
for f in os.listdir(f"{SPD}/tx"): files.setdefault(int(f.split("_")[0]), []).append(f)
rows = []
for slot, coin8, pay8 in want:
    for f in files.get(slot, []):
        t = json.load(open(f"{SPD}/tx/{f}")); d = collections.defaultdict(int); dec = {}
        for k, s in (("preTokenBalances", -1), ("postTokenBalances", 1)):
            for b in t["meta"][k] or []:
                if b.get("owner") == W:
                    d[b["mint"]] += s * int(b["uiTokenAmount"]["amount"]); dec[b["mint"]] = b["uiTokenAmount"]["decimals"]
        coin = [m for m in d if m.startswith(coin8) and d[m] > 0]
        pay = [m for m in d if m.startswith(pay8) and d[m] < 0]
        if coin and pay:
            rows.append((slot, t["blockTime"], coin[0], pay[0], -d[pay[0]] / 10 ** dec[pay[0]])); break
mints = sorted({r[3] for r in rows}) + ["So11111111111111111111111111111111111111112"]
px = json.load(urllib.request.urlopen("https://lite-api.jup.ag/price/v3?ids=" + ",".join(mints), timeout=30))
sol = px["So11111111111111111111111111111111111111112"]["usdPrice"]
out = []
for slot, bt, coin, pay, amt in rows:
    p = px.get(pay, {}).get("usdPrice")
    out.append((bt, coin, pay, amt, None if p is None else amt * p / sol))
json.dump(out, open(f"{SPD}/unpriced_val.json", "w"))
print(f"{len(lines)} unpriced lines, {len(rows)} matched; SOL ${sol:.2f}")
for m in mints[:-1]:
    print(m[:8], "price $", px.get(m, {}).get("usdPrice"))
import datetime
big = sorted([o for o in out if o[4] and o[4] >= 1.45])
print(f"\n{len(big)} of them worth 1.45+ SOL at today's price:")
for bt, coin, pay, amt, v in big:
    print(datetime.datetime.utcfromtimestamp(bt).strftime("%H:%M"), coin[:8], "paid", f"{amt:,.2f}", pay[:8], f"= {v:.2f} SOL")
by = collections.Counter(o[2][:8] for o in big); print(by)
