# Every SOL transfer from or to the wallet (system transfers, top level and inner, both directions) in its own
# transactions, and its balance after each transaction: where its money goes, and whether it is being emptied.
#   python3 -I flows.py TX_DIR WALLET
import json, sys, glob, datetime, collections
sys.path.insert(0, "/home/user/copy2/rafinhaaaaaa/analysis/final")
import g1lib as G
D, W = sys.argv[1], sys.argv[2]
SYS = "11111111111111111111111111111111"
f = lambda t: datetime.datetime.fromtimestamp(t, datetime.UTC).strftime("%m-%d %H:%M")
rows, bal = [], []
for fn in glob.glob(f"{D}/*.json"):
    tx = json.load(open(fn)); m = tx["meta"]
    if m.get("err"): continue
    keys = G.keys_of(tx)
    if W not in keys: continue
    i = keys.index(W); bal.append((tx["blockTime"], tx["slot"], m["postBalances"][i] / 1e9, keys[0] == W))
    msg = tx["transaction"]["message"]
    ins = [(x, True) for x in msg.get("instructions") or []]
    for g in m.get("innerInstructions") or []: ins += [(x, False) for x in g["instructions"]]
    tok = {keys[b["accountIndex"]] for side in ("preTokenBalances", "postTokenBalances") for b in (m.get(side) or [])}
    coins = any(b.get("owner") == W and b["mint"] != G.WSOL for side in ("preTokenBalances", "postTokenBalances") for b in (m.get(side) or []))
    for x, top in ins:
        if keys[x["programIdIndex"]] != SYS: continue
        d = G.b58dec(x.get("data") or "")
        if len(d) < 12 or int.from_bytes(d[:4], "little") != 2: continue
        a = x["accounts"]; src, dst = keys[a[0]], keys[a[1]]; amt = int.from_bytes(d[4:12], "little") / 1e9
        if W not in (src, dst) or src == dst: continue
        other = dst if src == W else src
        if other in tok: continue                       # its own token accounts (wrapping SOL)
        rows.append(dict(t=tx["blockTime"], dir="out" if src == W else "in", other=other, sol=amt, trade=coins,
                         signer=keys[0], sig=tx["transaction"]["signatures"][0]))
bal.sort()
print(f"balance: first {bal[0][2]:.2f} SOL at {f(bal[0][0])}, last {bal[-1][2]:.2f} SOL at {f(bal[-1][0])}; min {min(b[2] for b in bal):.2f}, max {max(b[2] for b in bal):.2f}")
# the balance each day at its last transaction
last = {}
for t, s, b, _ in bal: last[f(t)[:5]] = b
print("balance at each day's last transaction:", "  ".join(f"{d} {b:.1f}" for d, b in sorted(last.items())))
# transfers outside trades (no coin in the transaction), and the counterparties by total
non = [r for r in rows if not r["trade"]]
print(f"\n{len(rows)} SOL transfers in its transactions; {len(non)} in transactions with no coin (plain transfers)")
agg = collections.defaultdict(lambda: [0, 0.0, 0, 0.0])
for r in non:
    a = agg[r["other"]]
    if r["dir"] == "out": a[0] += 1; a[1] += r["sol"]
    else: a[2] += 1; a[3] += r["sol"]
print(f"{'counterparty':44} {'out n':>5} {'out SOL':>9} {'in n':>5} {'in SOL':>9}")
for k, v in sorted(agg.items(), key=lambda kv: -(kv[1][1] + kv[1][3]))[:15]:
    print(f"{k:44} {v[0]:5} {v[1]:9.3f} {v[2]:5} {v[3]:9.3f}")
print("\nplain transfers of 1 SOL or more:")
for r in sorted(non, key=lambda r: r["t"]):
    if r["sol"] >= 1: print(f"  {f(r['t'])} UTC {r['dir']:3} {r['sol']:9.3f} SOL {'to' if r['dir']=='out' else 'from'} {r['other']}  (signed by {'it' if r['signer']==W else r['signer'][:8]}) {r['sig'][:16]}")
