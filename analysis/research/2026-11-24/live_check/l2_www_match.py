# www (CqCAzte8) trade by trade: the live book (`www_live.txt`, the box's closed.jsonl pasted Nov 24 evening: coin, its
# slot, seen, stake, net lamports, reason) against the model on the same coin (f1_rows.py outputs: ../coin_filters/out
# and out/), the unit's exits (token coins tp 3x / 420 s / stall 240, SOL coins tp 2x / 120 s), 0.5 SOL a copy = (v +
# 0.0064) x 0.5 - 0.0064. Model buys in the live window that the bot did not take are listed apart.
#   python3 -I l2_www_match.py
import json, os, numpy as np, datetime as dt
H = os.path.dirname(os.path.abspath(__file__))
L = [l.split() for l in open(f"{H}/www_live.txt")]
rows = {}
for p in (f"{H}/../coin_filters/out/CqCAzte8.json", f"{H}/out/CqCAzte8.json"):
    d = json.load(open(p)); ex = d["exits"]
    for r in d["rows"]: rows[r["m"][:8]] = (r, ex)
def mval(r, ex):
    e = ex.index("tp 3x / 420 s / stall 240") if r["tok"] else ex.index("tp 2x / 120 s")
    v = -0.0004 if r["prem"] > 1.5 else r["g"][e]
    return (v + 0.0064) * 0.5 - 0.0064
both, live_only = [], []
print(f"{'coin':9s} {'seen UTC':12s} {'kind':5s} {'live':>7s} {'model':>7s} {'diff':>7s}  reason  our price over its (model)")
for m, slot, seen, stake, net, why in L:
    lv = int(net) / 1e9; t = dt.datetime.fromtimestamp(int(seen), dt.UTC).strftime("%m-%d %H:%M")
    if m in rows:
        r, ex = rows[m]; mv = mval(r, ex); both.append((lv, mv, r["tok"]))
        print(f"{m:9s} {t:12s} {'token' if r['tok'] else 'SOL':5s} {lv:+7.3f} {mv:+7.3f} {lv - mv:+7.3f}  {why:8s} {r['prem']:.2f}x")
    else:
        live_only.append(lv); print(f"{m:9s} {t:12s} {'?':5s} {lv:+7.3f} {'-':>7s}          {why:8s} (not a first buy of 0.5+ SOL in the data)")
b = np.array([x[:2] for x in both]); tk = np.array([x[2] for x in both])
print(f"\nmatched {len(b)}: live {b[:, 0].sum():+.3f}, model {b[:, 1].sum():+.3f}, live minus model {b[:, 0].sum() - b[:, 1].sum():+.3f} SOL "
      f"({(b[:, 0] - b[:, 1]).mean():+.4f} a trade, median {np.median(b[:, 0] - b[:, 1]):+.4f}); live better on {np.sum(b[:, 0] > b[:, 1])}")
for k, lab in ((True, "token coins"), (False, "SOL coins")):
    s = b[tk == k]
    if len(s): print(f"  {lab}: {len(s)}, live {s[:, 0].sum():+.3f}, model {s[:, 1].sum():+.3f}")
print(f"live only (no model row): {len(live_only)}, {sum(live_only):+.3f}")
t0, t1 = int(L[0][2]) - 60, int(L[-1][2])
taken = {x[0] for x in L}
miss = [(r, ex) for k, (r, ex) in rows.items() if t0 <= r["t"] <= t1 and k not in taken]
mv = [mval(r, ex) for r, ex in miss]
print(f"model buys in the live window the bot did not take: {len(miss)}, model {sum(mv):+.3f} SOL at 0.5")
for r, ex in sorted(miss, key=lambda x: x[0]["t"]):
    print(f"  {r['m'][:8]} {dt.datetime.fromtimestamp(r['t'], dt.UTC):%m-%d %H:%M} {'token' if r['tok'] else 'SOL':5s} its {r['size']:.2f} SOL, model {mval(r, ex):+.3f}, price {r['prem']:.2f}x")
