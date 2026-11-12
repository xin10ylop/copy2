# Search 3: the same profile on other launchpads (the copier only, through Jupiter): Raydium LaunchLab (letsbonk and
# others) and Meteora DBC. The program's whole landed transaction stream for HOURS back from now, every transaction read:
# a launch is a transaction whose logs show an Initialize* instruction of the program (the new mint = the token whose
# supply appears in it); a trade is any other transaction where the signer's balance of one non-wSOL token changes and
# its SOL (+wSOL) moves the other way. Per wallet: buys of MIN+ SOL within WIN s of the coin's launch, and its first
# sale of that coin in the stream (seconds after its buy).
#   python3 -I l1_launchpads.py NAME PROGRAM HOURS [MIN=1.0] [WIN=2]  ->  LK/l1_<NAME>.json, a table on stdout
import sys, os, json, time, statistics, collections
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lib
NAME, PROG, HOURS = sys.argv[1], sys.argv[2], float(sys.argv[3])
MIN = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0; WIN = float(sys.argv[5]) if len(sys.argv) > 5 else 2
TXO = {"encoding": "json", "maxSupportedTransactionVersion": 1, "commitment": "confirmed"}
op = f"{lib.OUT}/l1_{NAME}.json"
if os.path.exists(op): ev = json.load(open(op))
else:
    S, before, t1 = [], None, None
    while True:
        page = lib.sigs(PROG, before=before, cache=False)
        if not page: break
        t1 = t1 or page[0]["blockTime"]; before = page[-1]["signature"]
        S += [p for p in page if p.get("err") is None]
        if page[-1]["blockTime"] < t1 - HOURS * 3600: break
    S = [p for p in S if p["blockTime"] >= t1 - HOURS * 3600]
    print(time.strftime("%H:%M:%S"), len(S), "landed transactions", flush=True)
    def one(p):
        t = lib.rpc("getTransaction", [p["signature"], TXO], cache=False)
        if not t: return None
        m = t["meta"]; ks = t["transaction"]["message"]["accountKeys"] + sum(((m.get("loadedAddresses") or {}).get(x, []) for x in ("writable", "readonly")), [])
        logs = m.get("logMessages") or []
        init = any(l.startswith("Program log: Instruction: Initialize") and "ImmutableOwner" not in l and "Account" not in l for l in logs)
        w = ks[0]
        def tb(k, own=True):
            d = collections.Counter()
            for b in m.get(k) or []:
                if (b.get("owner") == w) == own: d[b["mint"]] += int(b["uiTokenAmount"]["amount"])
            return d
        pre, post = tb("preTokenBalances"), tb("postTokenBalances")
        sol = m["postBalances"][0] - m["preBalances"][0] + m["fee"] + post[lib.WSOL] - pre[lib.WSOL]
        mv = {k: post[k] - pre[k] for k in set(pre) | set(post) if k != lib.WSOL and post[k] != pre[k]}
        mints = sorted({b["mint"] for b in (m.get("postTokenBalances") or []) if b["mint"] != lib.WSOL})
        return dict(sig=p["signature"], slot=t["slot"], t=t["blockTime"], w=w, init=init, sol=sol, mv=mv, mints=mints if init else None)
    with ThreadPoolExecutor(48) as ex: ev = [x for x in ex.map(one, S) if x]
    json.dump(ev, open(op, "w"))
ev.sort(key=lambda e: (e["slot"], e["t"]))
launch = {}
for e in ev:
    if e["init"]:
        for m in e["mints"] or []: launch.setdefault(m, e["t"])
buys = collections.defaultdict(list); first_sale = {}
for e in ev:
    if e["init"] or len(e["mv"]) != 1: continue
    (m, q), = e["mv"].items()
    if q < 0 and e["sol"] > 0: first_sale.setdefault((e["w"], m), e["t"])
    if q > 0 and e["sol"] < 0 and m in launch and e["t"] - launch[m] <= WIN and -e["sol"] / 1e9 >= MIN:
        buys[e["w"]].append(dict(m=m, sol=-e["sol"] / 1e9, t=e["t"], dt=e["t"] - launch[m]))
end = ev[-1]["t"] if ev else 0
print(f"{NAME}: {len(ev)} transactions, {len(launch)} launches seen, {sum(len(v) for v in buys.values())} buys of {MIN}+ SOL within {WIN} s of a launch by {len(buys)} wallets")
rows = []
for w, b in buys.items():
    hs = [first_sale[(w, x["m"])] - x["t"] for x in b if (w, x["m"]) in first_sale and first_sale[(w, x["m"])] >= x["t"]]
    held = sum(1 for x in b if (w, x["m"]) not in first_sale and end - x["t"] >= 600)
    rows.append(dict(w=w, n=len(b), sol=statistics.median(x["sol"] for x in b), h50=statistics.median(hs) if hs else None,
                     ge120=sum(1 for h in hs if h >= 120), sold=len(hs), held10=held))
rows.sort(key=lambda r: -r["n"])
print(f"{'wallet':45s} {'coins':>5s} {'SOL med':>7s} {'sold':>4s} {'1st sale med s':>14s} {'120 s+':>6s} {'no sale 10m+':>12s}")
for r in rows[:30]:
    print(f"{r['w']:45s} {r['n']:5d} {r['sol']:7.2f} {r['sold']:4d} {str(r['h50']):>14s} {r['ge120']:6d} {r['held10']:12d}")
json.dump(rows, open(f"{lib.OUT}/l1_{NAME}_rank.json", "w"))
