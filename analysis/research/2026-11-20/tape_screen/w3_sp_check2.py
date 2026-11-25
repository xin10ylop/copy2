# Sell pressure on top of a wallet's exit (Nov 25; the owner on HtHkKxYN and 3SiQo8MJ: "also no sell pressure?").
# w3_sp_check.py with the base exit from SPBASE = "tp,hold,stall" (HtHkKxYN: 3,420,240, the units' exit; 3SiQo8MJ:
# 2,120,0): the base alone, or with 3-15 more sells than buys over 30-120 s (from 30 s), each alone on the 3 blind blocks.
#   SPBASE=3,420,240 LK=SP/lk COST=0.0064 python3 -I w3_sp_check2.py SP WALLET
import sys, os
tp, hold, st = os.environ.get("SPBASE", "3,420,240").split(","); tp, hold, st = float(tp), int(hold), int(st)
src = open("/home/user/copy2/analysis/research/2026-11-20/tape_screen/w3_robust.py").read()
a, b = src.split("MENU_EXITS = {", 1); b = b.split("}\n", 1)[1]
lab = f"tp {tp:g}x / {hold} s" + (f" / stall {st}" if st else "")
menu = "MENU_EXITS = {" + ", ".join(f'"{lab}, sell pressure {sp[0]}/{sp[1]} s": ({tp}, {hold}, {sp}, {st}, 0)' if sp else f'"{lab}, no sell pressure": ({tp}, {hold}, None, {st}, 0)'
                               for sp in [None, (3, 30), (3, 60), (5, 30), (5, 60), (5, 120), (8, 60), (10, 60), (15, 60), (15, 120)]) + "}\n"
src = a + menu + b
src = src.replace("real = rolling(G)", "os.environ['TABLE'] = '1'\nreal = rolling(G)")
exec(compile(src, "sp_check2", "exec"), {"__file__": "/home/user/copy2/analysis/research/2026-11-20/tape_screen/w3_robust.py", "__name__": "__main__"})
