# The finalists of rank.py (picked on the past, copyable, sorted by the last 28 days without the best 2 days): their
# fills of the last 30 days and current positions, then what each trades and how, and our copy's cost with its real
# fee rate at 5, 10 and 20 bp of slippage a side.
#   python3 -I finalists.py DATA_DIR [N=15]
import json, os, sys, time, urllib.request, collections, statistics as st, datetime

D = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 15
API = "https://api.hyperliquid.xyz/info"; GAP = 1.1; last = [0.0]; DAY = 86400 * 1000
def info(body):
    for i in range(8):
        dt = time.time() - last[0]
        if dt < GAP: time.sleep(GAP - dt)
        last[0] = time.time()
        try:
            req = urllib.request.Request(API, json.dumps(body).encode(), {"Content-Type": "application/json"})
            return json.loads(urllib.request.urlopen(req, timeout=60).read())
        except Exception as e:
            wait = 15 * (i + 1) if "429" in str(e) else 3 * (i + 1); time.sleep(wait)
    return None
rank = json.load(open(f"{D}/rank.json"))
# still funded (at least $100k) and trading this week (turnover at least 0.3x its equity): an emptied account's
# percentages are meaningless and it cannot be copied
fin = sorted([o for o in rank if o["pick"] and o["copyable"] and o["eq"] >= 1e5 and o["turn_w"] >= 0.3],
             key=lambda o: -o["score28_wo2"])[:N]
for sub in ("fills", "state"): os.makedirs(f"{D}/{sub}", exist_ok=True)
now = int(time.time() * 1000); start = now - 30 * DAY
res = []
for o in fin:
    a = o["a"]; ff, sf = f"{D}/fills/{a}.json", f"{D}/state/{a}.json"
    if not os.path.exists(ff):
        fills, s0 = [], start
        for page in range(5):
            f = info({"type": "userFillsByTime", "user": a, "startTime": s0, "endTime": now, "aggregateByTime": True})
            if not f: break
            fills += f
            if len(f) < 2000: break
            s0 = max(x["time"] for x in f) + 1
        json.dump({"address": a, "start": start, "now": now, "truncated": len(fills) >= 9990, "fills": fills}, open(ff, "w"))
    if not os.path.exists(sf): json.dump(info({"type": "clearinghouseState", "user": a}), open(sf, "w"))
    F = json.load(open(ff)); S = json.load(open(sf)) or {}; fills = F["fills"]
    note = sum(float(f["sz"]) * float(f["px"]) for f in fills) or 1.0
    fee = sum(float(f.get("fee") or 0) for f in fills)
    maker = sum(float(f["sz"]) * float(f["px"]) for f in fills if not f.get("crossed")) / note
    by = collections.Counter(); side = collections.Counter(); kind = collections.Counter()
    for f in fills:
        n = float(f["sz"]) * float(f["px"]); by[f["coin"]] += n
        kind["stocks/commodities (xyz:)" if f["coin"].startswith("xyz:") or ":" in f["coin"] else "spot" if f["coin"].startswith("@") or "/" in f["coin"] else "crypto perps"] += n
        d = f.get("dir") or ""
        if d.startswith("Open"): side["long" if "Long" in d else "short"] += n
    pos = S.get("assetPositions") or []
    eq = float((S.get("marginSummary") or {}).get("accountValue") or o["eq"] or 1)
    ntl = sum(abs(float(p["position"].get("positionValue") or 0)) for p in pos)
    cur = sorted(((p["position"]["coin"], float(p["position"]["szi"]), float(p["position"].get("positionValue") or 0),
                   (p["position"].get("leverage") or {}).get("value")) for p in pos), key=lambda x: -abs(x[2]))
    gaps = sorted((b["time"] - x["time"]) / 60000 for x, b in zip(fills, fills[1:]))
    days_span = (now - min((f["time"] for f in fills), default=now)) / DAY
    # its realized result by coin over the fills (closedPnl - fee): where the money comes from
    rc = collections.Counter()
    for f in fills: rc[f["coin"]] += float(f.get("closedPnl") or 0) - float(f.get("fee") or 0)
    vm = o["edge_bp"] and (o["month"] / (o["edge_bp"] / 1e4)) or 0
    res.append(dict(a=a, name=o["name"], eq=eq, fills=len(fills), trunc=F["truncated"], days=days_span,
                    fills_day=len(fills) / max(0.1, days_span), maker=maker, fee_bp=fee / note * 1e4,
                    kinds={k: v / note for k, v in kind.items()}, top=[(c, v / note) for c, v in by.most_common(5)],
                    opens_long=side["long"] / max(1, side["long"] + side["short"]), lev=ntl / eq, cur=cur[:5],
                    gap_med_min=st.median(gaps) if gaps else None, realized_by_coin=rc.most_common(3) + rc.most_common()[-2:],
                    edge_bp=o["edge_bp"], turn_w=o["turn_w"], weeks=o["weeks"], score28=o["score28"], wo2=o["score28_wo2"]))
json.dump(res, open(f"{D}/finalists.json", "w"))
for r in res:
    print(f"\n== {r['a']} {r['name']}  equity ${r['eq'] / 1e6:.2f}M, leverage now {r['lev']:.1f}x, {r['fills']} fills in {r['days']:.0f} d "
          f"({r['fills_day']:.0f}/day){' TRUNCATED' if r['trunc'] else ''}, maker {r['maker']:.0%}, its fee {r['fee_bp']:+.1f} bp")
    print("   markets: " + ", ".join(f"{k} {v:.0%}" for k, v in r["kinds"].items()) + " | top: " + ", ".join(f"{c} {v:.0%}" for c, v in r["top"]))
    print(f"   opens long {r['opens_long']:.0%} of its opening volume; median gap between fills {r['gap_med_min'] or 0:.1f} min")
    print("   now: " + "; ".join(f"{c} {'long' if s > 0 else 'short'} ${abs(v) / 1e3:,.0f}k x{lv}" for c, s, v, lv in r["cur"]))
    print("   realized by coin (30 d): " + ", ".join(f"{c} {v / 1e3:+,.0f}k" for c, v in r["realized_by_coin"]))
    for slip in (0.0005, 0.001, 0.002):
        extra = max(0.0, 0.00045 + slip - r["fee_bp"] / 1e4)
        print(f"   our copy at {slip * 1e4:.0f} bp slip: its edge {r['edge_bp']:.0f} bp a traded dollar, our extra cost "
              f"{extra * 1e4:.1f} bp -> {r['turn_w'] * extra:.1%} of equity a week")
    print("   last 4 weeks, our copy (5 bp slip, its fees as 0): " + " ".join(f"{x:+.1%}" for x in r["weeks"]) + f" = {r['score28']:+.1%}, without the best 2 days {r['wo2']:+.1%}")
