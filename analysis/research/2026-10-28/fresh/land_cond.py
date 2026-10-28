# land_pos.py under the live bot's conditions (Oct 28 evening): the stake and cap from the environment, the landing
# by block position, and FEE/BIAS from the environment (the live bot pays about 0.0014 SOL a transaction: a 0.001
# tip, a 0.0004 priority fee and the base fee; the fill premium is modelled by the position, so BIAS=0).
#   STAKE=0.1 CAP=1 FEE=0.0014 BIAS=0 NOT=AvcwGFaF,2FSWwQwj GRAD=1 python3 -I land_cond.py q 1 1.45 9
import os, sys
G = os.path.join(os.path.dirname(os.path.abspath(__file__)), "grid.py")
STAKE = float(os.environ.get("STAKE", "1.0"))
src = open(G).read()
old = '''    last = b["s"] + land
    ahead = [r for r in path if r[0] <= last]; va = ahead[-1][5] if ahead else vab
'''
new = '''    if isinstance(land, tuple):
        K = land[1]; last = b["s"]
        inb = lambda r: r[0] < b["s"] or (r[0] == b["s"] and (r[1] or 0) <= (b["i"] or 0) + K)
        ahead = [r for r in path if inb(r)]; va = ahead[-1][5] if ahead else vab
    else:
        inb = None; last = b["s"] + land
        ahead = [r for r in path if r[0] <= last]; va = ahead[-1][5] if ahead else vab
'''
assert src.count(old) == 1
src = src.replace(old, new)
old2 = '    rest = [r for r in path if r[0] > last]\n'
assert src.count(old2) == 1
src = src.replace(old2, '    rest = [r for r in path if not inb(r)] if inb else [r for r in path if r[0] > last]\n')
old3 = '''    for land in (1, 2, 3, 5, 10):
        show(f"landing {land} slot(s) after its slot", score(land=land)[0])'''
assert src.count(old3) == 1
src = src.replace(old3, f'''    for land in (1, ("pos", 100), ("pos", 30)):
        show(f"landing {{land}} stake {STAKE}", score(land=land, stake={STAKE})[0])''')
sys.argv = ["grid.py", "land"] + sys.argv[1:]
exec(compile(src, G, "exec"), {"__file__": G, "__name__": "__main__"})
