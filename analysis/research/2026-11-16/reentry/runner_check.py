# Checking reentry.py's runner result (Nov 16): keeping 10% cost about as much as keeping 50% (-4.61 / -6.04), so most
# of the cost was not the coins but the runner holding one of the two slots for ten minutes. Here the two effects
# apart: (a) the runner holds its slot (as reentry.py); (b) the runner does not count against the two slots (the bot
# would need a change for that); and what the kept share itself does on the copies left on a signal or its sale:
# how many of them reach tp 4 before the timer, and the kept share's own net.
#   python3 -I runner_check.py CQ ALL > out/runner_check.txt
import sys, os, random
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.argv = sys.argv[:3]
import reentry as RE
from reentry import L, ROWS, PREP, EX, R3, STAKE, SIGS, TP, HOLD, E, SIG_EXITS, CAPS, blk, day, B0
def score(f, block_slot):
    tot, b, days, wo = 0, [0, 0, 0], {}, []
    kept = []
    for n in L.LAND:
        open_, res = [], []
        for r in ROWS:
            open_ = [y for y in open_ if y[0] > r["t"]]
            if len(open_) >= 2 or sum(1 for y in open_ if y[1] == r["anchor"]) >= CAPS[r["anchor"]]: continue
            p, x = PREP[r["key"], n], EX[r["key"], n]
            if p["refused"]: res.append((r, -0.0004)); continue
            net, why, held = R3.model(p, x, STAKE, SIGS, TP, HOLD, E)
            if f and why in SIG_EXITS and len(p["px"]):
                k = L.model(p, STAKE * f, TP, HOLD, None, None)
                part = (k[0] + 0.0026) - 0.0013                       # the kept share: no buy of its own, one extra sale
                if n == 4: kept.append((part, k[1], net * f))
                net = net * (1 - f) + part + 0.0026 * f
                if block_slot: held = max(held, k[2])
            open_.append((r["t"] + held, r["anchor"])); res.append((r, net))
        v = sorted((q[1] for q in res), reverse=True); tot += sum(v) / 3; wo.append(sum(v[5:]))
        for r, net in res: b[blk(r)] += net / 3; days[day(r["t"])] = days.get(day(r["t"]), 0) + net / 3
    ks = sorted(days)[1:-1]
    return dict(tot=tot, b=b, wo5=sum(wo) / 3, days=[days[k] for k in ks], neg=sum(1 for k in ks if days[k] < 0), worst=min(days[k] for k in ks)), kept
random.seed(7)
print(f"the live setup {B0['tot']:+.2f} SOL; gain against it; * = ahead in all three blocks; noise of one change about +-3.4")
for block in (True, False):
    print(f"== the runner {'holds its slot (as reentry.py)' if block else 'does NOT count against the two slots'}")
    for f in (0.1, 0.2, 0.3, 0.5):
        s, kept = score(f, block); d = [a - c for a, c in zip(s["days"], B0["days"])]; dr = sorted(sum(random.choice(d) for _ in d) for _ in range(2000))
        star = "*" if all(s["b"][i] > B0["b"][i] for i in range(3)) else " "
        tpn = sum(1 for q in kept if q[1] == "tp")
        print(f"   keep {int(f * 100):2d}%: {s['tot']:+6.2f} | gain {s['tot'] - B0['tot']:+6.2f}{star} | blocks {s['b'][0] - B0['b'][0]:+5.2f} {s['b'][1] - B0['b'][1]:+5.2f} {s['b'][2] - B0['b'][2]:+5.2f} | w/o b5 {s['wo5']:+6.2f} | neg {s['neg']} | worst {s['worst']:+5.2f} | ahead in {sum(1 for y in dr if y > 0) / 20:5.1f}% [{dr[100]:+5.1f}, {dr[1900]:+5.1f}]"
              + f" | landing 4: {len(kept)} kept shares, {tpn} reach tp 4, the kept shares net {sum(q[0] for q in kept):+.2f} against {sum(q[2] for q in kept):+.2f} had they been sold with the rest")
