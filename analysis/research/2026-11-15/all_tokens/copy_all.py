# Our copy with more floats (Nov 15): the four floats live now (SOL, WBTC, PUMP, SPCX) and four candidates wallet 4
# pays with often (TTWofwAg = Take-Two, DJTu7vi8 = Trump Media, XsbEhLAt = Apple xStock: tokenized stocks; 98sMhvDw =
# HYPE). Since Oct 21 18:30 UTC, blocks A (to Oct 29 12:02), B (to Nov 6 05:32), C (to now). The live rule (tp 3.0,
# 600 s, his sale followed 30-290 s under 1.5x, no stop), 0.5 SOL, raw, mean of landings 4 / 8 / one block late.
# (1) each kind alone, every copy; (2) the bot's run with each candidate added, 2 and 3 open (1 open from each float,
# WBTC 2, SOL 1).
#   python3 -I copy_all.py SPD
import sys, os, datetime, collections
T0 = datetime.datetime(2026, 10, 21, 18, 30, tzinfo=datetime.timezone.utc).timestamp(); os.environ["FE_T0"] = str(T0)
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-14/float_exits"); sys.argv = sys.argv[:2] + ["0.5"]
import float_exits as F
import lib as L
RULE = dict(tp=3.0, hold=600, early=(30, 290, 1.5), sl=None)
TB = L.T_STOP; TC = datetime.datetime(2026, 11, 6, 5, 32, tzinfo=datetime.timezone.utc).timestamp()
blk = lambda r: 0 if r["t"] < TB else 1 if r["t"] < TC else 2
NEW = ("TTWofwAg", "98sMhvDw", "DJTu7vi8", "XsbEhLAt"); NAME = {"TTWofwAg": "TTWO", "98sMhvDw": "HYPE", "DJTu7vi8": "DJT", "XsbEhLAt": "AAPLx"}
days = (F.END - T0) / 86400
def blocks(rs, caps, max_open):
    out = []
    for b in range(3):
        x = [sorted((y[1] for y in F.sim([r for r in rs if blk(r) == b], n, RULE, caps=caps, max_open=max_open)), reverse=True) for n in L.LAND]
        out.append((sum(sum(v) for v in x) / 3, sum(sum(v[2:]) for v in x) / 3))
    return out
show = lambda h: " | ".join(f"{a:+6.2f} ({b:+6.2f})" for a, b in h) + f" | {sum(a for a, _ in h):+6.2f} ({sum(b for _, b in h):+6.2f})"
if __name__ == "__main__":
    c = collections.Counter(r["anchor"] for r in F.rows)
    print(f"{len(F.rows)} copyable buys, {days:.1f} days; by what we pay with: {dict(c)}")
    print(f"\n(1) each kind alone, every copy (no slot limit): A | B | C | all, net SOL (without the block's best 2)")
    for k in ("SOL", "WBTC", "PUMP", "SPCX") + NEW:
        rs = [r for r in F.rows if r["anchor"] == k]
        h = blocks(rs, {}, 10**6); n = len(rs)
        res = F.sim(rs, 4, RULE, max_open=10**6); ex = collections.Counter(x[2] for x in res)
        print(f"   {NAME.get(k, k):5s} {n:4d} ({n / days:4.1f} a day) | {show(h)} | {100 * sum(a for a, _ in h) / max(1, n - ex['refused']) / 0.5:+5.1f}% a copy, tp {ex['tp']}")
    base = {"SOL": 1, "WBTC": 2, "PUMP": 1, "SPCX": 1}
    print(f"\n(2) the bot's run: A | B | C | all (without the best 2); copies a day at landing 4")
    for mo in (2, 3):
        for name, add in (("live now (SOL, WBTC, PUMP, SPCX)", ()), *((f"+ {NAME[k]}", (k,)) for k in NEW), ("+ all four", NEW), ("+ TTWO and HYPE", ("TTWofwAg", "98sMhvDw"))):
            keep = set(base) | set(add); rs = [r for r in F.rows if r["anchor"] in keep]; caps = dict(base, **{k: 1 for k in add})
            n = len(F.sim(rs, 4, RULE, caps=caps, max_open=mo))
            print(f"   {mo} open, {name:34s} | {show(blocks(rs, caps, mo))} | {n / days:4.1f} a day")
        print()
