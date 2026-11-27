# One unit's exit, judged on its own copies without fitting the past (Nov 27; reads SP/exits_all/<unit>.npz from x1_grid.py).
# The copies are split by time into 4 blocks of equal count. The rules were written before any result was seen:
#  1. Walk-forward: for blocks 2, 3 and 4, the exit is picked on the blocks BEFORE it only (the most SOL without its best 2%
#     of copies, smoothed over each setting's neighbours on the five axes, as w2_grid.py picks), then scored once on that
#     block, blind. Against the live exit on the same blind copies.
#  2. Each axis alone (take profit, timer, sell pressure, stall, its sale): every other level against the live level, the
#     other four axes at every one of their settings (a paired difference a copy, its median over those settings), per block;
#     and the live exit with only that axis changed, per block.
#  3. The verdict:
#     A. a new exit (the pick on all 4 blocks) only if the walk-forward beats the live exit on the 3 blind blocks in total
#        AND without its best 2% AND in at least 2 of the 3 blocks;
#     B. else one axis changed from the live exit, if the changed exit beats live in at least 3 of 4 blocks, in total and
#        without its best 2%, and that level's median paired difference is above 0 in at least 3 of 4 blocks (the axis
#        helps whatever the rest of the exit is); of several, the highest without its best 2%;
#     C. else the live exit stays.
#   python3 -I x2_analyze.py SP UNIT
import sys, json, numpy as np
SP, LAB = sys.argv[1], sys.argv[2]
z = np.load(f"{SP}/exits_all/{LAB}.npz"); G = z["G"].astype(np.float64); SH = tuple(int(x) for x in z["SH"]); live = int(z["live"])
A = json.loads(str(z["axes"])); AX = ["TP", "HOLD", "SPS", "STALL", "ITS"]; LV = [A[k] for k in AX]
order = np.argsort(z["t"]); G = G[order]; t = z["t"][order]; N = len(G)
B = np.array_split(np.arange(N), 4)
def wo2(V):
    k = max(1, round(0.02 * len(V))); return V.sum(0) - np.sort(np.partition(V, -k, axis=0)[-k:], axis=0).sum(0)
def wo2v(v):
    k = max(1, round(0.02 * len(v))); return np.sort(v)[:-k].sum()
def smooth(v):
    a = v.reshape(SH); acc = a.copy(); cnt = 1
    for ax in range(5):
        pad = np.concatenate([a.take([0], ax), a, a.take([-1], ax)], axis=ax)
        acc = acc + pad.take(range(0, SH[ax]), ax) + pad.take(range(2, SH[ax] + 2), ax); cnt += 2
    return (acc / cnt).ravel()
def lvname(ax, v):
    if ax == "TP": return f"tp {v}x" if v else "no tp"
    if ax == "HOLD": return f"{v} s"
    if ax == "SPS": return f"sp {v[0]}/{v[1]}" if v else "no sp"
    if ax == "STALL": return f"stall {v}" if v else "no stall"
    return {"never": "its sale never", "always": "its sale always"}.get(v[0], f"its sale {v[1]}-{v[2]} s" + (" <1.5x" if v[3] < 1e8 else "") if v[0] == "early" else str(v))
def name(j): return ", ".join(lvname(ax, LV[i][k]) for i, (ax, k) in enumerate(zip(AX, np.unravel_index(j, SH))))
pick = lambda idx: int(np.argmax(smooth(wo2(G[idx]))))
pct = lambda v: 100 * np.mean(v) if len(v) else float("nan")
day = lambda x: __import__("datetime").datetime.fromtimestamp(x, __import__("datetime").UTC).strftime("%m-%d %H:%M")
print(f"{LAB}: {N} copies, {day(t[0])} to {day(t[-1])} UTC; blocks of {', '.join(str(len(b)) for b in B)}; % = a copy, of the stake")
print(f"live exit: {name(live)}")
print("\nfixed exits on the 4 blocks (no picking):")
fixed = [("live", live)]
def idx(tp, h, sp, st, it): return int(np.ravel_multi_index((LV[0].index(tp), LV[1].index(h), LV[2].index(sp), LV[3].index(st), LV[4].index(it)), SH))
for lab, j in [("standard tp 3 / 420 / stall 240", idx(3.0, 420, None, 240, ["never"])), ("wallet 4's live", idx(4.0, 600, [5, 60], 180, ["early", 30, 290, 1.5])),
               ("follow its sale, to 600 s", idx(None, 600, None, 0, ["always"])), ("tp 2 / 120 s", idx(2.0, 120, None, 0, ["never"])),
               ("tp 2 / 120 s / sp 5/60", idx(2.0, 120, [5, 60], 0, ["never"]))]:
    if j != live: fixed.append((lab, j))
for lab, j in fixed:
    per = [pct(G[b, j]) for b in B]
    print(f"  {lab:34s} " + " / ".join(f"{p:+6.1f}" for p in per) + f"  = {pct(G[:, j]):+6.1f}%  w/o 2% {100 * wo2v(G[:, j]) / N:+6.1f}%  blocks + {sum(p > 0 for p in per)}/4")
print("\n1. walk-forward (picked on the blocks before, scored blind):")
bl, lv_, wins = [], [], 0
for b in (1, 2, 3):
    tr = np.concatenate(B[:b]); j = pick(tr); v = G[B[b], j]; l = G[B[b], live]; bl.append(v); lv_.append(l); wins += v.sum() > l.sum()
    print(f"  block {b + 1}: picked on {len(tr)}: {name(j)}\n      blind {pct(v):+6.1f}%  live {pct(l):+6.1f}%  on {len(v)}")
bl, lv_ = np.concatenate(bl), np.concatenate(lv_)
print(f"  blind total {pct(bl):+.1f}% a copy (w/o 2% {100 * wo2v(bl) / len(bl):+.1f}%) against live {pct(lv_):+.1f}% (w/o 2% {100 * wo2v(lv_) / len(lv_):+.1f}%); better in {wins} of 3")
ruleA = bl.sum() > lv_.sum() and wo2v(bl) > wo2v(lv_) and wins >= 2
jall = pick(np.arange(N))
print(f"  the pick on all 4 blocks: {name(jall)}  ({pct(G[:, jall]):+.1f}% seen, flattering)")
print("\n2. each axis alone: [median paired diff a copy per block, other axes at every setting] | the live exit with only this changed")
lu = np.unravel_index(live, SH); cands = []
Gb = [G[b] for b in B]
for i, ax in enumerate(AX):
    for k, v in enumerate(LV[i]):
        if k == lu[i]: continue
        med = []
        for gb in Gb:
            a = gb.mean(0).reshape(SH); d = (a.take([k], i) - a.take([lu[i]], i)).ravel(); med.append(100 * np.median(d))
        jj = list(lu); jj[i] = k; jc = int(np.ravel_multi_index(tuple(jj), SH))
        per = [pct(G[b, jc]) - pct(G[b, live]) for b in B]; tot = pct(G[:, jc]) - pct(G[:, live]); w2d = 100 * (wo2v(G[:, jc]) - wo2v(G[:, live])) / N
        nm, nb = sum(m > 0 for m in med), sum(p > 0 for p in per)
        ok = nb >= 3 and tot > 0 and w2d > 0 and nm >= 3
        if ok: cands.append((w2d, jc, ax, v))
        if nm >= 3 or nb >= 3:
            print(f"  {lvname(ax, v):24s} median {' '.join(f'{m:+5.1f}' for m in med)} ({nm}/4) | changed {' '.join(f'{p:+5.1f}' for p in per)} ({nb}/4) total {tot:+5.1f} w/o2 {w2d:+5.1f}" + ("  <- passes B" if ok else ""))
print("\n3. VERDICT: ", end="")
if ruleA: print(f"A, a new exit: {name(jall)}")
elif cands:
    w2d, jc, ax, v = max(cands, key=lambda c: c[0]); print(f"B, one change: {lvname(ax, v)} -> {name(jc)} ({pct(G[:, jc]):+.1f}% against {pct(G[:, live]):+.1f}% live, w/o 2% {w2d:+.1f} points)")
else: print(f"C, keep the live exit ({pct(G[:, live]):+.1f}% a copy on all {N})")
