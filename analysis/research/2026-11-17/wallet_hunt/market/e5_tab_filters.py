# The TAB unit's filters reviewed (Nov 18, the owner: "review all the filters"). TAB16RxX's copies on the 4 days'
# float-quote coins (e3's set, but with no price refusal so the premium can be studied), the deployed exit with tp 3.5x
# (stall 180, sell pressure 5/60, 600 s, its sale never followed), the mean of the three landings, 0.0345 SOL a round
# trip. Each filter in bands, days 1-2 against 3-4 (Nov 16 01:07 UTC): a band earns a filter only if it loses on both.
#   python3 -I e5_tab_filters.py SP LAUNCHES,... > ../out/e5_tab_filters.txt
import sys, os, json, gzip, datetime as dt, numpy as np
SP = sys.argv[1]; O = f"{SP}/market"; PD = f"{O}/paths_full"
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(here, "..")); import hunt_lib as H
src = open(os.path.join(here, "e4_tab_grid.py")).read(); ns = {"H": H, "np": np}; exec(src[src.index("def model("):src.index("TPS = ")], ns); model = ns["model"]
TAB = "TAB16RxXmazWzCTpJbnKiREWUybdEoskuyidaV291u3"; W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
WSOL = "So11111111111111111111111111111111111111112"; COST = 0.0345 - 0.0026; MID = 1794791222; TP = float(os.environ.get("TP", 3.5))
FLOATS = {"3NZ9JMVB": "WBTC", "pumpCmXq": "PUMP", "SPCXxcqX": "SPCX", "TTWofwAg": "TTWO", "DJTu7vi8": "DJT", "98sMhvDw": "HYPE", "XsbEhLAt": "AAPLx"}; L = {}
for f_ in sys.argv[2].split(","): L.update({m: x for m, x in json.load(open(f_)).items() if x and x["quote"][:8] in FLOATS and os.path.exists(f"{PD}/{m}.json.gz")})
PR = json.load(open(f"{O}/prices.json")); su = PR[WSOL]["usdPrice"]; rate = lambda q: PR[q]["usdPrice"] / su * 1e9 / 10 ** PR[q]["decimals"] if q in PR else None
R = []
for m, x in L.items():
    r = rate(x["quote"]); tr = json.load(gzip.open(f"{PD}/{m}.json.gz")) if r else []
    i = next((j for j, e in enumerate(tr) if e["user"] == TAB), None)
    if i is None or not tr[i]["buy"]: continue
    sol = tr[i]["q"] * (1 + tr[i]["bps"] / 1e4) * r / 1e9
    if sol < 0.5 or tr[-1]["t"] - tr[i]["t"] < 600: continue
    ps = [H.prep(tr, i, r, n, pmax=1000) for n in (4, 8, "slot+1")]
    v = np.mean([model(p, TP, 600, (5, 60, 30), 180) for p in ps]) - COST
    prem = np.mean([(tr[i]["vt"] / p["ent"][0]) ** 2 for p in ps])
    w4 = any(e["user"] == W4 and e["buy"] and e["q"] * (1 + e["bps"] / 1e4) * r / 1e9 >= 1.3 for e in tr)
    R.append(dict(t=tr[i]["t"], v=v, sol=sol, q=FLOATS[x["quote"][:8]], prem=prem, fee=tr[i]["bps"], launch=tr[i]["slot"] - x["slot"], age=tr[i]["t"] - x["t"],
                  hour=dt.datetime.fromtimestamp(tr[i]["t"], dt.UTC).hour, w4=w4, refused=prem > 1.25))
def S(v):
    v = np.array(v); n = len(v)
    if not n: return "   0"
    return f"{n:3d} {100 * v.mean() / 0.5:+6.1f}%"
def band(title, key):
    print(f"\n{title}:")
    for lab, f in key:
        a = [r["v"] for r in R if f(r) and r["t"] < MID]; b = [r["v"] for r in R if f(r) and r["t"] >= MID]; c = [r["v"] for r in R if f(r)]
        flag = "   <- loses on both halves" if a and b and np.mean(a) < 0 and np.mean(b) < 0 else ""
        print(f"   {lab:26s} | days 1-2 {S(a)} | days 3-4 {S(b)} | all {S(c)}{flag}")
base = [r for r in R if not r["refused"]]
print(f"{len(R)} copies with no price refusal ({sum(r['refused'] for r in R)} past 1.25x); tp {TP}x. As deployed (refused past 1.25x): {len(base)} copies, {100 * np.mean([r['v'] for r in base]) / 0.5:+.1f}% a copy")
band("1. Its buy size (SOL; deployed: 0.5+)", [(f"{a}-{b}", (lambda r, a=a, b=b: a <= r["sol"] < b)) for a, b in ((0.5, 0.75), (0.75, 1.0), (1.0, 1.3), (1.3, 2.0), (2.0, 99))])
band("2. The quote token (deployed: all floats)", [(q, (lambda r, q=q: r["q"] == q)) for q in sorted({r["q"] for r in R})])
band("3. Our price over its price (deployed: refused past 1.25x)", [(f"{a}-{b}x", (lambda r, a=a, b=b: a <= r["prem"] < b)) for a, b in ((0, 1.05), (1.05, 1.1), (1.1, 1.25), (1.25, 1.5), (1.5, 99))])
band("4. The coin's fee tier (bps; deployed: all)", [(f"{f}", (lambda r, f=f: r["fee"] == f)) for f in sorted({r["fee"] for r in R}) if sum(1 for r in R if r["fee"] == f) >= 5] + [("other", lambda r: sum(1 for z in R if z["fee"] == r["fee"]) < 5)])
band("5a. When it buys: slots after the create", [("create slot or next", lambda r: r["launch"] <= 1), ("2-10 slots", lambda r: 2 <= r["launch"] <= 10), ("11+ slots", lambda r: r["launch"] > 10)])
band("5b. The coin's age at its buy", [("under 10 s", lambda r: r["age"] < 10), ("10-60 s", lambda r: 10 <= r["age"] < 60), ("60-300 s", lambda r: 60 <= r["age"] < 300), ("300 s+", lambda r: r["age"] >= 300)])
band("6. Time of day (UTC)", [(f"{h:02d}-{h + 6:02d}", (lambda r, h=h: h <= r["hour"] < h + 6)) for h in (0, 6, 12, 18)])
band("7. Coins wallet 4 also bought (1.3+ SOL; deployed: skipped when the main unit holds it)", [("wallet 4 bought it too", lambda r: r["w4"]), ("TAB16RxX alone", lambda r: not r["w4"])])
