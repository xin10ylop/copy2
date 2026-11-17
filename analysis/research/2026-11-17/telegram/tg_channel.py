# Telegram calls, each channel on its own (the owner, Nov 17: "each channel independently: study behaviour, logic, entry
# and exit"). Every call of a channel with a price path at the post: on the pump curve (tg_test.py's cache) or in its
# PumpSwap pool (tg_pool.py's cache). One path format: (time, quote reserve, coin reserve, fee) after each trade; our 0.5 SOL
# priced on the reserves (constant product: the curve's virtual reserves, the pool's real ones), the fee each way (the
# curve's own bps; 1% in a pool) and 0.0026 SOL of transaction costs.
# A fixed menu, the same for every channel (no setting fitted to one):
#   entries: post   = the first trade 1 s after the post
#            skip5x = the same, but no buy if the price ran 5x+ in the 10 min before the post (a late call)
#            dip    = the first trade within 10 min at 0.9x the post's price or lower (else no buy)
#            confirm= the first trade within 5 min at 1.2x the post's price or higher (else no buy)
#   exits:   tp1.5 / tp2 / tp3 (over our entry price; else 60 min), t10 / t30 / t60, tp2sl (tp2, or a stop at 0.6x)
# Per channel: the behaviour (run-up before the post, the median path, the peak), then each entry x exit on the first half
# of its calls by time (the pick) and the second half (the score), and every result without its best 3 (small samples).
#   python3 -I tg_channel.py TGDIR [MIN=10] > out/tg_channel.txt
import sys, os, json, gzip, glob, statistics as st
TG = sys.argv[1]; MIN = int(sys.argv[2]) if len(sys.argv) > 2 else 10; STAKE = 0.5; HOLD = 3600
def load(D):
    out = []
    for m, t, _ in json.load(open(f"{D}/calls.json")):
        P = None; f = f"{D}/paths/{m}.json.gz"
        if os.path.exists(f):
            x = json.load(gzip.open(f))
            if x.get("venue") == "pump" and x.get("tr") and 25e9 < x["tr"][0]["vq"] * x["tr"][0]["vt"] / 1.073e15 < 35e9 \
                    and not (x.get("complete") and x.get("last_t") and x["last_t"] < t):
                tr = x["tr"]
                if any(e["t"] <= t for e in tr) and any(e["t"] > t for e in tr):
                    P = [(e["t"], e["vq"], e["vt"], e["bps"] / 1e4) for e in tr]
                    g = next((i for i, e in enumerate(tr) if e.get("real") == 0 and e["t"] > t), None)
                    if g is not None: P = P[:g + 1] + [(t + HOLD + 1, tr[g]["vq"], tr[g]["vt"], 0.01)]   # graduated: our tokens move to the pool at that price
        if P is None:
            f = f"{D}/pools/{m}.json.gz"
            if os.path.exists(f):
                x = json.load(gzip.open(f)); px = x.get("px") or []
                if x.get("reached") and any(a <= t for a, _, _ in px) and any(a > t for a, _, _ in px):
                    P = [(a, q, b, 0.01) for a, q, b in px]
        if P: out.append((t, m, P))
    return sorted(out)
def sim(t, P, entry, ex):
    pr = lambda r: r[1] / r[2]
    pre = [r for r in P if r[0] <= t]; p0 = pr(pre[-1]); old = [r for r in P if r[0] <= t - 600]
    run = p0 / pr(old[-1]) if old else p0 / pr(P[0])
    aft = [r for r in P if r[0] >= t + 1]
    if entry == "skip5x" and run >= 5: return None
    if entry in ("post", "skip5x"): i = 0
    elif entry == "dip": i = next((k for k, r in enumerate(aft) if r[0] <= t + 600 and pr(r) <= 0.9 * p0), None)
    else: i = next((k for k, r in enumerate(aft) if r[0] <= t + 300 and pr(r) >= 1.2 * p0), None)
    if i is None or i >= len(aft) - 1: return None
    t0, Q, B, f = aft[i]; inn = STAKE * 1e9 * (1 - f); tok = B * inn / (Q + inn); pe = pr(aft[i])
    def sell(j): _, Q2, B2, f2 = aft[j]; return Q2 * tok / (B2 + tok) * (1 - f2) / 1e9 - STAKE - 0.0026
    cap = {"t10": 600, "t30": 1800}.get(ex, HOLD)
    for j in range(i + 1, len(aft)):
        r = aft[j]
        if r[0] - t0 >= cap: return sell(j)
        if ex.startswith("tp") and pr(r) >= float(ex[2:].replace("sl", "")) * pe: return sell(min(j + 1, len(aft) - 1))
        if ex == "tp2sl" and pr(r) <= 0.6 * pe: return sell(min(j + 1, len(aft) - 1))
    return sell(len(aft) - 1)
EN = ["post", "skip5x", "dip", "confirm"]; EX = ["tp1.5", "tp2", "tp3", "t10", "t30", "t60", "tp2sl"]
def summ(v):
    if not v: return "   0              "
    s = sorted(v, reverse=True); return f"{len(v):3d} {sum(v):+6.2f} w/o3 {sum(s[3:]):+6.2f}"
for cj in sorted(glob.glob(f"{TG}/**/calls.json", recursive=True)):
    D = os.path.dirname(cj); ch = os.path.relpath(D, TG); C = load(D)
    if len(C) < MIN: continue
    calls = json.load(open(cj)); days = (calls[-1][1] - calls[0][1]) / 86400 or 1
    pr = lambda r: r[1] / r[2]; runs, p10, p30, pk = [], [], [], []
    for t, m, P in C:
        pre = [r for r in P if r[0] <= t]; p0 = pr(pre[-1]); old = [r for r in P if r[0] <= t - 600]
        runs.append(p0 / pr(old[-1]) if old else p0 / pr(P[0]))
        at = lambda o: pr([r for r in P if r[0] <= t + o][-1]) / p0
        p10.append(at(600)); p30.append(at(1800)); pk.append(max(pr(r) for r in P if t < r[0] <= t + HOLD) / p0)
    print(f"\n=== {ch}: {len(calls)} calls in {days:.0f} days, {len(C)} with a price path at the post "
          f"({sum(1 for _, _, P in C if P[0][3] != 0.01)} curve, the rest pool)")
    print(f"  behaviour: run-up before the post median {st.median(runs):.2f}x ({sum(r >= 5 for r in runs)} at 5x+); price at +10 min {st.median(p10):.2f}, "
          f"+30 min {st.median(p30):.2f} (medians); peak in the hour median {st.median(pk):.2f}, reached 2x {sum(p >= 2 for p in pk) / len(pk):.0%}")
    h = len(C) // 2; best = None
    print(f"  entry   exit   | first half (pick)              | second half (score)")
    for en in EN:
        for ex in EX:
            a = [x for x in (sim(t, P, en, ex) for t, _, P in C[:h]) if x is not None]
            b = [x for x in (sim(t, P, en, ex) for t, _, P in C[h:]) if x is not None]
            if a and (best is None or sum(a) > best[0]): best = (sum(a), en, ex, b)
            if en == "post" or (best and best[1] == en and best[2] == ex):
                print(f"  {en:7s} {ex:6s} | {summ(a)}           | {summ(b)}")
    if best:
        print(f"  PICKED on the first half: {best[1]} + {best[2]} -> second half {summ(best[3])}; "
              f"a day at 0.5 SOL in the second half: {sum(best[3]) / (days / 2):+.2f} SOL")
