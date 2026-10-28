# One row of README.md's table from marks.py's <w8>_marks.json and grid.py's printed cap and land runs (out/).
#   python3 -I row.py WALLET [FLOOR=1.45]
import sys, os, json, re
SP = os.environ.get("SP", "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/score")
W = sys.argv[1]; FLOOR = float(sys.argv[2]) if len(sys.argv) > 2 else 1.45; w = W[:8]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
suf = "" if FLOOR == 1.45 else "_" + str(FLOOR)
M = json.load(open(f"{SP}/h9long/{w}_marks{suf}.json"))
def grid(name):
    f = f"{OUT}/{w}_grid_{name}{suf}.txt"
    if not os.path.exists(f): return {}
    out = {}
    for l in open(f):
        m = re.match(r"\s+(.+?)\s+P1\s+(\d+)\s+([+-][\d.]+) \(\s*([+-][\d.]+)\)\s+P2\s+(\d+)\s+([+-][\d.]+) \(\s*([+-][\d.]+)\)\s+P3\s+(\d+)\s+([+-][\d.]+) \(\s*([+-][\d.]+)\)", l)
        if m: out[m.group(1)] = m.groups()[1:]
    return out
def cell(g):
    return " / ".join(f"{g[i + 1]} ({g[i + 2]}), {g[i]}" for i in (0, 3, 6)) if g else "no copies"
m1 = " / ".join(f"{M[f'm1_{FLOOR}_{p}']['day']:.1f}" for p in ("P1", "P2", "P3"))
m1h = " / ".join(f"{M[f'm1_0.5_{p}']['day']:.1f}" for p in ("P1", "P2", "P3"))
meas = sum(M[f"m1_{FLOOR}_{p}"]["meas"] for p in ("P1", "P2", "P3")); c01 = sum(M[f"m1_{FLOOR}_{p}"]["c01"] for p in ("P1", "P2", "P3"))
q = ", ".join(f"{k} {v}" for k, v in M[f"m1_{FLOOR}_quotes"][:4])
m2 = M.get("m2_0", {}); m2b = M.get(f"m2_{FLOOR}", {})
rule = (f"{m2.get('n', 0)} trips; hold p25/50/75 {'/'.join(str(int(x)) for x in m2['sec'][1:4])} s; at 1,790 s+ {100 * m2['t1790'] / m2['n']:.0f}%; "
        f"sale multiple p10/50/90 {m2['marg'][0]}/{m2['marg'][2]}/{m2['marg'][4]}x") if m2.get("n") else "no one-buy one-sell trips"
m3 = " / ".join(f"{100 * M[f'm3_{p}']['early'] / M[f'm3_{p}']['n']:.0f}% of {M[f'm3_{p}']['n']}" if M.get(f"m3_{p}", {}).get("n") else "none" for p in ("P1", "P2", "P3"))
m4 = M["m4"]; m5 = M[f"m5_{FLOOR}"]; m5h = M["m5_0.5"]
m6 = " / ".join(f"{M[f'm6_{p}_all tokens'][1]:+.2f} ({M[f'm6_{p}_all tokens'][2]:+.2f})" for p in ("P1", "P2", "P3"))
cap = grid("cap"); land = grid("land")
as_built = cap.get("as built: tp 2.0 sl 0.8 1790 s")
l3 = land.get("landing 3 slot(s) after its slot")
m8 = M["m8"]
print(f"| {w} | {m1} ({m1h} at 0.5+); create+0/+1 {c01} of {meas}; {q} | {rule} | {m3} | "
      f"{100 * m4['fail'] / max(m4['fail'] + m4['own'], 1):.1f}% | {m5['abc']} of {m5['n']} ({100 * m5['abc'] / max(m5['n'], 1):.0f}%; 0.5+: {100 * m5h['abc'] / max(m5h['n'], 1):.0f}%) | "
      f"{m6} | {cell(as_built)}; slot +3: {cell(l3)} | {m8['n01']} (n {m8['n']}) |")
