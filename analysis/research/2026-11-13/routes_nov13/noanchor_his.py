# Wallet 4's own result on its 1.45+ SOL buys that have no route ("NoAnchor": its quote token has no PumpSwap pool to
# SOL or WBTC), since Oct 29 12:02 UTC, against the routable ones we copy. Per coin: its SOL and every token it paid
# with or was paid in, valued at PRICES (lamports per raw unit; today's Jupiter price for PUMP, the tokenized stocks,
# USDC...). A buy and its sale are in the same quote token minutes apart, so the % does not depend on that price;
# the SOL sizes do. Coins it still holds at the end, or traded together with another coin in one transaction, are
# left out.
# Buys the scan left "unpriced" (paid in a token it had no price for; the Oct 28 - Nov 12 scan priced only WBTC) are
# valued here; when paid in a token whose buys of Nov 13 had no route (NOPOOL: PUMP and two tokenized stocks,
# out/scan_priced.txt) they count as "no pool"; in any other token, as "not checked". No RPC is called.
#   python3 -I noanchor_his.py SPD/tx SPD/scan.out SPD/prices2.json
import sys, os, re, json, collections, datetime
TX, SCAN, PR = sys.argv[1:4]
W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"; WSOL = "So11111111111111111111111111111111111111112"
T0 = 1793274720 + 600            # Oct 29 12:02 UTC, as skipped_groups.py
WEEK2 = datetime.datetime(2026, 11, 5, 10, 0, tzinfo=datetime.timezone.utc).timestamp()   # Nov 5 12:00 Beirut
px = json.load(open(PR))
NOPOOL = ("pumpCmXq", "Xsc9qvGR", "XspzcW1P")
paid = {}                        # (slot, coin8) -> (its buy's value in lamports, the token it paid with)
bt, trips, mixed = {}, collections.defaultdict(lambda: dict(spent=0.0, back=0.0, held=0, first=None, unpriced=False)), set()
for f in os.listdir(TX):
    t = json.load(open(os.path.join(TX, f))); m = t["meta"]; bt[t["slot"]] = t["blockTime"]
    if m.get("err"): continue
    ks = t["transaction"]["message"]["accountKeys"] + sum(((m.get("loadedAddresses") or {}).get(x, []) for x in ("writable", "readonly")), [])
    if W4 not in ks: continue
    i = ks.index(W4)
    d = collections.defaultdict(int)
    for k, s in (("preTokenBalances", -1), ("postTokenBalances", 1)):
        for b in m.get(k) or []:
            if b.get("owner") == W4: d[b["mint"]] += s * int(b["uiTokenAmount"]["amount"])
    d = {k: v for k, v in d.items() if v}
    sol = m["postBalances"][i] - m["preBalances"][i] + d.pop(WSOL, 0)
    coins = [k for k in d if k not in px]
    if len(coins) != 1:
        mixed.update(coins); continue
    c = coins[0]; tr = trips[c]
    v = sol + sum(a * px[k] for k, a in d.items() if k != c)
    tr["held"] += d[c]
    if d[c] > 0:
        pay = [k for k, a in d.items() if k != c and a < 0]
        paid[(t["slot"], c[:8])] = (-v, pay[0][:8] if pay else "SOL")
        tr["spent"] += -v; tr["first"] = tr["first"] or t["blockTime"]
    else:
        tr["back"] += v
groups = collections.defaultdict(list)
for l in open(SCAN):
    u = re.match(r"(\d+) (\S{8}) unpriced: paid in (\S+)", l)
    if u and bt.get(int(u.group(1)), 0) >= T0:
        v, _ = paid.get((int(u.group(1)), u.group(2)), (0, ""))
        if v >= 1.45e9:
            groups["no pool" if u.group(3)[:8] in NOPOOL else "not checked"].append((int(u.group(1)), u.group(2), u.group(3)[:8]))
        continue
    g = re.match(r"(\d+) (\S{8}) ([\d.]+) SOL from (\S+) quote (\S+) jupiter (\S+): (ROUTABLE|no route)(.*)", l)
    if not g or bt.get(int(g.group(1)), 0) < T0: continue
    kind = "routable" if g.group(7) == "ROUTABLE" else ("3 hops" if "TooLong" in g.group(8) else "no pool")
    groups[kind].append((int(g.group(1)), g.group(2), g.group(5)[:8]))
by8 = {}
for c in trips: by8.setdefault(c[:8], c)
print("since Oct 29 12:02 UTC; tokens valued at", {k[:8]: round(v, 3) for k, v in px.items()})
print(f"{'group':11s} {'period':7s} {'buys':>4s} {'coins':>5s} {'spent':>7s} {'net':>7s} {'%':>7s} {'won':>4s} {'w/o best 2':>10s}")
rows = {}
for kind in ("routable", "3 hops", "no pool", "not checked"):
    seen = set()
    for slot, m8, q in groups[kind]:
        c = by8.get(m8)
        if not c or c in seen or c in mixed: continue
        tr = trips[c]
        if tr["held"] > 0 or tr["spent"] <= 0: continue
        seen.add(c); rows.setdefault(kind, []).append((tr["first"], c, q, tr["spent"] / 1e9, (tr["back"] - tr["spent"]) / 1e9))
    for per, f in (("week 1", lambda r: r[0] < WEEK2), ("week 2", lambda r: r[0] >= WEEK2), ("all", lambda r: True)):
        r = [x for x in rows.get(kind, []) if f(x)]
        nets = sorted((x[4] for x in r), reverse=True); sp = sum(x[3] for x in r)
        print(f"{kind:11s} {per:7s} {len(groups[kind]) if per == 'all' else '':>4} {len(r):5d} {sp:7.1f} {sum(nets):+7.2f} {100 * sum(nets) / sp if sp else 0:+6.1f}% {sum(1 for x in nets if x > 0):4d} {sum(nets[2:]):+10.2f}")
print("\nno pool and not checked, by the token it paid with:")
q = collections.defaultdict(list)
for x in rows.get("no pool", []) + rows.get("not checked", []): q[x[2]].append(x)
for k, r in sorted(q.items(), key=lambda kv: -len(kv[1])):
    sp = sum(x[3] for x in r); n = sum(x[4] for x in r)
    print(f"  {k}  {len(r):3d} coins  spent {sp:6.1f}  net {n:+6.2f}  {100 * n / sp:+6.1f}%  won {sum(1 for x in r if x[4] > 0)}")
print("\nNov 13 UTC, no pool:")
for x in sorted(rows.get("no pool", [])):
    if x[0] >= datetime.datetime(2026, 11, 13, tzinfo=datetime.timezone.utc).timestamp():
        print(" ", datetime.datetime.fromtimestamp(x[0], datetime.timezone.utc).strftime("%H:%M"), x[1][:8], x[2], f"spent {x[3]:.2f} net {x[4]:+.3f} ({100 * x[4] / x[3]:+.1f}%)")
