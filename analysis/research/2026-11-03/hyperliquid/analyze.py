# Hyperliquid top traders: is each one copyable, and is its profit skill or luck? From fetch.py's files.
# Per trader: its fills cut into position episodes (a coin's position from flat to flat; a flip closes one and opens
# the next), each with its entry, exit, hold, peak size and result after its fees. Our copy: the same episode scaled to
# a fixed peak notional STAKE (USD), every fill paid as a taker (TAKER) plus SLIP for arriving after it (both per side,
# on each fill's notional), an episode still open valued at the current mid. Periods by the episode's entry: days 1-4
# and 5-7 of the last 7 days (P1, P2), and the 3 weeks before (W1-W3). Luck checks: its result without its best 2
# episodes, its positive days of 30, the share of its best 2, its month and all-time results.
#   python3 -I analyze.py DATA_DIR [STAKE=1000] [TAKER=0.00045] [SLIP=0.0005]
import json, os, sys, glob, statistics as st, collections, urllib.request, time

D = sys.argv[1]
STAKE = float(sys.argv[2]) if len(sys.argv) > 2 else 1000.0
TAKER = float(sys.argv[3]) if len(sys.argv) > 3 else 0.00045
SLIP = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0005
DAY = 86400 * 1000
mids_f = f"{D}/mids.json"
if not os.path.exists(mids_f):
    req = urllib.request.Request("https://api.hyperliquid.xyz/info", b'{"type":"allMids"}', {"Content-Type": "application/json"})
    json.dump(json.loads(urllib.request.urlopen(req, timeout=60).read()), open(mids_f, "w"))
MIDS = {k: float(v) for k, v in json.load(open(mids_f)).items()}
top = json.load(open(f"{D}/top.json"))
def win(r, w): return next((v for k, v in r["windowPerformances"] if k == w), {})

def episodes(fills):
    """[episode] per coin from flat to flat; a fill that flips the side closes one and opens the next."""
    by = collections.defaultdict(list)
    for f in sorted(fills, key=lambda f: (f["time"], f.get("tid", 0))): by[f["coin"]].append(f)
    out = []
    for coin, fs in by.items():
        ep = None
        for f in fs:
            sz, px = float(f["sz"]), float(f["px"]); before = float(f["startPosition"])
            after = before + (sz if f["side"] == "B" else -sz)
            fee, cpnl, note = float(f.get("fee") or 0), float(f.get("closedPnl") or 0), sz * px
            if ep is None:
                ep = dict(coin=coin, t0=f["time"], pre=abs(before) > 1e-12, side=1 if (after if abs(after) > 1e-12 else before) > 0 else -1,
                          peak=abs(before) * px, pnl=0.0, fees=0.0, gross=0.0, notional=0.0, n=0, taker=0, open_sz=0.0, open_px=0.0, t1=None)
            ep["pnl"] += cpnl - fee; ep["gross"] += cpnl; ep["fees"] += fee; ep["notional"] += note; ep["n"] += 1
            ep["taker"] += 1 if f.get("crossed") else 0
            ep["peak"] = max(ep["peak"], abs(after) * px)
            if abs(after) > abs(before) and before * after >= 0:          # adds to the position
                ep["open_px"] = (ep["open_px"] * ep["open_sz"] + px * (abs(after) - abs(before))) / max(1e-12, abs(after))
                ep["open_sz"] = abs(after)
            if abs(after) < 1e-12 or before * after < 0:                   # flat, or flipped through flat
                ep["t1"] = f["time"]; out.append(ep); ep = None
                if before * after < 0:                                      # the flip opens the next episode
                    ep = dict(coin=coin, t0=f["time"], pre=False, side=1 if after > 0 else -1, peak=abs(after) * px, pnl=0.0,
                              fees=0.0, gross=0.0, notional=abs(after) * px, n=0, taker=0, open_sz=abs(after), open_px=px, t1=None)
            elif ep is not None:
                ep["pos"] = after
        if ep is not None:                                                   # still open: valued at the mid
            pos = ep.get("pos", 0.0); mid = MIDS.get(coin)
            if mid and ep["open_sz"] > 0:
                ep["unreal"] = pos * (mid - ep["open_px"]) if abs(pos) > 0 else 0.0
                ep["pnl"] += ep["unreal"]; ep["gross"] += ep["unreal"]; ep["notional"] += abs(pos) * mid  # we'd sell it too
            out.append(ep)
    return out

def ours(ep, k):
    """Our copy of an episode, its every fill scaled by the trader's fixed ratio k (live we mirror its position; we
    cannot know an episode's peak in advance), every fill a taker plus SLIP."""
    return ep["gross"] * k - ep["notional"] * k * (TAKER + SLIP)

def wo2(v): return sum(v) - sum(sorted(v)[-2:]) if len(v) > 2 else 0.0

rows = []
for k, r in enumerate(top):
    a = r["ethAddress"]; fn = f"{D}/fills/{a}.json"
    if not os.path.exists(fn): continue
    F = json.load(open(fn)); now = F["now"]; fills = F["fills"]
    av = float(r["accountValue"] or 0); wk, mo, at = win(r, "week"), win(r, "month"), win(r, "allTime")
    row = dict(rank=k + 1, a=a, name=r.get("displayName") or "", av=av, week=float(wk.get("pnl") or 0),
               week_roi=float(wk.get("roi") or 0), month=float(mo.get("pnl") or 0), allt=float(at.get("pnl") or 0),
               vlm_w=float(wk.get("vlm") or 0), nf=len(fills), trunc=F["truncated"])
    span = (now - min(f["time"] for f in fills)) / DAY if fills else 0
    row["span"] = span
    eps = [e for e in episodes(fills) if not e["pre"]]
    t7 = now - 7 * DAY
    def per(lo, hi): return [e for e in eps if lo <= e["t0"] < hi]
    P1, P2 = per(t7, t7 + 4 * DAY), per(t7 + 4 * DAY, now + 1)
    W = [per(now - (i + 1) * 7 * DAY, now - i * 7 * DAY) for i in (1, 2, 3)]
    # its own realized result by day (fills inside the window), for its positive days
    daily = collections.defaultdict(float)
    for f in fills: daily[(now - f["time"]) // DAY] += float(f.get("closedPnl") or 0) - float(f.get("fee") or 0)
    days_seen = [d for d in range(int(min(span, 30)))]
    row["pos_days"] = sum(1 for d in days_seen if daily.get(d, 0) > 0); row["days"] = len(days_seen)
    holds = [(e["t1"] - e["t0"]) / 60000 for e in eps if e["t1"]]
    rets = [e["pnl"] / e["peak"] for e in eps if e["peak"] > 0]
    coins = collections.Counter()
    for e in eps: coins[e["coin"]] += e["peak"]
    tot = sum(coins.values()) or 1
    row.update(n_ep=len(eps), n7=len(P1) + len(P2), hold_med=st.median(holds) if holds else None,
               ret_med=st.median(rets) if rets else None, taker=sum(e["taker"] for e in eps) / max(1, sum(e["n"] for e in eps)),
               coins=", ".join(f"{c} {v / tot:.0%}" for c, v in coins.most_common(3)),
               long=sum(e["peak"] for e in eps if e["side"] > 0) / tot,
               peak_med=st.median([e["peak"] for e in eps]) if eps else 0,
               its7=sum(e["pnl"] for e in P1 + P2), its7_wo2=wo2([e["pnl"] for e in P1 + P2]),
               best2_share=(sum(sorted([e["pnl"] for e in P1 + P2])[-2:]) / sum(e["pnl"] for e in P1 + P2))
               if P1 + P2 and sum(e["pnl"] for e in P1 + P2) > 0 else None)
    # the ratio: STAKE over its median peak before the scored days (its episodes before the last 7 days, else P1)
    base = [e["peak"] for e in eps if e["t0"] < t7 and e["peak"] > 0] or [e["peak"] for e in P1 if e["peak"] > 0]
    k = STAKE / st.median(base) if base else 0.0
    row["k"] = k; row["our_peak_max"] = max((e["peak"] * k for e in P1 + P2), default=0)
    for name, ps in (("P1", P1), ("P2", P2), ("W1", W[0]), ("W2", W[1]), ("W3", W[2])):
        v = [ours(e, k) for e in ps]
        row[name] = sum(v); row[name + "_n"] = len(v); row[name + "_wo2"] = wo2(v)
    rows.append(row)

json.dump(rows, open(f"{D}/analysis_{int(STAKE)}_{TAKER}_{SLIP}.json", "w"))
print(f"stake ${STAKE:,.0f} at its median trade size (fixed ratio), taker {TAKER:.3%} + slip {SLIP:.3%} a side; {len(rows)} traders")
hdr = f"{'#':>3} {'address':10} {'acct $M':>7} {'week $k':>8} {'month $k':>8} {'allT $k':>8} {'fills':>5} {'eps':>4} {'hold m':>6} {'ret':>6} {'tkr':>4} {'+days':>6} | {'P1':>7} {'P2':>7} {'P2w/o2':>7} {'W1':>7} {'W2':>7} {'W3':>7} | coins"
print(hdr)
for r in rows:
    f = lambda x: f"{x:+7.0f}"
    print(f"{r['rank']:3d} {r['a'][:10]} {r['av'] / 1e6:7.1f} {r['week'] / 1e3:8.0f} {r['month'] / 1e3:8.0f} {r['allt'] / 1e3:8.0f} "
          f"{r['nf']:5d}{'T' if r['trunc'] else ' '}{r['n_ep']:4d} {r['hold_med'] if r['hold_med'] is not None else -1:6.0f} "
          f"{(r['ret_med'] or 0):+6.1%} {r['taker']:4.0%} {r['pos_days']:2d}/{r['days']:<2d} | {f(r['P1'])} {f(r['P2'])} {f(r['P2_wo2'])} "
          f"{f(r['W1'])} {f(r['W2'])} {f(r['W3'])} | {r['coins']}")
