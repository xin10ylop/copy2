# Wallet 4's own result on the coins we copied live, from its transactions in SPD/w4tx: SOL (and wSOL) in and out of
# its wallet on every transaction that moved that coin, and the coin bought and sold. Run: python3 -I his_vs_ours.py SPD
import json, os, sys, datetime
SPD = sys.argv[1]; W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"; WSOL = "So11111111111111111111111111111111111111112"
# ours, on chain (README "First 3 closed"): coin -> (SOL in, SOL back)
OURS = {"Ci9Bg1Bx": None, "BttUQVPM": None, "5tePJcGm": None}
OURS_NET = {"Ci9Bg1Bx": -0.0597, "BttUQVPM": -0.0455, "5tePJcGm": 0.3531}
bt = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d %H:%M:%S")
ev = {k: [] for k in OURS}
for f in os.listdir(f"{SPD}/w4tx"):
    t = json.load(open(f"{SPD}/w4tx/{f}")); m = t["meta"]
    if m.get("err"): continue
    ks = t["transaction"]["message"]["accountKeys"] + (m.get("loadedAddresses") or {}).get("writable", []) + (m.get("loadedAddresses") or {}).get("readonly", [])
    if W4 not in ks: continue
    i = ks.index(W4)
    def tb(which):
        d = {}
        for b in m.get(which) or []:
            if b.get("owner") == W4: d[b["mint"]] = d.get(b["mint"], 0) + int(b["uiTokenAmount"]["amount"])
        return d
    pre, post = tb("preTokenBalances"), tb("postTokenBalances")
    sol = (m["postBalances"][i] - m["preBalances"][i]) / 1e9 + (post.get(WSOL, 0) - pre.get(WSOL, 0)) / 1e9
    for mint in set(pre) | set(post):
        if mint[:8] in ev:
            dt = post.get(mint, 0) - pre.get(mint, 0)
            if dt: ev[mint[:8]].append((t["blockTime"], t["slot"], sol, dt, t["transaction"]["signatures"][0][:8],
                                        {k[:8]: post.get(k, 0) - pre.get(k, 0) for k in set(pre) | set(post) if k != mint and k != WSOL and post.get(k, 0) != pre.get(k, 0)}))
last = max(json.load(open(f"{SPD}/w4tx/{f}"))["blockTime"] for f in os.listdir(f"{SPD}/w4tx"))
print(f"wallet 4's transactions fetched up to {bt(last)} Beirut")
print("coin       his SOL in  his SOL back  his %     our %    held (his)   other tokens moved")
for k, es in ev.items():
    es.sort(); spent = -sum(e[2] for e in es if e[3] > 0); back = sum(e[2] for e in es if e[3] < 0)
    left = sum(e[3] for e in es)
    held = (es[-1][0] - es[0][0]) if len(es) > 1 else None
    for e in es: print(f"    {bt(e[0])}  {'buy ' if e[3] > 0 else 'sell'} SOL {e[2]:+.4f}  coin {e[3]:+d}  {e[4]}  {e[5] or ''}")
    print(f"  {k}  {spent:9.4f}  {back:11.4f}  {100*(back-spent)/spent if spent else 0:+7.1f}%  {100*OURS_NET[k]/0.1:+7.1f}%  "
          f"{held if held is not None else '-'} s   coin left {left}")
