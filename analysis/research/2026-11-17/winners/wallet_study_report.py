# The report of wallet_study.py for one wallet: how it trades, which exit suits it, which of its buys pay. Everything
# chosen on the first half of its copies by time and scored on the second; every result also without the best 5.
#   python3 -I wallet_study_report.py SP WALLET8 > out/study_<w8>.txt
import sys, json, numpy as np, statistics as st
SP, W8 = sys.argv[1], sys.argv[2]; R = sorted(json.load(open(f"{SP}/winners/study_{W8}{sys.argv[3] if len(sys.argv) > 3 else ''}.json")), key=lambda r: r["t"])
R = [r for r in R if not r["refused"]]; half = R[len(R) // 2]["t"]; A = [r for r in R if r["t"] < half]; B = [r for r in R if r["t"] >= half]
EX = list(R[0]["ex"]); STAKE = 0.5
def S(v):
    if not v: return "   0"
    s = sorted(v, reverse=True); return f"{len(v):3d} {sum(v):+6.2f} ({np.mean(v) / STAKE:+6.1%}) w/o5 {sum(s[5:]):+6.2f}"
held = [r["held"] for r in R if r["held"] is not None]
print(f"{W8}: {len(R)} copies (0.5 SOL, one slot after its buy); first half {len(A)}, second half {len(B)}")
print(f"\n1. HOW IT TRADES: its size median {st.median(r['sol'] for r in R):.2f} SOL (quartiles {np.quantile([r['sol'] for r in R], [.25, .75]).round(2).tolist()}); "
      f"quote SOL {np.mean([r['quote'] in ('SOL', 'So11111111111111111111111111111111111111112') for r in R]):.0%}; curve sold at its buy median {st.median(r['prog'] for r in R):.0%}")
print(f"   it sold (first sale) after a median {st.median(held):.0f} s; within 30 s {np.mean([h < 30 for h in held]):.0%}, within 2 min {np.mean([h < 120 for h in held]):.0%}, "
      f"never in the window {1 - len(held) / len(R):.0%}")
print("\n2. EXITS (every copy): first half | second half")
best = sorted(EX, key=lambda e: -np.mean([r["ex"][e] for r in A]))
for e in EX: print(f"   {e:14s}: {S([r['ex'][e] for r in A])} | {S([r['ex'][e] for r in B])}{'   <- best on the first half' if e == best[0] else ''}")
def cuts(key): v = sorted(r[key] for r in A); return [v[len(v) // 3], v[2 * len(v) // 3]]
segs = {}
for key in ("sol", "prog", "hour"):
    c1, c2 = cuts(key)
    segs[f"{key} <= {c1:.3g}"] = lambda r, k=key, c=c1: r[k] <= c
    segs[f"{key} {c1:.3g}-{c2:.3g}"] = lambda r, k=key, a=c1, b=c2: a < r[k] <= b
    segs[f"{key} > {c2:.3g}"] = lambda r, k=key, c=c2: r[k] > c
segs["quote SOL"] = lambda r: r["quote"] in ("SOL", "So11111111111111111111111111111111111111112"); segs["quote other"] = lambda r: not segs["quote SOL"](r)
print("\n3. WHICH OF ITS BUYS PAY (thirds cut on the first half), with each segment's best exit on the first half:")
pick = None
for name, f in segs.items():
    a = [r for r in A if f(r)]; b = [r for r in B if f(r)]
    if len(a) < 8: continue   # shown from 8 (size thirds were hidden at 15 on the partial data); the pick still needs 20
    e = max(EX, key=lambda e: np.mean([r["ex"][e] for r in a])); va = [r["ex"][e] for r in a]; vb = [r["ex"][e] for r in b]
    print(f"   {name:22s} {e:14s}: first half {S(va)} | second half {S(vb)}")
    if len(a) >= 20 and (pick is None or np.mean(va) > pick[0]): pick = (np.mean(va), name, e, vb)
if pick: print(f"\n   PICKED on the first half: {pick[1]} + {pick[2]} -> second half {S(pick[3])}")
# 4. the VIP (the owner, Nov 17: "don't forget the vip"): its alert times of Nov 1-6 and 10-17 against this wallet's buys
VIP, SPANS = {}, []
for f in (f"{SP}/tg/vip/meta.json", f"{SP}/tg/vip2/meta.json"):
    try:
        mv = json.load(open(f)); ts = [v["t"] for v in mv.values()]; SPANS.append((min(ts), max(ts) - 600))   # a buy needs its 10 min inside
        for m, v in mv.items(): VIP.setdefault(m, v["t"])
    except FileNotFoundError: pass
cover = lambda t: any(a <= t <= b for a, b in SPANS)   # the exports' own spans (Oct 31 22:00 - Nov 6 19:49, Nov 9 22:01 - Nov 17 17:38 UTC)
C = [r for r in R if cover(r["t"])]
if C:
    for r in C: r["vip"] = VIP.get(r["m"], None)
    after = [r for r in C if r["vip"] is not None and 0 < r["vip"] - r["t"] <= 600]; before = [r for r in C if r["vip"] is not None and r["vip"] <= r["t"]]
    never = [r for r in C if r["vip"] is None or r["vip"] - r["t"] > 600]
    print(f"\n4. THE VIP: {len(C)} of its copies fall on the days of the VIP exports")
    print(f"   the VIP alerted the coin within 10 min AFTER its buy: {len(after)} ({len(after) / len(C):.0%}), a median {st.median([r['vip'] - r['t'] for r in after]) if after else 0:.0f} s later"
          f" | BEFORE its buy (it followed): {len(before)} ({len(before) / len(C):.0%}) | not within 10 min: {len(never)}")
    for e in ("its-sale", best[0], "t10m", "tp3"):
        print(f"   exit {e:14s}: alerted after {S([r['ex'][e] for r in after])} | alerted before {S([r['ex'][e] for r in before])} | not alerted {S([r['ex'][e] for r in never])}")
# 5. its buy size as a conviction signal (the owner, Nov 17: "why arent you filtering too by buy size?"); fixed bins, not fitted
print("\n5. BY ITS BUY SIZE (fixed bins; our copy is always 0.5 SOL): first half | second half")
for lo, hi in ((0, .3), (.3, .45), (.45, .7), (.7, 1.0), (1.0, 2.0), (2.0, 1e9)):
    a = [r for r in A if lo <= r["sol"] < hi]; b = [r for r in B if lo <= r["sol"] < hi]
    if not a and not b: continue
    for e in ("its-sale", "t2m", "tp2", "sp5/60s"):
        print(f"   size {lo:4.2f}-{hi if hi < 1e8 else 'up':<5} {e:9s}: {S([r['ex'][e] for r in a])} | {S([r['ex'][e] for r in b])}")
