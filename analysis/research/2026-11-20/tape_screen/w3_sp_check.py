# CqCAzte8 (Nov 22): tp 3x / 420 s / stall 240 with sell pressure off or 9 kinds, each alone on the 3 blind blocks (w3_robust.py, its menu replaced)
import sys, os
src = open("/home/user/copy2/analysis/research/2026-11-20/tape_screen/w3_robust.py").read()
a, b = src.split("MENU_EXITS = {", 1); b = b.split("}\n", 1)[1]
menu = "MENU_EXITS = {" + ", ".join(f'"tp 3x / 420 s / stall 240, sell pressure {sp[0]}/{sp[1]} s" if True else "": (3.0, 420, {sp}, 240, 0)' if sp else '"tp 3x / 420 s / stall 240, no sell pressure": (3.0, 420, None, 240, 0)'
                               for sp in [None, (3, 30), (3, 60), (5, 30), (5, 60), (5, 120), (8, 60), (10, 60), (15, 60), (15, 120)]) + "}\n"
src = a + menu + b
src = src.replace("real = rolling(G)", "import sys as _s\nos.environ['TABLE'] = '1'\nreal = rolling(G)")
exec(compile(src, "sp_check", "exec"), {"__file__": "/home/user/copy2/analysis/research/2026-11-20/tape_screen/w3_robust.py", "__name__": "__main__"})
