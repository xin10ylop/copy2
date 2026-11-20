# Why wallet 3's copies land late while the feed brings its buy at once (Nov 20: the box's "signal ... +0 blocks" for #47,
# then our buy sent in 97 ms landed 11 blocks after its buy): the crowd on the coin. For each of our buys since Nov 19
# 14:17 UTC: the leader's block, ours, and the curve trades (by anyone else) that landed between them on that coin.
#   python3 -I g2_crowd.py DIR > out/g2_crowd.txt
import sys, os, datetime as dt
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-19/rh_deep"); import rhd_lib as R
DATA = R.Data(sys.argv[1]); ME = "0x35bb5c55a531d14213380fd978a501f0e239a77e"
LEAD = {"0x9a3955a122ab8a649a8511df2dce169471fd0ec1": "w1", "0x5bc235acecff3dde394f4bfc696f7c35efd502f0": "w2", "0xc54d3914f91f984d61b63d491f38934c4e706b79": "w3",
        "0xa8603745beb925370089ec2af4e220d239b17466": "w7"}
T0 = dt.datetime(2026, 11, 19, 14, 17, tzinfo=dt.UTC).timestamp()
print(f"{'time':15s} {'coin':10s} {'who':4s} {'its blk':>10s} {'lag':>4s} {'trades between':>15s} {'in its block, after it':>23s} {'buys 1 s before its':>20s}")
for c in DATA.L:
    if c not in DATA.TR or not any(x[3] == ME for x in DATA.TR[c]): continue
    tr = DATA.path(c); b = next(i for i, e in enumerate(tr) if e["user"] == ME and e["buy"])
    if tr[b]["t"] < T0: continue
    ld = [(i, LEAD[e["user"]]) for i, e in enumerate(tr[:b]) if e["buy"] and e["user"] in LEAD and tr[b]["slot"] - e["slot"] <= 40]
    if not ld: continue
    k, who = ld[0]
    between = sum(1 for e in tr[k + 1:b] if e["user"] != ME)
    same = sum(1 for e in tr[k + 1:b] if e["slot"] == tr[k]["slot"])
    before = sum(1 for e in tr[:k] if tr[k]["slot"] - e["slot"] <= 10 and e["buy"])
    print(f"{dt.datetime.fromtimestamp(tr[b]['t'], dt.UTC):%m-%d %H:%M:%S} {c[:10]} {who:4s} {tr[k]['slot']:>10d} {tr[b]['slot'] - tr[k]['slot']:>4d} {between:>15d} {same:>23d} {before:>20d}")
