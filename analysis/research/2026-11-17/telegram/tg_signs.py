# Telegram calls: winners against losers. For every call on a SOL pump curve at the post (tg_test.py's cache), what was
# knowable at the post (and, separately, in the first minute after it), against the outcome:
#   winner = the price reached 1.5x the post's within the hour; loser = it did not (and "bad" = it was under 0.7x at 30 min).
# Signs at the post: the run-up (price at the post over 10 min and 1 min before), the curve's progress (share of its
# tokens sold), the 10 min before: trades, distinct buyers, net SOL flow, the biggest single buy, the share of sales.
# Signs in the first minute after the post (for a later entry): net SOL flow, buyers, sellers, the price at +60 s.
# For each sign: the median for winners and for losers, and the winner rate in its lower and upper half (split at the
# median of all calls), by channel group: the channels are split in two (A: the first half alphabetically, B: the other),
# so a sign that only works in one group shows it.
#   python3 -I tg_signs.py TGDIR > out/tg_signs.txt
import sys, os, json, gzip, glob, statistics as st
TG = sys.argv[1]; INIT_REAL = 793_100_000_000_000
pr = lambda e: e["vq"] / e["vt"]
rows = []
for cj in sorted(glob.glob(f"{TG}/**/calls.json", recursive=True)):
    D = os.path.dirname(cj); ch = os.path.relpath(D, TG)
    if ch == "kolscope/klevercalls": continue   # the same calls as the channel's own export
    for m, t, _ in json.load(open(cj)):
        f = f"{D}/paths/{m}.json.gz"
        if not os.path.exists(f): continue
        x = json.load(gzip.open(f))
        if x.get("venue") != "pump" or not x.get("tr"): continue
        tr = x["tr"]
        if not 25e9 < tr[0]["vq"] * tr[0]["vt"] / 1.073e15 < 35e9: continue
        if x.get("complete") and x.get("last_t") and x["last_t"] < t: continue
        pre = [e for e in tr if e["t"] <= t]; aft = [e for e in tr if t < e["t"] <= t + 3600]
        if not pre or not aft: continue
        p0 = pr(pre[-1]); w10 = [e for e in pre if e["t"] > t - 600]
        at = lambda o: pr([e for e in tr if e["t"] <= t + o][-1]) / p0
        old = [e for e in tr if e["t"] <= t - 600]; m1 = [e for e in pre if e["t"] <= t - 60]
        a60 = [e for e in aft if e["t"] <= t + 60]
        pk = max(pr(e) for e in aft) / p0
        rows.append(dict(ch=ch, win=pk >= 1.5, bad=at(1800) < 0.7,
            run10=p0 / pr(old[-1]) if old else p0 / pr(tr[0]), run1=p0 / pr(m1[-1]) if m1 else 1.0,
            prog=max(0.0, 1 - (pre[-1].get("real") or INIT_REAL) / INIT_REAL),
            n10=len(w10), buyers10=len({e["user"] for e in w10 if e["buy"]}),
            flow10=(sum(e["q"] for e in w10 if e["buy"]) - sum(e["q"] for e in w10 if not e["buy"])) / 1e9,
            big10=max([e["q"] for e in w10 if e["buy"]] or [0]) / 1e9, sellshare10=sum(not e["buy"] for e in w10) / max(1, len(w10)),
            flow60=(sum(e["q"] for e in a60 if e["buy"]) - sum(e["q"] for e in a60 if not e["buy"])) / 1e9,
            buyers60=len({e["user"] for e in a60 if e["buy"]}), sellers60=len({e["user"] for e in a60 if not e["buy"]}), p60=at(60)))
chs = sorted({r["ch"] for r in rows}); A = set(chs[:len(chs) // 2])
print(f"{len(rows)} curve calls from {len(chs)} channels; winners (1.5x in the hour) {sum(r['win'] for r in rows)} ({sum(r['win'] for r in rows) / len(rows):.0%}); "
      f"bad (under 0.7x at 30 min) {sum(r['bad'] for r in rows)}")
print(f"group A: {', '.join(sorted(A))}\ngroup B: the rest")
SIGNS = [("run10", "at the post"), ("run1", "at the post"), ("prog", "at the post"), ("n10", "at the post"), ("buyers10", "at the post"),
         ("flow10", "at the post"), ("big10", "at the post"), ("sellshare10", "at the post"),
         ("flow60", "first minute"), ("buyers60", "first minute"), ("sellers60", "first minute"), ("p60", "first minute")]
print("\nsign          when          | median: winners / losers | winner rate below / above the median: group A | group B")
for k, when in SIGNS:
    v = [r[k] for r in rows]; md = st.median(v)
    wm = st.median([r[k] for r in rows if r["win"]] or [0]); lm = st.median([r[k] for r in rows if not r["win"]] or [0])
    def rate(g, lo):
        s = [r for r in rows if (r["ch"] in A) == g and ((r[k] <= md) if lo else (r[k] > md))]
        return f"{sum(r['win'] for r in s) / len(s):4.0%} ({len(s):3d})" if s else "   -      "
    print(f"{k:12s}  {when:12s}  | {wm:8.2f} / {lm:8.2f}     | {rate(True, True)} / {rate(True, False)} | {rate(False, True)} / {rate(False, False)}")
json.dump(rows, open(f"{TG}/signs_rows.json", "w"))
