# Step 3. Entry filters: every rule the bot could apply when it sees wallet 4's buy (or, for the refusal limit, at our
# own fill), run as the bot runs (2 open, SOL 1 / WBTC 2 / PUMP 1 / SPCX 1; a skipped copy frees its slot), the live
# exit rule, mean of the three landings. The grid: each numeric feature, skip its lowest or its highest 10 / 20 / 30 /
# 40% (cut values from all 781 buys), each category value, and a tighter refusal limit. A filter "holds" when its net
# beats the baseline in each of the blocks A, B and C. Also: picked on two blocks, scored on the third (each way
# round), and how often a RANDOM skip of the same share holds in all three blocks (the chance rate).
#   python3 -I filters.py > out/filters.txt
import sys, os, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import common as C
NUM = ["sol", "size_vs_recent", "progress", "mcap", "bps", "impact", "hops", "nslot_before", "nslot_sell_before", "slot_buysol_before",
       "w4_big_10m", "w4_big_60m", "mins_since_last_big", "w4_tx_1500slots", "paper_last10_net", "paper_last10_tp", "w4_last10_ret",
       "n_before", "tx_60s", "fail_share", "dev_share", "slots_since_create", "creator_prev", "creator_prev_net", "age_s"]
def grid():
    F = []
    for k in NUM:
        v = sorted(r["f"][k] for r in C.R)
        for q in (0.1, 0.2, 0.3, 0.4):
            lo = v[int(len(v) * q)]; hi = v[int(len(v) * (1 - q)) - 1]
            F.append((f"{k} < {lo:.4g}", lambda r, n, k=k, lo=lo: r["f"][k] < lo))
            F.append((f"{k} > {hi:.4g}", lambda r, n, k=k, hi=hi: r["f"][k] > hi))
    for a in ("SOL", "WBTC", "PUMP", "SPCX"): F.append((f"pays with {a}", lambda r, n, a=a: r["anchor"] == a))
    for h in ("copied", "curve"): F.append((f"route {h}", lambda r, n, h=h: r["f"]["how"] == h))
    for w in range(7): F.append((f"Beirut weekday {w}", lambda r, n, w=w: r["f"]["wday"] == w))
    for h0 in (0, 6, 12, 18): F.append((f"UTC hour {h0}-{h0 + 5}", lambda r, n, h0=h0: h0 <= r["f"]["hour"] < h0 + 6))
    F.append(("first trade is not a create", lambda r, n: not r["f"]["is_create"]))
    F.append(("creator seen before", lambda r, n: r["f"]["creator_prev"] > 0))
    for pm in (1.05, 1.10, 1.15, 1.20): F.append((f"refusal limit {pm}", lambda r, n, pm=pm: r["pxin"][n] > pm))
    # drop rules that skip nothing or the same buys as an earlier one
    seen, out = set(), []
    for name, fn in F:
        s = frozenset((r["key"], n) for r in C.R for n in C.LAND if fn(r, n))
        if not s or s in seen: continue
        seen.add(s); out.append((name, fn))
    return out
def score(base, m):
    d = [m["blocks"][b] - base["blocks"][b] for b in range(3)]
    return d, all(x > 0 for x in d)
if __name__ == "__main__":
    base = C.measures()
    FL = grid()
    print(f"{len(FL)} distinct entry filters tried (after dropping empty and duplicate ones)\n")
    print("baseline (live rule, no filter)"); print("   " + C.HDR); print("   " + C.row(base))
    res = []
    for name, fn in FL:
        m = C.measures(fn, base); d, ok = score(base, m); res.append((name, fn, m, d, ok))
    print("\n== every filter: change of net against the baseline in A / B / C, and over all; TP lost; rows skipped (mean of landings)")
    for name, fn, m, d, ok in res:
        print(f"   {name:34s} | {d[0]:+6.2f} {d[1]:+6.2f} {d[2]:+6.2f} | all {sum(d):+6.2f} | w/o5 {m['wo5'] - base['wo5']:+6.2f} | TP lost {m['tp_lost']:4.1f} new {m['tp_new']:3.1f} | skipped {m['rows_skipped']:5.1f} {'  <- better in all three' if ok else ''}")
    P = [x for x in res if x[4]]
    print(f"\n== better in each of A, B and C: {len(P)} of {len(res)}")
    print("   " + "filter".ljust(34) + " | " + C.HDR + " | days ahead")
    for name, fn, m, d, ok in sorted(P, key=lambda x: -sum(x[3])):
        print(f"   {name:34s} | {C.row(m, base)} | {100 * C.boot(m, base):.1f}%")
    print("\n== picked on two blocks (best summed gain there), scored on the third")
    for out in range(3):
        two = [b for b in range(3) if b != out]
        cand = [x for x in res if all(x[3][b] > 0 for b in two)]
        best = max(cand, key=lambda x: sum(x[3][b] for b in two)) if cand else None
        if best: print(f"   held out {'ABC'[out]}: {len(cand)} filters better on {'ABC'[two[0]]} and {'ABC'[two[1]]}; best there: {best[0]} ({best[3][two[0]]:+.2f} {best[3][two[1]]:+.2f}) -> on {'ABC'[out]} {best[3][out]:+.2f}; "
                       f"of the {len(cand)}, {sum(1 for x in cand if x[3][out] > 0)} also better on {'ABC'[out]}")
    print("\n== the chance rate: random skips of a share of the buys (the same buys at each landing), 400 draws a share")
    rnd = random.Random(7)
    for q in (0.05, 0.1, 0.2, 0.3, 0.4):
        hits = 0; gains = []
        for _ in range(400):
            s = {r["key"] for r in C.R if rnd.random() < q}
            m = C.measures(lambda r, n, s=s: r["key"] in s); d, ok = score(base, m); hits += ok; gains.append(sum(d))
        gains.sort()
        print(f"   skip {int(q * 100):2d}% at random: better in all three blocks in {100 * hits / 400:4.1f}% of draws; change of net median {gains[200]:+.2f}, 90th pct {gains[360]:+.2f}, best {gains[-1]:+.2f}")
