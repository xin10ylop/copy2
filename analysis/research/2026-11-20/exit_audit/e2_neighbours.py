# With wallet 4's sale followed at any time and no sell pressure (e1's leader), the other settings around the live ones:
# take profit, timer, stall. The same 146 copies, 1 SOL.   LK=SP/lk python3 -I e2_neighbours.py SP > out/e2_neighbours.txt
import sys, numpy as np
sys.argv += []; exec(open("e1_exits.py").read().split("V = {")[0])
h = len(ps) // 2
print(f"{'tp':>5s} {'hold':>5s} {'stall':>5s} {'SOL':>7s} {'w/o 2%':>7s} {'halves':>15s}")
for tp in (3.0, 4.0, 5.0, None):
    for hold in (300, 600, 900):
        for stall in (0, 120, 180, 240):
            x = np.array([exit_value(p, tp=tp, hold=hold, sp=None, stall=stall, its="always") for p in ps]); k2 = max(1, round(0.02 * len(x)))
            mark = "  <- live's tp/hold/stall" if (tp, hold, stall) == (4.0, 600, 180) else ""
            print(f"{str(tp):>5s} {hold:5d} {stall:5d} {x.sum():+7.2f} {np.sort(x)[:-k2].sum():+7.2f} {x[:h].sum():+7.2f} / {x[h:].sum():+5.2f}{mark}")
