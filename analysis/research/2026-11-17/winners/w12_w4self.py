# Wallet 4's own buys, every size and quote (w4_history.py with MINSOL=0.1 MAXP=1.0, a random 400 copied by
# wallet_study.py, w9_buyctx.py's create and pre-buy context): what we copy live (another token as the quote, 1.3+ SOL)
# against what we do not (SOL coins; other-token buys under 1.3 SOL), each under the exits of the menu, then the create
# signals inside each group. Halves by time; at COST SOL a round trip (default 0.0345).
#   python3 -I w12_w4self.py SP > out/w4self.txt
import sys, os, json, numpy as np
SP = sys.argv[1]; COST = float(os.environ.get("COST", 0.0345)); W8 = "H9kuqGKN"
R = sorted((r for r in json.load(open(f"{SP}/winners/study_{W8}.json")) if not r["refused"]), key=lambda r: r["t"])
try: CTX = json.load(open(f"{SP}/winners/ctx_{W8}.json"))
except FileNotFoundError: CTX = {}
SOLQ = {"11111111111111111111111111111111", "So11111111111111111111111111111111111111112", "SOL"}
for r in R:
    r["ex"] = {k: v - (COST - 0.0026) for k, v in r["ex"].items()}; c = CTX.get(f"{r['m']}:{r['t']}") or {}; r["cr"] = c.get("create") or {}
    r["grp"] = "SOL coin" if r["quote"] in SOLQ else ("other token, 1.3+ SOL (copied live)" if r["sol"] >= 1.3 else "other token, under 1.3 SOL")
half = R[len(R) // 2]["t"]
def S(v):
    if not v: return "  0" + " " * 33
    s = sorted(v); return f"{len(v):3d} {sum(v):+6.2f} ({100 * np.mean(v) / 0.5:+6.1f}%) w/o5 {sum(s[:-5]) if len(s) > 5 else 0:+6.2f}"
print(f"wallet 4: {len(R)} copies at {COST} SOL a round trip; create read {sum(1 for r in R if r['cr'])}")
EX = ["its-sale", "tp1.5", "tp2", "tp3", "t1m", "t2m", "t5m", "sp3/30s", "sp5/60s", "sp10/60s", "trail1.5/35%"]
for g in sorted({r["grp"] for r in R}):
    X = [r for r in R if r["grp"] == g]
    print(f"\n== {g}: {len(X)} copies; its size median {np.median([r['sol'] for r in X]):.2f}, curve sold median {np.median([r['prog'] for r in X]):.0%}")
    for e in EX: print(f"   {e:12s}: 1st half {S([r['ex'][e] for r in X if r['t'] < half])} | 2nd half {S([r['ex'][e] for r in X if r['t'] >= half])}")
    best = max(EX, key=lambda e: sum(r["ex"][e] for r in X if r["t"] < half)); print(f"   best on the 1st half: {best}")
    cut = lambda x, cs: "unknown" if x is None else next((f"<= {c:g}" for c in cs if x <= c), f"> {cs[-1]:g}")
    for name, key in (("dev buy", lambda r: cut(r["cr"].get("dev_buy"), [0, 0.5, 2, 5])), ("tips", lambda r: cut(r["cr"].get("tips"), [0, 0.001])),
                      ("mayhem", lambda r: r["cr"].get("mayhem", "unknown")), ("its size", lambda r: cut(r["sol"], [0.3, 0.6, 1, 1.3, 2])),
                      ("curve sold", lambda r: cut(r["prog"], [0.02, 0.2, 0.5]))):
        G = {}
        for r in X: G.setdefault(key(r), []).append(r)
        print(f"   by {name} ({best}):")
        for k in sorted(G, key=str): print(f"      {str(k):10s} 1st {S([r['ex'][best] for r in G[k] if r['t'] < half])} | 2nd {S([r['ex'][best] for r in G[k] if r['t'] >= half])}")
