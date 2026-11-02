# Step 3c: score the simulated launch buys (out/sim.json) by period, P1 Oct 19-22 (where rules were picked) and P2
# Oct 23-26 (out of sample), for a selection of coins, each sampled coin counted with its weight (t0_sample.py: picks 1,
# R2 non-picks and the base sample by their sampling rates). Each coin's fill is its own half-and-half draw (float: F0 or
# F1, jup: F1 or F2, by crc32(mint)); "F0".."F2" force one.
# Columns: sampled trades (n), trades they stand for (N), total SOL, weighted median trade, win share, take-profit share,
# total without the period's best 2 sampled trades (with their weights), total with the quote's price held (no move).
#   python3 -I score.py [table|quote|rot|all] -> printed
import sys, os, collections, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blib
from u1_universe import sym
from f2_rule import RULES
SIM = blib.jl(blib.OUT + "/sim.json")
S = blib.jl(blib.OUT + "/sample.json")
TB = {t["mint"]: t for t in blib.jl(blib.OUT + "/table.json")}
R2 = RULES["R2 R1 + manual create tx (ata[+cb]+pump[+sys])"]; R3 = RULES["R3 R2 + dev buy 0.1-2 SOL"]; R4 = RULES["R4 R2 + dev buy 0.5-2 SOL"]
pkq = collections.Counter(t["quote"] for t in TB.values() if t["pick"])
ACTIVE = {q for q, n in pkq.items() if n >= 5}
def tree3(t):   # the depth-3 tree of f2_rule.py (target pick), its leaves with a P1 rate >= 30%
    return t["prior"] == 0 and t["progs"] == "ata+cb+pump" and t["dev_sol"] > 0.469
SEL = {
    "its picks (all sizes)": lambda t, s: t["pick"] == 1,
    "its 1.45+ SOL picks": lambda t, s: t["big"] == 1,
    "its picks under 1.45 SOL": lambda t, s: t["pick"] == 1 and not t["big"],
    "R2 (picks and not)": lambda t, s: R2(t),
    "R2, not its picks": lambda t, s: R2(t) and not t["pick"],
    "R3 (R2, dev buy 0.1-2)": lambda t, s: R3(t),
    "R4 (R2, dev buy 0.5-2)": lambda t, s: R4(t),
    "tree3 (prior 0, ata+cb+pump, dev > 0.47)": lambda t, s: tree3(t),
    "every launch of the active quotes": lambda t, s: t["quote"] in ACTIVE,
    "active quotes, not R2, not picks": lambda t, s: t["quote"] in ACTIVE and not R2(t) and not t["pick"],
}
def rows(sel, cfg, fill="mix", quote=None, per=None):
    """[(pnl, pnl0, w, kind, mint)] of the selection under cfg = model|exit|stake"""
    model = cfg.split("|")[0]
    out = []
    for m, s in S.items():
        r = SIM.get(m); t = TB[m]
        if not r or "err" in r: continue
        if quote and t["quote"] != quote: continue
        if per and t["per"] != per: continue
        if not sel(t, s): continue
        F = (r["_h"] + (1 if model == "jup" else 0)) if fill == "mix" else int(fill[1])
        x = r.get(f"{cfg}|F{F}")
        if not x: continue
        out.append((x["pnl"], x["pnl0"], s["w"], x["kind"], m))
    return out
def wmed(L):
    L = sorted((p, w) for p, _, w, _, _ in L); tot = sum(w for _, w in L); a = 0
    for p, w in L:
        a += w
        if a >= tot / 2: return p
    return 0.0
def stats(L):
    if not L: return dict(n=0, N=0, tot=0, med=0, win=0, tp=0, wo2=0, tot0=0)
    N = sum(w for _, _, w, _, _ in L); tot = sum(p * w for p, _, w, _, _ in L)
    srt = sorted(L, key=lambda x: -x[0])
    wo2 = sum(p * w for p, _, w, _, _ in srt[2:])
    return dict(n=len(L), N=N, tot=tot, med=wmed(L), win=sum(w for p, _, w, _, _ in L if p > 0) / N,
                tp=sum(w for _, _, w, k, _ in L if k == "tp") / N, wo2=wo2, tot0=sum(p0 * w for _, p0, w, _, _ in L))
def fmt(s):
    if not s["n"]: return f"{'0':>5s} {'':>6s} {'':>8s} {'':>7s} {'':>5s} {'':>5s} {'':>8s} {'':>8s}"
    return f"{s['n']:5d} {s['N']:6.0f} {s['tot']:+8.2f} {s['med']:+7.3f} {s['win']:5.0%} {s['tp']:5.1%} {s['wo2']:+8.2f} {s['tot0']:+8.2f}"
HDR = f"{'n':>5s} {'N':>6s} {'total':>8s} {'median':>7s} {'win':>5s} {'TP':>5s} {'w/o b2':>8s} {'no move':>8s}"
def table(cfgs=("float|its|1.0", "float|ours|1.0", "jup|its|1.0", "jup|ours|1.0", "float|ours|0.1", "jup|ours|0.1"), sels=None, fill="mix"):
    for name in (sels or SEL):
        print(f"\n== {name}   (fill {fill})")
        print(f"{'config':16s} | P1 Oct 19-22: {HDR} | P2 Oct 23-26: {HDR}")
        for cfg in cfgs:
            a = stats(rows(SEL[name], cfg, fill, per="P1")); b = stats(rows(SEL[name], cfg, fill, per="P2"))
            ok = "PASS" if b["tot"] > 0 and b["wo2"] > 0 else ""
            print(f"{cfg:16s} | {'':14s}{fmt(a)} | {'':14s}{fmt(b)} {ok}")
def by_quote(cfg="float|ours|1.0", sels=("its picks (all sizes)", "its 1.45+ SOL picks", "R2 (picks and not)", "every launch of the active quotes"), minp=8):
    qs = [q for q, n in pkq.most_common() if n >= minp]
    print(f"\n== by quote token, {cfg}: total (sampled trades) [w/o best 2], P1 | P2; its own net on its picks")
    print(f"{'quote':10s} " + " ".join(f"{s[:26]:>40s}" for s in sels) + f" {'its net P1 / P2':>18s}")
    for q in qs:
        cells = []
        for sn in sels:
            a = stats(rows(SEL[sn], cfg, quote=q, per="P1")); b = stats(rows(SEL[sn], cfg, quote=q, per="P2"))
            cells.append(f"{a['tot']:+7.2f} ({a['n']:3d}) | {b['tot']:+7.2f} ({b['n']:3d}) [{b['wo2']:+6.2f}]")
        n1 = sum(t["w4net"] for t in TB.values() if t["quote"] == q and t["pick"] and t["per"] == "P1")
        n2 = sum(t["w4net"] for t in TB.values() if t["quote"] == q and t["pick"] and t["per"] == "P2")
        print(f"{sym(q):10s} " + " ".join(f"{c:>40s}" for c in cells) + f" {n1:+8.2f} / {n2:+7.2f}")
if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    print(f"simulated coins: {sum(1 for m in S if m in SIM and 'err' not in SIM[m])} of {len(S)} sampled "
          f"({collections.Counter(S[m]['set'] for m in S if m in SIM and 'err' not in SIM[m])})")
    if what in ("table", "all"): table()
    if what in ("quote", "all"):
        for cfg in ("float|ours|1.0", "jup|ours|1.0", "float|its|1.0"): by_quote(cfg)
def qpick(sel_name, cfg, min_n=5, show=True):
    """the rotation test: per quote, the selection's P1 total; the quotes positive on P1 (with min_n+ sampled trades)
    are the pick; their P2 total is the out-of-sample score."""
    qs = sorted({TB[m]["quote"] for m in S})
    p1 = {}
    for q in qs:
        a = stats(rows(SEL[sel_name], cfg, quote=q, per="P1"))
        if a["n"] >= min_n: p1[q] = a
    keep = {q for q, a in p1.items() if a["tot"] > 0}
    sel = SEL[sel_name]
    A = stats(rows(lambda t, s: sel(t, s) and t["quote"] in keep, cfg, per="P1"))
    B = stats(rows(lambda t, s: sel(t, s) and t["quote"] in keep, cfg, per="P2"))
    if show:
        print(f"  {sel_name[:34]:34s} {cfg:15s} quotes positive on P1: {len(keep)} of {len(p1)} ({', '.join(sym(q) for q in sorted(keep, key=lambda q: -p1[q]['tot'])[:8])})")
        print(f"  {'':34s} {'':15s} P1 {fmt(A)} | P2 {fmt(B)} {'PASS' if B['tot'] > 0 and B['wo2'] > 0 else ''}")
    return keep, A, B
