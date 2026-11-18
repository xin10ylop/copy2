# Exit engineering for a found wallet, the way wallet 4's exit was built (Nov 18, the owner: "start by testing exit
# after its sell, then start applying filters, hold time, tp, sell pressure, stall, sell after its sell, exactly like we
# engineered for wallet 4"). The copies are m5_confirm's (its first buys of 0.5+ SOL outside the screen's 48 h, the
# same NS sample, seed 7, the same cached paths; our 0.5 SOL at the landing 4 / 8 trades / next slot, each landing a
# copy row averaged). The exit menu is fixed here, before any result is read; each exit is PICKED on the first half of
# the copies by time and SCORED on the second; 0.0345 SOL a round trip; take profits from OUR entry; every exit capped
# at 600 s unless it is a shorter time cap. Wallet 4 can be run the same way as the yardstick.
# Then (the owner: "also on which coins to copy and buy size, wallet 4 we use floats and 1.2 sol+ buys"): a grid of the
# coin class (all / other-token / SOL / the quotes we can trade today: SOL or a float we hold) x its buy size (0.5+ /
# 1.0+ / 1.3+ / 2.0+ SOL) x the exits, the best picked on the 1st half (8+ copies in each half), scored on the 2nd.
#   RPC_URL=... CPDIR=... NS=100 python3 -I e1_exits.py SP WALLET ... > ../out/e1_exits.txt
import sys, os, json, glob, random, re, numpy as np
SP = sys.argv[1]; WALLETS = sys.argv[2:]; os.environ["HOLD"] = "900"; A, B = 1794704822, 1794877622; NS = int(os.environ.get("NS", 100))
here = "/home/user/copy2/analysis/research/2026-11-17/winners"; src = open(f"{here}/w5_copy.py").read().split("EX = [")[0]
sys.argv = ["x", SP, "6ua7w2Gv"]; ns = {"__file__": f"{here}/w5_copy.py"}; exec(compile(src, "w5_copy.py", "exec"), ns)
cpath, rate_of, H, SOLQ = ns["cpath"], ns["rate_of"], ns["H"], ns["SOLQ"]
ws = open(f"{here}/wallet_study.py").read(); sim_src = ws[ws.index("def sim("):ws.index("def menu(")]
exec(sim_src, ns); sim = ns["sim"]; COST = 0.0345 - 0.0026
def stall_mask(p, S, e0):
    px, age = p["px"], p["age"]
    if not len(px): return np.zeros(0, bool)
    pk = np.maximum.accumulate(px); newhi = np.concatenate([[True], pk[1:] > pk[:-1]]); lasthi = np.maximum.accumulate(np.where(newhi, age, -1e9))
    return (age - lasthi >= S)
def with_mask(p, m): q = dict(p); q["sell"] = m; return q
def exits(p, e0):
    its = p["sell"]; o = {}
    o["its sale"] = sim(p, its=True, hold=600)
    for c in (30, 60, 120, 300, 600): o[f"time {c}s"] = sim(p, hold=c)
    for t in (1.2, 1.5, 2, 3, 4): o[f"tp {t}x"] = sim(p, tp=t * e0, hold=600)
    for nn, w in ((3, 30), (5, 60), (10, 60)): o[f"sp {nn}/{w}s"] = sim(p, sp=(nn, w), hold=600)
    for S in (60, 120, 180): o[f"stall {S}s"] = sim(with_mask(p, stall_mask(p, S, e0)), its=True, hold=600)
    o["its sale + tp 2x"] = sim(p, its=True, tp=2 * e0, hold=600); o["its sale + tp 4x"] = sim(p, its=True, tp=4 * e0, hold=600)
    o["its sale + sp 5/60"] = sim(p, its=True, sp=(5, 60), hold=600)
    o["sp 5/60 + stall 180 + tp 4x"] = sim(with_mask(p, stall_mask(p, 180, e0)), its=True, sp=(5, 60), tp=4 * e0, hold=600)
    o["its sale + sp 5/60 + stall 180 + tp 4x"] = sim(with_mask(p, its | stall_mask(p, 180, e0)), its=True, sp=(5, 60), tp=4 * e0, hold=600)
    o["wallet 4's live model"] = H.model(p)[0]
    return {k: v - COST for k, v in o.items()}
def S(v):
    v = np.array(v); n = len(v)
    if not n: return "  0"
    s = np.sort(v); k = max(1, round(0.02 * n)); return f"{n:3d} {v.sum():+6.2f} ({100 * v.mean() / 0.5:+6.1f}%) w/o 2% {s[:-k].sum() if n > 1 else 0:+6.2f}"
NAMES = ['its sale', 'time 30s', 'time 60s', 'time 120s', 'time 300s', 'time 600s', 'tp 1.2x', 'tp 1.5x', 'tp 2x', 'tp 3x', 'tp 4x', 'sp 3/30s', 'sp 5/60s', 'sp 10/60s', 'stall 60s', 'stall 120s', 'stall 180s', 'its sale + tp 2x', 'its sale + tp 4x', 'its sale + sp 5/60', 'sp 5/60 + stall 180 + tp 4x', 'its sale + sp 5/60 + stall 180 + tp 4x', "wallet 4's live model"]   # the menu, in its declared order
for w in WALLETS:
    h = json.load(open(glob.glob(f"{SP}/winners/hist/{w}*.json")[0])); first = {}
    for e in sorted(h["trades"], key=lambda e: e["t"]):
        if e["buy"]: first.setdefault(e["m"], e)
    buys = []
    for m, e in first.items():   # m5_confirm's selection, unchanged
        r = rate_of(e["quote"])
        if r is None or A <= e["t"] < B: continue
        sol = e["q"] * (1 + e["bps"] / 1e4) * r / 1e9
        if sol >= 0.5: buys.append((m, e, r, sol))
    random.Random(7).shuffle(buys); buys = buys[:NS]
    rows = []
    for m, e, r, sol in buys:
        try: tr = cpath(m, e["slot"], e["t"])
        except Exception: continue
        k = next((j for j, y in enumerate(tr) if y["user"] == w and y["buy"] and y["slot"] == e["slot"]), None)
        if k is None: continue
        acc = None
        for n in (4, 8, "slot+1"):
            p = H.prep(tr, k, r, n)
            if p["refused"] or not len(p["px"]): ex = None
            else:
                e0 = p["ent_px"] if "ent_px" in p else (tr[k]["vt"] / p["ent"][0]) ** 2
                ex = exits(p, e0)
            if ex is None: ex = {kk: -0.0004 - COST * 0 for kk in NAMES}   # a refused landing: no trade, ~0 in every exit
            acc = ex if acc is None else {kk: acc[kk] + ex[kk] for kk in NAMES}
        rows.append(dict(t=e["t"], other=e["quote"] not in SOLQ, quote=e["quote"] or "", sol=sol, ex={kk: v / 3 for kk, v in acc.items()}))
    rows = [r_ for r_ in rows if any(abs(v + 0.0004) > 1e-9 for v in r_["ex"].values())]; rows.sort(key=lambda r_: r_["t"]); hf = len(rows) // 2; P1, P2 = rows[:hf], rows[hf:]
    print(f"\n== {w}: {len(rows)} copies (outside the screen; 1st half {len(P1)}, 2nd {len(P2)}); 0.0345 SOL a round trip")
    names = NAMES if rows else []
    print(f"   {'exit':40s} | 1st half (pick)                    | 2nd half (score)")
    for e_ in names: print(f"   {e_:40s} | {S([r_['ex'][e_] for r_ in P1 if e_ in r_['ex']])} | {S([r_['ex'][e_] for r_ in P2 if e_ in r_['ex']])}")
    if names:
        best = max(names, key=lambda e_: np.mean([r_["ex"][e_] for r_ in P1 if e_ in r_["ex"]]))
        v = np.array([r_["ex"][best] for r_ in P2 if best in r_["ex"]]); bs = np.random.default_rng(7).choice(v, size=(10000, len(v))).mean(axis=1) if len(v) else np.zeros(1)
        print(f"   PICKED on the 1st half: {best} -> 2nd half {S(v)}; P(mean>0) {100 * np.mean(bs > 0):.1f}%")

        FLOATS = ("3NZ9JMVB", "pumpCmXq", "SPCXxcqX", "TTWofwAg", "DJTu7vi8", "98sMhvDw", "XsbEhLAt")   # the box's floats, Nov 18 status
        CLS = {"all": lambda r_: True, "other-token": lambda r_: r_["other"], "SOL": lambda r_: not r_["other"],
               "tradable now": lambda r_: (not r_["other"]) or r_["quote"][:8] in FLOATS}
        cand = []
        for cn, cf in CLS.items():
            for mn in (0.5, 1.0, 1.3, 2.0):
                a1 = [r_ for r_ in P1 if cf(r_) and r_["sol"] >= mn]; a2 = [r_ for r_ in P2 if cf(r_) and r_["sol"] >= mn]
                if len(a1) < 8 or len(a2) < 8: continue
                for e_ in NAMES: cand.append((np.mean([r_["ex"][e_] for r_ in a1]), cn, mn, e_, a1, a2))
        cand.sort(key=lambda c: -c[0])
        print(f"   FILTER x EXIT grid ({len(cand)} options with 8+ copies in each half): the 5 best on the 1st half, and how they score on the 2nd")
        for c in cand[:5]:
            print(f"     {c[1]:12s} its {c[2]:.1f}+ SOL | {c[3]:38s} | 1st {S([r_['ex'][c[3]] for r_ in c[4]])} | 2nd {S([r_['ex'][c[3]] for r_ in c[5]])}")
        if cand:
            c = cand[0]; v = np.array([r_["ex"][c[3]] for r_ in c[5]]); bs = np.random.default_rng(7).choice(v, size=(10000, len(v))).mean(axis=1)
            print(f"   PICKED (filter + exit) on the 1st half: {c[1]}, its {c[2]:.1f}+ SOL, {c[3]} -> 2nd half {S(v)}; P(mean>0) {100 * np.mean(bs > 0):.1f}%")
