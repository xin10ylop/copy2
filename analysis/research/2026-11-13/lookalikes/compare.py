# The comparison table: each wallet against wallet 4 on three numbers, per week: its real result on the coins we would
# copy, our copy raw (the model) and corrected (raw + its gap x copies: the model's measured caution for that wallet,
# copyscore.py), (without each week's best 2). Read from copyscore.py's json files in LK.
#   python3 -I compare.py FILE...   (copyscore_<w8>_<floor>..._.json names, wallet 4's first)
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lib
POL = ("HOLD (tp 2.5, 30 min; live)", "FOLLOW (behind its sale, 30 min cap)")
print("Week 1 = Oct 29 12:02 -> Nov 5 06:49 UTC (pick), week 2 = Nov 5 06:49 -> Nov 12 06:49 UTC (test). 1 SOL, 2 open, landing 4 trades after its buy.")
print("real = its own SOL result on the coins we copy (w/o its best 2); raw / corr = our copy, model / model + gap x copies (w/o best 2)\n")
print(f"{'wallet (coins)':34s} {'wk':3s} {'its real':>17s} {'gap':>5s} | {'HOLD raw (w/o 2)':>17s} {'corr':>7s} {'n':>4s} | {'FOLLOW raw (w/o 2)':>18s} {'corr':>7s} | {'exit picked on week 1: wk 2 raw (w/o 2), corr':>52s}")
for f in sys.argv[1:]:
    j = json.load(open(f if os.path.exists(f) else f"{lib.OUT}/{f}"))
    lab = f"{j['W'][:8]} {j.get('kind', 'pump, other quote')[6:9]}{' parts' if j.get('multi') else ''} {j['floor']}+"
    for p, wk in (("P1", "1"), ("P2", "2")):
        r = j.get("real", {}).get(p); g = j["gap"].get(p, 0)
        real = f"{r['net']:+6.2f} ({r['net2']:+6.2f})" if r else "-"
        cells = []
        for pol in POL:
            k, s, s2, ref, corr = j["table"][f"{pol}|4 after|{p}"]
            cells.append((s, s2, corr, k))
        pick = ""
        if p == "P2" and "p2land" in j["best"]:
            k, s, s2, ref = j["best"]["p2land"][0]
            rl = j['best']['rule'].split(); pick = f"{rl[0]} tp {rl[2]} stop {rl[4]} {rl[5]}: {s:+6.2f} ({s2:+6.2f}) {s + g / 100 * k:+7.2f}"
        print(f"{lab:34s} {wk:3s} {real:>17s} {g:+5.1f} | {cells[0][0]:+7.2f} ({cells[0][1]:+6.2f}) {cells[0][2]:+7.2f} {cells[0][3]:4d} | "
              f"{cells[1][0]:+8.2f} ({cells[1][1]:+6.2f}) {cells[1][2]:+7.2f} | {pick:>52s}")
