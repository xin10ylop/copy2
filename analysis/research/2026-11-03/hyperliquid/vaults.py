# Hyperliquid vaults: copying by depositing (no bot, no slippage; a user vault's leader keeps 10% of the profit).
# The open vaults with $500k+ and 180+ days, each through rank.py's tests on its own portfolio: its history before the
# last 28 days (money made both in BTC-up and BTC-down 10-day steps, positive 30-day blocks), its deepest drawdown, and
# the last 28 days week by week, after the leader's 10% (out of sample for the pick).
#   python3 -I vaults.py DATA_DIR
import json, os, sys, time, bisect, urllib.request, datetime

D = sys.argv[1]; API = "https://api.hyperliquid.xyz/info"; DAY = 86400 * 1000; last = [0.0]
def info(body):
    for i in range(8):
        dt = time.time() - last[0]
        if dt < 1.1: time.sleep(1.1 - dt)
        last[0] = time.time()
        try:
            req = urllib.request.Request(API, json.dumps(body).encode(), {"Content-Type": "application/json"})
            return json.loads(urllib.request.urlopen(req, timeout=60).read())
        except Exception as e:
            time.sleep(15 * (i + 1) if "429" in str(e) else 3 * (i + 1))
    return None
def at(p, t):
    ts = [x[0] for x in p]; i = bisect.bisect_left(ts, t)
    if i <= 0: return p[0][1]
    if i >= len(p): return p[-1][1]
    (t0, v0), (t1, v1) = p[i - 1], p[i]
    return v0 + (v1 - v0) * (t - t0) / max(1, t1 - t0)
btc = [(int(x["t"]) + DAY, float(x["c"])) for x in json.load(open(f"{D}/candles1d_BTC.json"))]
V = json.load(open(f"{D}/vault_cands.json")); out = []
d = lambda ms: datetime.datetime.fromtimestamp(ms / 1000, datetime.UTC).strftime("%Y-%m-%d")
for x in V:
    s = x["summary"]; a = s["vaultAddress"]; pf = f"{D}/port/{a}.json"
    if not os.path.exists(pf): json.dump(info({"type": "portfolio", "user": a}), open(pf, "w"))
    port = json.load(open(pf)) or []
    ser = lambda n: next((v for k, v in port if k == n), None)
    pa = ser("allTime")
    if not pa or len(pa["pnlHistory"]) < 8: continue
    pn = [(int(t), float(v)) for t, v in pa["pnlHistory"]]; av = [(int(t), float(v)) for t, v in pa["accountValueHistory"]]
    pm = ser("month"); pmn = [(int(t), float(v)) for t, v in pm["pnlHistory"]]; amn = [(int(t), float(v)) for t, v in pm["accountValueHistory"]]
    now = pmn[-1][0]; cut = now - 28 * DAY
    steps, t = [], pn[0][0]
    while t + 10 * DAY <= cut:
        e = at(av, t); dp = at(pn, t + 10 * DAY) - at(pn, t)
        if e > 1e4 and t >= btc[0][0]: steps.append((dp, dp / e, at(btc, t + 10 * DAY) / at(btc, t) - 1))
        t += 10 * DAY
    up = [q for q in steps if q[2] > 0]; dn = [q for q in steps if q[2] <= 0]
    blocks = [sum(q[0] for q in steps[i:i + 3]) for i in range(0, len(steps) - 2, 3)]
    usd_up, usd_dn = sum(q[0] for q in up), sum(q[0] for q in dn)
    pick = len(steps) >= 18 and usd_up > 0 and usd_dn > 0 and blocks and sum(1 for b in blocks if b > 0) / len(blocks) >= 0.6
    # deepest drawdown of its cumulative PnL from a high, on its largest TVL so far (from its funding)
    hi, mx, dd = None, 0.0, 0.0
    eqs = dict(av)
    for tt, v in pn:
        e = eqs.get(tt, 0.0)
        if e < 1e4 and hi is None: continue
        mx = max(mx, e); hi = v if hi is None else max(hi, v); dd = min(dd, (v - hi) / mx)
    share = 0.9 if s.get("relationship", {}).get("type") == "normal" else 1.0     # a user vault's leader keeps 10%
    weeks = []
    for i in range(4):
        lo, hi_ = cut + i * 7 * DAY, cut + (i + 1) * 7 * DAY
        e = at(amn, lo); g = at(pmn, hi_) - at(pmn, lo)
        weeks.append((g * (share if g > 0 else 1.0)) / e if e > 0 else 0.0)
    life = (now - s["createTimeMillis"]) / DAY
    yr = (pn[-1][1] - pn[0][1]) / max(1.0, st_mean := sum(v for _, v in av) / len(av)) * 365 / max(1.0, life)
    out.append(dict(name=s["name"], a=a, tvl=float(s["tvl"]), apr=float(x["apr"] or 0), life=life, pick=bool(pick),
                    usd_up=usd_up, usd_dn=usd_dn, up=f"{sum(1 for q in up if q[0] > 0)}/{len(up)}", dn=f"{sum(1 for q in dn if q[0] > 0)}/{len(dn)}",
                    blocks=f"{sum(1 for b in blocks if b > 0)}/{len(blocks)}", dd=dd, weeks=weeks, w28=sum(weeks),
                    pnl_all=pn[-1][1] - pn[0][1], yr_on_avg_tvl=yr, kind=s.get("relationship", {}).get("type")))
json.dump(out, open(f"{D}/vaults_rank.json", "w"))
print(f"{len(out)} vaults tested; picked on their history: {sum(1 for o in out if o['pick'])}")
print(f"{'vault':32} {'TVL $M':>7} {'age d':>5} {'all PnL $M':>10} {'a yr':>6} | {'BTC-up $M':>9} {'+':>5} {'BTC-dn $M':>9} {'+':>5} {'30d+':>5} {'maxDD':>6} | {'W-4':>6} {'W-3':>6} {'W-2':>6} {'W-1':>6} {'28d':>6} pick")
for o in sorted(out, key=lambda o: (-o["pick"], -o["w28"])):
    print(f"{o['name'][:32]:32} {o['tvl'] / 1e6:7.2f} {o['life']:5.0f} {o['pnl_all'] / 1e6:10.2f} {o['yr_on_avg_tvl']:+6.0%} | {o['usd_up'] / 1e6:+9.2f} {o['up']:>5} {o['usd_dn'] / 1e6:+9.2f} {o['dn']:>5} {o['blocks']:>5} {o['dd']:+6.0%} | "
          + " ".join(f"{w:+6.1%}" for w in o["weeks"]) + f" {o['w28']:+6.1%} {'YES' if o['pick'] else ''}")
