# For each address: SOL now, how active (signatures in the last 24 h / 7 d, newest), and a sample of its newest
# transactions it signed: venues, Axiom router, SOL change, tips, as Rafinhaaaaaa's own fingerprint would show.
#   python3 -I linked.py ADDR...
import json, sys, time, urllib.request, datetime, collections
sys.path.insert(0, "/home/user/copy2/rafinhaaaaaa/analysis/final")
import g1lib as G
U = "https://api.mainnet-beta.solana.com"; last = [0.0]
def rpc(m, p):
    for i in range(8):
        dt = time.time() - last[0]
        if dt < 0.4: time.sleep(0.4 - dt)
        last[0] = time.time()
        try:
            b = json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode()
            r = json.loads(urllib.request.urlopen(urllib.request.Request(U, b, {"Content-Type": "application/json"}), timeout=60).read())
            if "result" in r: return r["result"]
        except Exception: pass
        time.sleep(3 * (i + 1))
    return None
now = time.time(); f = lambda t: datetime.datetime.fromtimestamp(t, datetime.UTC).strftime("%m-%d %H:%M")
for a in sys.argv[1:]:
    bal = (rpc("getBalance", [a]) or {}).get("value", 0) / 1e9
    sigs = rpc("getSignaturesForAddress", [a, {"limit": 1000}]) or []
    ok = [s for s in sigs if not s.get("err")]
    d1 = sum(1 for s in ok if (s.get("blockTime") or 0) > now - 86400); d7 = sum(1 for s in ok if (s.get("blockTime") or 0) > now - 7 * 86400)
    oldest = f(sigs[-1]["blockTime"]) if sigs and sigs[-1].get("blockTime") else "-"
    ven, axiom, signed, sizes, tips = collections.Counter(), 0, 0, [], []
    for s in ok[:12]:
        tx = rpc("getTransaction", [s["signature"], {"encoding": "json", "maxSupportedTransactionVersion": 1}])
        if not tx: continue
        k = G.keys_of(tx)
        if k[0] != a: continue
        signed += 1; v = G.venue(tx); axiom += "Axiom router" in v
        for x in v:
            if x != "Axiom router": ven[x] += 1
        i = k.index(a); dsol = (tx["meta"]["postBalances"][i] - tx["meta"]["preBalances"][i]) / 1e9
        if dsol < -0.5: sizes.append(round(-dsol, 2))
        tips.append(round(sum(x for _, x in G.fee_tip(tx, a)[2]), 3))
    print(f"{a}  {bal:9.2f} SOL | sigs {len(sigs)}{'+' if len(sigs) == 1000 else ''} (oldest {oldest}), last 24h {d1}, 7d {d7}, newest {f(ok[0]['blockTime']) if ok else '-'}"
          f" | of its newest 12: signed {signed}, Axiom {axiom}, venues {dict(ven.most_common(4))}, SOL out {sizes[:6]}, tips {sorted(set(tips))[:5]}", flush=True)
