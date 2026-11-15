# Shared loader for signals.py / signals2.py (see signals.py's header).
# Sell on what the other holders do (the owner, Nov 15 evening: "analyze top 10 holders, if they sell, these
# things"). The paths start at wallet 4's buy, so a holder's whole bag is not known; what is known is every trade on
# the curve after it: who, buy or sell, how many tokens, how much SOL. A pump coin has 1,000,000,000 tokens; a
# top-10 holder of a young coin holds about 1-4% of them, so "a sell of 2%+ of the supply" is a top holder selling.
# Signals, each checked on every trade after our buy (wallet 4's own trades and ours left out; the sale on the trade
# after the signal, as the early sale and tp):
#   big     a sell of s% of the supply or more (a top holder dumping)
#   bigsum  sells of s% of the supply or more within w seconds, added up
#   cluster k different sellers within w seconds
#   flow    the coin's net SOL (buys - sells) over the last w seconds at -X SOL or worse
#   drain   sells minus buys since our buy at X SOL or more
#   each from age 0 or only after 30 s, and either at any price or only while under 1.5x (a winner keeps running)
# On top of the live rule (tp 3.0, 600 s, early 30-290 s under 1.5x). The setup and data as ../trail/trail.py: seven
# kinds, 1.3+ SOL, every fee tier, 2 open, caps; 0.5 SOL; mean of three landings; blocks A / B / C; picked on two
# blocks, scored on the third.
#   python3 -I signals.py CQ ALL > out/signals.txt
import sys, datetime, collections, itertools
import numpy as np
CQ, ALL = sys.argv[1], sys.argv[2]
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-14/float_exits"); import lib as L
CAPS = {"SOL": 1, "WBTC": 2, "PUMP": 1, "SPCX": 1, "TTWofwAg": 1, "DJTu7vi8": 1, "98sMhvDw": 1}
OURS = {L.W4, "Eao8T2Pk2aDzPWUFCA8si7oWd5ndFKfnX3HjYMpERst6"}
T0 = datetime.datetime(2026, 10, 21, 18, 30, tzinfo=datetime.timezone.utc).timestamp()
TB = L.T_STOP; TC = datetime.datetime(2026, 11, 6, 5, 32, tzinfo=datetime.timezone.utc).timestamp()
blk = lambda r: 0 if r["t"] < TB else 1 if r["t"] < TC else 2
day = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d")
PREP, EX, ROWS = {}, {}, []
for SPD, lo, hi in ((ALL, 1.45, 1e9), (CQ, 1.3, 1.45)):
    rows, P, info = L.load(SPD, T0)
    for r in rows:
        if r["anchor"] not in CAPS or not (lo <= r["sol"] < hi): continue
        ps = [L.prep(r, P, n) for n in L.LAND]
        if any(p is None for p in ps): continue
        m, tr = P[r["key"]]
        k = next(i for i, e in enumerate(tr) if e["user"] == L.W4 and e["buy"] and e["slot"] == r["slot"])
        for n, p in zip(L.LAND, ps):
            PREP[r["key"], n] = p
            rest = tr[len(tr) - len(p["px"]):]               # the trades lib.prep keeps after our entry
            j = len(tr) - len(p["px"]) - 1
            other = np.array([e["user"] not in OURS for e in rest], dtype=bool)
            EX[r["key"], n] = dict(other=other, sell=np.array([not e["buy"] for e in rest], dtype=bool) & other,
                                   tok=np.array([e["tok"] / 1e15 for e in rest]),
                                   sol=np.array([e["q"] * p["rate"] / 1e9 * (1 if e["buy"] else -1) for e in rest]) * other,
                                   user=[e["user"] for e in rest], pin=(tr[k]["vt"] / tr[j]["vt"]) ** 2)
        ROWS.append(r)
ROWS.sort(key=lambda r: r["t"])
