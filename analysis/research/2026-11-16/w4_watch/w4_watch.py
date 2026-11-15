# The daily check on wallet 4 (the owner, Nov 16: "track him every day, if he is using a new wallet"). From its landed
# transactions in SPD/w4tx (fetch them first with since_stop/fetch_w4.py) and a few live RPC reads:
#   1. its last transaction, and every gap of 3+ hours without one in the last DAYS days;
#   2. its balance now: SOL, and its token holdings worth 1+ SOL at Jupiter's price;
#   3. by Beirut day: transactions, coin buys, 1.45+ SOL buys, its own result on the coins it closed that day;
#   4. money in and out that is not trading (SOL or a token moved with no coin): who, how much;
#   5. where large amounts went: each destination's own activity (transactions, pump trades, last seen), to spot a
#      successor wallet or an exchange.
#   python3 -I w4_watch.py SPD [DAYS]
import sys, os, json, time, datetime, collections, urllib.request
SPD = sys.argv[1]; DAYS = int(sys.argv[2]) if len(sys.argv) > 2 else 10
W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"; WSOL = "So11111111111111111111111111111111111111112"
PUMP_PROGS = {"6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P", "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"}
KNOWN = {"EXzuWDVba3BQL14UYxSbvz1pZwZNYHXbyQwMBQutPFey": "its cash-out wallet since Oct 30"}
R = open("/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad/month/.triton_url").read().strip()
def call(m, p):
    for k in range(5):
        try:
            req = urllib.request.Request(R, json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), {"content-type": "application/json"})
            r = json.load(urllib.request.urlopen(req, timeout=60))
            if "error" in r: raise RuntimeError("rpc error")
            return r["result"]
        except Exception: time.sleep(2 * (k + 1))
    return None
def jup(ids):
    out = {}
    for i in range(0, len(ids), 40):
        for k in range(4):
            try: out.update(json.load(urllib.request.urlopen("https://lite-api.jup.ag/price/v3?ids=" + ",".join(ids[i:i + 40] + [WSOL]), timeout=30))); break
            except Exception: time.sleep(4 * (k + 1))
    return out
bt_ = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc)
f = lambda t: bt_(t).strftime("%m-%d %H:%M")
now = time.time(); t0 = now - DAYS * 86400
txs = []
for fn in os.listdir(f"{SPD}/w4tx"):
    t = json.load(open(f"{SPD}/w4tx/{fn}"))
    if (t.get("blockTime") or 0) >= t0 - 86400: txs.append(t)
txs.sort(key=lambda t: (t["slot"], t["blockTime"]))
last = max(t["blockTime"] for t in txs)
print(f"wallet 4 = {W4}; checked {f(now)} Beirut; its transactions on file to {f(last)} Beirut ({(now - last) / 60:.0f} min ago)")
# 1. quiet gaps
times = [t["blockTime"] for t in txs if t["blockTime"] >= t0]
gaps = [(a, b) for a, b in zip(times, times[1:]) if b - a >= 3 * 3600]
print(f"\n1. gaps of 3+ hours with no transaction, last {DAYS} days: {len(gaps)}" + "".join(f"\n   {f(a)} to {f(b)} ({(b - a) / 3600:.1f} h)" for a, b in gaps))
# 2. balance now
bal = call("getBalance", [W4]); toks = []
for prog in ("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"):
    r = call("getTokenAccountsByOwner", [W4, {"programId": prog}, {"encoding": "jsonParsed"}]) or {"value": []}
    for a in r["value"]:
        i = a["account"]["data"]["parsed"]["info"]; amt = float(i["tokenAmount"]["uiAmountString"] or 0)
        if amt > 0: toks.append((i["mint"], amt))
px = jup([m for m, _ in toks]); sol_usd = px.get(WSOL, {}).get("usdPrice", 0)
held = sorted(((m, a, a * px[m]["usdPrice"] / sol_usd) for m, a in toks if m in px and px[m].get("usdPrice") and sol_usd), key=lambda x: -x[2])
big = [h for h in held if h[2] >= 1]
print(f"\n2. balance now: {bal['value'] / 1e9:.2f} SOL; {len(toks)} token accounts with a balance, {len(big)} worth 1+ SOL: " + ", ".join(f"{m[:8]} {v:.1f} SOL" for m, a, v in big[:10])
      + f"; all tokens priced {sum(h[2] for h in held):.1f} SOL (SOL ${sol_usd:.2f})")
# 3 and 4. per transaction: coin trades, plain moves
# lamports per raw unit: the study's table (97 paying tokens, Nov 15 prices) updated with the live holdings' prices
lpu = json.load(open(f"{SPD}/prices_full2.json")) if os.path.exists(f"{SPD}/prices_full2.json") else {}
dec_live = {m: None for m in px}
px_now = {m: px[m]["usdPrice"] / sol_usd for m in px if px[m].get("usdPrice") and sol_usd}   # SOL per whole token
per_day = collections.defaultdict(lambda: dict(tx=0, buys=0, big=0, sells=0)); moves = []; trips = collections.defaultdict(lambda: [0.0, 0.0, 0, None])
unpriced, bad = set(), set()                                  # transactions and coins with a token we cannot price
for t in txs:
    m = t["meta"]; d = bt_(t["blockTime"]).strftime("%m-%d")
    if m.get("err"): continue
    ks = t["transaction"]["message"]["accountKeys"] + sum(((m.get("loadedAddresses") or {}).get(x, []) for x in ("writable", "readonly")), [])
    if W4 not in ks: continue
    i = ks.index(W4); dlt = collections.defaultdict(int); dec = {}
    for k, s in (("preTokenBalances", -1), ("postTokenBalances", 1)):
        for b in m.get(k) or []:
            dec[b["mint"]] = b["uiTokenAmount"]["decimals"]
            if b.get("owner") == W4: dlt[b["mint"]] += s * int(b["uiTokenAmount"]["amount"])
    dlt = {k: v for k, v in dlt.items() if v}; sol = (m["postBalances"][i] - m["preBalances"][i] + dlt.pop(WSOL, 0)) / 1e9
    if t["blockTime"] >= t0: per_day[d]["tx"] += 1
    progs = {ks[ix["programIdIndex"]] for ix in t["transaction"]["message"]["instructions"]} | {ks[x["programIdIndex"]] for g in m.get("innerInstructions") or [] for x in g["instructions"]}
    trade = bool(progs & PUMP_PROGS) or len(dlt) >= 2 or (len(dlt) == 1 and abs(sol) > 0.01 and (list(dlt.values())[0] > 0) == (sol < 0))
    if trade:
        ups = [k for k, v in dlt.items() if v > 0]; downs = [k for k, v in dlt.items() if v < 0]
        def val(mint, raw):
            if mint in px_now: return raw / 10 ** dec.get(mint, 0) * px_now[mint]
            if mint in lpu: return raw * lpu[mint] / 1e9
            unpriced.add(t["transaction"]["signatures"][0]); return 0.0
        if len(ups) == 1:                                    # a buy of `ups[0]` paid in SOL or another token
            paid = -sol + sum(-val(k, dlt[k]) for k in downs)
            if t["blockTime"] >= t0: per_day[d]["buys"] += 1; per_day[d]["big"] += paid >= 1.45
            tr = trips[ups[0]]; tr[0] += paid; tr[2] += dlt[ups[0]]
            if t["transaction"]["signatures"][0] in unpriced: bad.add(ups[0])
        if len(downs) == 1 and not ups or (len(downs) == 1 and len(ups) == 1 and ups[0] in px_now):
            back = sol + sum(val(k, dlt[k]) for k in ups); c = downs[0]
            tr = trips[c]; tr[1] += back; tr[2] += dlt[c]; tr[3] = t["blockTime"]
            if t["transaction"]["signatures"][0] in unpriced: bad.add(c)
            if t["blockTime"] >= t0: per_day[d]["sells"] += 1
    elif t["blockTime"] >= t0:
        # a plain move: SOL or a token in or out with no coin: who else's balance changed
        others = []
        for j, k in enumerate(ks[:len(m["postBalances"])]):
            dd = (m["postBalances"][j] - m["preBalances"][j]) / 1e9
            if k != W4 and abs(dd) >= 0.5: others.append((k, round(dd, 2)))
        for b in m.get("postTokenBalances") or []:
            if b.get("owner") and b["owner"] != W4:
                pre = next((int(x["uiTokenAmount"]["amount"]) for x in m.get("preTokenBalances") or [] if x["accountIndex"] == b["accountIndex"]), 0)
                dd = int(b["uiTokenAmount"]["amount"]) - pre
                if dd: others.append((b["owner"], f"{dd / 10 ** b['uiTokenAmount']['decimals']:+.2f} {b['mint'][:8]}"))
        tokv = sum(dlt[k] / 10 ** dec.get(k, 0) * px_now.get(k, 0) for k in dlt)
        if abs(sol) >= 1 or abs(tokv) >= 1: moves.append((t["blockTime"], sol, {k[:8]: v / 10 ** dec.get(k, 0) for k, v in dlt.items()}, others, t["transaction"]["signatures"][0]))
closed = collections.defaultdict(list)
for c, (spent, back, h, lt) in trips.items():
    if lt and h <= 0 and spent >= 0.05 and c not in bad: closed[bt_(lt).strftime("%m-%d")].append((back - spent) / spent)
print(f"\n3. by Beirut day (tokens at today's price): transactions | coin buys | buys of 1.45+ SOL | coin sales | its result on the coins it closed that day (coins of 0.05+ SOL, every leg priced)")
for d in sorted(per_day):
    c = closed.get(d, []); x = per_day[d]
    print(f"   {d}: {x['tx']:5d} | {x['buys']:4d} | {x['big']:3d} | {x['sells']:4d} | " + (f"{len(c)} coins, {100 * sum(c) / len(c):+5.1f}% a coin, {sum(1 for v in c if v > 0)} won" if c else "-"))
print(f"\n4. money in and out that is not a coin trade, 1+ SOL (or its worth), last {DAYS} days: {len(moves)}")
for tt, sol, tk, others, sig in moves:
    print(f"   {f(tt)} SOL {sol:+.2f} tokens {tk} | others: " + ", ".join(f"{k[:8]}{' (' + KNOWN[k] + ')' if k in KNOWN else ''} {v}" for k, v in others[:4]) + f" | {sig[:10]}")
# 5. destinations of large moves
dest = collections.Counter()
for tt, sol, tk, others, sig in moves:
    for k, v in others:
        if isinstance(v, (int, float)) and v > 0 and sol < 0: dest[k] += v
        elif isinstance(v, str) and v.startswith("+"): dest[k] += 1
print(f"\n5. where it sent money, and what those wallets do:")
for k, v in dest.most_common(8):
    sigs = call("getSignaturesForAddress", [k, {"limit": 200}]) or []
    pump = 0
    for s in sigs[:25]:
        tx = call("getTransaction", [s["signature"], {"encoding": "json", "maxSupportedTransactionVersion": 0}])
        if tx:
            kk = tx["transaction"]["message"]["accountKeys"] + sum(((tx["meta"].get("loadedAddresses") or {}).get(x, []) for x in ("writable", "readonly")), [])
            pump += bool(set(kk) & PUMP_PROGS)
    b = call("getBalance", [k]) or {"value": 0}
    print(f"   {k}{' (' + KNOWN[k] + ')' if k in KNOWN else ''}: received {v:.2f}; its balance {b['value'] / 1e9:.2f} SOL; {len(sigs)}{'+' if len(sigs) == 200 else ''} recent transactions"
          + (f", newest {f(sigs[0]['blockTime'])}, oldest of these {f(sigs[-1]['blockTime'])}" if sigs else "") + f"; pump trades in its last 25: {pump}")

# 6. what the cash-out wallet did with it
for k in [k for k in KNOWN] + [k for k, _ in dest.most_common(3) if k not in KNOWN]:
    sigs = [x for x in (call("getSignaturesForAddress", [k, {"limit": 100}]) or []) if (x.get("blockTime") or 0) >= t0]
    print(f"\n6. {k[:8]}'s own moves in the last {DAYS} days ({len(sigs)} transactions): where its money went")
    for x in reversed(sigs):
        tx = call("getTransaction", [x["signature"], {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}])
        if not tx or tx["meta"].get("err"): continue
        outs = []
        for ins in tx["transaction"]["message"]["instructions"] + [y for g in tx["meta"].get("innerInstructions") or [] for y in g["instructions"]]:
            pi = ins.get("parsed") if isinstance(ins.get("parsed"), dict) else None
            if not pi: continue
            info = pi.get("info", {})
            if pi.get("type") == "transfer" and info.get("source") == k and "lamports" in info: outs.append((info["destination"], f"{info['lamports'] / 1e9:.2f} SOL"))
            elif pi.get("type") in ("transfer", "transferChecked") and info.get("authority") == k:
                amt = info.get("tokenAmount", {}).get("uiAmountString") or info.get("amount")
                outs.append((info.get("destination"), f"{amt} {(info.get('mint') or '?')[:8]} (to token account)"))
        if outs: print(f"   {f(x['blockTime'])} " + "; ".join(f"{d[:8] if d else '?'} {a}" for d, a in outs[:4]))
