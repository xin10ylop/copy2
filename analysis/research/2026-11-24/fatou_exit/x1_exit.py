# An exit for FatoU1bj, a 20-second flipper (Nov 24; the owner: "let's run it, but engineer a super good exit, re-analyze
# his trades well; 0.1 SOL for 20 trades then raise"). Its first buys of 0.5+ SOL (SOL coins), our copy landing at the end
# of the slot after its buy (or two slots: LAND), 1 SOL, COST a round trip, the coin's trades from the cached paths
# (../../2026-11-13/tab_exits/cmodel.py). The menu, fixed before any result was seen:
#   follow its sale: we sell in the first trade D slots after its sale (D = 0: the next trade; 1, 2, 3 = about 0.4,
#     0.8, 1.2 s later: the live bot sees its sale in its slot and lands one or two slots after) | never
#   x a hold cap from its buy: 15, 30, 45, 60, 90, 120, 300 s   x a take profit (x its price): none, 1.2, 1.3, 1.5, 2, 3
# (a trigger sells on the next trade; graduation ends the trip; a copy over 1.5x its price is refused, -0.0004).
# Picked on its buys to Nov 23 15:13 UTC (the deep test's data, 4 time blocks): the most SOL without the best 2%, at D = 2;
# checked on its buys after that (the new fetch, unseen by the pick) and at every D and LAND.
#   LK=SP/lk RPC_URL=... COST=0.0064 python3 -I x1_exit.py SP OLD_HIST_DIR NEW_HIST_DIR
import sys, os, json, collections, datetime as dt, numpy as np, concurrent.futures as cf
SP, OLD, NEW = sys.argv[1], sys.argv[2], sys.argv[3]
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, "../../2026-11-13/tab_exits")); import cmodel as M
W = "FatoU1bj1cwMEZ7nNBUu47s8HpJNAFR5ZajGPtP8Fph1"; COST = float(os.environ.get("COST", 0.0064)); STAKE = 1.0; PMAX = 1.5
def load(d):
    tr = [e for l in open(f"{d}/FatoU1bj_trades.jsonl") for e in (json.loads(l)["trades"] or [])]
    return tr, json.load(open(f"{d}/FatoU1bj_sigs.json"))
tr_o, s_o = load(OLD); tr_n, s_n = load(NEW)
cut = max(t for _, t in s_o)                                   # the old data's end
sigs = sorted({(t, s) for s, t in s_o + s_n})
by = collections.defaultdict(list)
for e in tr_o + tr_n: by[e["m"]].append(e)
firsts = []
for m, es in by.items():
    es = sorted({(e["slot"], e["t"], e["buy"], e["q"], e["quote"] or "") for e in es}, key=lambda x: (x[0], not x[2]))
    sl, t, buy, q, quote = es[0]
    if not buy or not (quote == "" or quote.startswith("1111")) or not (float(os.environ.get("MINSOL", 0.5)) <= q / 1e9 < float(os.environ.get("MAXSOL", 1e9))): continue   # Nov 24: a band of its buy
    end = cut if t <= cut - 700 else max(t_ for t_, _ in sigs)
    if t > end - 700: continue
    firsts.append(dict(m=m, slot=sl, t=t, sol=q / 1e9, new=t > cut - 700))
firsts.sort(key=lambda c: c["t"])
anchor = lambda c: next((s for t, s in sigs if t >= c["t"] + 640), sigs[-1][1])
with cf.ThreadPoolExecutor(8) as ex: paths = list(ex.map(lambda c: M.path(c["m"], c["slot"], anchor(c), threads=8), firsts))
TPS = [None, 1.2, 1.3, 1.5, 2.0, 3.0]; CAPS = [15, 30, 45, 60, 90, 120, 300]; DS = [None, 0, 1, 2, 3]
def copy(c, tr, land):
    k = next((i for i, e in enumerate(tr) if e["user"] == W and e["buy"] and e["slot"] == c["slot"]), None)
    if k is None: return None
    its = tr[k]; vta, t0 = its["vt"], its["t"]
    j = k + len([e for e in tr[k + 1:] if e["slot"] <= its["slot"] + land])
    ent = tr[j]; rest = tr[j + 1:]
    if (vta / ent["vt"]) ** 2 > PMAX: return dict(refused=True)
    net_in = STAKE * 1e9 * 1e4 / (1e4 + ent["bps"]); tok = ent["vt"] - ent["vt"] * ent["vq"] / (ent["vq"] + net_in)
    def val(i):
        if i is None or not rest: vq, vt, b = ent["vq"], ent["vt"], ent["bps"]
        else: e = rest[min(i, len(rest) - 1)]; vq, vt, b = e["vq"], e["vt"], e["bps"]
        vq_r = vq + net_in; vt_r = vt * vq / vq_r
        return (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - b / 1e4) / 1e9 - STAKE - COST
    n = len(rest); px = np.array([(vta / e["vt"]) ** 2 for e in rest]); age = np.array([e["t"] - t0 for e in rest], float)
    slot = np.array([e["slot"] for e in rest]); grad = next((i for i, e in enumerate(rest) if e.get("real") == 0), None)
    sale = next((e for e in tr[k + 1:] if e["user"] == W and not e["buy"]), None)
    hold = sale["t"] - t0 if sale else None
    first = lambda m_: int(np.argmax(m_)) if n and m_.any() else None
    out = {}
    for d in DS:
        fs = None
        if d is not None and sale is not None:
            fs = first(slot >= sale["slot"] + d) if d > 0 else first(np.array([e["slot"] > sale["slot"] or (e["slot"] == sale["slot"] and e is not sale and tr.index(e) > tr.index(sale)) for e in rest]))
        for tp in TPS:
            ti = None if tp is None else first(px >= tp)
            ti = None if ti is None else min(ti + 1, n - 1)
            for cap in CAPS:
                ci = first(age >= cap)
                ex_ = [x for x in (fs, ti, ci, grad) if x is not None]
                out[(d, tp, cap)] = val(min(ex_) if ex_ else n - 1)
    return dict(refused=False, v=out, hold=hold, prem=(vta / ent["vt"]) ** 2)
KEYS = [(d, tp, cap) for d in DS for tp in TPS for cap in CAPS]
def table(land):
    rows = []
    for c, tr in zip(firsts, paths):
        r = copy(c, tr, land)
        if r is None: continue
        r["new"] = c["new"]; r["t"] = c["t"]; rows.append(r)
    V = np.array([[-0.0004] * len(KEYS) if r["refused"] else [r["v"][k_] for k_ in KEYS] for r in rows])
    return rows, V
def wo2(v):
    k = max(1, round(0.02 * len(v))); return v.sum() - np.sort(v)[-k:].sum()
def name(k_):
    d, tp, cap = k_
    return (f"its sale +{d} slot{'s' if d != 1 else ''}" if d else "its sale, next trade" if d == 0 else "never its sale") + f", tp {tp or 'none'}, cap {cap} s"
rows, V = table(1)
old = np.array([not r["new"] for r in rows]); new = ~old
blocks = np.array_split(np.where(old)[0], 4)
hold = np.array([r["hold"] for r in rows if r.get("hold") is not None])
print(f"FatoU1bj: {len(rows)} copies of its first buys of 0.5+ SOL ({old.sum()} to {dt.datetime.fromtimestamp(cut, dt.UTC):%m-%d %H:%M} UTC, "
      f"{new.sum()} after); refused over {PMAX}x: {sum(r['refused'] for r in rows)}; its hold to its first sale: median {np.median(hold):.0f} s, "
      f"10% {np.percentile(hold, 10):.0f} s, 90% {np.percentile(hold, 90):.0f} s; COST {COST}")
print(f"\n1. the pick on the old data at D = 2 (the most SOL without the best 2%); % a copy at 1 SOL")
cand = [i for i, k_ in enumerate(KEYS) if k_[0] in (2, None)]
sc = sorted(((wo2(V[old, i]), i) for i in cand), reverse=True)
print(f"   {'exit':48s} {'old: blocks 1 / 2 / 3 / 4':>34s} {'all':>7s} {'w/o 2%':>7s}   {'NEW':>7s} {'n':>3s} {'w/o 2%':>7s}")
def line(i):
    k_ = KEYS[i]; per = " / ".join(f"{100 * V[b, i].mean():+6.1f}" for b in blocks)
    return (f"   {name(k_):48s} {per:>34s} {100 * V[old, i].mean():+6.1f}% {wo2(V[old, i]):+7.2f}   "
            f"{100 * V[new, i].mean() if new.any() else float('nan'):+6.1f}% {new.sum():3d} {wo2(V[new, i]) if new.sum() > 2 else float('nan'):+7.2f}")
for s_, i in sc[:12]: print(line(i))
print("   for reference:")
for k_ in [(2, None, 600 if 600 in CAPS else 300), (None, 3.0, 300), (None, 1.5, 60), (0, None, 300), (2, None, 300)]:
    if k_ in KEYS: print(line(KEYS.index(k_)))
best = sc[0][1]; bk = KEYS[best]
print(f"\nPICK: {name(bk)}")
print("\n2. the pick and its neighbours at every landing of our sale (D) and our buy (LAND), all copies, % a copy (w/o 2% SOL)")
for land in (1, 2):
    rows_l, V_l = table(land)
    for tp in sorted({bk[1], None, 1.3, 1.5}, key=lambda x: (x is not None, x or 0)):
        for cap in sorted({bk[2], 30, 60}):
            cells = []
            for d in DS:
                i = KEYS.index((d, tp, cap)); cells.append(f"{100 * V_l[:, i].mean():+5.1f}% ({wo2(V_l[:, i]):+5.2f})")
            print(f"   buy slot+{land}, tp {str(tp or 'none'):4s}, cap {cap:3d} s:  " + "  ".join(f"{('never' if d is None else f'D={d}'):5s} {c}" for d, c in zip(DS, cells)))
