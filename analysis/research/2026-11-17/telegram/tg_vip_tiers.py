# SolHouse VIP by tier (and by pool, market cap, age, channels spotted in): its sampled calls (tg_vip_calls.py) priced by
# tg_test.py / tg_pool.py, our copy as tg_channel.py (same menu: entries post / skip5x / nospike / dip / confirm, exits
# tp1.5 / tp2 / tp3 / t10 / t30 / t60 / tp2sl / st2tp2). For each tier: the share of calls that reached 2x (and 1.5x)
# within the hour of the post, against the 34% bar (tg_vip.py), then each entry x exit on the first half of the 8 days
# (pick) and the second half (score), without the best 5.
#   python3 -I tg_vip_tiers.py TGDIR > out/tg_vip_tiers.txt
import sys, os, json, collections, statistics as st
TG = sys.argv[1]; D = f"{TG}/vip"; here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, "tg_channel.py")).read().split("for cj in sorted(glob.glob")[0]
sys.argv = [sys.argv[0], TG]; ns = {}; exec(compile(src, "tg_channel.py", "exec"), ns); load, sim, EN, EX = ns["load"], ns["sim"], ns["EN"], ns["EX"]
meta = json.load(open(f"{D}/meta.json")); calls = json.load(open(f"{D}/calls.json")); C = load(D)
pr = lambda r: r[1] / r[2]
def peak(t, P):
    pre = [r for r in P if r[0] <= t]; p0 = pr(pre[-1]); return max(pr(r) for r in P if t < r[0] <= t + 3600) / p0
T0, T1 = calls[0][1], calls[-1][1]; mid = (T0 + T1) / 2
print(f"{len(calls)} calls sampled, {len(C)} with a price path at the post; {(T1 - T0) / 86400:.1f} days, split at the middle")
def report(name, sub):
    if len(sub) < 10: print(f"\n== {name}: {len(sub)} calls (too few)"); return
    pk = [peak(t, P) for t, _, P in sub]
    print(f"\n== {name}: {len(sub)} calls; reached 2x {sum(p >= 2 for p in pk) / len(pk):.0%} (the bar: 34%), 1.5x {sum(p >= 1.5 for p in pk) / len(pk):.0%}; median peak {st.median(pk):.2f}")
    a = [x for x in sub if x[0] < mid]; b = [x for x in sub if x[0] >= mid]; best = None
    for en in EN:
        for ex in EX:
            va = [v for v in (sim(t, P, en, ex) for t, _, P in a) if v is not None]
            vb = [v for v in (sim(t, P, en, ex) for t, _, P in b) if v is not None]
            if va and (best is None or sum(va) > best[0]): best = (sum(va), en, ex, va, vb)
            if en == "post" and ex in ("tp1.5", "tp2", "t10", "t30"):
                f = lambda v: f"{len(v):3d} {sum(v):+6.2f} ({sum(v) / len(v) / 0.5:+5.1%}) w/o5 {sum(sorted(v, reverse=True)[5:]):+6.2f}" if v else "0"
                print(f"  post + {ex:6s}: 1st half {f(va)} | 2nd half {f(vb)}")
    if best:
        _, en, ex, va, vb = best; s = sorted(vb, reverse=True)
        print(f"  PICKED on the 1st half: {en} + {ex} ({sum(va):+.2f}) -> 2nd half {len(vb)} copies {sum(vb):+.2f}, w/o5 {sum(s[5:]):+.2f}")
tier = {m: meta[m]["tier"] for m in meta}
for tname in ("Diamond", "Safe", "Gamble", "Gamble Risk"): report(f"tier {tname}", [x for x in C if tier.get(x[1]) == tname])
report("all tiers", C)
for lab, f in (("on the pump curve at the post", lambda x: (meta[x[1]]["pool"] or "").strip() == "Pump.fun"),
               ("in a pool at the post", lambda x: (meta[x[1]]["pool"] or "").strip() != "Pump.fun"),
               ("market cap under 20K", lambda x: meta[x[1]]["mc"] < 2e4), ("market cap 20K-100K", lambda x: 2e4 <= meta[x[1]]["mc"] < 1e5),
               ("market cap 100K+", lambda x: meta[x[1]]["mc"] >= 1e5), ("spotted in 2+ channels", lambda x: meta[x[1]]["spotted"] >= 2)):
    report(lab, [x for x in C if f(x)])
