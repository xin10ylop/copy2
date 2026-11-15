# The worst losing run of the setup live on Nov 16 (tp 3.0, 600 s, early 30-290 s under 1.5x; floats WBTC, PUMP,
# SPCX, TTWO, DJT; SOL 1 / WBTC 2 / one from each other float open; 2 open), with and without the fee rule
# (min_fee_bps = 125), at 0.5 and 0.7 SOL. Over the wider dataset (Oct 21 - Nov 15 12:10 UTC), each landing: the
# deepest fall from a high (trade by trade), losing days, the worst day, the total.
#   python3 -I risk_now.py ALL   (in weekdays/: written for the same day)
import sys, os, datetime, collections
T0 = datetime.datetime(2026, 10, 21, 18, 30, tzinfo=datetime.timezone.utc).timestamp(); os.environ["FE_T0"] = str(T0)
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-14/float_exits"); ALL = sys.argv[1]; sys.argv = ["x", ALL, "0.5"]
import float_exits as F, lib as L
RULE = dict(tp=3.0, hold=600, early=(30, 290, 1.5), sl=None)
CAPS = {"SOL": 1, "WBTC": 2, "PUMP": 1, "SPCX": 1, "TTWofwAg": 1, "DJTu7vi8": 1}
rows = [r for r in F.rows if r["anchor"] in CAPS]
bps = {r["key"]: next(e for e in F.P[r["key"]][1] if e["user"] == L.W4 and e["buy"] and e["slot"] == r["slot"])["bps"] for r in rows}
day = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d")
last = max(day(r["t"]) for r in rows)
print(f"{len(rows)} buys of the six kinds; days {day(min(r['t'] for r in rows))} to {last} (the first and last partial, left out of the day counts)")
for stake in (0.5, 0.7):
    for name, keep in (("no fee rule", lambda r: True), ("fee rule on", lambda r: not (0 < bps[r["key"]] < 125))):
        cells = []
        for n in L.LAND:
            res = F.sim([r for r in rows if keep(r)], n, RULE, stake=stake, caps=CAPS)
            cum = hi = lo = 0.0; at = None; start = res[0][0]["t"]
            for r, net, why in res:
                cum += net
                if cum > hi: hi = cum; start = r["t"]
                if cum - hi < lo: lo = cum - hi; at = (start, r["t"])
            d = collections.defaultdict(float)
            for r, net, why in res: d[day(r["t"])] += net
            v = sorted(x for k, x in d.items() if k not in ("10-21", last))
            cells.append((sum(x[1] for x in res), lo, sum(1 for x in v if x < 0), v[0], len(v), at))
        f = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d %H:%M")
        print(f"   {stake} SOL, {name:12s}: total " + " / ".join(f"{c[0]:+6.2f}" for c in cells) + " | deepest fall " + " / ".join(f"{c[1]:+5.2f}" for c in cells)
              + f" | losing days " + " / ".join(f"{c[2]}" for c in cells) + f" of {cells[0][4]} | worst day " + " / ".join(f"{c[3]:+5.2f}" for c in cells)
              + f" | the deepest fall at landing 4: {f(cells[0][5][0])} to {f(cells[0][5][1])} Beirut")
print("(each cell: landing 4 / 8 / one block late)")
