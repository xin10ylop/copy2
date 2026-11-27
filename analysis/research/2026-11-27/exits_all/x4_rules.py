# The whole copy rule of one unit, picked blind (Nov 27; the owner: "even for the by size, if it's sol or floats or these
# things, like everything"). Reads SP/exits_all/<unit>.npz (the copies it takes) and <unit>_out.npz (a sample of those it
# does not: first buys of 0.1+ SOL outside its floor or coin kind, each standing for `w` of them). What the bot can run
# (config.rs): one floor for all coins (min_sol); its SOL-priced coins copied or not (copy_sol_coins); a price limit
# (max_premium); one exit for token coins, and a separate one for SOL coins (sol_exits: sol_take_profit, sol_max_hold_s,
# sol_stall_s, sol_sell_pressure), the rule on its own sale shared by both. So a rule is:
#   coins: all | token only (2) x floor 0.1 0.25 0.5 1.0 1.3 2.0 SOL (6) x limit 1.25x 1.5x (2)
#   x the token-coin exit (12,960) x the SOL-coin exit (the same grid, the same its-sale level).
# Blocks: 4 by time, at the quartiles of the copies the unit takes now (copies outside that span are left out).
#  1. Walk-forward: for blocks 2-4, the rule picked on the blocks before (each part's most SOL without its best 2% of copies,
#     smoothed over the exit's neighbours), scored blind on the block, against the live rule on the same block. Values are
#     stakes won (a copy's result over the stake, summed; a copy not taken counts 0), so rules taking more or fewer coins
#     compare in SOL.
#  2. One change from the live rule, the live exit kept: another floor; SOL coins added (token-only units) or dropped; the
#     1.25x limit; a SOL-coin exit of its own (walk-forward, the token exit live).
#  3. The verdict, the same rules as x2_analyze.py: A the walk-forward rule if it beats live on the 3 blind blocks in total,
#     without its best 2% and in 2 of 3; else B one change that beats live in 3 of 4 blocks, in total and without its best
#     2% (the SOL exit: in 2 of 3 blind blocks, total and without its best 2%); else C the live rule stays.
#   python3 -I x4_rules.py SP UNIT
import sys, json, numpy as np
SP, LAB = sys.argv[1], sys.argv[2]
sys.argv = [sys.argv[0], SP, LAB]
src = open(__file__.replace("x4_rules.py", "x2_analyze.py")).read().split('print(f"{LAB}: {N} copies')[0]
h = {}; exec(compile(src, "x2", "exec"), h)
smooth, name, SH, LV = h["smooth"], h["name"], h["SH"], h["LV"]
U = dict(qqq=("token", 1.3), eee=("all", 0.5), rrr=("token", 0.5), ttt=("token", 0.5), yyy=("token", 0.25), uuu=("all", 0.5),
         iii=("all", 0.5), ooo=("all", 0.5), ppp=("token", 0.1), ddd=("all", 0.5), hhh=("all", 0.5), www=("all", 0.5))
KIND0, MIN0 = U[LAB]
zi = np.load(f"{SP}/exits_all/{LAB}.npz"); zo = np.load(f"{SP}/exits_all/{LAB}_out.npz")
live = int(zi["live"]); its_l = np.unravel_index(np.arange(int(np.prod(SH))), SH)[4]
G = np.concatenate([zi["G"], zo["G"]]).astype(np.float64); t = np.concatenate([zi["t"], zo["t"]])
w = np.concatenate([np.ones(len(zi["G"])), np.full(len(zo["G"]), float(zo["w"]))]); ins = np.r_[np.ones(len(zi["G"]), bool), np.zeros(len(zo["G"]), bool)]
sol = np.concatenate([zi["sol"], zo["sol"]]); tok = np.concatenate([zi["tok"], zo["tok"]]).astype(bool); prem = np.concatenate([zi["prem"], zo["prem"]])
q = np.quantile(zi["t"], [0, .25, .5, .75, 1]); keep = (t >= q[0]) & (t <= q[4])
G, t, w, sol, tok, prem, ins = G[keep], t[keep], w[keep], sol[keep], tok[keep], prem[keep], ins[keep]
blk = np.clip(np.searchsorted(q[1:4], t, side="right"), 0, 3)
REF = -0.0004 / {"qqq": 1.0, "uuu": 1.0, "iii": 1.0, "ppp": 0.25}.get(LAB, 0.5)
FLOORS, LIMS = [0.1, 0.25, 0.5, 1.0, 1.3, 2.0], [1.25, 1.5]
def part(mask, lim):
    """copies x settings, weighted, a copy refused over the limit"""
    V = G[mask].copy(); V[prem[mask] > lim] = REF; return V * w[mask][:, None]
def wo2m(M):
    if len(M) == 0: return np.zeros(M.shape[1])
    k = max(1, round(0.02 * len(M))); return M.sum(0) - np.sort(np.partition(M, -k, axis=0)[-k:], axis=0).sum(0) if len(M) > k else np.zeros(M.shape[1])
def wo2v(v):
    k = max(1, round(0.02 * len(v))); return np.sort(v)[:-k].sum() if len(v) > k else 0.0
def taken(kind, fl, lim, et, es, sel):
    """stakes won on the copies `sel` (a bool mask), and each copy's value (0 if not taken)"""
    v = np.zeros(len(G)); tm = sel & tok & (sol >= fl - 1e-6); sm = sel & ~tok & (sol >= fl - 1e-6) & (kind == "all")
    for m, e in ((tm, et), (sm, es)):
        x = G[m, e].copy(); x[prem[m] > lim] = REF; v[m] = x * w[m]
    return v.sum(), v[sel & (v != 0)]
def pick(sel):
    best = None
    for fl in FLOORS:
        for lim in LIMS:
            vt = smooth(wo2m(part(sel & tok & (sol >= fl - 1e-6), lim))); vs = smooth(wo2m(part(sel & ~tok & (sol >= fl - 1e-6), lim)))
            for l in range(SH[4]):
                m = its_l == l; et = int(np.flatnonzero(m)[np.argmax(vt[m])]); es = int(np.flatnonzero(m)[np.argmax(vs[m])])
                for kind in ("all", "token"):
                    sc = vt[et] + (vs[es] if kind == "all" else 0)
                    if best is None or sc > best[0]: best = (sc, kind, fl, lim, et, es)
    return best[1:]
def rname(r):
    kind, fl, lim, et, es = r
    return f"{kind} coins, {fl}+ SOL, limit {lim}x; token coins: {name(et)}" + (f"; SOL coins: {name(es)}" if kind == "all" else "")
LIVE = (KIND0, MIN0, 1.5, live, live)
allc = np.ones(len(G), bool); bm = [blk == b for b in range(4)]
print(f"{LAB}: {int(ins.sum())} copies it takes + {int((~ins).sum())} sampled of those it does not (each for {float(zo['w']):.1f}); blocks by time of "
      + ", ".join(str(int(m.sum())) for m in bm) + " copies")
lb = [taken(*LIVE, m)[0] for m in bm]
print(f"live rule: {rname(LIVE)}\n  stakes won by block " + " / ".join(f"{x:+6.2f}" for x in lb) + f" = {sum(lb):+.2f}")
print("\n1. walk-forward (the rule picked on the blocks before, blind on the block):")
bl, lvv, wins, bv, lv_ = 0, 0, 0, [], []
for b in (1, 2, 3):
    r = pick(blk < b); s, v = taken(*r, bm[b]); s0, v0 = taken(*LIVE, bm[b]); bl += s; lvv += s0; wins += s > s0; bv.append(v); lv_.append(v0)
    print(f"  block {b + 1}: {rname(r)}\n      blind {s:+.2f} stakes on {len(v)} copies, live {s0:+.2f} on {len(v0)}")
bv, lv_ = np.concatenate(bv), np.concatenate(lv_)
print(f"  blind total {bl:+.2f} stakes (w/o its best 2% {wo2v(bv):+.2f}) against live {lvv:+.2f} (w/o 2% {wo2v(lv_):+.2f}); better in {wins} of 3")
ruleA = bl > lvv and wo2v(bv) > wo2v(lv_) and wins >= 2
rall = pick(allc); print(f"  the pick on all 4 blocks: {rname(rall)}")
print("\n2. one change, the live exit kept (stakes won by block; vs live):")
cands = []
def test(lab, r):
    per = [taken(*r, m)[0] for m in bm]; d = [p - l for p, l in zip(per, lb)]; tot = sum(d)
    wv = wo2v(taken(*r, allc)[1]) - wo2v(taken(*LIVE, allc)[1]); nb = sum(x > 0 for x in d); ok = nb >= 3 and tot > 0 and wv > 0
    print(f"  {lab:32s} " + " / ".join(f"{x:+6.2f}" for x in per) + f" = {sum(per):+6.2f}  vs live {tot:+6.2f} ({nb}/4), w/o 2% {wv:+6.2f}" + ("  <- passes B" if ok else ""))
    if ok: cands.append((wv, lab, r))
for fl in FLOORS:
    if fl != MIN0: test(f"floor {fl} SOL", (KIND0, fl, 1.5, live, live))
test("SOL coins added" if KIND0 == "token" else "SOL coins dropped", ("all" if KIND0 == "token" else "token", MIN0, 1.5, live, live))
test("limit 1.25x", (KIND0, MIN0, 1.25, live, live))
kind_s = "all"; bs, b0, ws = 0, 0, 0; sv, s0v = [], []
for b in (1, 2, 3):   # a SOL-coin exit of its own, picked on the blocks before
    vs = smooth(wo2m(part((blk < b) & ~tok & (sol >= MIN0 - 1e-6), 1.5))); m = its_l == its_l[live]; es = int(np.flatnonzero(m)[np.argmax(vs[m])])
    s, v = taken("all", MIN0, 1.5, live, es, bm[b]); s0, v0 = taken("all", MIN0, 1.5, live, live, bm[b]); bs += s; b0 += s0; ws += s > s0; sv.append(v); s0v.append(v0)
sv, s0v = np.concatenate(sv), np.concatenate(s0v)
vs = smooth(wo2m(part(~tok & (sol >= MIN0 - 1e-6), 1.5))); m = its_l == its_l[live]; esall = int(np.flatnonzero(m)[np.argmax(vs[m])])
okS = bs > b0 and wo2v(sv) > wo2v(s0v) and ws >= 2
print(f"  a SOL-coin exit of its own, walk-forward: blind {bs:+.2f} against {b0:+.2f} (SOL coins copied with the live exit), better in {ws} of 3, "
      f"w/o 2% {wo2v(sv) - wo2v(s0v):+.2f}; on all: {name(esall)}" + ("  <- passes" if okS else ""))
print("\n3. VERDICT: ", end="")
if ruleA: print(f"A, the rule picked on all 4 blocks: {rname(rall)}")
elif cands: wv, lab, r = max(cands, key=lambda c: c[0]); print(f"B, one change: {lab} ({rname(r)})")
else: print("C, the live rule stays")
if okS: print(f"   and SOL coins (if copied) with their own exit: {name(esall)}")
