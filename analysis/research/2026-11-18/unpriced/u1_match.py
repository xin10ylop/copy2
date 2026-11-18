# The bot's "its buy has no SOL value (paid in an unpriced token)" skips of Nov 15 13:00 - Nov 18 00:15 UTC (the owner's
# journal paste, out/skips_nov15_18.txt: time UTC, the coin's first 8 characters) matched to wallet 4's own trades
# (SP/winners/hist/H9kuqGKN*.json, w4_history.py, Nov 12 04:46 - Nov 18 00:04 UTC): the coin, the token its curve is
# priced in, and its buy's size in SOL at Jupiter's price of now (lite-api, public).
#   python3 -I u1_match.py SP > out/u1_match.txt
import sys, json, glob, collections, datetime as d, urllib.request
SP = sys.argv[1]; here = __file__.rsplit("/", 1)[0]
h = json.load(open(glob.glob(f"{SP}/winners/hist/H9kuqGKN*.json")[0])); T = h["trades"]
S = []
for l in open(f"{here}/out/skips_nov15_18.txt"):
    mo, dd, hh, m8 = l.split(); t = int(d.datetime.strptime(f"2026 {mo} {dd} {hh}", "%Y %b %d %H:%M:%S").replace(tzinfo=d.UTC).timestamp()); S.append((t, m8))
buys = [e for e in T if e["buy"]]
SOLQ = {"11111111111111111111111111111111", "So11111111111111111111111111111111111111112", None}
qs = sorted({e["quote"] for e in buys if e["quote"] not in SOLQ})
PR = {}
for i in range(0, len(qs), 50):
    r = json.load(urllib.request.urlopen(f"https://lite-api.jup.ag/price/v3?ids={','.join(qs[i:i + 50]) + ',So11111111111111111111111111111111111111112'}", timeout=30))
    PR.update({k: v for k, v in r.items() if v})
sol_usd = PR["So11111111111111111111111111111111111111112"]["usdPrice"]
def sol_of(e):
    q = e["quote"]
    if q in SOLQ: return e["q"] / 1e9
    p = PR.get(q); return e["q"] / 10 ** p["decimals"] * p["usdPrice"] / sol_usd if p else None
rows = []
for t, m8 in S:
    c = [e for e in buys if e["m"].startswith(m8) and abs(e["t"] - t) <= 5]
    if not c: rows.append(dict(t=t, m8=m8, found=False)); continue
    e = min(c, key=lambda e: abs(e["t"] - t)); rows.append(dict(t=t, m8=m8, found=True, m=e["m"], quote=e["quote"], sol=sol_of(e), q=e["q"]))
json.dump(rows, open(f"{SP}/winners/unpriced_skips.json", "w"))
f = [r for r in rows if r["found"]]
print(f"{len(rows)} skips; matched to wallet 4's own buy (same coin, within 5 s): {len(f)}; its history ends Nov 18 00:04 UTC")
by = collections.defaultdict(list)
for r in f: by[r["quote"][:8] if r["quote"] else "?"].append(r)
print("paid in   | skips | its size at today's price: 1.3+ SOL, under 1.3, unpriced | median SOL")
for k, v in sorted(by.items(), key=lambda x: -len(x[1])):
    big = sum(1 for r in v if r["sol"] is not None and r["sol"] >= 1.3); small = sum(1 for r in v if r["sol"] is not None and r["sol"] < 1.3); un = sum(1 for r in v if r["sol"] is None)
    s = sorted(r["sol"] for r in v if r["sol"] is not None); print(f"{k:9s} | {len(v):5d} | {big:4d} {small:5d} {un:4d} | {s[len(s) // 2] if s else 0:6.2f}")
