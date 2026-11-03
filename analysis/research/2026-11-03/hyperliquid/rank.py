# Rank the candidates by the owner's process. Picked on the past, scored on the last 28 days:
#   PICK (its perpAllTime history up to 28 days ago): at least 180 days, money made both in the 10-day steps when BTC
#     rose and in those when it fell, at least 60% positive 30-day blocks.
#   COPYABLE: its month PnL per traded dollar at least 3x our cost (taker + slip = 9.5 bp: >= 30 bp), and weekly turnover
#     (volume / equity) at most 50.
#   SCORE (the last 28 days, out of sample for the pick): our mirror copy week by week, its perp PnL less our cost on
#     its volume (taker + slip, its own fees assumed 0: conservative), in % of its equity at each week's start; the
#     28 days without the best 2 days; positive weeks.
#   python3 -I rank.py DATA_DIR [TAKER=0.00045] [SLIP=0.0005]
import json, os, sys, bisect, statistics as st

D = sys.argv[1]; DAY = 86400 * 1000
COST = (float(sys.argv[2]) if len(sys.argv) > 2 else 0.00045) + (float(sys.argv[3]) if len(sys.argv) > 3 else 0.0005)
cands = json.load(open(f"{D}/cands.json"))
# LINKS=1: rank the addresses found by track.py (sub-accounts, counterparties, vaults) instead; their rows are built
# from the leaderboard when they are on it, else from their own portfolio
OUT = "rank.json"
if os.environ.get("LINKS") == "1":
    lb = {r["ethAddress"].lower(): r for r in json.load(open(f"{D}/leaderboard.json"))["leaderboardRows"]}
    links = json.load(open(f"{D}/links.json")); seen = set(); cands = []
    for src, b, rel, o_, i_ in links:
        if not b.startswith("0x") or b in seen: continue
        seen.add(b)
        row = dict(lb.get(b) or {"ethAddress": b, "accountValue": "0", "windowPerformances": [], "displayName": None})
        row["ethAddress"] = b; row["_from"] = src; row["_rel"] = rel; row["_out"] = o_; row["_in"] = i_
        cands.append(row)
    OUT = "rank_links.json"
btc = [(int(x["t"]) + DAY, float(x["c"])) for x in json.load(open(f"{D}/candles1d_BTC.json"))]
def at(p, t):
    ts = [x[0] for x in p]; i = bisect.bisect_left(ts, t)
    if i <= 0: return p[0][1]
    if i >= len(p): return p[-1][1]
    (t0, v0), (t1, v1) = p[i - 1], p[i]
    return v0 + (v1 - v0) * (t - t0) / max(1, t1 - t0)
def ser(port, name):
    v = next((x for k, x in port if k == name), None)
    if not v: return [], [], 0.0
    return ([(int(t), float(x)) for t, x in v.get("pnlHistory") or []],
            [(int(t), float(x)) for t, x in v.get("accountValueHistory") or []], float(v.get("vlm") or 0))
def wv(r, k):
    v = dict(r["windowPerformances"]).get(k, {})
    return float(v.get("pnl") or 0), float(v.get("vlm") or 0)

out = []
for r in cands:
    a = r["ethAddress"]; pf = f"{D}/port/{a}.json"
    if not os.path.exists(pf): continue
    port = json.load(open(pf)) or []
    pa, aa, _ = ser(port, "perpAllTime"); pm, am, vm = ser(port, "perpMonth"); pw, aw, vw = ser(port, "perpWeek")
    if len(pa) < 8 or len(pm) < 8: continue
    now = pm[-1][0]; cut = now - 28 * DAY
    # PICK on its history before the cut
    steps, t = [], pa[0][0]
    while t + 10 * DAY <= cut:
        e = at(aa, t); dp = at(pa, t + 10 * DAY) - at(pa, t)
        if e > 1000 and t >= btc[0][0]: steps.append((dp, dp / e, at(btc, t + 10 * DAY) / at(btc, t) - 1))
        t += 10 * DAY
    hist_days = (cut - pa[0][0]) / DAY
    up = [s for s in steps if s[2] > 0]; dn = [s for s in steps if s[2] <= 0]
    blocks = [sum(s[0] for s in steps[i:i + 3]) for i in range(0, len(steps) - 2, 3)]
    usd_up, usd_dn = sum(s[0] for s in up), sum(s[0] for s in dn)
    pick = (hist_days >= 180 and usd_up > 0 and usd_dn > 0 and blocks and sum(1 for b in blocks if b > 0) / len(blocks) >= 0.6)
    # COPYABLE: from its month (perp PnL per volume) and week turnover
    eq = am[-1][1] if am else float(r["accountValue"] or 0)
    if not r.get("windowPerformances"): r["windowPerformances"] = [["allTime", {"pnl": str(pa[-1][1] - pa[0][1])}], ["month", {"pnl": str(pm[-1][1] - pm[0][1])}]]
    m_pnl = pm[-1][1] - pm[0][1]
    edge_bp = m_pnl / vm * 1e4 if vm > 0 else 0.0
    turn_w = vw / eq if eq > 0 else 0.0
    copyable = edge_bp >= 3 * COST * 1e4 and turn_w <= 50
    # SCORE on the last 28 days: 4 weeks, each its PnL less our cost on its volume (spread evenly), on its equity
    per_day_vol = vm / 30
    weeks = []
    for i in range(4):
        lo, hi = cut + i * 7 * DAY, cut + (i + 1) * 7 * DAY
        e = at(am, lo); g = at(pm, hi) - at(pm, lo)
        weeks.append(((g - per_day_vol * 7 * COST) / e) if e > 0 else 0.0)
    days = []
    for i in range(28):
        lo = cut + i * DAY; e = at(am, lo)
        days.append(((at(pm, lo + DAY) - at(pm, lo)) - per_day_vol * COST) / e if e > 0 else 0.0)
    d_sorted = sorted(days)
    out.append(dict(a=a, frm=r.get("_from"), rel=r.get("_rel"), moved_out=r.get("_out"), moved_in=r.get("_in"),
                    name=r.get("displayName") or "", eq=eq, allt=wv(r, "allTime")[0], month=wv(r, "month")[0],
                    hist_days=hist_days, n_steps=len(steps), usd_up=usd_up, usd_dn=usd_dn, up_n=len(up), dn_n=len(dn),
                    up_pos=sum(1 for s in up if s[0] > 0), dn_pos=sum(1 for s in dn if s[0] > 0),
                    blocks_pos=sum(1 for b in blocks if b > 0), blocks=len(blocks), pick=bool(pick),
                    edge_bp=edge_bp, turn_w=turn_w, copyable=bool(copyable),
                    weeks=weeks, w_pos=sum(1 for x in weeks if x > 0), score28=sum(weeks),
                    score28_wo2=sum(days) - sum(d_sorted[-2:]), days_pos=sum(1 for x in days if x > 0)))
json.dump(out, open(f"{D}/{OUT}", "w"))
n_pick = sum(1 for o in out if o["pick"]); n_both = sum(1 for o in out if o["pick"] and o["copyable"])
print(f"{len(out)} scored; picked on the past {n_pick}; picked and copyable {n_both}; our cost {COST * 1e4:.1f} bp a side")
print(f"{'address':12} {'name':14} {'eq $M':>6} {'allT $M':>7} {'hist d':>6} {'BTC-up $M (+/n)':>16} {'BTC-dn $M (+/n)':>16} {'30d+':>5} | {'edge bp':>7} {'turn/wk':>7} | {'W-4':>6} {'W-3':>6} {'W-2':>6} {'W-1':>6} {'28d':>6} {'w/o2d':>6} {'d+':>5}")
for o in sorted([o for o in out if o["pick"] and o["copyable"]], key=lambda o: -o["score28_wo2"]):
    print(f"{o['a'][:12]} {o['name'][:14]:14} {o['eq'] / 1e6:6.2f} {o['allt'] / 1e6:7.1f} {o['hist_days']:6.0f} "
          f"{o['usd_up'] / 1e6:+7.2f} ({o['up_pos']:2d}/{o['up_n']:2d}) {o['usd_dn'] / 1e6:+7.2f} ({o['dn_pos']:2d}/{o['dn_n']:2d}) {o['blocks_pos']:2d}/{o['blocks']:<2d} | "
          f"{o['edge_bp']:7.0f} {o['turn_w']:7.1f} | " + " ".join(f"{x:+6.1%}" for x in o["weeks"]) +
          f" {o['score28']:+6.1%} {o['score28_wo2']:+6.1%} {o['days_pos']:2d}/28")
