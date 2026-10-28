# Where our buy lands inside wallet 4's own slot (Oct 28 evening): grid.py's `land` grid extended to block positions.
# grid.py fills our buy on the state after the last trade at slot <= its slot + land. Here `("pos", K)` fills it after
# the last trade in its own slot at block index <= its index + K (the path rows carry the index in the block, r[1]),
# so K = 0 is the trade right behind its buy, and K = 600 is the end of its slot (= land 0). Same costs and model as
# grid.py (q + lift, CAP from the environment, NOT/GRAD for the bot's set).
#   CAP=4 python3 -I land_pos.py [q 1 1.45 9]; CAP=4 NOT=AvcwGFaF,2FSWwQwj GRAD=1 python3 -I land_pos.py q 1 1.45 9
import os, sys
G = os.path.join(os.path.dirname(os.path.abspath(__file__)), "grid.py")
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
src = src.replace("for land in (1, 2, 3, 5, 10):",
                  'for land in (("pos", 0), ("pos", 30), ("pos", 60), ("pos", 100), ("pos", 130), ("pos", 300), ("pos", 600), 0, 1, 2):')
sys.argv = ["grid.py", "land"] + sys.argv[1:]
exec(compile(src, G, "exec"), {"__file__": G, "__name__": "__main__"})
