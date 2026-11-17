# The report of wallet_study.py for one wallet: how it trades, which exit suits it, which of its buys pay. Everything
# chosen on the first half of its copies by time and scored on the second; every result also without the best 5.
#   python3 -I wallet_study_report.py SP WALLET8 > out/study_<w8>.txt
import sys, json, numpy as np, statistics as st
SP, W8 = sys.argv[1], sys.argv[2]; R = sorted(json.load(open(f"{SP}/winners/study_{W8}.json")), key=lambda r: r["t"])
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
    if len(a) < 15: continue
    e = max(EX, key=lambda e: np.mean([r["ex"][e] for r in a])); va = [r["ex"][e] for r in a]; vb = [r["ex"][e] for r in b]
    print(f"   {name:22s} {e:14s}: first half {S(va)} | second half {S(vb)}")
    if len(a) >= 20 and (pick is None or np.mean(va) > pick[0]): pick = (np.mean(va), name, e, vb)
if pick: print(f"\n   PICKED on the first half: {pick[1]} + {pick[2]} -> second half {S(pick[3])}")
