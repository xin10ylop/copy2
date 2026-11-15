# Does TAB16RxX add trades, or the same ones? Its copies (TAB live 2: tp 4.0, 600 s, its sale followed 0-60 s) split by
# whether wallet 4 bought the same coin with 1.3+ SOL within 30 minutes (those the wallet-4 bot copies already).
#   python3 -I overlap.py PATHS SCAN W4SCAN > out/overlap.txt
import sys, re, collections
sys.argv = sys.argv[:4]
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import tab_now as T
w4 = collections.defaultdict(list)
for l in open(sys.argv[3]):
    m = re.match(r"(\d+) (\S{8}) ([\d.]+) SOL", l)
    if m and float(m.group(3)) >= 1.3: w4[m.group(2)].append(int(m.group(1)))
sigs, tp, hold, early = T.RULES["TAB live 2 (Nov 13): tp 4.0, 600 s, its sale 0-60 s"]
g = collections.defaultdict(list)
for r in T.ROWS:
    both = any(abs(s - r["slot"]) < 4500 for s in w4.get(r["mint8"], []))
    nets = [T.model(T.PREP[r["key"], n], T.EX[r["key"], n], T.STAKE, sigs, tp, hold, early)[0] for n in T.L.LAND]
    g["wallet 4 bought it too (1.3+ SOL)" if both else "TAB16RxX alone"].append(sum(nets) / 3)
for k, v in g.items():
    s = sorted(v, reverse=True)
    print(f"{k:34s}: {len(v):3d} copies, net {sum(v):+6.2f} SOL ({100 * sum(v) / len(v) / T.STAKE:+5.1f}% a copy), {100 * sum(1 for y in v if y > 0) / len(v):4.1f}% won, without the best 2 {sum(s[2:]):+6.2f}, the best 3: " + " ".join(f"{y:+.2f}" for y in s[:3]))
