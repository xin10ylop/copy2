# Wallet 4's real result per coin from its own transactions (since_stop/vs_him_week.py's sums, every coin, any week):
# SOL and wSOL in and out per coin, WBTC moved in the same transactions at the median of its SOL<->WBTC swap rates.
# A coin traded together with another coin in one transaction is marked bad (not counted), as there.
import os, json, statistics
W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"; WSOL = "So11111111111111111111111111111111111111112"; WB = "3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh"
def per_coin(SPD):
    coins = {r["mint8"] for r in json.load(open(f"{SPD}/routable.json"))}
    txs, rates = [], []
    for f in os.listdir(f"{SPD}/w4tx"):
        t = json.load(open(f"{SPD}/w4tx/{f}")); m = t["meta"]
        if m.get("err"): continue
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
        txs.append((sol, mv))
    R = statistics.median(rates) / 1e9; his = {}
    for sol, mv in txs:
        cs = [k for k in mv if k != WB and k[:8] in coins]
        if len(cs) != 1 or len([k for k in mv if k != WB]) != 1:
            for k in cs: his.setdefault(k[:8], dict(net=0, spent=0, tok=0, bad=True))["bad"] = True
            continue
        k = cs[0][:8]; c = his.setdefault(k, dict(net=0, spent=0, tok=0, bad=False)); v = sol + mv.get(WB, 0) * R; c["net"] += v; c["tok"] += mv[cs[0]]
        if mv[cs[0]] > 0: c["spent"] += -v
    for c in his.values():
        if c["tok"] > 0: c["bad"] = True          # still held at the end of the data
    return his
