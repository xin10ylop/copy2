# The bot's real take profits and the buy it missed for lack of SOL, in the model under each candidate rule (landing
# 4, 0.5 SOL): the coin's high, when it passed 3.0x and 4.0x, and each rule's result.
#   python3 -I winners.py SPD
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lib as L
rows, P, info = L.load(sys.argv[1], 0); by = {r["mint8"]: r for r in rows}
RULES = (("old 2.4/1790", dict(tp=2.4, hold=1790, early=(30, 180, 1.5), sl=None)), ("live 3.0/1200", dict(tp=3.0, hold=1200, early=(30, 290, 1.5), sl=None)),
         ("3.0/600", dict(tp=3.0, hold=600, early=(30, 290, 1.5), sl=None)), ("4.0/600", dict(tp=4.0, hold=600, early=(30, 290, 1.5), sl=None)))
for m8, note in (("5tePJcGm", "real win #2"), ("Eymbsj8M", "real win #5"), ("BUdiaswB", "real win #10"), ("HdBaFgoC", "missed Nov 14 06:13 UTC, SOL under the stake"),
                 ("4TMzhGzY", "#18"), ("6KpdMXAS", "#19"), ("DHcZRxRX", "#20"), ("EH6yuh4Y", "#17")):
    if m8 not in by: print(m8, "not in the rows"); continue
    p = L.prep(by[m8], P, 4); w = p["age"] < 1790; i3, i4 = L.first(p["px"] >= 3.0), L.first(p["px"] >= 4.0)
    at = lambda s: p["px"][p["age"] <= s][-1] if (p["age"] <= s).any() else float("nan")
    print(f"{m8} ({note}): high {p['px'][w].max():.2f}x; 3.0x at {None if i3 is None else int(p['age'][i3])} s, 4.0x at {None if i4 is None else int(p['age'][i4])} s; price at 600 s {at(600):.2f}x, at 1200 s {at(1200):.2f}x")
    print("      " + " | ".join(f"{n}: {L.model(p, 0.5, **kw)[0]:+.3f} ({L.model(p, 0.5, **kw)[1]} {L.model(p, 0.5, **kw)[2]} s)" for n, kw in RULES))
