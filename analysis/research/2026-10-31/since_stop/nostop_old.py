# The stop question on the earlier data (fresh/grid.py, Oct 19-28, the bot's set): tp 2.0 / 2.5, with the 0.8 stop, a
# 0.7 stop and none, at slot +1 and 30 positions behind its buy, at the backtest's costs and the live ones. The old paths
# end at its own sale, so every variant here sells behind its early sales (rare before Oct 27).
#   (from analysis/research/2026-10-28/fresh) CAP=3 NOT=AvcwGFaF,2FSWwQwj GRAD=1 python3 -I ../../2026-10-31/since_stop/nostop_old.py
import sys, os
G = os.path.abspath("grid.py"); src = open(G).read()
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
src = src.replace(old, new).replace('    rest = [r for r in path if r[0] > last]\n', '    rest = [r for r in path if not inb(r)] if inb else [r for r in path if r[0] > last]\n')
sys.argv = ["grid.py", "none", "q", "1", "1.45", "9"]
ns = {"__file__": G, "__name__": "__main__"}; exec(compile(src, G, "exec"), ns)
for fee, bias, name in ((0.0095, 0.0155, "the backtest's costs"), (0.0014, 0.0, "the live costs")):
    ns["FEE"], ns["BIAS"] = fee, bias
    print(f"== {name}")
    for land in (1, ("pos", 30)):
        for tp in (2.0, 2.5):
            for sl in (0.8, 0.7, None):
                ns["show"](f"land {land} tp {tp} stop {sl}", ns["score"](tp=tp, sl=sl, land=land)[0])
