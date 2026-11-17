# Telegram calls, the followers' behaviour (the owner, Nov 17: "study the behavior of the followers to tune an entry and
# exit"). From the curve paths the tests cached (tg_test.py: DIR/paths/, the curve's trades from 10 min before the post to
# an hour after; busy coins sampled 1 in 4 after the first 2 min), every call still on a SOL curve at the post:
#  - the price at fixed times after the post over the price at the post (the last trade at or before it);
#  - the run-up before the post: the price at the post over the price 10 min before (did the caller or insiders buy first?);
#  - the first minute's flow: buys and sales by wallets other than... everyone (the followers and bots), in SOL;
#  - the peak in the hour and when, the lowest point before the peak.
# No RPC; reads the caches only, so it can be rerun as the tests fill them.
#   python3 -I tg_study.py TGDIR > out/tg_study.txt
import sys, os, json, gzip, glob, statistics as st, collections
TG = sys.argv[1]; OFF = [5, 15, 30, 60, 120, 300, 600, 1800, 3600]
def sol_curve(tr): return 25e9 < tr[0]["vq"] * tr[0]["vt"] / 1.073e15 < 35e9
def price(e): return e["vq"] / e["vt"]
rows = []
for cj in sorted(glob.glob(f"{TG}/**/calls.json", recursive=True)):
    D = os.path.dirname(cj); ch = os.path.relpath(D, TG)
    for m, t, _ in json.load(open(cj)):
        f = f"{D}/paths/{m}.json.gz"
        if not os.path.exists(f): continue
        x = json.load(gzip.open(f))
        if x.get("venue") != "pump" or not x.get("tr"): continue
        tr = x["tr"]
        if not sol_curve(tr): continue
        before = [e for e in tr if e["t"] <= t]; after = [e for e in tr if e["t"] > t]
        if not before or not after: continue
        if x.get("complete") and x.get("last_t") and x["last_t"] < t: continue
        p0 = price(before[-1]); pre = [e for e in tr if e["t"] <= t - 600]
        run = p0 / price(pre[-1]) if pre else p0 / price(tr[0])
        path = {}
        for o in OFF:
            k = [e for e in tr if e["t"] <= t + o]
            path[o] = price(k[-1]) / p0 if k and k[-1]["t"] > t - 1 or k else None
        grad = next((e["t"] - t for e in after if e.get("real") == 0), None)
        if grad is not None:   # after graduation the curve stops: hold its last price
            for o in OFF:
                if o >= grad: path[o] = price([e for e in after if e["t"] - t <= grad][-1]) / p0
        hour = [e for e in after if e["t"] <= t + 3600]
        pk_i = max(range(len(hour)), key=lambda i: price(hour[i])); pk = price(hour[pk_i]) / p0
        low = min(price(e) for e in hour[:pk_i + 1]) / p0
        m1 = [e for e in after if e["t"] <= t + 60]
        buy = sum(e["q"] for e in m1 if e["buy"]) / 1e9; sell = sum(e["q"] for e in m1 if not e["buy"]) / 1e9
        rows.append(dict(ch=ch, t=t, m=m, run=run, path=path, pk=pk, pk_t=hour[pk_i]["t"] - t, low=low, grad=grad,
                         buy=buy, sell=sell, nb=sum(e["buy"] for e in m1), ns=sum(not e["buy"] for e in m1)))
print(f"{len(rows)} calls on a SOL curve at the post, from {len({r['ch'] for r in rows})} channels")
def q(v): v = sorted(v); return f"{v[len(v) // 4]:5.2f} {st.median(v):5.2f} {v[3 * len(v) // 4]:5.2f}" if v else "-"
print("\nthe price after the post over the price at the post: quartiles 25% / median / 75% (graduated coins held at the curve's end)")
for o in OFF: print(f"  +{o:5d} s: {q([r['path'][o] for r in rows if r['path'][o]])}")
print(f"\npeak in the hour: {q([r['pk'] for r in rows])}; reached 2x {sum(r['pk'] >= 2 for r in rows) / len(rows):.0%}, 1.5x {sum(r['pk'] >= 1.5 for r in rows) / len(rows):.0%}; "
      f"its time median {st.median(r['pk_t'] for r in rows):.0f} s; lowest before the peak {q([r['low'] for r in rows])}")
print(f"first minute: buys {q([r['buy'] for r in rows])} SOL, sales {q([r['sell'] for r in rows])} SOL; buyers {st.median(r['nb'] for r in rows):.0f}, sellers {st.median(r['ns'] for r in rows):.0f} (medians)")
print("\nby the run-up before the post (price at the post over 10 min before): calls, peak 2x+, price at +10 min and +30 min (median)")
for lo, hi in ((0, 1.2), (1.2, 2), (2, 5), (5, 1e9)):
    v = [r for r in rows if lo <= r["run"] < hi]
    if v: print(f"  {lo:>4}-{hi if hi < 1e9 else '':<4}x: {len(v):4d}, {sum(r['pk'] >= 2 for r in v) / len(v):4.0%}, "
                f"{st.median(r['path'][600] for r in v if r['path'][600]):5.2f}, {st.median(r['path'][1800] for r in v if r['path'][1800]):5.2f}")
print("\nper channel: calls, peak 2x+, median price at +1 min / +10 min / +30 min, median run-up before")
by = collections.defaultdict(list)
for r in rows: by[r["ch"]].append(r)
for ch, v in sorted(by.items(), key=lambda x: -len(x[1])):
    med = lambda o: st.median([r["path"][o] for r in v if r["path"][o]] or [0])
    print(f"  {ch:32s} {len(v):4d}, {sum(r['pk'] >= 2 for r in v) / len(v):4.0%}, {med(60):5.2f} / {med(600):5.2f} / {med(1800):5.2f}, run-up {st.median(r['run'] for r in v):4.2f}")
json.dump(rows, open(f"{TG}/study_rows.json", "w"))
