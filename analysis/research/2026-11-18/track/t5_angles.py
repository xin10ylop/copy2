# The ladder, new angles (the owner, Nov 18: "when something fails find another solution, on and on"). On a ladder
# wallet's copies after the screen (paying any price): (1) exits that watch the TEAM: sell at the first sale by any of the
# coin's ladder wallets (the create-slot buyers at the ladder sizes), alone, with a take profit 1.2 / 1.3x, or with a time
# cap 30 / 60 / 120 s; (2) an entry filter, the real demand before our entry: outside buyers (not the ladder, not the
# creator) in the launch slots. Halves by time; at 0.0345 SOL a round trip; the fair measures.
#   python3 -I t5_angles.py SP WALLET8 SUFFIX RES > out/t5_<w8>.txt
import sys, os, json, numpy as np
SP, W8, SUF, RES = sys.argv[1:5]; os.environ["RES"] = RES
here = "/home/user/copy2/analysis/research/2026-11-17/winners"; src = open(f"{here}/wallet_study.py").read().split("def one(ix):")[0]
sys.argv = ["x", SP, W8, "300", "1800"]; ns = {"__file__": f"{here}/wallet_study.py", "__name__": "ws"}; exec(compile(src, "wallet_study.py", "exec"), ns)
sim, cpath, H, own, full, rate_of = ns["sim"], ns["cpath"], ns["H"], ns["own"], ns["full"], ns["rate_of"]
SIZES = (1.10, 1.54, 2.18); S0 = 1794877620
R = sorted((r for r in json.load(open(f"{SP}/winners/study_{W8}{SUF}.json")) if not r["refused"] and (os.environ.get("ALL") or r["t"] >= S0)), key=lambda r: r["t"])
rows = []
for r in R:
    b = next((e for e in own.get(r["m"], []) if e["buy"]), None)
    if not b: continue
    tr = cpath(r["m"], b["slot"], b["t"]); k = next((j for j, y in enumerate(tr) if y["user"] == full and y["buy"] and y["slot"] == b["slot"]), None)
    if k is None: continue
    p = H.prep(tr, k, rate_of(b["quote"]), "slot+1", pmax=1000)
    lad = {e["user"] for e in tr if e["slot"] == b["slot"] and e["buy"] and any(abs(e["q"] / 1e9 - s) <= 0.005 for s in SIZES)}
    j = k + len([e for e in tr[k + 1:] if e["slot"] <= b["slot"] + 1]); rest = tr[j + 1:]
    team = np.array([e["user"] in lad and not e["buy"] for e in rest], dtype=bool)
    outside = [e for e in tr[:j + 1] if e["buy"] and e["user"] not in lad]
    q = dict(p); q["sell"] = team
    e0 = (tr[k]["vt"] / tr[j]["vt"]) ** 2   # our entry price over its price: take profits below are from OUR entry (Nov 18 fix)
    nxt = np.zeros(len(rest), dtype=bool); nxt[:1] = True; f = dict(p); f["sell"] = nxt
    ex = {"its-sale (followed)": r["ex"]["its-sale"], "sell at the next trade": sim(f, its=True), "team-sale": sim(q, its=True)}
    for tpo in (1.1, 1.2, 1.3, 1.5):
        for cap in (30, 60, 300): ex[f"ours x{tpo} cap {cap}s"] = sim(p, tp=tpo * e0, hold=cap)
        ex[f"ours x{tpo} or team-sale"] = sim(q, its=True, tp=tpo * e0)
    rows.append(dict(t=r["t"], ex=ex, n_lad=len(lad), n_out=len(outside), sol_out=sum(e["q"] for e in outside) / 1e9))
h = len(rows) // 2; A, B = rows[:h], rows[h:]
def S(v):
    v = np.array(v); s = np.sort(v); k = max(1, round(0.02 * len(v))) if len(v) else 0
    return f"{len(v):3d} {v.sum():+6.2f} ({100 * v.mean() / 0.5 if len(v) else 0:+6.1f}%) w/o 2% {s[:-k].sum() if len(v) > 1 else 0:+6.2f}"
print(f"{W8}: {len(rows)} copies after the screen (1st half {len(A)}, 2nd {len(B)}), 0.0345 SOL a round trip")
for e in rows[0]["ex"]: print(f"   {e:22s}: 1st {S([r['ex'][e] - 0.0319 for r in A])} | 2nd {S([r['ex'][e] - 0.0319 for r in B])}")
print("\nentry filter: outside buyers before our entry (exit tp1.3 and team-sale+tp1.3):")
cut = lambda x: "0" if x == 0 else ("1-2" if x <= 2 else ("3-5" if x <= 5 else "6+"))
for g in ("0", "1-2", "3-5", "6+"):
    a = [r for r in A if cut(r["n_out"]) == g]; b_ = [r for r in B if cut(r["n_out"]) == g]
    for e in ("sell at the next trade", "ours x1.2 cap 60s"): print(f"   {g:4s} {e:16s}: 1st {S([r['ex'][e] - 0.0319 for r in a])} | 2nd {S([r['ex'][e] - 0.0319 for r in b_])}")
print("ladder wallets seen:", {n: sum(1 for r in rows if r["n_lad"] == n) for n in sorted({r["n_lad"] for r in rows})})

# by day and time of day (UTC), the quick flip (ours x1.2 cap 30 s) and the team-sale exit: an attention market needs buyers
import datetime as dt
blk = lambda t: (dt.datetime.fromtimestamp(t, dt.UTC).strftime("%m-%d"), "00-08" if dt.datetime.fromtimestamp(t, dt.UTC).hour < 8 else ("08-16" if dt.datetime.fromtimestamp(t, dt.UTC).hour < 16 else "16-24"))
G = {}
for r in rows: G.setdefault(blk(r["t"]), []).append(r)
print("\nby day and UTC block (in the screen until Nov 17 01:07):   ours x1.2 cap 30s | team-sale")
for k in sorted(G): print(f"   {k[0]} {k[1]}: {S([r['ex']['ours x1.2 cap 30s'] - 0.0319 for r in G[k]])} | {S([r['ex']['team-sale'] - 0.0319 for r in G[k]])}")
for b in ("00-08", "08-16", "16-24"):
    X = [r for k, v in G.items() if k[1] == b for r in v]; print(f"   ALL DAYS {b}: {S([r['ex']['ours x1.2 cap 30s'] - 0.0319 for r in X])} | {S([r['ex']['team-sale'] - 0.0319 for r in X])}")

v = np.array([r["ex"]["ours x1.2 cap 30s"] - 0.0319 for r in rows]); k = max(1, round(0.02 * len(v))) if len(v) else 0
if len(v):
    bs = np.random.default_rng(7).choice(v, size=(10000, len(v))).mean(axis=1)
    print(f"\nTHE FROZEN FLIP (ours x1.2 cap 30s), these copies: {len(v)}, {v.sum():+.2f} SOL ({100 * v.mean() / 0.5:+.1f}% a copy); without the best 2% {np.sort(v)[:-k].sum():+.2f}; P(mean > 0) {np.mean(bs > 0):.1%}")
