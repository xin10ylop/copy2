# The test with less room for luck (Nov 22; the owner: "how can we avoid that kind of overfitting? ... do that for these 3
# wallets, as a test"). w2_grid.py picked the best of 24.5 million settings on one older half of 60 buys; the pick lost
# half to two thirds of its edge on the blind half. Here:
#  - a MENU of 48 settings fixed before any data is seen: 8 exits (wallet 4's live exit, the same without its sale,
#    tp 2x/120 s, tp 1.5x/60 s, held 300 s, its sale (to 600 s), tp 3x/420 s/stall 240, tp 2.5x/300 s/sell pressure 5/60)
#    x the coin's quote all | SOL | a token x its buy 0.5+ | 1.3+ SOL, price limit 1.5x;
#  - ALL its first buys of 0.5+ SOL (or MAXN at random, spread over its whole history), not 60 a half;
#  - ROLLING blind periods: its buys in time order cut in 4 blocks; pick on blocks 1, test block 2; pick on 1-2, test 3;
#    pick on 1-3, test 4 (an expanding window). Each test block is unseen when its pick is made;
#  - a LUCK baseline: the same rolling pick on the copies with each setting's mean taken out (no edge left): what the
#    pick gains on its own seen blocks by luck alone, to read the seen numbers against.
# The pick on seen blocks: the most SOL without their best 2% of copies. PASS: the blind mean positive, positive in at
# least 2 of the 3 blind blocks, and the blind blocks together positive without their best 2%.
#   HELIUS_URL=... RPC_URL=... LK=SP/lk COST=0.0064 python3 -I w3_robust.py SP WALLET [MAXN=700]
import sys, os, random, numpy as np
SP, W = sys.argv[1], sys.argv[2]; MAXN = int(sys.argv[3]) if len(sys.argv) > 3 else 700
HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv = [sys.argv[0], SP, W, "0", "0", "14"]
src = open(os.path.join(HERE, "w2_grid.py")).read()
exec(src.split("firsts.sort(key=lambda c: c[\"t\"]); h = len(firsts) // 2")[0])   # its own history (stops if it loses), grid(), first()
MENU_EXITS = {"live (tp 4, 600 s, sp 5/60, stall 180, its early sale)": (4.0, 600, (5, 60), 180, 2),
              "live without its sale": (4.0, 600, (5, 60), 180, 0), "tp 2x / 120 s": (2.0, 120, None, 0, 0),
              "tp 1.5x / 60 s": (1.5, 60, None, 0, 0), "held 300 s": (None, 300, None, 0, 0), "its sale (to 600 s)": (None, 600, None, 0, 1),
              "tp 3x / 420 s / stall 240": (3.0, 420, None, 240, 0), "tp 2.5x / 300 s / sp 5/60": (2.5, 300, (5, 60), 0, 0)}
IDX = [np.ravel_multi_index((TP.index(tp), HOLD.index(h_), SPS.index(sp), STALL.index(st), it), SH) for tp, h_, sp, st, it in MENU_EXITS.values()]
ENAMES = list(MENU_EXITS); FILT = [(kd, mn) for kd in ("all", "SOL", "token") for mn in (0.5, 1.3)]
if os.environ.get("PICK_ALL"): FILT = [("all", 0.5)]   # Nov 22 check: the pick among the 8 exits on all its coins only
firsts.sort(key=lambda c: c["t"])
if len(firsts) > MAXN:
    random.seed(7); firsts = sorted(random.sample(firsts, MAXN), key=lambda c: c["t"])
rows = []
for i in range(0, len(firsts), 30):                      # 30 coins at a time; each copy keeps only the menu's 8 exits
    for r_ in fetch(firsts[i:i + 30]):
        r_["g"] = r_["g"][IDX]; rows.append(r_)
rows.sort(key=lambda r_: r_["t"])
print(f"copies: {len(rows)} of its {len(firsts)} first buys of 0.5+ SOL tested; menu: {len(ENAMES)} exits x {len(FILT)} filters = {len(ENAMES) * len(FILT)} settings")
G = np.stack([r_["g"] for r_ in rows]); prem = np.array([r_["prem"] for r_ in rows]); sol = np.array([r_["sol"] for r_ in rows]); tok = np.array([r_["tok"] for r_ in rows])
def value(f, G_=G):
    kd, mn = f; keep = (sol >= mn) & ((kd == "all") | ((kd == "token") == tok)); ref = prem > 1.5
    return np.where((keep & ~ref)[:, None], G_, np.where((keep & ref)[:, None], np.float32(-0.0004), np.float32(0))), keep
def wo2(v):
    k = max(1, round(0.02 * len(v))); return v.sum() - np.sort(v)[-k:].sum() if len(v) else 0.0
blocks = np.array_split(np.arange(len(rows)), 4)
def rolling(G_):
    out = []
    for b in (1, 2, 3):
        seen_ix = np.concatenate(blocks[:b]); test_ix = blocks[b]; best = None
        for f in FILT:
            V, keep = value(f, G_)
            for e in range(len(ENAMES)):
                ks = seen_ix[keep[seen_ix]]
                if len(ks) < 10: continue
                sc = wo2(V[ks, e])
                if best is None or sc > best[0]: best = (sc, f, e, V[ks, e].mean(), len(ks))
        if best is None: out.append(None); continue
        sc, f, e, sm, ns = best; V, keep = value(f, G_); kt = test_ix[keep[test_ix]]
        out.append(dict(f=f, e=e, seen=sm, ns=ns, blind=V[kt, e], nb=len(kt)))
    return out
# gate 1 (Nov 22): an edge without tuning: the mean of the 8 menu exits, all its coins of 0.5+ SOL, on each blind block
V1, k1 = value(("all", 0.5)); gm = [float(V1[blocks[b]][k1[blocks[b]]].mean()) * 100 if k1[blocks[b]].any() else float("nan") for b in (1, 2, 3)]
g1 = np.nanmean(gm) > 0 and sum(1 for v in gm if v > 0) >= 2
print(f"gate 1, the menu's mean exit (no picking) on the 3 blind blocks: " + " / ".join(f"{v:+.1f}%" for v in gm) + f" -> {'pass' if g1 else 'FAIL'}")
real = rolling(G)
luck = rolling(G - G.mean(0, keepdims=True))
print(f"{'blind block':>12s} {'its buys':>23s} {'picked on the blocks before':58s} {'seen':>7s} {'blind':>7s} {'n':>4s}")
for b, r_, l_ in zip((2, 3, 4), real, luck):
    if r_ is None: print(f"{b:12d}  (under 10 seen copies)"); continue
    ix = blocks[b - 1]; span = f"{dt.datetime.fromtimestamp(rows[ix[0]]['t'], dt.UTC):%m-%d %H:%M}-{dt.datetime.fromtimestamp(rows[ix[-1]]['t'], dt.UTC):%m-%d %H:%M}"
    lab = f"{ENAMES[r_['e']]}, {r_['f'][0]} coins, {r_['f'][1]}+ SOL"
    print(f"{b:12d} {span:>23s} {lab:58s} {100 * r_['seen']:+6.1f}% "
          f"{100 * r_['blind'].mean() if r_['nb'] else float('nan'):+6.1f}% {r_['nb']:4d}   (luck alone, seen: {100 * l_['seen'] if l_ else float('nan'):+.1f}%)")
ok = [r_ for r_ in real if r_ and r_["nb"]]
allb = np.concatenate([r_["blind"] for r_ in ok]) if ok else np.array([])
pos = sum(1 for r_ in ok if r_["blind"].mean() > 0)
print(f"blind, all 3 blocks: {allb.sum():+.3f} SOL on {len(allb)} copies ({100 * allb.mean() if len(allb) else float('nan'):+.1f}% a copy), "
      f"without the best 2% {wo2(allb):+.3f}; positive in {pos} of {len(ok)} blocks")
print("RESULT: " + ("PASS" if g1 and len(allb) and allb.mean() > 0 and pos >= 2 and wo2(allb) > 0 else "FAIL") + ("" if g1 else " (gate 1)"))
if os.environ.get("TABLE"):   # each menu exit on its own over the 3 blind blocks (no pick), % a copy, per quote filter
    bl = np.concatenate(blocks[1:])
    print(f"\neach exit alone on the blind blocks ({len(bl)} copies), % a copy: block 2 / 3 / 4 = all blind (n), without the best 2% in SOL")
    for kd in ("all", "SOL", "token"):
        V, keep = value((kd, 0.5))
        for e in range(len(ENAMES)):
            per = [V[blocks[b]][keep[blocks[b]], e] for b in (1, 2, 3)]; a = V[bl][keep[bl], e]
            print(f"  {kd:5s} {ENAMES[e]:52s} " + " / ".join(f"{100 * p.mean():+6.1f}" for p in per) + f" = {100 * a.mean():+6.1f}% ({len(a)})  w/o 2% {wo2(a):+.2f}")
