# What a coin did after we sold it (the owner, Nov 15 night: "from the sell pressure exits, has any coin hit the 4x tp
# if we would have held?"). For each of our closed copies named by its coin's first letters: the coin's trades from
# wallet 4's buy to 31 minutes after it (cmodel.path, as the backtest's paths), the price in multiples of the price its
# buy left (the bot's "x"), our sale, and then: the highest price before the 600 s timer, the price at the timer, the
# highest in the 31 minutes, and what the other live rules would have done without the rule that sold us.
#   RPC_URL=... LK=<cache dir> python3 -I after_exit.py OUR_WALLET COIN8[,COIN8...] > out/after_exit_<date>.txt
import sys, os, json, datetime
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-13/tab_exits"); import lib, cmodel as M
ME, COINS = sys.argv[1], sys.argv[2].split(","); W4 = lib.W4
f = lambda t: datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%H:%M:%S")
mine = lib.sigs(ME, limit=1000, cache=False); legs = {}
for s in reversed(mine):
    if s["err"]: continue
    t = lib.rpc("getTransaction", [s["signature"], M.TXO]); m = t["meta"]
    for b in (m.get("preTokenBalances") or []) + (m.get("postTokenBalances") or []):
        if b.get("owner") == ME and b["mint"][:8] in COINS:
            amt = lambda lst: sum(int(x["uiTokenAmount"]["amount"]) for x in lst or [] if x.get("owner") == ME and x["mint"] == b["mint"])
            d = amt(m.get("postTokenBalances")) - amt(m.get("preTokenBalances"))
            if d: legs.setdefault(b["mint"], {})["buy" if d > 0 else "sell"] = (t["slot"], t["blockTime"], s["signature"])
print("coin     | its buy   | our sale: after, at | then, before the 600 s timer: highest (when) | at the timer | highest in 31 min (when) | reached 4x after our sale")
for c in COINS:
    mint = next((k for k in legs if k[:8] == c), None)
    if not mint or "buy" not in legs[mint] or "sell" not in legs[mint]: print(f"{c} | not found among our last {len(mine)} transactions"); continue
    bslot, bt, _ = legs[mint]["buy"]; sslot, st, ssig = legs[mint]["sell"]; slot0 = bslot - 3
    page, anchor, before = None, None, None                   # a signature of the coin just past 31 minutes after the buy
    for _ in range(60):
        page = lib.sigs(mint, before=before, cache=False)
        if not page: break
        later = [x for x in page if x["slot"] >= slot0 + 4800]
        if later: anchor = later[-1]["signature"]
        if page[-1]["slot"] < slot0 + 4800 or len(page) < 1000: break
        before = page[-1]["signature"]
    tr = M.path(mint, slot0, anchor, threads=6)
    k = next((i for i, e in enumerate(tr) if e["user"] == W4 and e["buy"] and e["slot"] <= bslot), None)
    if k is None: print(f"{c} | its buy not found in {len(tr)} trades"); continue
    vref, t0 = tr[k]["vt"], tr[k]["t"]; px = lambda e: (vref / e["vt"]) ** 2
    j = next((i for i, e in enumerate(tr) if e["sig"] == ssig), None)
    if j is None: j = max(i for i, e in enumerate(tr) if e["slot"] <= sslot)
    ours = px(tr[j]); aft = [(e["t"] - t0, px(e)) for e in tr[j + 1:]]
    inwin = [(a, p) for a, p in aft if a <= 600]
    hi = max(inwin, key=lambda q: q[1]) if inwin else (st - t0, ours); at600 = inwin[-1][1] if inwin else ours
    hi31 = max(aft, key=lambda q: q[1]) if aft else (st - t0, ours)
    hit = next((a for a, p in aft if p >= 4.0), None)
    print(f"{c} | {f(t0)} | {st - t0:4d} s, {ours:4.2f}x | {hi[1]:5.2f}x (at {hi[0]:4d} s) | {at600:5.2f}x | {hi31[1]:5.2f}x (at {hi31[0]:4d} s) | "
          + (f"YES, {hit} s after its buy" + (" (before the timer)" if hit <= 600 else " (after the timer)") if hit is not None else "no") + f" | {len(tr)} trades")
