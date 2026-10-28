# One line of verdict per wallet (rank.py's top 15 and the four named ones) against wallet 4's profile:
#  (a) buys big other-token launches at create+0/+1 often: 20+ other-quote coins with an early buy of 0.45+ SOL
#      (of wallet 4's ~740 other-quote coins in 8.6 days: 2+ a day) and a median early buy of 0.45+ SOL;
#  (b) holds minutes rather than flipping: median hold to its first sale >= 60 s and at most 25% of its sales within 5 s;
#  (c) is followed by a frenzy: median others' buys in the 2 slots after its buy >= wallet 4's median on the same coins;
#  (d) lands: at most 15% failed among its transactions on these curves, and at most 15% in its newest 1,000 signatures;
#  (e) active late: coins on Oct 27-28 at least half wallet 4's late share of its coins, and a signature in the last 6 h
#      before the activity run.
# Worth a full scoring = (a) and (b) and (d) and (e).
#   python3 -I verdict.py   ->  printed (out/verdict.txt)
import sys, os, json, time, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nlib as L
R = json.load(open(L.OUT + "/rank.json")); A = json.load(open(L.OUT + "/activity.json"))
w4 = R["w4"]; late4 = w4["late"] / w4["coins"]
now = max(a["newest"] for a in A.values())
def ts(t): return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%m-%d %H:%M")
print(f"wallet 4 baseline: {w4['coins']} coins, {w4['late']} on Oct 27-28 ({late4:.1%}), median frenzy {w4['fr']}, its return {w4['ret']:+.3f}; newest signature seen {ts(now)} UTC")
print(f"{'wallet':44s} {'coins':>5s} {'big':>4s} {'SOL':>5s} {'hold_s':>6s} {'flip':>5s} {'frz':>4s} {'fail':>5s} {'live':>5s} {'late':>4s} {'ret':>6s} {'last sig':>11s}  a b c d e  verdict")
for u in list(dict.fromkeys(R["top"] + list(R["named"].values()))):
    s = R["sum"].get(u); a = A.get(u)
    if not s: print(f"{u:44s} not an early buyer on these coins"); continue
    big_other = sum(1 for r in R["recs"][u] if r["other"] and r["size"] >= 0.45)
    ca = big_other >= 20 and s["size"] >= 0.45
    flips = s["flip"] / s["sold"] if s["sold"] else 0
    cb = s["hold"] is not None and s["hold"] >= 60 and flips <= 0.25
    cc = s["fr"] >= w4["fr"]
    fail = s["fail"] / s["ntx"] if s["ntx"] else 0
    cd = fail <= 0.15 and (a is None or a["failed"] <= 0.15)
    ce = s["late"] / s["coins"] >= late4 / 2 and a is not None and a["newest"] >= now - 6 * 3600
    v = "WORTH A FULL SCORING" if ca and cb and cd and ce else "no"
    why = [n for n, ok in zip("abcde", (ca, cb, cc, cd, ce)) if not ok]
    hold = f"{s['hold']:.0f}" if s["hold"] is not None else "-"
    print(f"{u:44s} {s['coins']:5d} {big_other:4d} {s['size']:5.2f} {hold:>6s} {flips:5.0%} {s['fr']:4.0f} {fail:5.0%} "
          f"{(a['failed'] if a else float('nan')):5.0%} {s['late']:4d} {s['ret']:+6.3f} {ts(a['newest']) if a else '-':>11s}  "
          + " ".join("y" if ok else "." for ok in (ca, cb, cc, cd, ce)) + f"  {v}" + (f" (fails {','.join(why)})" if why else ""))
