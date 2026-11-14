# The model against wallet 4's bot's 21 real trades of Nov 12-14 (the journal's net, pasted by the owner): the same
# coin, our real stake and the rule live at the time, our buy 2 / 4 / 8 trades after its own. real - model in points
# of the stake = what the raw model misses (the "correction" of lib.CAL was measured on Oct 28-29).
#   python3 -I live_gap_w4.py SPD
import sys, os, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lib as L
rows, P, info = L.load(sys.argv[1], 0)
E = (30, 180, 1.5); E2 = (30, 290, 1.5)
REAL = [  # id, coin, stake, real net, real exit, tp then, early rule then, timer then
    (0, "Ci9Bg1Bx", 0.1, -0.0597, "time", 2.5, None, 1790), (1, "BttUQVPM", 0.1, -0.0455, "time", 2.5, None, 1790), (2, "5tePJcGm", 0.1, 0.3531, "tp", 2.5, None, 1790),
    (3, "7dDprVHP", 0.5, -0.1106, "time", 2.5, None, 1790), (4, "57pQW4mw", 0.5, -0.0124, "time", 2.5, None, 1790), (5, "Eymbsj8M", 0.5, 0.6228, "tp", 2.5, None, 1790),
    (6, "GZn6HC8d", 0.5, -0.3763, "time", 2.4, None, 1790), (7, "GaHAZThn", 0.5, -0.1884, "time", 2.4, None, 1790), (8, "3EKoHX4f", 0.5, -0.0600, "time", 2.4, E, 1790),
    (9, "6S3iL67j", 0.5, -0.0907, "time", 2.4, E, 1790), (10, "BUdiaswB", 0.5, 1.3340, "tp", 2.4, E, 1790), (11, "GLmWEbqA", 0.5, -0.2837, "time", 2.4, E, 1790),
    (12, "3a8RGrQg", 0.5, -0.2201, "time", 2.4, E, 1790), (13, "BTCmcoKg", 0.5, 0.5786, "tp", 2.4, E, 1790), (14, "FAVdiH3q", 1.0, -0.0851, "time", 2.4, E, 1790),
    (15, "KgcdZjU4", 1.0, -0.2493, "time", 2.4, E, 1790), (16, "oxbezHbo", 1.0, -0.4291, "its_sell", 2.4, E, 1790), (17, "EH6yuh4Y", 1.0, -0.4260, "time", 2.4, E, 1790),
    (18, "4TMzhGzY", 0.5, -0.0310, "its_sell", 3.0, E2, 1200), (19, "6KpdMXAS", 0.5, -0.2420, "its_sell", 3.0, E2, 1200), (20, "DHcZRxRX", 0.4775, -0.1991, "time", 3.0, E2, 1200)]
by = {r["mint8"]: r for r in rows}
print(f"{'#':>3s} {'coin':8s} {'stake':>5s} {'real':>8s} {'exit':8s} | model at landing 2 / 4 / 8 (its exit)                    | real - model at 4, points of the stake")
gaps = {}; tot = [0, 0, 0, 0]
for i, m8, st, net, ex, tp, early, hold in REAL:
    r = by.get(m8)
    if not r: print(f"{i:3d} {m8} not in the rows (no path)"); continue
    o = []
    for n in (2, 4, 8):
        p = L.prep(r, P, n); o.append(L.model(p, st, tp=tp, hold=hold, early=early, sl=None) if p else None)
    if None in o: print(f"{i:3d} {m8} its buy not in the path"); continue
    g = 100 * (net - o[1][0]) / st; gaps.setdefault(ex, []).append(g)
    tot[0] += net; tot[1] += o[0][0]; tot[2] += o[1][0]; tot[3] += o[2][0]
    print(f"{i:3d} {m8} {st:5.1f} {net:+8.4f} {ex:8s} | " + " / ".join(f"{x[0]:+7.4f} ({x[1][:4]})" for x in o) + f" | {g:+6.1f}")
print(f"\ntotal real {tot[0]:+.4f} SOL; model at landing 2 {tot[1]:+.4f}, 4 {tot[2]:+.4f}, 8 {tot[3]:+.4f}")
for ex, g in gaps.items(): print(f"  {ex:8s} {len(g):2d} trades: real - model at landing 4, median {statistics.median(g):+.1f} points, mean {statistics.mean(g):+.1f}")
allg = [x for g in gaps.values() for x in g]; print(f"  all      {len(allg):2d} trades: median {statistics.median(allg):+.1f}, mean {statistics.mean(allg):+.1f}")
