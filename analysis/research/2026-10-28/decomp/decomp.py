# Wallet 4's +36.92 SOL in check.sh's window (Oct 26 15:00 Beirut -> Oct 27 11:45), coin by coin: what kind of coin it
# was (from the backtest data up to Oct 27 00:19 UTC, then from the bot's own detection on the fetched transactions)
# against what the copy bot did with it.   python3 -I decomp.py SCAN_OUTPUT
import json, sys, re, collections, os
D = os.path.dirname(os.path.abspath(__file__))
rows = [(l.rstrip("\n").split("\t") + [""])[:6] for l in open(f"{D}/check_w4.tsv")]
kt = json.load(open(f"{D}/kind_trips.json"))
TOKENS = {"pumpCmXq": "PUMP", "DJTu7vi8": "DJTU", "DoGEV7LA": "DOGE", "SPCXxcqX": "SPCX", "XsqE9cRR": "xStock"}
GRAD = set("rLmt8bBq 3zXt7sGv FSTybnc1 93V9oUvK EEF4au54 ETFpgjkR 9djTdh3W 6dw91Xvo J3dcS61q".split())
scan = {}
for l in open(sys.argv[1]):
    m = re.match(r"(\d+) (\w{8}) (.*)", l)
    if not m or m.group(2) in scan: continue
    rest = m.group(3)
    if rest.startswith("SOL-priced"): scan[m.group(2)] = "sol"
    elif rest.startswith("unpriced"): scan[m.group(2)] = "other unroutable"
    elif "ROUTABLE" in rest: scan[m.group(2)] = "other routable"
    elif "no route" in rest: scan[m.group(2)] = "other unroutable"
def kind(m, sol):
    if m in TOKENS: return "F token it pays with / holds"
    if m in GRAD: return "E graduated coin (PumpSwap pool only)"
    k = None
    if m in kt:
        k = kt[m][0]
        if k == "sol": return "D SOL-priced"
        k = "other routable" if k[-1] in "ABC" else "other unroutable"
    k = k or scan.get(m)
    if k is None: return "? not found"
    if k == "sol": return "D SOL-priced"
    if sol < 1.45: return "C other token, under 1.45 SOL"
    return "A other token, 1.45+, routable (LONG COPY)" if k == "other routable" else "B other token, 1.45+, not routable"
ST = {"C": "copied", "CR": "copied", "CN": "copied", "CO": "copied", "CNS": "copied", "SO": "skipped", "NS": "not seen", "NW": "not watched"}
g = collections.defaultdict(lambda: [0, 0.0, 0.0])
detail = collections.defaultdict(list)
for t, m, net, sol, st, our in rows:
    k = kind(m, float(sol)); s = ST[st]
    v = 0.0 if net == "H" else float(net)
    for key in ((k, s), (k, "ALL"), ("ALL", s)):
        g[key][0] += 1; g[key][1] += v; g[key][2] += float(our) if our else 0.0
    detail[k].append((v, m, sol, s))
kinds = sorted({k for k, _ in g if k != "ALL"})
cols = ["copied", "skipped", "not seen", "not watched", "ALL"]
print(f"{'kind':44s}" + "".join(f"{c:>22s}" for c in cols))
for k in kinds + ["ALL"]:
    print(f"{k:44s}" + "".join(f"{g[(k, c)][0]:5d} {g[(k, c)][1]:+8.2f}{'':9s}" if g[(k, c)][0] else f"{'':22s}" for c in cols))
print("\nour copies by kind:", {k: round(g[(k, 'copied')][2], 4) for k in kinds if g[(k, 'copied')][0]})
for k in kinds:
    big = sorted(detail[k], reverse=True)
    print(f"\n{k}: best {', '.join(f'{m} {v:+.2f} ({sol}, {s})' for v, m, sol, s in big[:4])}; worst {', '.join(f'{m} {v:+.2f}' for v, m, sol, s in big[-2:])}")
