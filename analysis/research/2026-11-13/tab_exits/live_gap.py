# TAB16RxX's real trades against the model at our exact landing: our wallet's buy and sell on chain, the coin's
# path (cmodel.path), our own trade's position on it, the live rule of the time.   RPC_URL=... LK=... python3 -I gap.py
import sys, json, os, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import cmodel as M
URL = os.environ["RPC_URL"]; ME = "7ByEajSYmXjBK56LX4Wj3kVBAAeLYNW3soRE1T1WTubs"; W = "TAB16RxXmazWzCTpJbnKiREWUybdEoskuyidaV291u3"
def call(m, p):
    r = json.load(urllib.request.urlopen(urllib.request.Request(URL, json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), {"Content-Type": "application/json"}), timeout=60))
    if "error" in r: raise RuntimeError(str(r["error"])[:200])
    return r["result"]
# (coin prefix, its SOL, rule: tp, hold, follow window)
TRADES = [("481Ntemy", 1.829, 3.0, 300, None)] + [(c, sol, 4.0, 600, (0, 60, 1e9)) for c, sol in (
    ("4NBwggZy", 2.0), ("fdjHiwNk", 1.5), ("6MPM3y2N", 1.5), ("98VsxJ8T", 1.5), ("DhY4Gmmm", 2.0), ("8yxHek5W", 1.5),
    ("9XT4cpFG", 1.5), ("3a8RGrQg", 2.0), ("GTZPXNgi", 2.0), ("Ciy2H6NU", 1.5))]
txs = {}
for s in call("getSignaturesForAddress", [ME, {"limit": 200}]):
    if s["err"]: continue
    t = call("getTransaction", [s["signature"], {"encoding": "json", "maxSupportedTransactionVersion": 0}])
    m = t["meta"]; ks = t["transaction"]["message"]["accountKeys"] + m["loadedAddresses"]["writable"] + m["loadedAddresses"]["readonly"]
    d = (m["postBalances"][ks.index(ME)] - m["preBalances"][ks.index(ME)]) / 1e9
    for b in (m.get("postTokenBalances") or []) + (m.get("preTokenBalances") or []):
        if b.get("owner") == ME: txs.setdefault(b["mint"], {})[s["signature"]] = (t["slot"], d)
tot_r = tot_m = 0
for pre, sol, tp, hold, fol in TRADES:
    mint = next(k for k in txs if k.startswith(pre)); legs = sorted(txs[mint].values())
    real = sum(d for _, d in legs); slot = legs[0][0]
    tr = M.path(mint, slot - 2, None, threads=8)
    k = next(i for i, e in enumerate(tr) if e["user"] == W and e["buy"]); me = next(i for i, e in enumerate(tr) if e["user"] == ME and e["buy"])
    r = dict(m=mint, slot=tr[k]["slot"], t=tr[k]["t"], sol=sol)
    o = M.model(W, r, tr, 0.1, me - k, tp=tp, sl=None, hold=hold, follow=False)
    if fol:   # the early-dump rule: its first sale within 60 s of its buy takes us out behind it
        s1 = next((i for i, e in enumerate(tr[k + 1:], k + 1) if e["user"] == W and not e["buy"]), None)
        if s1 is not None and tr[s1]["t"] - tr[k]["t"] < fol[1] and s1 > me:
            o = M.model(W, r, tr[:s1 + 2], 0.1, me - k, tp=tp, sl=None, hold=10**9, follow=True)
    tot_r += real; tot_m += o["net"]
    print(f"{pre}: landed {me - k - 1} trades after its buy (slot {'same' if tr[me]['slot'] == tr[k]['slot'] else '+' + str(tr[me]['slot'] - tr[k]['slot'])}); real {real:+.4f}, model {o['net']:+.4f} ({o['exit']}, peak {o['peak']:.2f}x) -> {100 * (real - o['net']) / 0.1:+.1f} points")
print(f"all: real {tot_r:+.4f}, model {tot_m:+.4f}, {100 * (tot_r - tot_m) / 0.1 / len(TRADES):+.1f} points a trade")
