# The VIP-alert rule (Nov 17): copy the wallet's buy; if the SolHouse VIP alerts the coin within K s of the buy, keep
# holding under exit E; if not, sell at K. Only the copies on the VIP exports' days (the report's section 4).
# APPROXIMATE: a coin not alerted by K is valued at the t{K} exit (sold at K), so an exit E that would have sold it
# before K is ignored; an alerted coin is valued at E from the buy (E's own exits before the alert stand).
# Fixed before looking: K in {1, 2} min, E in {its-sale, sp5/60s, tp3}; halves by time; without the best 5.
#   python3 -I vip_rule.py SP WALLET8 [SUFFIX]
import sys, json, numpy as np
SP, W8 = sys.argv[1], sys.argv[2]; SUF = sys.argv[3] if len(sys.argv) > 3 else ""
COST = float(__import__("os").environ.get("COST", 0.0345))   # sim() charged 0.0026; this charges COST
R = [r for r in json.load(open(f"{SP}/winners/study_{W8}{SUF}.json")) if not r["refused"]]
for r in R: r["ex"] = {k: v - (COST - 0.0026) for k, v in r["ex"].items()}
VIP, SPANS = {}, []
for f in (f"{SP}/tg/vip/meta.json", f"{SP}/tg/vip2/meta.json"):
    mv = json.load(open(f)); ts = [v["t"] for v in mv.values()]; SPANS.append((min(ts), max(ts) - 600))
    for m, v in mv.items(): VIP.setdefault(m, v["t"])
C = sorted((r for r in R if any(a <= r["t"] <= b for a, b in SPANS)), key=lambda r: r["t"]); h = len(C) // 2
def S(v):
    s = sorted(v); return f"{len(v):3d} {sum(v):+6.2f} ({100 * np.mean(v) / 0.5 if v else 0:+6.1f}%) w/o5 {sum(s[:-5]) if len(s) > 5 else 0:+6.2f}"
print(f"{W8}: {len(C)} copies on the VIP days")
for e in ("its-sale", "sp5/60s", "tp3"):
    for k in (1, 2):
        def val(r):
            a = VIP.get(r["m"]); return r["ex"][e] if (a is not None and 0 <= a - r["t"] <= 60 * k) else r["ex"][f"t{k}m"]
        v = [val(r) for r in C]; base = [r["ex"][e] for r in C]
        print(f"   sell at {k} min unless alerted, then {e:9s}: all {S(v)} | 1st half {S(v[:h])} | 2nd half {S(v[h:])}   (plain {e}: {S(base)})")
