# SolHouse VIP, a different angle: WHO holds the coin at the alert (the owner, Nov 17: "test something that logically
# could solve everything ... a different angle"). The counts at the call are the same for winners and losers
# (tg_vip_why.py); the identities are not counted there. Each wallet gets a record as it goes: every earlier alert (posted
# more than an hour before, so its result was known) on a coin the wallet was HOLDING at that alert, and what a copy of
# that alert made (bought 1 s after, sold at 2x or 60 min). For a new alert: its holders with a record of MINREC+ coins,
# the mean of their records ("who": the crowd's past), how many of them have a positive record, how many a bad one.
# No look-ahead: holders from the trades up to the post; records from alerts at least 3600 s older.
# Calls in time order; the first third only builds records; the rest is cut in two halves by time.
#   python3 -I tg_vip_who.py TGDIR [dir ...] > out/tg_vip_who.txt       (default dirs: vip vip_rest vip_h1 = Nov 10-17)
import sys, os, json, gzip, numpy as np, collections, statistics as st
TG = sys.argv[1]; DIRS = sys.argv[2:] or ["vip", "vip_rest", "vip_h1"]; here = os.path.dirname(os.path.abspath(__file__)); os.environ.setdefault("COST", "0.01")
MINREC = 3
src = open(os.path.join(here, "tg_vip_lab.py")).read().split("# ---- 1. signs")[0]
R = []
for v in DIRS:
    os.environ["VDIR"] = v; ns = {"__file__": os.path.join(here, "tg_vip_lab.py")}; sys.argv = ["x", TG]
    exec(compile(src, "tg_vip_lab.py", "exec"), ns)
    for r in ns["rows"]: r["dir"] = v
    R += ns["rows"]
entry, trade, STAKE = ns["entry"], ns["trade"], ns["STAKE"]
cns = {}; sys.argv = ["x", TG]; exec(open(os.path.join(here, "tg_channel.py")).read().split("for cj in sorted(glob.glob")[0], cns); order_slots = cns["order_slots"]
seen = set(); rows = []
for r in sorted(R, key=lambda r: r["t"]):
    if r["m"] in seen: continue
    seen.add(r["m"]); k = entry(r, delay=1)
    if k is None: continue
    f = f"{TG}/{r['dir']}/paths/{r['m']}.json.gz"; x = json.load(gzip.open(f)); bal = collections.Counter()
    for e in order_slots(x.get("tr") or []):
        if e["t"] > r["t"]: break
        bal[e["user"]] += e["tok"] if e["buy"] else -e["tok"]
    r["holders"] = {u for u, b in bal.items() if b > 1e9 and u != x.get("creator")}   # over 1,000 tokens (dust is not a holder)
    r["pnl"] = trade(r, k, tp=2, cap=3600); rows.append(r)
rec = collections.defaultdict(lambda: [0, 0.0]); pending = []   # wallet -> [coins, sum of the copies' results]
for r in rows:
    while pending and pending[0]["t"] + 3600 < r["t"]:
        o = pending.pop(0)
        for u in o["holders"]: rec[u][0] += 1; rec[u][1] += o["pnl"]
    known = [(rec[u][0], rec[u][1] / rec[u][0]) for u in r["holders"] if rec[u][0] >= MINREC]
    r["n_known"] = len(known); r["who"] = float(np.mean([m for _, m in known])) / STAKE if len(known) >= 5 else None
    r["good"] = sum(m > 0 for _, m in known); r["bad"] = sum(m < -0.15 for _, m in known)
    r["good_share"] = r["good"] / len(known) if len(known) >= 5 else None
    pending.append(r)
n = len(rows); live = rows[n // 3:]; half = live[len(live) // 2]["t"]
print(f"{n} alerts in time order ({', '.join(DIRS)}); the first {n // 3} only build the wallets' records; {len(live)} scored; "
      f"{sum(1 for v in rec.values() if v[0] >= MINREC)} wallets with a record of {MINREC}+ coins")
print(f"every scored alert: {np.mean([r['pnl'] for r in live]) / STAKE:+.1%} a copy; holders with a record, median {st.median(r['n_known'] for r in live):.0f} an alert")
def show(name, key, cuts):
    v = [r for r in live if r[key] is not None]
    print(f"\n{name}: a copy (tp2 / 60 min), all | first half / second half | won | without the best 5")
    for lo, hi in zip(cuts, cuts[1:]):
        s = [r for r in v if lo <= r[key] < hi]
        if len(s) < 15: continue
        a = [r["pnl"] for r in s if r["t"] < half]; b = [r["pnl"] for r in s if r["t"] >= half]; x = a + b
        print(f"  [{lo:g}, {hi:g}): {len(s):3d} alerts {np.mean(x) / STAKE:+6.1%} | {np.mean(a) / STAKE if a else 0:+6.1%} / {np.mean(b) / STAKE if b else 0:+6.1%} | {np.mean([p > 0 for p in x]):3.0%} | {sum(sorted(x, reverse=True)[5:]):+6.2f}")
q = lambda key, ps: [-9] + [float(np.quantile([r[key] for r in live if r[key] is not None], p)) for p in ps] + [9]
show("the holders' past (the mean result of their earlier alerts), by quintile", "who", q("who", (0.2, 0.4, 0.6, 0.8)))
show("share of the known holders whose own record is positive, by quintile", "good_share", q("good_share", (0.2, 0.4, 0.6, 0.8)))
show("holders with a positive record (count)", "good", [0, 1, 3, 6, 10, 20, 9999])
show("holders with a bad record, under -15% (count)", "bad", [0, 5, 15, 30, 60, 9999])
json.dump({u: v for u, v in rec.items() if v[0] >= 10}, open(f"{TG}/who_records_{DIRS[0]}.json", "w"))
