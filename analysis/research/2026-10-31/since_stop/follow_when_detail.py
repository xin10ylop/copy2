# The best window rule of follow_when.py (follow its sale at 30-180 s after its buy if we are below 1.5x), coin by coin
# at landing 4 against live (never follow): what the live rule did on the copies it changes, the raw gain, and the
# gain after the live calibration per exit (timer +9.3, take profit +18.9 points; a sale behind its sale taken as a
# quick exit like a stop, +3.9). Every copy, no open-slot limit.
#   python3 -I follow_when_detail.py SPD
import sys, os, io, contextlib
SPD = sys.argv[1]
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv = ["x", SPD, ]; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import follow_when as F
CAL = {"time": 0.093, "tp": 0.189, "its_sell": 0.039, "graduated": 0.093, "refused": 0.0}
for wk, rs in (("week 1", F.E.A), ("week 2", F.E.B)):
    ch = []
    for r in rs:
        a = F.model(r, 4, 0, 0); b = F.model(r, 4, 30, 180, 1.5)
        if a and b and b[1] == "its_sell": ch.append((a, b))
    raw = sum(b[0] - a[0] for a, b in ch); cal = sum(b[0] + CAL[b[1]] - a[0] - CAL[a[1]] for a, b in ch)
    from collections import Counter
    print(f"{wk}: {len(ch)} copies followed; live did {dict(Counter(a[1] for a, _ in ch))}; "
          f"better {sum(1 for a, b in ch if b[0] > a[0])}, worse {sum(1 for a, b in ch if b[0] < a[0])}; raw {raw:+.2f} SOL, calibrated {cal:+.2f}")
