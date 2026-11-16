# Wallet 4's buys of SOL-priced coins (the owner, Nov 16: "study now"), from its landed transactions on disk: every
# pump trade event of its own on a curve quoted in SOL. For each coin: its first buy (slot, time, SOL, how much of the
# curve was sold before it: a launch buy or a later one), its later buys and its sales, and its own net on the coin
# (curve SOL in and out, fees left out). -> OUT/sol_buys.json
#   python3 -I collect.py OUT TXDIR [TXDIR ...]
import sys, os, json, collections
OUT, DIRS = sys.argv[1], sys.argv[2:]
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-15/skip_filters/fable")
sys.argv = ["x", "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/floatq", "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/skipq_fable"]
src = open("/home/user/copy2/analysis/research/2026-11-15/skip_filters/fable/fee_parts.py").read(); exec(src[:src.index("files = collections.defaultdict(list)")])
SOLQ = {None, "So11111111111111111111111111111111111111112", "11111111111111111111111111111111"}
INIT_VT = 1_073_000_000_000_000                             # a pump curve's virtual tokens at its creation
seen, coins = set(), collections.defaultdict(lambda: dict(buys=[], sells=[]))
for D in DIRS:
    for f in os.listdir(D):
        t = json.load(open(f"{D}/{f}")); m = t["meta"]; sig = t["transaction"]["signatures"][0]
        if m.get("err") or sig in seen: continue
        seen.add(sig)
        ks = t["transaction"]["message"]["accountKeys"] + sum(((m.get("loadedAddresses") or {}).get(x, []) for x in ("writable", "readonly")), [])
        for g in m.get("innerInstructions") or []:
            for ix in g["instructions"]:
                if ks[ix["programIdIndex"]] != C.PUMP: continue
                raw = C.b58d(ix.get("data", ""))
                if raw[:8] != E.EVENT_IX_TAG or raw[8:16] != E.DISC_TRADE: continue
                try: e = decode(raw[16:])
                except Exception: continue
                if e["user"] != W4 or e.get("quote") not in SOLQ: continue
                rec = dict(slot=t["slot"], t=t["blockTime"], sol=e["sol"] / 1e9, tok=e["tok"], vt=e["vt"], sig=sig)
                coins[e["mint"]]["buys" if e["buy"] else "sells"].append(rec)
out = []
for mint, c in coins.items():
    if not c["buys"]: continue
    b = sorted(c["buys"], key=lambda r: (r["slot"], r["t"])); s = c["sells"]
    first = b[0]; pre_vt = first["vt"] + first["tok"]
    out.append(dict(mint=mint, slot=first["slot"], t=first["t"], sol=first["sol"], sold_before=1 - pre_vt / INIT_VT, nbuys=len(b), buy_sol=sum(r["sol"] for r in b),
                    sell_sol=sum(r["sol"] for r in s), nsells=len(s), sig=first["sig"]))
out.sort(key=lambda r: r["t"]); json.dump(out, open(f"{OUT}/sol_buys.json", "w"))
import datetime
f = lambda t: datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%m-%d %H:%M")
print(f"{len(seen)} transactions; SOL-priced coins it bought: {len(out)}, {f(out[0]['t'])} to {f(out[-1]['t'])} UTC" if out else "none")
day = collections.Counter(f(r["t"])[:5] for r in out); print("coins a day (UTC):", dict(sorted(day.items())))
for lo, hi in ((0, 0.5), (0.5, 1.0), (1.0, 1.3), (1.3, 99)):
    v = [r for r in out if lo <= r["sol"] < hi]; cl = [r for r in v if r["nsells"]]
    print(f"   first buy {lo}-{hi} SOL: {len(v)} coins; launch buys (under 1% of the curve sold before) {sum(1 for r in v if r['sold_before'] < 0.01)};"
          f" its own net on the {len(cl)} it sold: {sum(r['sell_sol'] - r['buy_sol'] for r in cl):+.2f} SOL on {sum(r['buy_sol'] for r in cl):.2f} in")
