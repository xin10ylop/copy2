# Wallet 4's own result over the last 7 days, from its transactions in SPD/w4tx: per coin, SOL (and wSOL) out on its
# buys and back on its sales, fees and tips included. WBTC that moves in the same transactions (it often buys or sells
# through its WBTC float) is valued at the median rate of its own SOL<->WBTC swaps that week (8,442 lamports a unit,
# range 8,336-8,866). Coins where another token is left over (the quote token) are counted apart.
#   python3 -I his_week.py SPD
import json, os, sys, datetime, statistics
SPD = sys.argv[1]; W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
WSOL = "So11111111111111111111111111111111111111112"; WB = "3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh"
rows = json.load(open(f"{SPD}/routable.json")); END = max(r["t"] for r in rows); T0 = END - 7 * 86400
copied = {r["mint8"] for r in rows if T0 <= r["t"] <= END and r["ok"]}
txs = []; rates = []
for f in os.listdir(f"{SPD}/w4tx"):
    t = json.load(open(f"{SPD}/w4tx/{f}")); m = t["meta"]
    if m.get("err") or not (T0 - 86400 <= t["blockTime"] <= END + 86400): continue
    ks = t["transaction"]["message"]["accountKeys"] + sum(((m.get("loadedAddresses") or {}).get(x, []) for x in ("writable", "readonly")), [])
    if W4 not in ks: continue
    i = ks.index(W4)
    def tb(w):
        d = {}
        for b in m.get(w) or []:
            if b.get("owner") == W4: d[b["mint"]] = d.get(b["mint"], 0) + int(b["uiTokenAmount"]["amount"])
        return d
    pre, post = tb("preTokenBalances"), tb("postTokenBalances")
    sol = (m["postBalances"][i] - m["preBalances"][i]) / 1e9 + (post.get(WSOL, 0) - pre.get(WSOL, 0)) / 1e9
    mv = {k: post.get(k, 0) - pre.get(k, 0) for k in set(pre) | set(post) if k != WSOL and post.get(k, 0) != pre.get(k, 0)}
    if list(mv) == [WB] and abs(sol) > 0.05: rates.append(abs(sol * 1e9 / mv[WB]))
    txs.append((t["blockTime"], sol, mv))
R = statistics.median(rates) / 1e9
coin = {}
for bt_, sol, mv in txs:
    coins = [k for k in mv if k != WB]
    if not coins: continue
    k = max(coins, key=lambda c: (c[:8] in copied, abs(mv[c])))     # the coin this transaction trades
    c = coin.setdefault(k, dict(t=bt_, net=0.0, tok=0, spent=0.0, other=set()))
    v = sol + mv.get(WB, 0) * R; c["t"] = min(c["t"], bt_); c["net"] += v; c["tok"] += mv[k]
    if mv[k] > 0: c["spent"] += -v
    c["other"] |= {o for o in coins if o != k}
bt = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d %H:%M")
print(f"{bt(T0)} to {bt(END)} Beirut, coins wallet 4 first bought that week; WBTC at {R*1e9:.0f} lamports a unit "
      f"(median of its {len(rates)} SOL<->WBTC swaps)")
for name, sel in (("the coins we copy", lambda k: k[:8] in copied), ("all its coins", lambda k: True)):
    wk = {k: c for k, c in coin.items() if T0 <= c["t"] <= END and c["spent"] > 0 and sel(k)}
    done = {k: c for k, c in wk.items() if c["tok"] <= 0 and not c["other"]}
    odd = [k for k, c in wk.items() if c["tok"] > 0 or c["other"]]
    v = sorted((c["net"] for c in done.values()), reverse=True); spent = sum(c["spent"] for c in done.values())
    print(f"  {name}: {len(done)} closed, {sum(1 for x in v if x > 0)} won; spent {spent:.2f} SOL, net {sum(v):+.2f} SOL "
          f"({100*sum(v)/spent:+.1f}%), without its best 2 {sum(v[2:]):+.2f}; left out (still held or another token left) {len(odd)}")
    days = {}
    for c in done.values(): days.setdefault(bt(c["t"])[:5], []).append(c["net"])
    print("    by day:", "  ".join(f"{d} {len(x)} {sum(x):+.2f}" for d, x in sorted(days.items())))
    if name == "the coins we copy":
        for k in odd: print(f"    left out: {k[:8]} net so far {wk[k]['net']:+.3f} tokens left {wk[k]['tok']} other {[o[:8] for o in wk[k]['other']]}")
