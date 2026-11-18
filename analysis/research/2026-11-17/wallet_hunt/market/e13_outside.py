# A wallet found on the 4-day screen, engineered there, then judged on its OTHER days (Nov 18, 5KcKcGcz): its first
# buys of 0.5+ SOL on coins priced in another token, outside the screen's 48 h (m5_confirm's set and paths, cached),
# under e8's full grid. Prints the settings picked on the 4 days, scored here, and this period's own best (for scale).
#   CACHED_ONLY=1 RPC_URL=x python3 -I e13_outside.py SP WALLET "name=size,prem,tp,hold,sp,stall,its" ...
import sys, os, numpy as np, datetime as dt
here = os.path.dirname(os.path.abspath(__file__)); SP, WL = sys.argv[1], sys.argv[2]; SETS = sys.argv[3:]
e8 = open(os.path.join(here, "e8_engineer.py")).read().split("rows = []")[0]
sys.argv = ["x", SP, WL]; exec(e8)
m5 = open(os.path.join(here, "m5_confirm.py")).read(); pre = m5.split("def S(v):")[0]
sys.argv = ["x", SP, WL]; exec(pre)
A_, B_ = map(int, os.environ.get("SCREEN", "1794704822,1794877622").split(",")); h = json.load(open(f"{SP}/winners/hist/{WL}.json")); fb = {}
for e in sorted(h["trades"], key=lambda e: e["t"]):
    if e["buy"]: fb.setdefault(e["m"], e)
rows = []
for m, e in fb.items():
    r = rate_of(e["quote"])
    if r is None or A_ <= e["t"] < B_ or e["quote"] in SOLQ: continue
    sol = e["q"] * (1 + e["bps"] / 1e4) * r / 1e9
    if sol < 0.5: continue
    try: tr = cpath(m, e["slot"], e["t"])
    except Exception: continue
    k = next((j for j, y in enumerate(tr) if y["user"] == WL and y["buy"] and y["slot"] == e["slot"]), None)
    if k is None: continue
    ps = [H.prep(tr, k, r, n, pmax=1000) for n in (4, 8, "slot+1")]
    rows.append(dict(t=e["t"], sol=sol, cls="float" if e["quote"][:8] in FLOATS else "wsol", prems=[(tr[k]["vt"] / p["ent"][0]) ** 2 for p in ps],
                     vl=np.array([copy_vals(p) for p in ps]) - COST))
rows.sort(key=lambda r: r["t"]); T = np.array([r["t"] for r in rows]); CL = np.array([r["cls"] for r in rows]); tmid = np.median(T); A = T < tmid
print(f"{WL}: {len(rows)} copies outside the screen (other-token coins, 0.5+ SOL), {dt.datetime.fromtimestamp(T.min(), dt.UTC):%m-%d} to {dt.datetime.fromtimestamp(T.max(), dt.UTC):%m-%d}; float-quoted {int((CL == 'float').sum())}")
def ix(z):
    return (TP.index(1e9 if z[2] == "none" else float(z[2])), HOLD.index(int(z[3])), SPS.index(None if z[4] == "off" else tuple(int(x) for x in z[4].split("/"))),
            STALL.index(0 if z[5] == "off" else int(z[5])), ITS.index(z[6]))
def score(spec, only=None):
    z = spec.split(","); e = ix(z); pm = 1e9 if z[1] == "none" else float(z[1]); v = []
    for i, r in enumerate(rows):
        if r["sol"] < float(z[0]) or (only and r["cls"] != only): v.append(0.0); continue
        v.append(np.mean([r["vl"][l][e] if r["prems"][l] <= pm else -0.0004 for l in range(3)]))
    v = np.array(v); b = v != 0; x = v[b]
    if not len(x): return "no copies"
    k = max(1, round(0.02 * len(x))); bs = np.random.default_rng(7).choice(x, size=(10000, len(x))).mean(axis=1)
    return (f"{b.sum()} copies | {x.sum():+.2f} SOL ({100 * x.mean() / 0.5:+.1f}% a copy) | half 1 {v[A & b].sum():+.2f} half 2 {v[~A & b].sum():+.2f} | "
            f"w/o 2% {np.sort(x)[:-k].sum():+.2f} | won {100 * np.mean(x > 0):.0f}% | P(mean>0) {100 * np.mean(bs > 0):.1f}%")
for s_ in SETS:
    nm, spec = s_.split("=", 1)
    print(f"\n{nm}: {spec}\n   all     {score(spec)}\n   floats  {score(spec, 'float')}\n   others  {score(spec, 'wsol')}")
V = np.array([r["vl"].mean(axis=0) for r in rows]); best = np.unravel_index(int(np.argmax(V.sum(axis=0))), V.shape[1:])
print(f"\nthis period's own best exit (0.5+, no price limit; hindsight, for scale only): tp {TP[best[0]]}, {HOLD[best[1]]} s, sp {SPS[best[2]]}, stall {STALL[best[3]]}, its {ITS[best[4]]}: "
      f"{V.sum(axis=0)[best]:+.2f} SOL; exits positive in total: {int((V.sum(axis=0) > 0).sum())} of {V[0].size}")
# the full grid from scratch on these days (Nov 18, the owner: "engineer the exit from scratch"): every buy size x price
# limit x exit, for all coins, floats only and the others; the settings that make money, and the best (hindsight)
SOLA = np.array([r["sol"] for r in rows]); VL3 = np.array([r["vl"] for r in rows]); PM3 = np.array([r["prems"] for r in rows])
print("\nTHE FULL GRID FROM SCRATCH (13 sizes x 4 price limits x 9,720 exits = 505,440 settings), on these days:")
for lab, cm in (("all coins", np.ones(len(rows), bool)), ("floats only", CL == "float"), ("others only", CL == "wsol")):
    npos = nboth = 0; best = (-1e9, None)
    for a, sz in enumerate(SIZE):
        for b_, pm in enumerate(PREM):
            f = cm & (SOLA >= sz)
            if f.sum() < 20: continue
            ok3 = PM3[f] <= pm                                    # per landing: refused above the limit
            v = np.where(ok3[:, :, None, None, None, None, None], VL3[f], -0.0004).mean(axis=1)
            s = v.sum(axis=0); h1 = v[A[f]].sum(axis=0); h2 = v[~A[f]].sum(axis=0)
            npos += int((s > 0).sum()); nboth += int(((h1 > 0) & (h2 > 0)).sum())
            j = np.unravel_index(int(np.argmax(s)), s.shape)
            if s[j] > best[0]: best = (s[j], (sz, pm, j, int(f.sum()), h1[j], h2[j]))
    if best[1] is None: print(f"   {lab:12s}: under 20 copies"); continue
    sz, pm, j, n, a1, a2 = best[1]
    print(f"   {lab:12s}: settings making money {npos:,}, on both halves {nboth:,}; the best (hindsight): its buy {sz}+, limit {'none' if pm > 1e8 else pm}, "
          f"tp {'none' if TP[j[0]] > 1e8 else TP[j[0]]}, {HOLD[j[1]]} s, sp {SPS[j[2]] or 'off'}, stall {STALL[j[3]] or 'off'}, its {ITS[j[4]]}: "
          f"{n} copies {best[0]:+.2f} SOL (half 1 {a1:+.2f}, half 2 {a2:+.2f})")
# each part, every value (Nov 18, the owner: "stall? sell pressure? buy size? tp's?"): for each value, the BEST setting
# that has it (the others free, hindsight), its SOL and its weaker half; if even the best with that value loses, that
# value cannot save the copy
for lab, cm in (("all coins", np.ones(len(rows), bool)), ("floats only", CL == "float")):
    G = np.full((len(SIZE), len(PREM)) + VL3.shape[2:], np.nan); W_ = G.copy()
    for a, sz in enumerate(SIZE):
        for b_, pm in enumerate(PREM):
            f = cm & (SOLA >= sz)
            if f.sum() < 20 or (A & f).sum() == 0 or (~A & f).sum() == 0: continue
            v = np.where((PM3[f] <= pm)[:, :, None, None, None, None, None], VL3[f], -0.0004).mean(axis=1)
            G[a, b_] = v.sum(axis=0); W_[a, b_] = np.minimum(v[A[f]].sum(axis=0), v[~A[f]].sum(axis=0))
    print(f"\nEACH PART, EVERY VALUE ({lab}): the best setting with that value (the rest picked with hindsight): SOL all | its weaker half")
    names = [("its buy size", [f"{x}+" for x in SIZE]), ("price limit", ["1.1x", "1.25x", "1.5x", "none"]), ("take profit", [("none" if x > 1e8 else f"{x}x") for x in TP]),
             ("time", [f"{x}s" for x in HOLD]), ("sell pressure", ["off"] + [f"{n}/{w}s" for n, w in SPS[1:]]), ("stall", ["off"] + [f"{x}s" for x in STALL[1:]]), ("its sale", ITS)]
    for d, (nm, vals) in enumerate(names):
        cells = []
        for j, vl in enumerate(vals):
            g = np.take(G, j, axis=d); w = np.take(W_, j, axis=d)
            cells.append(f"{vl} {np.nanmax(g):+.2f}|{np.nanmax(w):+.2f}" if np.isfinite(np.nanmax(g)) else f"{vl} -")
        print(f"   {nm:13s}: " + "   ".join(cells))
