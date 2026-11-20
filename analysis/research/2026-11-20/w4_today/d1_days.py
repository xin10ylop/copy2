# Wallet 4 day by day (Nov 20; the owner: "what is happening today with wallet 4? check his trades"). Its own pump curve
# trades from the chain (candidates/c1_fetch.py, SUB=w4today, 1.9 days), each priced in SOL at Jupiter's rate of its quote
# token when fetched (Nov 20 ~20:30 UTC; floats move a little within a day). Per coin: what it put in, what it took out,
# when it first sold; per UTC day: coins, its copyable ones (first buy 1.3+ SOL), its own result on them.
#   python3 -I d1_days.py SP > out/d1_days.txt
import sys, json, collections, datetime as dt, numpy as np
SP = sys.argv[1]; SOLM = "So11111111111111111111111111111111111111112"
rows = [json.loads(l) for l in open(f"{SP}/w4today/H9kuqGKN_trades.jsonl")]
P = json.load(open(f"{SP}/w4today/prices.json")); sol_usd = P[SOLM]["usdPrice"]
def lam(q, quote):   # lamports per the trade's quote amount
    if not quote or quote.startswith("1111") or quote == SOLM: return q
    p = P.get(quote)
    return None if not p else q * p["usdPrice"] / sol_usd * 1e9 / 10 ** p["decimals"]
C = collections.defaultdict(list)
for r in rows:
    for e in (r["trades"] or []): C[e["m"]].append(e)
coins = []
for m, es in C.items():
    es.sort(key=lambda e: (e["slot"], not e["buy"]))
    if not es[0]["buy"]: continue                       # bought before the window
    v = [lam(e["q"], e["quote"]) for e in es]
    if any(x is None for x in v): continue
    b = [(e, x) for e, x in zip(es, v) if e["buy"]]; s = [(e, x) for e, x in zip(es, v) if not e["buy"]]
    tb = sum(e["tok"] for e, _ in b); ts = sum(e["tok"] for e, _ in s)
    first_sale = (s[0][0]["t"] - es[0]["t"]) if s else None
    coins.append(dict(m=m, t=es[0]["t"], first=b[0][1] / 1e9, inn=sum(x for _, x in b) / 1e9, out=sum(x for _, x in s) / 1e9,
                      holding=ts < 0.99 * tb, first_sale=first_sale, quote=(es[0]["quote"] or "SOL")[:8]))
day = lambda t: dt.datetime.fromtimestamp(t, dt.UTC).strftime("%m-%d")
print(f"wallet 4, {len(coins)} coins it opened from {dt.datetime.fromtimestamp(min(c['t'] for c in coins), dt.UTC):%m-%d %H:%M} to "
      f"{dt.datetime.fromtimestamp(max(c['t'] for c in coins), dt.UTC):%m-%d %H:%M} UTC; SOL ${sol_usd:.2f}")
for d in sorted({day(c["t"]) for c in coins}):
    for name, sel in (("all", lambda c: True), ("copyable (1.3+ SOL)", lambda c: c["first"] >= 1.3)):
        x = [c for c in coins if day(c["t"]) == d and sel(c)]; cl = [c for c in x if not c["holding"]]
        if not x: continue
        pnl = [c["out"] - c["inn"] for c in cl]; pct = [100 * (c["out"] / c["inn"] - 1) for c in cl]
        early = [c for c in cl if c["first_sale"] is not None and c["first_sale"] < 290]
        print(f"{d} {name:20s}: {len(x):4d} coins, {sum(c['inn'] for c in x):7.2f} SOL in; closed {len(cl):4d}: {sum(pnl):+7.2f} SOL "
              f"({np.mean(pct) if pct else 0:+.1f}% a coin, median {np.median(pct) if pct else 0:+.1f}%), won {sum(1 for p in pnl if p > 0)}, "
              f"first sale under 290 s {len(early)} ({100 * len(early) / max(1, len(cl)):.0f}%); still holding {len(x) - len(cl)}")
print("\ntoday's copyable coins, in order (its own result):")
for c in sorted((c for c in coins if day(c["t"]) == max(day(c['t']) for c in coins) and c["first"] >= 1.3), key=lambda c: c["t"]):
    r = "holding" if c["holding"] else f"{100 * (c['out'] / c['inn'] - 1):+7.1f}%  {c['out'] - c['inn']:+.3f} SOL"
    fs = f"{c['first_sale']:>5d}s" if c["first_sale"] is not None else "    -"
    print(f"  {dt.datetime.fromtimestamp(c['t'], dt.UTC):%H:%M:%S} {c['m'][:8]} {c['quote']:8s} first {c['first']:5.2f} in {c['inn']:6.2f}  first sale {fs}  {r}")
# SOL coins (its own buys on SOL-quoted curves; the bot never copies them, docs/20: a SolBuy is not a trigger) against
# token coins (what the bot copies), its copyable size
print("\nby the coin's quote, copyable (1.3+ SOL), its own result:")
for d in sorted({day(c["t"]) for c in coins}):
    for name, sel in (("SOL coins", lambda c: c["quote"].startswith("1111")), ("token coins", lambda c: not c["quote"].startswith("1111"))):
        x = [c for c in coins if day(c["t"]) == d and c["first"] >= 1.3 and sel(c) and not c["holding"]]
        if not x: continue
        pnl = [c["out"] - c["inn"] for c in x]
        print(f"  {d} {name:11s}: {len(x):3d} closed, {sum(pnl):+7.2f} SOL ({100 * np.mean([c['out'] / c['inn'] - 1 for c in x]):+.1f}% a coin), won {sum(1 for p in pnl if p > 0)}")
