# Step 8: the ranking table of the README from s5_rank.json, s6_holds.json and the overlap with wallet 4 (s7's test).
#   python3 -I s8_table.py [TOP=21] [EXTRA_WALLET ...]  ->  markdown on stdout
# Rule for the mechanical mark: flips = first sale within 10 s on 80%+ of its checked coins; holds = first sale at
# 60 s or later on 50%+; mixed otherwise.
import sys, os, time, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crc
TOP = int(sys.argv[1]) if len(sys.argv) > 1 else 21
R = crc.json.load(open(crc.OUT + "/s5_rank.json")); H = crc.json.load(open(crc.OUT + "/s6_holds.json"))
rows = [r for r in R["rows"] if r.get("indep")][:TOP]
rows += [r for r in R["rows"] if r["user"] in sys.argv[2:] and r not in rows]
W = R["coins"][crc.W4]
print("| # | Wallet | Coins +0/+1 (1.0+ SOL) | Median SOL | At +0 | First sale (median; <=10 s / >=60 s) | Trades by others within 2 slots | Net SOL, newest closed (won) | Shared with w4 (after w4) | Active (hours; last buy UTC) | Mark |")
print("|---:|---|---:|---:|---:|---|---:|---:|---:|---|---|")
for i, r in enumerate(rows):
    u = r["user"]; h = [x for x in H.get(u, {}).values() if "err" not in x]
    fs = [x["first"] for x in h if x["first"] is not None]
    closed = [x for x in h if x["gone"] is not None and x["curve_share"] and x["curve_share"] > 0.99]
    net = sum(x["sol_out"] - x["sol_in"] - x["sol_fee"] for x in closed); won = sum(1 for x in closed if x["sol_out"] - x["sol_in"] - x["sol_fee"] > 0)
    f10 = sum(1 for x in fs if x <= 10); f60 = sum(1 for x in fs if x >= 60)
    mark = "flips" if fs and f10 >= 0.8 * len(fs) else "holds" if fs and f60 >= 0.5 * len(fs) else "mixed" if fs else "?"
    cs = R["coins"][u]; sh = [m for m in cs if m in W] if u != crc.W4 else []
    aft = sum(1 for m in sh if (cs[m]["slot"], cs[m]["idx"] or 0) > (W[m]["slot"], W[m]["idx"] or 0))
    rank = [x["user"] for x in R["rows"] if x.get("indep")].index(u) + 1
    print(f"| {rank} | `{u}` | {r['n']} ({r['n_big']}) | {r['med_sol']:.2f} | {r['at0']:.0%} | "
          f"{st.median(fs) if fs else float('nan'):.0f} s; {f10} / {f60} of {len(fs)} | {r['fol']:.1f} | "
          f"{net:+.2f} on {len(closed)} ({won}) | {'calibration' if u == crc.W4 else f'{len(sh)} ({aft})'} | "
          f"{r['hours']}; {time.strftime('%H:%M', time.gmtime(r['last']))} | {mark} |")
