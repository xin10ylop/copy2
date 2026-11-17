# SolHouse VIP: why following it loses, and what the winners have in common (the owner, Nov 17: "see what works and what
# fails, and exactly why"). The priced calls of Nov 10-17 (the fixed lab's rows) and their curve trades (who traded).
#   python3 -I tg_vip_why.py TGDIR > out/tg_vip_why.txt
import sys, os, json, gzip, numpy as np, statistics as st
TG = sys.argv[1]; here = os.path.dirname(os.path.abspath(__file__)); os.environ.setdefault("COST", "0.01")
src = open(os.path.join(here, "tg_vip_lab.py")).read().split("# ---- 1. signs")[0]
R = []
for v in ("vip", "vip_rest", "vip_h1"):
    os.environ["VDIR"] = v; ns = {"__file__": os.path.join(here, "tg_vip_lab.py")}; sys.argv = ["x", TG]
    exec(compile(src, "tg_vip_lab.py", "exec"), ns)
    for r in ns["rows"]: r["dir"] = v
    R += ns["rows"]
entry, trade, STAKE = ns["entry"], ns["trade"], ns["STAKE"]; order_slots = None
chs = open(os.path.join(here, "tg_channel.py")).read().split("for cj in sorted(glob.glob")[0]; cns = {}; sys.argv = ["x", TG]; exec(chs, cns); order_slots = cns["order_slots"]
print(f"{len(R)} VIP calls on the pump curve, Nov 10-17; a copy = 0.5 SOL bought 1 s after the post; costs {os.environ['COST']} SOL")
# 1. the price after the post
print("\n1. THE PRICE AFTER THE ALERT (over the price at the post): median, mean, share above the post's price")
for o in (10, 60, 120, 300, 600, 1800, 3600):
    x = [r["pr"][int(np.searchsorted(r["T"], r["t"] + o, side="right")) - 1] / r["p0"] for r in R]
    print(f"   +{o:4d} s: median {st.median(x):.2f}, mean {np.mean(x):.2f}, above the post's price {np.mean([v > 1 for v in x]):.0%}, under half of it {np.mean([v < 0.5 for v in x]):.0%}")
# 2. the arithmetic of a copy held to 2x or 60 min
pn = [(r, trade(r, entry(r, delay=1), tp=2, cap=3600)) for r in R if entry(r, delay=1) is not None]
w = [p for _, p in pn if p > 0]; l = [p for _, p in pn if p <= 0]; big = [p for _, p in pn if p >= 0.35]
print(f"\n2. THE ARITHMETIC (sell at 2x or after 60 min): {len(pn)} copies")
print(f"   won {len(w) / len(pn):.0%} of the copies, on average {np.mean(w) / STAKE:+.0%} each; of them reached 2x: {len(big) / len(pn):.0%} of all copies")
print(f"   lost {len(l) / len(pn):.0%} of the copies, on average {np.mean(l) / STAKE:+.0%} each; lost more than half: {np.mean([p < -0.25 for _, p in pn]):.0%} of all copies")
print(f"   so a copy makes {len(w) / len(pn):.2f} x {np.mean(w) / STAKE:+.2f} + {len(l) / len(pn):.2f} x {np.mean(l) / STAKE:+.2f} = {np.mean([p for _, p in pn]) / STAKE:+.1%}")
need = -np.mean(l) / (np.mean(w) - np.mean(l))
print(f"   to break even with wins and losses of this size, {need:.0%} of the copies must win (they win {len(w) / len(pn):.0%})")
# 3. who trades after the alert
tot = dict(b_new=0.0, b_old=0.0, s_new=0.0, s_old=0.0, s_dev=0.0); neg = []; n = 0
for r in R:
    f = f"{TG}/{r['dir']}/paths/{r['m']}.json.gz"
    if not os.path.exists(f): continue
    x = json.load(gzip.open(f)); tr = order_slots(x.get("tr") or []); t = r["t"]
    old = {e["user"] for e in tr if e["t"] <= t and e["buy"]}; aft = [e for e in tr if t < e["t"] <= t + 120]
    if not aft: continue
    n += 1; fl = 0.0
    for e in aft:
        q = e["q"] / 1e9; k = ("b_" if e["buy"] else "s_") + ("old" if e["user"] in old else "new"); tot[k] += q; fl += q if e["buy"] else -q
        if not e["buy"] and e["user"] == x.get("creator"): tot["s_dev"] += q
    neg.append(fl)
print(f"\n3. WHO TRADES IN THE 2 MINUTES AFTER THE ALERT ({n} calls, SOL on the curve)")
B_, S_ = tot["b_new"] + tot["b_old"], tot["s_new"] + tot["s_old"]
print(f"   bought: {B_:.0f} SOL ({tot['b_new'] / B_:.0%} by wallets new to the coin, {tot['b_old'] / B_:.0%} by wallets already in it)")
print(f"   sold:   {S_:.0f} SOL ({tot['s_old'] / S_:.0%} by wallets that had bought BEFORE the alert, {tot['s_new'] / S_:.0%} by wallets that bought after it; the dev {tot['s_dev'] / S_:.0%})")
print(f"   net: {B_ - S_:+.0f} SOL; a call's net flow in those 2 min: median {st.median(neg):+.2f} SOL, negative on {np.mean([v < 0 for v in neg]):.0%} of the calls")
# 4. the winners against the losers, in SOL terms
print("\n4. WHAT THE WINNERS HAVE (a copy sold at 2x or 60 min): the median of each sign for copies that reached 2x / that lost more than half / all")
W_ = [r for r, p in pn if p >= 0.35]; L_ = [r for r, p in pn if p < -0.25]; A_ = [r for r, _ in pn]
for k, name in (("s_holders", "holders at the call"), ("s_buyers", "buyers since launch"), ("s_avgbuy", "average buy, SOL"), ("s_top10", "top 10 holders' share"),
                ("s_dev", "dev's share"), ("s_bundle", "bought in the launch slot (share)"), ("s_n10", "trades in the 10 min before"), ("s_run10", "price run before the call"),
                ("s_mc", "market cap in the post, $"), ("s_age", "age in the post, min"), ("s_prog", "curve sold"), ("a_p120", "price 2 min after / at the post"), ("a_flow2", "net SOL in the 2 min after")):
    f_ = lambda v: st.median([r[k] for r in v if k in r]) if any(k in r for r in v) else float("nan")
    print(f"   {name:36s}: {f_(W_):10.3g} / {f_(L_):10.3g} / {f_(A_):10.3g}")
print(f"   ({len(W_)} copies reached 2x, {len(L_)} lost more than half, {len(A_)} in all)")
