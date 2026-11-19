# Are the first live results normal? (Nov 19; the owner: "are the results normal?") For every live trade of rh-copier
# (our buys and sales read from the chain, the wallet as in the journal): (1) the backtest model on the SAME coin, under
# the live settings, at the backtest's landings (2, 3, 5 blocks after its buy) and at our real landing; against what we
# really got. (2) How often the backtest's own copies lose this much: 13 copies drawn from each wallet's backtest
# copies (rhd3's method), the live mix of wallets, 100,000 draws.
#   python3 -I rhd6_live_vs_model.py DIR > out/rhd6_live_vs_model.txt
import sys, os, collections, numpy as np, datetime as dt
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here); import rhd_lib as R
D = sys.argv[1]; DATA = R.Data(D)
ME = "0x35bb5c55a531d14213380fd978a501f0e239a77e"
W = {1: ("0x9a3955a122ab8a649a8511df2dce169471fd0ec1", 0.1, 0.5, 1.5, (R.TP.index(4), R.HOLD.index(600), 0, 0, 0)),
     2: ("0x5bc235acecff3dde394f4bfc696f7c35efd502f0", 0.05, 0, 1.5, (R.TP.index(3.5), R.HOLD.index(600), R.SPS.index((10, 30)), 0, 0)),
     3: ("0xc54d3914f91f984d61b63d491f38934c4e706b79", 0.03, 0, 1e9, (R.TP.index(2.5), R.HOLD.index(300), R.SPS.index((8, 60)), R.STALL.index(240), 0))}
# the journal's trades: id -> (wallet, the curve's first 10 characters)
J = {1: (1, "0x5b0e4f50"), 2: (3, "0xadd10db6"), 3: (1, "0x69bae698"), 4: (3, "0x3a227ce5"), 5: (2, "0x11efe1a6"), 6: (3, "0x4196e3bb"), 7: (2, "0xb09c7168"),
     8: (2, "0xc6664449"), 9: (2, "0x2ff7d4b7"), 10: (2, "0x69453a1c"), 11: (1, "0xc983a044"), 12: (2, "0x4ff3da98"), 13: (1, "0xca5c7f4b"), 14: (2, "0x7bf345a4")}
curves = {cv: c for c in DATA.TR for cv in [c[:10]]}
def val(tr, k, j_list, w):
    _, mn, mx, lim, ix = W[w]; out = []
    for j in j_list:
        if j is None: out.append(np.nan); continue
        p = R.H.prep(tr, k, R.RATE, j - k, pmax=1000); p["rate"] = R.RATE; prem = (tr[k]["vt"] / p["ent"][0]) ** 2
        out.append(((R.copy_vals(p) - R.COST)[ix] if prem <= lim else -0.0004) / R.RATE)
    return out
print(f"{'#':>2} {'w':>1} {'coin':10s} {'its blk':>10s} {'lag':>4s} {'model +2/+3/+5 blocks (mean)':>30s} {'model at our landing':>21s} {'LIVE':>9s}")
live_tot = mod_tot = mod_ours_tot = 0.0; n = 0
for i, (w, c10) in J.items():
    cv = curves.get(c10)
    if not cv or cv not in DATA.L: print(f"{i:>2} {w} {c10}: not in the data"); continue
    tr = DATA.path(cv); addr = W[w][0]
    j_our = next((j for j, e in enumerate(tr) if e["user"] == ME and e["buy"]), None)
    sale = next((e for e in tr if e["user"] == ME and not e["buy"]), None)
    k = max((j for j, e in enumerate(tr) if e["user"] == addr and e["buy"] and (j_our is None or j < j_our)), default=None)
    if k is None: print(f"{i:>2} {w} {c10}: its buy not found"); continue
    m = val(tr, k, R.landings(tr, k), w)
    if j_our is None:   # our buy reverted: what the price had done by then
        print(f"{i:>2} {w} {c10} {tr[k]['slot']:>10d}  our buy reverted; model +2/+3/+5: " + " / ".join(f"{x / 0.02 * 100:+.0f}%" if not np.isnan(x) else "-" for x in m)
              + f"; the price 2/3/5 blocks after its buy: " + " / ".join(f"{(tr[k]['vt'] / tr[j]['vt']) ** 2:.2f}x" if j is not None else "-" for j in R.landings(tr, k)))
        continue
    mo = val(tr, k, [j_our - 1], w)[0]
    # what we really got: our sale's net quote out minus 0.02 (gas is apart)
    live = (sale["q"] / 1e9 - 0.02) if sale else {14: -0.00788}.get(i, np.nan)   # #14's sale came after the data: the journal's net
    n += 1; live_tot += live; mod_tot += np.nanmean(m); mod_ours_tot += mo
    print(f"{i:>2} {w} {c10} {tr[k]['slot']:>10d} {tr[j_our]['slot'] - tr[k]['slot']:>4d} {' / '.join(f'{x / 0.02 * 100:+5.0f}%' for x in m):>22s} ({np.nanmean(m) / 0.02 * 100:+4.0f}%) {mo / 0.02 * 100:+20.1f}% {live / 0.02 * 100:+8.1f}%")
print(f"\n{n} closed trades: LIVE {live_tot:+.4f} ETH ({live_tot / n / 0.02 * 100:+.1f}% a copy) | model at our landing {mod_ours_tot:+.4f} ({mod_ours_tot / n / 0.02 * 100:+.1f}%) | model at +2/+3/+5 {mod_tot:+.4f} ({mod_tot / n / 0.02 * 100:+.1f}%)")
# (3) every exit audited: from the chain, when each rule of the live settings first fires (the others' trades only,
# as the bot counts them: sales minus buys over the window, from `from` s; take profit and stall on its price), against
# the exit the bot took (its sale's time after its buy)
SP_ = {1: None, 2: (10, 30, 30), 3: (8, 60, 30)}; ST_ = {1: 0, 2: 0, 3: 240}; TPX = {1: 4.0, 2: 3.5, 3: 2.5}; HOLDS = {1: 600, 2: 600, 3: 300}
print("\nEXITS AUDITED (age = seconds after its buy):")
print(f"{'#':>2} {'w':>1} {'bot: exit at age':>22s} | {'rules, first firing':>58s} | {'max net sales in a window':>26s}")
for i, (w, c10) in J.items():
    cv = curves.get(c10)
    if i == 7 or not cv or cv not in DATA.L: continue
    tr = DATA.path(cv); addr = W[w][0]; t0 = None
    j_our = next((j for j, e in enumerate(tr) if e["user"] == ME and e["buy"]), None)
    s_i = next((j for j, e in enumerate(tr) if e["user"] == ME and not e["buy"]), None)
    k = max((j for j, e in enumerate(tr) if e["user"] == addr and e["buy"] and j < j_our), default=None)
    if k is None or j_our is None: continue
    t0 = tr[k]["t"]; vtk = tr[k]["vt"]; after = [e for e in tr[j_our + 1:]]
    fire = {}
    # take profit
    for e in after:
        if (vtk / e["vt"]) ** 2 >= TPX[w]: fire["take_profit"] = e["t"] - t0; break
    # sell pressure: others' sales minus buys over the window, from `from`
    best = 0
    if SP_[w]:
        n_, win, fr = SP_[w]; others = [(e["t"], not e["buy"]) for e in tr[k + 1:] if e["user"] not in (addr, ME)]
        for e in after:
            a = e["t"] - t0; wnd = [s_ for t_, s_ in others if e["t"] - win <= t_ <= e["t"]]; net = sum(1 if s_ else -1 for s_ in wnd)
            if a >= fr: best = max(best, net)
            if a >= fr and net >= n_ and "sell_pressure" not in fire: fire["sell_pressure"] = a
    # stall: no new high (on its price) for ST_ s, once at its price or above
    if ST_[w]:
        pk, hi_t = 1.0, t0
        for e in after:
            px = (vtk / e["vt"]) ** 2
            if px > pk: pk, hi_t = px, e["t"]
            if pk >= 1.0 and e["t"] - hi_t >= ST_[w]: fire["stall"] = e["t"] - t0; break
    fire["time"] = HOLDS[w]
    first = min(fire.items(), key=lambda x: x[1])
    bot = (tr[s_i]["t"] - t0) if s_i is not None else None
    print(f"{i:>2} {w} {('sold at ' + format(bot, '.0f') + ' s') if bot is not None else 'sale after the data':>22s} | first: {first[0]} at {first[1]:.0f} s; "
          + ", ".join(f"{k_} {v:.0f}" for k_, v in sorted(fire.items(), key=lambda x: x[1]) if k_ != first[0])[:40].ljust(40) + f" | {best if SP_[w] else '-':>26}")
# (2) the backtest's own spread: each wallet's copies over the data (rhd3's method), the live mix
mix = collections.Counter(w for i, (w, _) in J.items() if i != 7)
pool = {}
for w, (addr, mn, mx, lim, ix) in W.items():
    xs = []
    for c in DATA.L:
        if c not in DATA.TR or not any(x[3] == addr and x[2] for x in DATA.TR[c]): continue
        tr = DATA.path(c); k = next((j for j, e in enumerate(tr) if e["user"] == addr and e["buy"]), None)
        if k is None or tr[k]["q"] / 1e9 < mn or tr[k]["t"] > DATA.t_end - 600: continue
        before = (tr[k - 1]["vq"] / 1e9 - R.V0) if k else 0.0
        if (mx and before >= mx) or tr[k]["vq"] / 1e9 - R.V0 >= 3.8: continue
        xs.append(np.nanmean(val(tr, k, R.landings(tr, k), w)))
    pool[w] = np.array([x for x in xs if not np.isnan(x)])
    print(f"wallet {w}: {len(pool[w])} backtest copies, {pool[w].mean() / 0.02 * 100:+.1f}% a copy, won {100 * np.mean(pool[w] > 0):.0f}%")
rng = np.random.default_rng(7); S = sum(rng.choice(pool[w], size=(100_000, k_)).sum(1) for w, k_ in mix.items())
print(f"\nthe live mix ({dict(mix)}): 100,000 draws of the backtest's copies; P(sum <= live {live_tot:+.4f}) = {100 * np.mean(S <= live_tot):.1f}%; "
      f"the median draw {np.median(S):+.4f} ETH; 10% of draws below {np.percentile(S, 10):+.4f}; P(2 or fewer winners of {n}) = "
      f"{100 * np.mean(sum((rng.choice(pool[w], size=(100_000, k_)) > 0).sum(1) for w, k_ in mix.items()) <= 2):.1f}%")
