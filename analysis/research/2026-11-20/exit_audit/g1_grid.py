# Every combination, picked on two weeks and scored on the weeks after (Nov 20; the owner: "2 weeks seen then 2 weeks
# unseen ... test all the combinations, take profits, timers, in all increments"). Wallet 4's token-coin buys, e4_long's
# 1,175 copies (Oct 21 - Nov 14 01:07 and Nov 15 19:56 - Nov 20 17:12 UTC), our 1 SOL landing in the slot after its buy,
# the live bot's rules for each part (stall from our fill, its early sale 30-290 s under 1.5x, a trigger sells on the next
# trade, 0.0345 SOL a round trip):
#   take profit (x its price) 1.5 2 2.5 3 3.5 4 5 6 8 none | timer 120 180 300 450 600 900 1200 s
#   sell pressure off, or N of 3 5 8 10 15 more sells than buys over W of 30 60 120 s (from 30 s)
#   stall off 60 90 120 180 240 300 s | its sale never / early / always | price limit 1.25 1.5 2 none | its buy 1.3+ 1.5+ 2+
# = 282,240 settings. Two splits: A = seen Oct 21 - Nov 4, unseen Nov 4 - Nov 20; B (the latest) = seen Oct 31 - Nov 14,
# unseen Nov 15 - Nov 20. The pick on the seen part = the most SOL without the seen part's best 2% of copies.
#   LK=SP/lk python3 -I g1_grid.py SP > out/g1_grid.txt
import sys, numpy as np, datetime as dt, itertools
exec(open("e4_long.py").read().split("V = {")[0])
TP = [1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8, None]; HOLD = [120, 180, 300, 450, 600, 900, 1200]
SPS = [None] + [(n, w) for n in (3, 5, 8, 10, 15) for w in (30, 60, 120)]; STALL = [0, 60, 90, 120, 180, 240, 300]; ITS = ["never", "early", "always"]
LIM = [1.25, 1.5, 2.0, 1e9]; MIN = [1.3, 1.5, 2.0]
SH = (len(TP), len(HOLD), len(SPS), len(STALL), len(ITS))
def grid(p):
    if p["refused"]: return None
    px, age, n = p["px"], p["age"], len(p["px"]); BIG = 10 ** 9
    trig = lambda i: BIG if i is None else min(i + 1, n - 1); at = lambda i: BIG if i is None else i
    tp_i = np.array([trig(first(px >= t)) if t else BIG for t in TP]); h_i = np.array([at(first(age >= h)) for h in HOLD])
    s = np.concatenate([[0], np.cumsum(p["osell"])]); b = np.concatenate([[0], np.cumsum(p["obuy"])]); sp_i = []
    for sp in SPS:
        if sp is None: sp_i.append(BIG); continue
        lo = np.searchsorted(age, age - sp[1], side="left"); sp_i.append(trig(first(((s[1:] - s[lo]) - (b[1:] - b[lo]) >= sp[0]) & (age >= 30))))
    pk = np.maximum.accumulate(px); newhi = np.concatenate([[True], pk[1:] > pk[:-1]]); lasthi = np.maximum.accumulate(np.where(newhi, age, -1e9))
    st_i = np.array([BIG if st == 0 else trig(first((pk >= p["prem"]) & (age - lasthi >= st))) for st in STALL])
    it_i = np.array([BIG, trig(first(p["sell"] & (age >= 30) & (age < 290) & (px < 1.5))), trig(first(p["sell"]))])
    E = np.full(SH, min(at(first(p["grad"])), n - 1), dtype=np.int64)
    for arr in (tp_i[:, None, None, None, None], h_i[None, :, None, None, None], np.array(sp_i)[None, None, :, None, None],
                st_i[None, None, None, :, None], it_i[None, None, None, None, :]):
        E = np.minimum(E, arr)
    return p["val"][np.minimum(E, n - 1)].astype(np.float32)
T = np.array([p["t"] for p in ps]); S = np.array([p["sol"] for p in ps])
PR = np.array([p["prem"] if not p["refused"] else 99 for p in ps])
G = np.stack([grid(p) if not p["refused"] else np.full(SH, -0.0004, np.float32) for p in ps])   # copies x settings
print(f"{len(ps)} copies, {np.prod(SH) * len(LIM) * len(MIN):,} settings", flush=True)
d = lambda y, m, dd: dt.datetime(y, m, dd, tzinfo=dt.UTC).timestamp()
SPLITS = {"A: seen Oct 21 - Nov 4, unseen Nov 4 - Nov 20": (T < d(2026, 11, 4), T >= d(2026, 11, 4)),
          "B: seen Oct 31 - Nov 14, unseen Nov 15 - Nov 20": ((T >= d(2026, 10, 31)) & (T < d(2026, 11, 15)), T >= d(2026, 11, 15))}
names = list(itertools.product(TP, HOLD, SPS, STALL, ITS))
LIVE = (TP.index(4), HOLD.index(600), SPS.index((5, 60)), STALL.index(180), ITS.index("early"))
def wo2(M):   # M: copies x settings -> sum without the best 2% of copies, per setting
    k = max(1, round(0.02 * M.shape[0])); return M.sum(0) - np.sort(M, 0)[-k:].sum(0)
for sname, (seen, unseen) in SPLITS.items():
    print(f"\n=== {sname}: {seen.sum()} / {unseen.sum()} copies (all sizes 1.3+)")
    rows_ = []
    for li, lim in enumerate(LIM):
        for mi, mn in enumerate(MIN):
            V = np.where((PR <= lim)[:, None, None, None, None, None], G, np.float32(-0.0004)).reshape(len(ps), -1)
            V = np.where((S >= mn)[:, None], V, 0)
            a, b_ = V[seen], V[unseen]
            rows_.append((li, mi, wo2(a), a.sum(0), wo2(b_), b_.sum(0), (S[seen] >= mn).sum(), (S[unseen] >= mn).sum()))
    # the live setting
    for li, mi, sw, ss, uw, us, ns_, nu_ in rows_:
        if LIM[li] == 1.5 and MIN[mi] == 1.3:
            j = np.ravel_multi_index(LIVE, SH)
            print(f"LIVE (tp 4, 600 s, sp 5/60, stall 180, its early, limit 1.5x, 1.3+): seen {ss[j]:+.2f} (w/o 2% {sw[j]:+.2f}) -> unseen {us[j]:+.2f} (w/o 2% {uw[j]:+.2f})")
    allsw = np.concatenate([r[2] for r in rows_]); allus = np.concatenate([r[5] for r in rows_]); alluw = np.concatenate([r[4] for r in rows_]); allss = np.concatenate([r[3] for r in rows_])
    order = np.argsort(-allsw); N = allsw.size
    rank_u = np.empty(N, int); rank_u[np.argsort(-alluw)] = np.arange(1, N + 1)
    def desc(i):
        r, j = divmod(i, np.prod(SH)); li, mi = divmod(r, len(MIN)); tp, h, sp, st, its = names[j]
        return f"tp {tp or 'none'}, {h} s, sp {('%d/%d' % sp) if sp else 'off'}, stall {st or 'off'}, its {its}, limit {LIM[li] if LIM[li] < 1e8 else 'none'}, {MIN[mi]}+"
    print(f"the 10 best on the seen part (w/o its best 2%), and how they did unseen (rank of {N:,} unseen, w/o 2%):")
    for i in order[:10]:
        print(f"  seen {allss[i]:+7.2f} (w/o 2% {allsw[i]:+7.2f}) -> unseen {allus[i]:+7.2f} (w/o 2% {alluw[i]:+6.2f}, rank {rank_u[i]:,})  {desc(i)}")
    jl = (LIM.index(1.5) * len(MIN) + MIN.index(1.3)) * np.prod(SH) + np.ravel_multi_index(LIVE, SH)
    rank_us = np.empty(N, int); rank_us[np.argsort(-allus)] = np.arange(1, N + 1); rank_s = np.empty(N, int); rank_s[order] = np.arange(1, N + 1)
    print(f"LIVE ranks: seen {rank_s[jl]:,} of {N:,} (w/o 2%); unseen {rank_us[jl]:,} (SOL), {rank_u[jl]:,} (w/o 2%)")
    top = order[: N // 100]
    print(f"the top 1% seen ({len(top):,} settings): unseen median {np.median(allus[top]):+.2f} (w/o 2% {np.median(alluw[top]):+.2f}); all settings' unseen median {np.median(allus):+.2f}")
    print("each part alone, the mean over every other setting: seen | unseen (SOL)")
    full = np.stack([np.stack([r[3] for r in rows_]).reshape(len(LIM), len(MIN), *SH), np.stack([r[5] for r in rows_]).reshape(len(LIM), len(MIN), *SH)])
    for ax, lab, vals in ((3, "take profit", TP), (4, "timer", HOLD), (5, "sell pressure", SPS), (6, "stall", STALL), (7, "its sale", ITS), (1, "limit", LIM), (2, "its buy", MIN)):
        m = [full[(slice(None),) * ax + (k,)].reshape(2, -1).mean(1) for k in range(len(vals))]
        lbl = lambda v: "off" if v is None else ("%d/%d" % v if isinstance(v, tuple) else ("none" if v == 1e9 else str(v)))
        print(f"  {lab:13s}: " + "  ".join(f"{lbl(v)}: {x[0]:+.1f}|{x[1]:+.1f}" for v, x in zip(vals, m)))
