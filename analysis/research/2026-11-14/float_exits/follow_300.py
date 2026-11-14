# His sales at his own 300 s timer (290-330 s after his buy, the coin under 1.5x): sell behind them or hold?
# Coin by coin, every copy (no slot limit), tp 3.0, 1200 s: the copies where the two rules differ. Also his later
# sales (330-1200 s), and all of his sales.
#   python3 -I follow_300.py SPD
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.argv = sys.argv[:2] + ["0.5"]; import float_exits as F
import lib as L
base = dict(tp=3.0, hold=1200, sl=None)
for name, alt in (("also 290-330 s (30-330)", (30, 330, 1.5)), ("also to 600 s (30-600)", (30, 600, 1.5)), ("every sale under 1.5x (30-1200)", (30, 1200, 1.5)), ("every sale, any price (0-1200)", (0, 1e9, 1e9))):
    print(f"hold (window 30-290 s) against {name}: copies the change touches, landing 4 / 8 / late")
    for h in (0, 1):
        out = []
        for n in L.LAND:
            d = []
            for r in F.rows:
                if F.HALF(r) != h: continue
                p = F.PREP[r["key"], n]
                a = L.model(p, 0.5, early=(30, 290, 1.5), **base); b = L.model(p, 0.5, early=alt, **base)
                if a[1] != b[1] or a[2] != b[2]: d.append((b[0] - a[0], a, b))
            won_cut = sum(1 for x in d if x[1][1] == "tp")
            out.append(f"{len(d)} copies, selling behind him {sum(x[0] for x in d):+.2f} SOL ({sum(1 for x in d if x[0] > 0)} better, {sum(1 for x in d if x[0] < 0)} worse, {won_cut} take profits cut)")
        print(f"   {'first' if h == 0 else 'second'} half: " + " | ".join(out))
