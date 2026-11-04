# Stage 1 of the two-stage test: our copy on 40 of a wallet's trips of the last 7 days (spread over day x quote x size),
# priced with the validated model (our buy and each of our sales 2 trades behind its own, the fitted curve, our impact
# at 1 SOL; reprice.score), following its sales; plus its own result a trip and its hold. Wallets whose copy is not
# clearly losing go to stage 2 (run.sh: its own exit rules, picked on days 1-4, scored on days 5-7, the week before).
#   python3 -I quick.py WALLET          (trips/<w>.quick.json from build.py with MAXT=40 OUTSFX=.quick)
import sys, os, json, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reprice as RP
from concurrent.futures import ThreadPoolExecutor
F = os.path.dirname(os.path.abspath(__file__)); w = sys.argv[1]
d = json.load(open(f"{F}/trips/{w}.quick.json")); mid = d["t0"] + 4 * 86400
CREATES = set()
def own_dc(t):                                   # its coin change in its own buy transaction (a mis-keyed trip has none)
    tx = RP.R.tx_of(t["sig0"])
    if not tx: return None
    m = tx["meta"]; ch = 0.0
    if any("Instruction: Create" in x for x in (m.get("logMessages") or [])): CREATES.add(t["sig0"])   # it launched the coin
    for side, sg in (("preTokenBalances", -1), ("postTokenBalances", 1)):
        for b in m.get(side) or []:
            if b.get("owner") == w and b["mint"] == t["mint"]: ch += sg * float(b["uiTokenAmount"]["uiAmount"] or 0)
    return ch
def one(t):
    try:
        dc = own_dc(t)
        if dc is not None and dc <= 0.01 * t["peak"]: return t, "mis-keyed", None
        if t["usd_in"] < 0.10: return t, "dust", None
        r = RP.score(w, t, False, 2)[0]
        return t, ("ok" if r else "unpriced"), r
    except Exception as e: return t, "error", None
    finally: RP.SEQ.clear() if len(RP.SEQ) > 2000 else None
with ThreadPoolExecutor(3) as ex: res = list(ex.map(one, d["trips"]))
ok = [(t, r) for t, k, r in res if k == "ok" and r and 0.2 <= r["entry_base"] <= 3 and 0 <= (r.get("entry_imp1") or 0) <= 1
      and all(0.2 <= l[2] <= 3 and 0 <= l[3] <= 1 for l in r.get("legs") or [])]
c = [r["copy"] for t, r in ok]
def wo2(v): v = sorted(v); return sum(v[:-2]) if len(v) > 2 else 0.0
p1 = [r["copy"] for t, r in ok if t["t0"] < mid]; p2 = [r["copy"] for t, r in ok if t["t0"] >= mid]
its = [(t["usd_out"] - t["usd_in"]) / t["usd_in"] for t, k, r in res if k in ("ok", "unpriced") and t["usd_in"] > 0]
hold = [t["sells"][0]["t"] - t["t0"] for t, k, r in res if t["sells"] and k in ("ok", "unpriced")]
prem = [r["entry_base"] * (1 + (r.get("entry_imp1") or 0)) - 1 for t, r in ok]
kinds = {k: sum(1 for _, x, _ in res if x == k) for k in ("ok", "unpriced", "mis-keyed", "dust", "error")}
med = lambda v: st.median(v) if v else float("nan")
# unpriced is not losing: too few priced trips, or its own typical trip at +10% or more, always goes to the full test
go = len(c) < 10 or med(its) >= 0.10 or sum(c) > -0.05 * len(c) or bool(p2 and sum(p2) > 0)
launcher = len(CREATES) >= 0.5 * max(1, len(d["trips"]))
if launcher: go = False                         # its buys are its own creates: a coin launcher, not a trader to copy
if d["trips_in_window"] < 12: go = False        # under 12 closed trades in 7 days: too few to pick on days 1-4 and score on 5-7
print(f"{w[:8]} quick: {d['trips_in_window']} trips in 7 days, {len(d['trips'])} tested {kinds}; its own a trip median {100 * med(its):+.1f}%, "
      f"first-sale hold median {med(hold):.0f} s; our entry median {100 * med(prem):+.1f}% over its price; our copy at 1 SOL "
      f"{sum(c):+.2f} ({100 * med(c):+.1f}% a trip median), days 1-4 {sum(p1):+.2f} ({len(p1)}), days 5-7 {sum(p2):+.2f} ({len(p2)}), "
      f"without the best 2 {wo2(c):+.2f} -> {'coin launcher: %d of its %d buys are its own creates' % (len(CREATES), len(d['trips'])) if launcher else 'no trades in the last 7 days' if not d['trips'] else f"too few trades to test ({d['trips_in_window']})" if d['trips_in_window'] < 12 else 'FULL TEST' if go else 'copy clearly losing'}{' (too few priced)' if d['trips'] and len(c) < 10 else ''}", flush=True)
