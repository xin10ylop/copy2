# Rafinhaaaaaa's trades from its own transactions (chain): each buy and sale, sized as its whole SOL change (fees and
# tip included, as the copier values it), venue, tip; then by day: buys, sizes, 5.1+ buys, holds, first-sale multiples.
#   python3 -I behav.py TX_DIR OUT_JSON
import json, sys, os, glob, datetime, collections, statistics as st
sys.path.insert(0, "/home/user/copy2/rafinhaaaaaa/analysis/final")
W = "Hn6vBWWySnxA8XjxRQDEmZEuH5QL7KqosnJGcLcUzFJ6"
WSOL = "So11111111111111111111111111111111111111112"
STABLE = {"EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v": "USDC", "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB": "USDT",
          "USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB": "USD1"}
import g1lib as G
rows = []
for fn in glob.glob(f"{sys.argv[1]}/*.json"):
    tx = json.load(open(fn)); meta = tx["meta"]
    if meta.get("err"): continue
    keys = G.keys_of(tx)
    if W not in keys: continue
    i = keys.index(W)
    sol = (meta["postBalances"][i] - meta["preBalances"][i]) / 1e9          # fee included
    tok = collections.defaultdict(float)
    for side, sign in (("preTokenBalances", -1), ("postTokenBalances", 1)):
        for b in meta.get(side) or []:
            if b.get("owner") == W: tok[b["mint"]] += sign * float(b["uiTokenAmount"]["uiAmount"] or 0)
    sol += tok.pop(WSOL, 0.0)
    stab = {STABLE[m]: tok.pop(m) for m in list(tok) if m in STABLE}
    coins = {m: v for m, v in tok.items() if abs(v) > 0}
    fee, prio, tips, *_ = G.fee_tip(tx, W)
    signer = keys[0] == W
    for m, v in coins.items():
        side = "buy" if v > 0 else "sell"
        rows.append(dict(sig=tx["transaction"]["signatures"][0], slot=tx["slot"], t=tx["blockTime"], mint=m, side=side,
                         dc=v, sol=sol, stab=stab, venue=G.venue(tx), tip=sum(x for _, x in tips), fee=fee, signer=signer,
                         ncoins=len(coins)))
rows.sort(key=lambda r: (r["slot"], r["sig"]))
json.dump(rows, open(sys.argv[2], "w"))
day = lambda t: datetime.datetime.fromtimestamp(t, datetime.UTC).strftime("%m-%d")
q = lambda v, p: sorted(v)[min(len(v) - 1, int(p * len(v)))] if v else float("nan")
by = collections.defaultdict(list)
for r in rows: by[day(r["t"])].append(r)
first_buy = {}; out = collections.defaultdict(lambda: dict(spent=0.0, got=0.0, first_sell=None, buy=None))
for r in rows:
    k = r["mint"]
    if r["side"] == "buy" and k not in first_buy: first_buy[k] = r
    o = out[k]
    if r["side"] == "buy": o["spent"] += -r["sol"]; o["buy"] = o["buy"] or r
    else:
        o["got"] += r["sol"]
        if o["first_sell"] is None and o["buy"]: o["first_sell"] = r
print(f"{'day':5} {'buys':>4} {'sells':>5} {'SOL a buy p10/50/90':>22} {'5.1+':>4} {'USDC':>4} {'venues of buys (top)':40} {'hold to 1st sale p50 s':>8} {'tip p50':>7}")
for dd in sorted(by):
    b = [r for r in by[dd] if r["side"] == "buy"]; s = [r for r in by[dd] if r["side"] == "sell"]
    sz = [-r["sol"] for r in b if r["sol"] < 0]
    big = sum(1 for x in sz if x >= 5.1)
    ven = collections.Counter("/".join(v for v in r["venue"] if v not in ("Axiom router", "Jupiter")) or "?" for r in b).most_common(4)
    holds = [out[r["mint"]]["first_sell"]["t"] - r["t"] for r in b if out[r["mint"]]["first_sell"] and out[r["mint"]]["buy"] is r]
    tips = [r["tip"] for r in b]
    print(f"{dd:5} {len(b):4} {len(s):5} {q(sz,.1):7.2f}/{q(sz,.5):6.2f}/{q(sz,.9):6.2f} {big:4} {sum(1 for r in b if r['stab']):4} {str(ven)[:40]:40} {q(holds,.5) if holds else float('nan'):8.0f} {q(tips,.5) if tips else 0:7.3f}")
