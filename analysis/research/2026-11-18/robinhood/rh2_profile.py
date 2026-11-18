# Wallet 4's look-alikes on Robinhood Chain's Pons launchpad (Nov 18): every wallet's OWN curve trading over the days
# fetched by rh1 (no copy model yet), its first buys of MINQ+ ETH on ETH-quoted coins. As p1_profile.py on Solana:
# coins, ETH in, its own result (sales + what it still holds at the coin's last curve price, 0.9 of it; a coin that
# graduated is marked at its last curve price), without its best 2 coins, coins won, days active / positive, the median
# hold (first buy to first sale), the share of sales on one fixed delay (a timer bot), the share sold within 10 s, the
# share bought within 10 s of the launch. Week 1 and week 2 are shown apart: a wallet found on week 1 must hold on week 2.
#   python3 -I rh2_profile.py DIR [MINQ] > out/rh2_profile.txt
import sys, os, json, gzip, glob, bisect, collections, statistics as st, datetime as dt
D = sys.argv[1]; MINQ = float(sys.argv[2]) if len(sys.argv) > 2 else 0.05
T = json.load(open(f"{D}/topics.json")); B = {int(k): v for k, v in json.load(open(f"{D}/blocks.json")).items()}; bk = sorted(B)
WETH = "0x0bd7d308f8e1639fab988df18a8011f41eacad73"; ZERO = "0x" + "0" * 40; FACTORY = "0x7ed598bcef8bd9edd8c97a195c6d13f40801ec7e"
def tm(n):   # block -> unix time, linear between the sampled blocks
    i = bisect.bisect_left(bk, n); i = min(max(i, 1), len(bk) - 1); a, b = bk[i - 1], bk[i]
    return B[a] + (B[b] - B[a]) * (n - a) / max(1, b - a)
addr = lambda h: "0x" + h[-40:]; words = lambda d: [int(d[2 + 64 * i: 2 + 64 * (i + 1)], 16) for i in range((len(d) - 2) // 64)]
L, TR, GRAD = {}, collections.defaultdict(list), {}
SEEN = set()
for f in glob.glob(f"{D}/logs_*.json.gz"):
    for l in json.load(gzip.open(f)):
        if (l["blockNumber"], l["logIndex"]) in SEEN: continue   # overlapping chunks (a later fetch from a newer tip)
        SEEN.add((l["blockNumber"], l["logIndex"])); t0, n = l["topics"][0], int(l["blockNumber"], 16)
        if t0 == T["TokenLaunched"]:
            w = words(l["data"])
            if l["address"].lower() != FACTORY or len(w) < 3: continue   # the same event name from another launchpad
            L[addr(l["topics"][2])] = dict(token=addr(l["topics"][1]), pair="0x%040x" % w[0], n=n, thr=w[2])
        elif t0 == T["LaunchSwept"]: GRAD[addr(l["topics"][1])] = n
        elif t0 in (T["CurveBuy"], T["CurveSell"]):
            w = words(l["data"]); buy = t0 == T["CurveBuy"]
            TR[l["address"].lower()].append(dict(n=n, i=int(l["logIndex"], 16), buy=buy, u=addr(l["topics"][2] if buy else l["topics"][1]),
                                                 q=w[0] / 1e18 if buy else w[1] / 1e18, tok=(w[1] if buy else w[0]) / 1e18))
pairs = collections.Counter(x["pair"] for x in L.values()); print(f"{len(L)} launches in the window, quoted in: {pairs.most_common(6)}")
ETHQ = {c for c, x in L.items() if x["pair"] in (ZERO, WETH)}
t_all = [tm(e["n"]) for c in TR for e in TR[c]]; t0, t1 = min(t_all), max(t_all); tmid = t0 + (t1 - t0) / 2
print(f"{sum(len(v) for v in TR.values())} curve trades on {len(TR)} curves, {dt.datetime.fromtimestamp(t0, dt.UTC):%m-%d %H:%M} to {dt.datetime.fromtimestamp(t1, dt.UTC):%m-%d %H:%M} UTC; ETH-quoted curves launched in the window: {len(ETHQ)}")
W = collections.defaultdict(list)
for c, tr in TR.items():
    if c not in ETHQ: continue
    tr.sort(key=lambda e: (e["n"], e["i"])); last = tr[-1]; px = (last["q"] / last["tok"]) if last["tok"] else 0
    led = {}
    for e in tr:
        d = led.get(e["u"])
        if d is None:
            if not e["buy"]: continue
            d = led[e["u"]] = dict(n=e["n"], inn=0.0, out=0.0, tok=0.0, fs=None)
        if e["buy"]: d["inn"] += e["q"]; d["tok"] += e["tok"]
        else:
            d["out"] += e["q"]; d["tok"] -= e["tok"]
            if d["fs"] is None: d["fs"] = e["n"]
    ln = L[c]["n"]
    for u, d in led.items():
        if d["inn"] < MINQ or tm(last["n"]) - tm(d["n"]) < 600: continue
        W[u].append(dict(t=tm(d["n"]), inn=d["inn"], pnl=d["out"] + max(0, d["tok"]) * px * 0.9 - d["inn"], hold=(tm(d["fs"]) - tm(d["n"])) if d["fs"] else None,
                         early=tm(d["n"]) - tm(ln) <= 10))
def prof(cs):
    if not cs: return None
    p = sorted((c["pnl"] for c in cs), reverse=True); h = [c["hold"] for c in cs if c["hold"] is not None]; days = collections.defaultdict(float)
    for c in cs: days[dt.datetime.fromtimestamp(c["t"], dt.UTC).strftime("%m-%d")] += c["pnl"]
    mode = collections.Counter(round(x / 10) for x in h).most_common(1)
    return dict(n=len(cs), inn=sum(c["inn"] for c in cs), pnl=sum(p), pnl2=sum(p[2:]), won=sum(x > 0 for x in p) / len(p), days=len(days), dpos=sum(v > 0 for v in days.values()),
                hold=st.median(h) if h else None, timer=mode[0][1] / len(h) if h else 0, quick=sum(x <= 10 for x in h) / len(h) if h else 0, early=sum(c["early"] for c in cs) / len(cs))
def line(u, r, r1, r2):
    f = lambda x: f"{x['n']:3d} {x['pnl']:+7.3f}" if x else "  0        "
    return (f"{u[:10]} {r['n']:4d} {r['inn']:7.2f} {r['pnl']:+7.3f} {r['pnl2']:+7.3f} {100 * r['won']:4.0f}% {r['days']:2d}/{r['dpos']:<2d} {r['hold'] if r['hold'] is not None else -1:6.0f} "
            f"{100 * r['timer']:4.0f}% {100 * r['quick']:4.0f}% {100 * r['early']:4.0f}% | wk1 {f(r1)} | wk2 {f(r2)}")
hdr = "wallet     coins  ETH in  result  w/o 2  won days/+ hold_s timer <=10s launch| week 1: coins result | week 2: coins result"
P = {u: prof(cs) for u, cs in W.items() if len(cs) >= 5}
like = {u: r for u, r in P.items() if r["n"] >= 15 and r["days"] >= 4 and r["pnl"] > 0 and r["pnl2"] > 0 and r["dpos"] >= r["days"] / 2 and r["hold"] is not None
        and 30 <= r["hold"] <= 1800 and r["timer"] < 0.5 and r["quick"] < 0.15}
print(f"\n{len(W)} wallets with a first buy of {MINQ}+ ETH on an ETH-quoted Pons coin; {len(P)} with 5+ coins")
print(f"\nWALLET-4-LIKE ({len(like)}): 15+ coins on 4+ days, own result positive with and without its best 2 coins, positive on half its days or more, holds 30-1800 s, no fixed timer, under 15% sold within 10 s; by the result without its best 2:\n" + hdr)
for u, r in sorted(like.items(), key=lambda x: -x[1]["pnl2"])[:40]:
    print(line(u, r, prof([c for c in W[u] if c["t"] < tmid]), prof([c for c in W[u] if c["t"] >= tmid])))
print("\nFOR SCALE, the 15 biggest own results among wallets with 15+ coins (no behaviour filter):\n" + hdr)
for u, r in sorted([(u, r) for u, r in P.items() if r["n"] >= 15], key=lambda x: -x[1]["pnl2"])[:15]:
    print(line(u, r, prof([c for c in W[u] if c["t"] < tmid]), prof([c for c in W[u] if c["t"] >= tmid])))
json.dump({u: W[u] for u in like}, open(f"{D}/like.json", "w"))
