# How often holding past wallet 4's sale pays (the 5tePJcGm case: it sold at +113%, we held to the take profit). Every
# coin, Oct 29 14:02 - Nov 12 08:49 Beirut, 1 SOL, raw model, landing 4; hold (live) against selling behind it.
#   python3 -I hold_wins.py SPD
import sys, os, io, contextlib
SPD = sys.argv[1]
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv = ["x", SPD]; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import exit_search as E
LIVE = dict(tp=2.5, sl=None, hold=1790, follow=None, pmax=1.25, trail=None)
for name, rs in (("week 1", E.A), ("week 2", E.B), ("both", E.A + E.B)):
    d = []
    for r in rs:
        h = E.model(r, 4, **LIVE); f = E.model(r, 4, **dict(LIVE, follow=1e9))
        if h and f and h[1] != "refused": d.append((h[0] - f[0], h, f))
    sold_first = [x for x in d if x[2][1] == "its_sell"]          # it sold before our own exit
    tp_after = [x for x in sold_first if x[1][1] == "tp"]         # we held past its sale and reached the take profit
    better = [x for x in sold_first if x[0] > 0.005]; worse = [x for x in sold_first if x[0] < -0.005]
    print(f"{name}: {len(d)} copies; it sold before our exit on {len(sold_first)}")
    print(f"  holding past its sale reached take profit (the 5tePJcGm case): {len(tp_after)} coins, "
          f"+{sum(x[0] for x in tp_after):.2f} SOL over selling behind it ({sum(x[0] for x in tp_after)/max(1,len(tp_after)):+.2f} each)")
    print(f"  holding better: {len(better)} coins, {sum(x[0] for x in better):+.2f} SOL | holding worse: {len(worse)} coins, "
          f"{sum(x[0] for x in worse):+.2f} SOL ({sum(x[0] for x in worse)/max(1,len(worse)):+.3f} each) | net {sum(x[0] for x in d):+.2f}")
