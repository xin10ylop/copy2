# One wallet's setup by coin kind x its buy size x exit (Nov 23; the owner on CgyPomTG: "shouldn't we now see the best
# setup for it? types of coins? buy size? exit?"). w3_robust.py's copies (cached), no pick: every cell over the 4 time
# blocks of its buys, % a copy at 1 SOL, and how many of the 4 blocks are positive. A cell to trust is positive in 4 of 4
# (or 3 of 4) AND positive without its best 2%; a big mean from one block is noise.
#   RPC_URL=... LK=SP/lk COST=0.0064 python3 -I w3_setup.py SP WALLET
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "w3_robust.py")).read().split("real = rolling(G)")[0]
src += '''
bands = (("0.5+ SOL", 0.5, 1e9), ("0.5-1.3", 0.5, 1.3), ("1.3+", 1.3, 1e9))
print(f"\\n{'coins':6s} {'its buy':8s} {'exit':52s} {'block 1':>7s} {'2':>7s} {'3':>7s} {'4':>7s}  {'all (n)':>13s} {'w/o 2%':>7s} {'+blocks':>7s}")
for kd in ("all", "SOL", "token"):
    for bn, lo, hi in bands:
        keep = (sol >= lo) & (sol < hi) & ((kd == "all") | ((kd == "token") == tok)); ref = prem > 1.5
        for e in range(len(ENAMES)):
            v_all = np.where(ref, -0.0004, G[:, e])
            per = [v_all[b][keep[b]] for b in blocks]; a = v_all[keep]
            if len(a) < 12: continue
            pos = sum(1 for p in per if len(p) and p.mean() > 0)
            print(f"{kd:6s} {bn:8s} {ENAMES[e]:52s} " + " ".join(f"{100 * p.mean():+6.1f}%" if len(p) else "     - " for p in per)
                  + f"  {100 * a.mean():+6.1f}% ({len(a):3d}) {wo2(a):+7.2f} {pos:4d}/4")
'''
exec(compile(src, "w3_setup", "exec"), {"__file__": os.path.join(HERE, "w3_robust.py"), "__name__": "__main__"})
