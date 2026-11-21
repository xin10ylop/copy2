# The whole process on one wallet's two weeks (b1_paths.py): our copy at 1 SOL in the slot after its buy, 0.0345 SOL a round
# trip (COST env to change), and every setting: its buy floor 0.5 0.7 1 1.3 1.5 2 SOL x coins all / SOL / token x price
# limit 1.25 1.5 2 none x take profit 1.5-8 or none x timer 120-1200 s x sell pressure off or 3-15 over 30-120 s x stall off
# 60-300 s x its sale never / early / always (1,693,440 settings). Picked on week 1 (seen) by the SOL without its best 2%,
# scored on week 2 (unseen); also halves of each week.
#   LK=SP/lk python3 -I b2_grid.py SP WALLET > out/b2_<w8>.txt
import sys, os, json, gzip, itertools, numpy as np, datetime as dt
SP, W = sys.argv[1], sys.argv[2]; LK = os.environ["LK"]; D = f"{SP}/cand_{W[:8]}"
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-17/wallet_hunt"); import hunt_lib as H
STAKE = 1.0; COST = float(os.environ.get("COST", 0.0345)) - 0.0026
TP = [1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8, None]; HOLD = [120, 180, 300, 450, 600, 900, 1200]
SPS = [None] + [(n, w) for n in (3, 5, 8, 10, 15) for w in (30, 60, 120)]; STALL = [0, 60, 90, 120, 180, 240, 300]; ITS = ["never", "early", "always"]
LIM = [1.25, 1.5, 2.0, 1e9]; FLOOR = [0.5, 0.7, 1.0, 1.3, 1.5, 2.0]; KIND = ["all", "SOL", "token"]; SH = (len(TP), len(HOLD), len(SPS), len(STALL), len(ITS))
def first(m):
    i = np.flatnonzero(m); return int(i[0]) if len(i) else None
coins = json.load(open(f"{D}/coins.json")); rows = []
for c in coins:
    f = f"{LK}/paths/{c['slot']}_{c['m']}.json.gz"
    if not os.path.exists(f): continue
    tr = json.load(gzip.open(f)); k = next((i for i, e in enumerate(tr) if e["user"] == W and e["buy"] and e["slot"] == c["slot"]), None)
    if k is None: continue
    p = H.prep(tr, k, c["rate"], "slot+1", pmax=1e9)
    if not len(p["px"]): continue
    vt0, vq0, b0 = p["ent"]; Q = STAKE * 1e9 / c["rate"]; net_in = Q * 1e4 / (1e4 + b0); tok = vt0 - vt0 * vq0 / (vq0 + net_in)
    vq_r = p["vq"] + net_in; vt_r = p["vt"] * p["vq"] / vq_r
    val = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - p["bps"] / 1e4) * c["rate"] / 1e9 - STAKE - 0.0026 - COST
    prem = (tr[k]["vt"] / vt0) ** 2; px, age, n = p["px"], p["age"], len(p["px"]); BIG = 10 ** 9
    trig = lambda i: BIG if i is None else min(i + 1, n - 1); at = lambda i: BIG if i is None else i
    tp_i = np.array([trig(first(px >= t)) if t else BIG for t in TP]); h_i = np.array([at(first(age >= h)) for h in HOLD])
    s = np.concatenate([[0], np.cumsum(p["osell"])]); b = np.concatenate([[0], np.cumsum(p["obuy"])]); sp_i = []
    for sp in SPS:
        if sp is None: sp_i.append(BIG); continue
        lo = np.searchsorted(age, age - sp[1], side="left"); sp_i.append(trig(first(((s[1:] - s[lo]) - (b[1:] - b[lo]) >= sp[0]) & (age >= 30))))
    pk = np.maximum.accumulate(px); newhi = np.concatenate([[True], pk[1:] > pk[:-1]]); lasthi = np.maximum.accumulate(np.where(newhi, age, -1e9))
    st_i = np.array([BIG if st == 0 else trig(first((pk >= prem) & (age - lasthi >= st))) for st in STALL])
    it_i = np.array([BIG, trig(first(p["sell"] & (age >= 30) & (age < 290) & (px < 1.5))), trig(first(p["sell"]))])
    E = np.full(SH, min(at(first(p["grad"])), n - 1), dtype=np.int64)
    for arr in (tp_i[:, None, None, None, None], h_i[None, :, None, None, None], np.array(sp_i)[None, None, :, None, None], st_i[None, None, None, :, None], it_i[None, None, None, None, :]):
        E = np.minimum(E, arr)
    fs = first(p["sell"]); hold = float(age[fs]) if fs is not None else None
    rows.append(dict(hold=hold, t=c["t"], sol=c["its_sol"], kind="SOL" if c["sol"] else "token", prem=prem, g=val[np.minimum(E, n - 1)].astype(np.float32).ravel()))
rows.sort(key=lambda r: r["t"]); T = np.array([r["t"] for r in rows]); S = np.array([r["sol"] for r in rows]); K = np.array([r["kind"] for r in rows])
PR = np.array([r["prem"] for r in rows]); G = np.stack([r["g"] for r in rows])
t0, t1 = T.min(), T.max(); cut = t0 + (t1 - t0) / 2; seen, unseen = T < cut, T >= cut
f = lambda t: dt.datetime.fromtimestamp(t, dt.UTC).strftime("%m-%d %H:%M")
hs = [r["hold"] for r in rows if r["hold"] is not None]
print(f"its holding (buy to its first sale): median {np.median(hs):.0f} s, under 20 s on {100 * np.mean(np.array(hs) < 20):.0f}% of its coins; no sale within 31 min on {sum(r['hold'] is None for r in rows)}")
print(f"{W}: {len(rows)} copies with a path, {f(t0)} to {f(t1)} UTC; seen (week 1) {seen.sum()}, unseen (week 2) {unseen.sum()}; 1 SOL a copy, cost {COST + 0.0026:.4f}")
def wo2(M):
    if M.shape[0] == 0: return np.zeros(M.shape[1])
    k = max(1, round(0.02 * M.shape[0])); return M.sum(0) - np.sort(M, 0)[-k:].sum(0)
names = list(itertools.product(TP, HOLD, SPS, STALL, ITS)); out = []
for li, lim in enumerate(LIM):
    for fi, fl in enumerate(FLOOR):
        for ki, kd in enumerate(KIND):
            sel = (S >= fl) & ((K == kd) if kd != "all" else True)
            V = np.where((PR <= lim)[:, None], G, np.float32(-0.0004)) * sel[:, None]
            a, b_ = V[seen & sel], V[unseen & sel]
            out.append((li, fi, ki, wo2(a), a.sum(0), wo2(b_), b_.sum(0), (seen & sel).sum(), (unseen & sel).sum()))
ns = len(names); sw = np.concatenate([o[3] for o in out]); ss = np.concatenate([o[4] for o in out]); uw = np.concatenate([o[5] for o in out]); us = np.concatenate([o[6] for o in out])
cnt_s = np.concatenate([np.full(ns, o[7]) for o in out]); cnt_u = np.concatenate([np.full(ns, o[8]) for o in out])
MS, MU = int(os.environ.get("MIN_SEEN", 20)), int(os.environ.get("MIN_UNSEEN", 10))
ok = (cnt_s >= MS) & (cnt_u >= MU)   # a setting needs MS+ seen and MU+ unseen copies (20 / 10)
def desc(i):
    r, j = divmod(i, ns); li, r2 = divmod(r, len(FLOOR) * len(KIND)); fi, ki = divmod(r2, len(KIND)); tp, h, sp, st, its = names[j]
    return f"{FLOOR[fi]}+ {KIND[ki]}, limit {LIM[li] if LIM[li] < 1e8 else 'none'}, tp {tp or 'none'}, {h} s, sp {('%d/%d' % sp) if sp else 'off'}, stall {st or 'off'}, its {its}"
j_def = (LIM.index(1.5) * len(FLOOR) * len(KIND) + FLOOR.index(0.5) * len(KIND) + KIND.index("all")) * ns + names.index((4, 600, (5, 60), 180, "early"))
print(f"\nwallet 4's live exit, every copy (0.5+ all, 1.5x): seen {ss[j_def]:+.2f} SOL on {cnt_s[j_def]} (w/o 2% {sw[j_def]:+.2f}) -> unseen {us[j_def]:+.2f} on {cnt_u[j_def]} (w/o 2% {uw[j_def]:+.2f})")
idx = np.flatnonzero(ok); order = idx[np.argsort(-sw[idx])]
print(f"the 10 best on week 1 (of {ok.sum():,} settings with {MS}+ / {MU}+ copies), and week 2:")
for i in order[:10]:
    print(f"  seen {ss[i]:+6.2f} on {cnt_s[i]} (w/o 2% {sw[i]:+6.2f}) -> unseen {us[i]:+6.2f} on {cnt_u[i]} ({100 * us[i] / cnt_u[i]:+.1f}% a copy, w/o 2% {uw[i]:+6.2f})  {desc(i)}")
top = order[: max(1, len(order) // 100)]
print(f"the top 1% on week 1: week 2 median {np.median(us[top]):+.2f} SOL (w/o 2% {np.median(uw[top]):+.2f}); every setting's week 2 median {np.median(us[idx]):+.2f}; "
      f"share of all settings up in week 2: {100 * np.mean(us[idx] > 0):.0f}%")
