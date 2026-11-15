# The HYPE float (the owner, Nov 16: "let's add HYPE"): the HYPE-paid buys' fee tiers (the fee rule skips under 125
# bps) and sizes, our copy of them, and the bot's run with HYPE added to the setup live since Nov 15 14:47 UTC (six
# kinds, min_sol 1.3 where the data has it: 1.45+ from ALL, 1.3-1.45 from CQ; the fee rule on), 2 open, 0.5 SOL.
#   python3 -I hype.py CQ ALL
import sys, os, datetime, collections
CQ, ALL = sys.argv[1], sys.argv[2]
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-14/float_exits"); import lib as L
RULE = dict(tp=3.0, hold=600, early=(30, 290, 1.5), sl=None)
CAPS = {"SOL": 1, "WBTC": 2, "PUMP": 1, "SPCX": 1, "TTWofwAg": 1, "DJTu7vi8": 1, "98sMhvDw": 1}
T0 = datetime.datetime(2026, 10, 21, 18, 30, tzinfo=datetime.timezone.utc).timestamp()
TB = L.T_STOP; TC = datetime.datetime(2026, 11, 6, 5, 32, tzinfo=datetime.timezone.utc).timestamp()
blk = lambda r: 0 if r["t"] < TB else 1 if r["t"] < TC else 2
PREP, ROWS, BPS = {}, [], {}
for SPD, lo, hi in ((ALL, 1.45, 1e9), (CQ, 1.3, 1.45)):
    rows, P, info = L.load(SPD, T0)
    for r in rows:
        if r["anchor"] not in CAPS or not (lo <= r["sol"] < hi): continue
        ps = [L.prep(r, P, n) for n in L.LAND]
        if any(p is None for p in ps): continue
        m, tr = P[r["key"]]; BPS[r["key"]] = next(e for e in tr if e["user"] == L.W4 and e["buy"] and e["slot"] == r["slot"])["bps"]
        for n, p in zip(L.LAND, ps): PREP[r["key"], n] = p
        ROWS.append(r)
ROWS.sort(key=lambda r: r["t"])
hy = [r for r in ROWS if r["anchor"] == "98sMhvDw"]
print(f"HYPE-paid buys with a path: {len(hy)} (1.3-1.45 SOL ones only if CQ has them: {sum(1 for r in hy if r['sol'] < 1.45)}); fee tiers {dict(collections.Counter(BPS[r['key']] for r in hy).most_common(6))}")
ok = [r for r in hy if not (0 < BPS[r["key"]] < 125)]
nets = [sum(L.model(PREP[r["key"], n], 0.5, **RULE)[0] for n in L.LAND) / 3 for r in ok]
b = [sum(x for r, x in zip(ok, nets) if blk(r) == k) for k in range(3)]
print(f"after the fee rule: {len(ok)} copies, every copy {sum(nets):+.2f} SOL (A {b[0]:+.2f}  B {b[1]:+.2f}  C {b[2]:+.2f}), {100 * sum(nets) / max(1, len(ok)) / 0.5:+.1f}% a copy")
def sim(rs, n):
    out, open_ = [], []
    for r in rs:
        open_ = [x for x in open_ if x[0] > r["t"]]
        if len(open_) >= 2 or sum(1 for x in open_ if x[1] == r["anchor"]) >= CAPS[r["anchor"]]: continue
        net, why, held = L.model(PREP[r["key"], n], 0.5, **RULE)
        if why != "refused": open_.append((r["t"] + held, r["anchor"]))
        out.append((r, net))
    return out
for name, keep in (("live (six kinds, min_sol 1.3, fee rule)", lambda r: r["anchor"] != "98sMhvDw"), ("+ HYPE", lambda r: True)):
    rs = [r for r in ROWS if keep(r) and not (0 < BPS[r["key"]] < 125) and not (r["sol"] < 1.45 and r["anchor"] == "98sMhvDw" and False)]
    m = [0.0] * 4; w5 = 0.0
    for n in L.LAND:
        res = sim(rs, n); s = sorted((x[1] for x in res), reverse=True); w5 += sum(s[5:]) / 3
        for k in range(3): m[k] += sum(x[1] for x in res if blk(x[0]) == k) / 3
    print(f"   {name:42s}: {sum(m[:3]):+6.2f} (without the best 5 {w5:+6.2f}) | A {m[0]:+6.2f}  B {m[1]:+6.2f}  C {m[2]:+6.2f}")
