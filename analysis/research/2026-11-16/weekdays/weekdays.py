# "Is it normal the bot is slow on Sundays?" (the owner, Nov 16). Wallet 4's buys by Beirut weekday, full days only
# (Oct 22 - Nov 14; the data ends Nov 15 14:10 Beirut): all its buys, its 1.45+ SOL buys priced in another token, and those the bot can copy now
# (paid with SOL, WBTC, PUMP, SPCX, TTWO or DJT), from the scan with every paying token as a float (scan_all.out).
#   python3 -I weekdays.py SPD
import sys, os, re, json, datetime, collections
SPD = sys.argv[1]; W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
day = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc)
FULL0, FULL1 = datetime.date(2026, 10, 22), datetime.date(2026, 11, 14)   # the data ends Nov 15 14:10 Beirut
bt, allb = {}, collections.Counter()
for f in os.listdir(f"{SPD}/w4tx"):
    t = json.load(open(f"{SPD}/w4tx/{f}")); bt[t["slot"]] = t["blockTime"]; m = t["meta"]
    if m.get("err"): continue
    up = any(b.get("owner") == W4 for b in m.get("postTokenBalances") or []) and not any(b.get("owner") == W4 and b["mint"] == x["mint"] for b in m.get("preTokenBalances") or [] for x in [b])
    d = day(t["blockTime"]).date()
    if FULL0 <= d <= FULL1: allb[d] += 1                       # every landed transaction of wallet 4
KEEP = {"So111111", "3NZ9JMVB", "pumpCmXq", "SPCXxcqX", "TTWofwAg", "DJTu7vi8"}
big, cop = collections.Counter(), collections.Counter()
for l in open(f"{SPD}/scan_all.out"):
    g = re.match(r"(\d+) (\S{8}) ([\d.]+) SOL from (\S+) quote (\S+) jupiter (\S+): (ROUTABLE|no route)(.*)", l)
    if not g or int(g.group(1)) not in bt: continue
    d = day(bt[int(g.group(1))]).date()
    if not (FULL0 <= d <= FULL1): continue
    big[d] += 1
    m = re.search(r"input: (\w{8})", l)
    if g.group(7) == "ROUTABLE" and m and m.group(1) in KEEP: cop[d] += 1
days = sorted(allb); W = collections.defaultdict(list)
for d in days: W[d.strftime("%a")].append(d)
print(f"{len(days)} full Beirut days, {days[0]} to {days[-1]}; per day: its transactions | its 1.45+ SOL buys in another token | of them copyable now")
for wd in ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"):
    ds = W[wd]; n = len(ds)
    print(f"   {wd} ({n} days: {', '.join(d.strftime('%b %d') for d in ds)}): {sum(allb[d] for d in ds) / n:7.0f} | {sum(big[d] for d in ds) / n:5.1f} | {sum(cop[d] for d in ds) / n:5.1f}   by day: " + " ".join(str(cop[d]) for d in ds))
wk = [d for d in days if d.weekday() < 5]; we = [d for d in days if d.weekday() >= 5]
for name, ds in (("weekdays", wk), ("weekend", we)):
    print(f"   {name:8s}: {sum(allb[d] for d in ds) / len(ds):7.0f} | {sum(big[d] for d in ds) / len(ds):5.1f} | {sum(cop[d] for d in ds) / len(ds):5.1f}")
