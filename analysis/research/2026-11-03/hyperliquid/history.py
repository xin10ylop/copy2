# Skill or the market? Each trader's whole perp history (portfolio perpAllTime: a PnL and an account-value point every
# ~10 days since it started) against BTC over the same intervals: its return in intervals when BTC rose and when it
# fell, the share of positive 30-day blocks, and how much of its result the market explains (beta, r2).
#   python3 -I history.py DATA_DIR  -> DATA_DIR/history.json and a table
import json, os, sys, bisect, statistics as st, datetime

D = sys.argv[1]; DAY = 86400 * 1000
top = json.load(open(f"{D}/top.json"))
btc = [(int(x["t"]) + DAY, float(x["c"])) for x in json.load(open(f"{D}/candles1d_BTC.json"))]
def at(p, t):
    ts = [x[0] for x in p]; i = bisect.bisect_left(ts, t)
    if i <= 0: return p[0][1]
    if i >= len(p): return p[-1][1]
    (t0, v0), (t1, v1) = p[i - 1], p[i]
    return v0 + (v1 - v0) * (t - t0) / max(1, t1 - t0)

out = []
for k, r in enumerate(top):
    a = r["ethAddress"]; pf = f"{D}/port/{a}.json"
    if not os.path.exists(pf): continue
    port = json.load(open(pf)) or []
    v = next((x for kk, x in port if kk == "perpAllTime"), None)
    if not v or len(v.get("pnlHistory") or []) < 6: continue
    pn = [(int(t), float(x)) for t, x in v["pnlHistory"]]; av = [(int(t), float(x)) for t, x in v["accountValueHistory"]]
    t0, t1 = pn[0][0], pn[-1][0]
    days = (t1 - t0) / DAY
    # 10-day steps (the series' own spacing), returns on the equity at each step's start
    steps, t = [], t0
    while t + 10 * DAY <= t1:
        e = at(av, t); dp = at(pn, t + 10 * DAY) - at(pn, t)
        b = at(btc, t + 10 * DAY) / at(btc, t) - 1 if t >= btc[0][0] else None
        if e > 1000 and b is not None: steps.append((dp / e, b, dp))
        t += 10 * DAY
    if len(steps) < 6: continue
    up = [s for s in steps if s[1] > 0]; dn = [s for s in steps if s[1] <= 0]
    xs, ys = [s[1] for s in steps], [s[0] for s in steps]
    mx, my = st.mean(xs), st.mean(ys)
    vx = sum((x - mx) ** 2 for x in xs)
    beta = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / vx if vx > 0 else 0.0
    res = [y - my - beta * (x - mx) for x, y in zip(xs, ys)]
    r2 = 1 - sum(e * e for e in res) / max(1e-18, sum((y - my) ** 2 for y in ys))
    blocks = [sum(s[2] for s in steps[i:i + 3]) for i in range(0, len(steps) - 2, 3)]   # ~30-day blocks, USD
    out.append(dict(rank=k + 1, a=a, days=days, n=len(steps), pnl_all=pn[-1][1] - pn[0][1],
                    up_n=len(up), up_ret=sum(s[0] for s in up), up_pos=sum(1 for s in up if s[0] > 0),
                    dn_n=len(dn), dn_ret=sum(s[0] for s in dn), dn_pos=sum(1 for s in dn if s[0] > 0),
                    usd_up=sum(s[2] for s in up), usd_dn=sum(s[2] for s in dn),
                    beta=beta, r2=r2, blocks_pos=sum(1 for b in blocks if b > 0), blocks=len(blocks),
                    start=datetime.datetime.fromtimestamp(t0 / 1000, datetime.UTC).strftime("%Y-%m-%d")))
json.dump(out, open(f"{D}/history.json", "w"))
print(f"{'#':>3} {'address':10} {'since':10} {'days':>4} {'allPnL $M':>9} | {'BTC up: n':>9} {'its sum':>7} {'+':>3} {'$M':>7} | {'BTC down: n':>11} {'its sum':>7} {'+':>3} {'$M':>7} | {'beta':>5} {'r2':>4} | 30d blocks +")
for o in out:
    print(f"{o['rank']:3d} {o['a'][:10]} {o['start']} {o['days']:4.0f} {o['pnl_all'] / 1e6:9.1f} | {o['up_n']:9d} {o['up_ret']:+7.0%} {o['up_pos']:3d} {o['usd_up'] / 1e6:+7.1f} | "
          f"{o['dn_n']:11d} {o['dn_ret']:+7.0%} {o['dn_pos']:3d} {o['usd_dn'] / 1e6:+7.1f} | {o['beta']:+5.1f} {o['r2']:4.2f} | {o['blocks_pos']}/{o['blocks']}")
