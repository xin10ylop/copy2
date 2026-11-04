# Hyperliquid top traders, copied by mirroring: we hold its positions scaled to our equity (k = ours / its equity), so
# over a period our result is its perp PnL (realized + unrealized, its fees and funding inside) times k, less what
# our copy pays on top of it on the same volume: a taker fee and the slippage of arriving later, minus the fee rate it
# already paid (read from its fills). Its PnL by period comes from its portfolio history (perpWeek: a point every few
# hours; perpMonth: about every 16 h), so the 10,000-fill cap does not matter. Volume by period: the week's and the
# month's totals, spread by its fills where they cover the period, else evenly.
#   python3 -I analyze2.py DATA_DIR [TAKER=0.00045] [SLIP=0.0005]
# Periods: P1 = days 1-4 of the last 7, P2 = days 5-7, W1..W3 = the 3 weeks before. Results in % of its equity.
import json, os, sys, bisect, statistics as st, collections

D = sys.argv[1]
TAKER = float(sys.argv[2]) if len(sys.argv) > 2 else 0.00045
SLIP = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0005
DAY = 86400 * 1000
top = json.load(open(f"{D}/top.json"))
def win(r, w): return next((v for k, v in r["windowPerformances"] if k == w), {})

def series(port, name):
    v = next((x for k, x in port if k == name), None)
    if not v: return [], [], 0.0
    p = [(int(t), float(x)) for t, x in v.get("pnlHistory") or []]
    a = [(int(t), float(x)) for t, x in v.get("accountValueHistory") or []]
    return p, a, float(v.get("vlm") or 0)

def at(p, t):
    """the cumulative PnL at time t (linear between points; flat outside)."""
    if not p: return 0.0
    ts = [x[0] for x in p]; i = bisect.bisect_left(ts, t)
    if i <= 0: return p[0][1]
    if i >= len(p): return p[-1][1]
    (t0, v0), (t1, v1) = p[i - 1], p[i]
    return v0 + (v1 - v0) * (t - t0) / max(1, t1 - t0)

# the market: BTC (and ETH, HYPE) from 4h candles; its move in each period, and daily moves for each trader's beta
MK = {}
for c in ("BTC", "ETH", "HYPE"):
    kk = json.load(open(f"{D}/candles_{c}.json"))
    MK[c] = [(int(x["t"]) + 4 * 3600 * 1000, float(x["c"])) for x in kk]
def mpx(c, t):
    return at(MK[c], t)

rows = []
for k, r in enumerate(top):
    a = r["ethAddress"]
    pf, ff, sf = f"{D}/port/{a}.json", f"{D}/fills/{a}.json", f"{D}/state/{a}.json"
    if not (os.path.exists(pf) and os.path.exists(ff)): continue
    port = json.load(open(pf)) or []; F = json.load(open(ff)); state = json.load(open(sf)) if os.path.exists(sf) else {}
    now = F["now"]; fills = F["fills"]; t7 = now - 7 * DAY
    pw, aw, vw = series(port, "perpWeek"); pm, am, vm = series(port, "perpMonth"); pa, aa, va = series(port, "perpAllTime")
    if not pw and not pm: continue
    eq = float(r["accountValue"] or 0) or (aw[-1][1] if aw else 0)
    if eq <= 0: continue
    # its fee rate and how its volume spreads over the periods, from its fills
    fee = sum(float(f.get("fee") or 0) for f in fills); note = sum(float(f["sz"]) * float(f["px"]) for f in fills)
    fee_rate = fee / note if note > 0 else 0.0
    f0 = min((f["time"] for f in fills), default=now)
    def vol(lo, hi):
        if fills and f0 <= lo:                         # its fills cover the period
            return sum(float(f["sz"]) * float(f["px"]) for f in fills if lo <= f["time"] < hi)
        per_day = (vw / 7) if hi > t7 else (vm / 30)  # else its window's volume, spread evenly
        return per_day * (hi - lo) / DAY
    def pnl(lo, hi):
        p = pw if lo >= pw[0][0] - 3 * 3600 * 1000 else pm if pw else pm
        return at(p, hi) - at(p, lo)
    per = {"P1": (t7, t7 + 4 * DAY), "P2": (t7 + 4 * DAY, now),
           "W1": (now - 14 * DAY, now - 7 * DAY), "W2": (now - 21 * DAY, now - 14 * DAY), "W3": (now - 28 * DAY, now - 21 * DAY)}
    out = {}
    for name, (lo, hi) in per.items():
        g, v = pnl(lo, hi), vol(lo, hi)
        cost = v * max(0.0, TAKER + SLIP - fee_rate)
        out[name] = (g / eq, (g - cost) / eq, v)          # its, ours (both in % of its equity), volume
    # days of the last 7 (perpWeek) and of the month (perpMonth), positive or not
    d7 = [at(pw, t7 + (i + 1) * DAY) - at(pw, t7 + i * DAY) for i in range(7)] if pw else []
    d30 = [at(pm, now - (i) * DAY) - at(pm, now - (i + 1) * DAY) for i in range(28)] if pm else []
    # drawdown over the month: the deepest fall of its cumulative PnL from a high, in % of equity
    dd, hi_ = 0.0, -1e30
    for t, v in pm:
        hi_ = max(hi_, v); dd = min(dd, (v - hi_) / eq)
    pos = (state or {}).get("assetPositions") or []
    ntl = sum(abs(float(p["position"].get("positionValue") or 0)) for p in pos)
    coins = collections.Counter()
    for f in fills: coins[f["coin"]] += float(f["sz"]) * float(f["px"])
    tot = sum(coins.values()) or 1
    side = collections.Counter()
    for p in pos: side["long" if float(p["position"]["szi"]) > 0 else "short"] += abs(float(p["position"].get("positionValue") or 0))
    gaps = sorted((b["time"] - a_["time"]) / 1000 for a_, b in zip(fills, fills[1:]))
    # beta to BTC from daily moves over 28 days: its daily PnL / equity against BTC's daily return
    xs = [mpx("BTC", now - i * DAY) / mpx("BTC", now - (i + 1) * DAY) - 1 for i in range(28)]
    ys = [x / eq for x in d30]
    if len(ys) == 28 and st.pvariance(xs) > 0:
        mx, my = st.mean(xs), st.mean(ys)
        beta = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
        alpha_wk = (my - beta * mx) * 7
        res = [y - (my + beta * (x - mx)) for x, y in zip(xs, ys)]
        r2 = 1 - sum(e * e for e in res) / max(1e-18, sum((y - my) ** 2 for y in ys))
    else:
        beta, alpha_wk, r2 = 0.0, 0.0, 0.0
    long_ntl = sum(abs(float(p["position"].get("positionValue") or 0)) for p in pos if float(p["position"]["szi"]) > 0)
    rows.append(dict(rank=k + 1, a=a, beta=beta, alpha_wk=alpha_wk, r2=r2, net_side=(2 * long_ntl - ntl) / eq, name=r.get("displayName") or "", eq=eq,
                     week=float(win(r, "week").get("pnl") or 0), month=float(win(r, "month").get("pnl") or 0),
                     allt=float(win(r, "allTime").get("pnl") or 0), allt_perp=pa[-1][1] if pa else None,
                     vlm_w=vw, turn_w=vw / eq, edge_bps=(pw[-1][1] - pw[0][1]) / vw * 1e4 if vw > 0 and pw else None,
                     fee_bps=fee_rate * 1e4, nf=len(fills), trunc=F["truncated"], fills_days=(now - f0) / DAY if fills else 0,
                     lev=ntl / eq, pos_side=dict(side), npos=len(pos),
                     coins=", ".join(f"{c} {v / tot:.0%}" for c, v in coins.most_common(3)),
                     gap_med=st.median(gaps) if gaps else None,
                     d7_pos=sum(1 for x in d7 if x > 0), d30_pos=sum(1 for x in d30 if x > 0), d30_n=len(d30),
                     best2_share_7d=(sum(sorted(d7)[-2:]) / sum(d7)) if d7 and sum(d7) > 0 else None,
                     dd_month=dd, **{f"{n}_its": v[0] for n, v in out.items()}, **{f"{n}_our": v[1] for n, v in out.items()},
                     **{f"{n}_vol": v[2] for n, v in out.items()}))

tag = f"{TAKER}_{SLIP}"
json.dump(rows, open(f"{D}/mirror_{tag}.json", "w"))
print(f"mirror copy, taker {TAKER:.3%} + slip {SLIP:.3%} a side less its own fee rate; {len(rows)} traders; % of its equity")
now0 = rows[0] and json.load(open(f"{D}/fills/{rows[0]['a']}.json"))["now"]
t70 = now0 - 7 * DAY
pers = {"P1": (t70, t70 + 4 * DAY), "P2": (t70 + 4 * DAY, now0), "W1": (now0 - 14 * DAY, now0 - 7 * DAY),
        "W2": (now0 - 21 * DAY, now0 - 14 * DAY), "W3": (now0 - 28 * DAY, now0 - 21 * DAY)}
print("BTC in each period: " + ", ".join(f"{n} {mpx('BTC', hi) / mpx('BTC', lo) - 1:+.1%}" for n, (lo, hi) in pers.items()))
print(f"{'#':>3} {'address':10} {'eq $M':>6} {'wk $k':>7} {'mo $k':>7} {'allT $k':>8} {'turn':>5} {'edge':>5} {'lev':>4} "
      f"{'d7+':>3} {'d30+':>5} {'ddMo':>5} | {'P1 its':>6} {'P1 our':>6} {'P2 our':>6} {'W1 our':>6} {'W2 our':>6} {'W3 our':>6} | coins")
for r in sorted(rows, key=lambda r: r["rank"]):
    print(f"{r['rank']:3d} {r['a'][:10]} {r['eq'] / 1e6:6.1f} {r['week'] / 1e3:7.0f} {r['month'] / 1e3:7.0f} {r['allt'] / 1e3:8.0f} "
          f"{r['turn_w']:5.1f} {r['edge_bps'] if r['edge_bps'] is not None else 0:5.0f} {r['lev']:4.1f} {r['d7_pos']:3d} "
          f"{r['d30_pos']:2d}/{r['d30_n']:<2d} {r['dd_month']:+5.0%} | {r['P1_its']:+6.1%} {r['P1_our']:+6.1%} {r['P2_our']:+6.1%} "
          f"{r['W1_our']:+6.1%} {r['W2_our']:+6.1%} {r['W3_our']:+6.1%} | beta {r['beta']:+5.1f} r2 {r['r2']:.2f} alpha/wk {r['alpha_wk']:+6.1%} net {r['net_side']:+4.1f} | {r['coins'][:50]}")
