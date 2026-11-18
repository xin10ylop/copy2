# Step 1 of the wallet hunt (the owner, Nov 17: "find other wallets ... dont do the mistakes of the wallets we found
# before"): who else buys the other-token coins on disk, and what OUR copy of their buys would make. No fetch: the
# 1,559 other-token coins wallet 4 bought Oct 21 - Nov 16 with a path on disk (allq, cq, since_stop, newq: every trade
# on the coin for 31 minutes from wallet 4's buy). For each wallet: its first buy of a coin inside the path (time from
# wallet 4's buy 0-1200 s, so our 600 s fit), valued at wallet 4's own rate for the quote; its first sale after it;
# and our copy of it with the frozen live setup (landing 4 / 8 trades or the next slot after ITS buy, refused past 1.25x
# of the price its buy left, tp 4.0, its sale followed 30-290 s under 1.5x, sell_pressure [5, 60, 30], stall 180 s,
# 600 s, 0.5 SOL), every copy, no slot limit. The exits are not tuned to any wallet (the lesson of TAB16RxX).
# Wallets that buy before wallet 4 are not seen here (the path starts at its buy): step 2 reads them from their own
# history. A wallet that mostly buys in wallet 4's slot or the next (a follower or a racer of the same signal) is
# marked: it adds no coins.
#   python3 -I screen.py SP > out/screen.txt
import sys, os, json, gzip, collections, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
# FIX=1 (Nov 18): every path put in its true in-slot order first (the cached paths list a busy slot's transactions in
# reverse); writes hunt_screen_fixed.json.gz. Without it, the original run.
FIX = os.environ.get("FIX") == "1"; sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-18/churn"); import slot_order as _SO
SP = sys.argv[1]; MINSOL = float(sys.argv[2]) if len(sys.argv) > 2 else 0.9
W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"; ME = "Eao8T2Pk2aDzPWUFCA8si7oWd5ndFKfnX3HjYMpERst6"
TAB = "TAB16RxXmazWzCTpJbnKiREWUybdEoskuyidaV291u3"
TB = 1793274720 + 600; TC = datetime.datetime(2026, 11, 6, 5, 32, tzinfo=datetime.timezone.utc).timestamp()
blk = lambda t: "A" if t < TB else "B" if t < TC else "C"
coins = {}
for d in ["allq", "cq", "since_stop", "newq"]:
    P = json.load(gzip.open(f"{SP}/{d}/paths.json.gz")); R = {f"{r['slot']}_{r['mint8']}": r for r in json.load(open(f"{SP}/{d}/routable.json"))}
    for k, v in P.items():
        if not v or k not in R: continue
        m, tr = v
        if FIX: tr = _SO.reorder(tr)   # the true in-slot order (Nov 18, 2026-11-18/churn/)
        if m in coins and len(coins[m][1]) >= len(tr): continue
        k4 = next((i for i, e in enumerate(tr) if e["user"] == W4 and e["buy"] and e["slot"] == R[k]["slot"]), None)
        if k4 is None: continue
        e = tr[k4]; rate = R[k]["sol"] * 1e9 / (e["q"] * (1 + e["bps"] / 1e4))
        coins[m] = (k4, tr, rate, R[k]["sol"])
print(f"{len(coins)} coins with wallet 4's buy in the path")
from hunt_lib import prep, model, first
W = collections.defaultdict(list)
for m, (k4, tr, rate, w4sol) in coins.items():
    t4 = tr[k4]["t"]; done = set()
    for i, e in enumerate(tr):
        u = e["user"]
        if u in done or u in (ME,) or not e["buy"]: continue
        if u != W4 and any(x["user"] == u for x in tr[:i]): done.add(u); continue      # it sold before (bought before the path)
        done.add(u)
        if e["t"] - t4 > 1200: continue
        sol = e["q"] * (1 + e["bps"] / 1e4) * rate / 1e9
        if sol < MINSOL: continue
        nxt = next((x for x in tr[i + 1:] if x["user"] == u and not x["buy"]), None)
        net = [model(prep(tr, i, rate, n))[0] for n in (4, 8, "slot+1")]
        W[u].append(dict(m=m, t=e["t"], sol=sol, lag=e["slot"] - tr[k4]["slot"], held=(nxt["t"] - e["t"]) if nxt else None, net=sum(net) / 3,
                         own=(nxt["q"] * rate / 1e9 / sol * (nxt["tok"] / max(1, e["tok"]))) if nxt else None, w4big=w4sol >= 1.3))
print(f"wallets with a {MINSOL}+ SOL buy: {len(W)}; with 20+: {sum(1 for v in W.values() if len(v) >= 20)}")
def row(u, v):
    nets = sorted((x["net"] for x in v), reverse=True); days = len({datetime.datetime.utcfromtimestamp(x['t']).date() for x in v})
    held = [x["held"] for x in v if x["held"] is not None]; sold = len(held)
    b = {k: sum(x["net"] for x in v if blk(x["t"]) == k) for k in "ABC"}
    fol = sum(1 for x in v if x["lag"] <= 1) / len(v)
    alone = [x["net"] for x in v if not x["w4big"]]
    return (f"{u[:8]} {len(v):4d} buys {days:2d} days | size med {np.median([x['sol'] for x in v]):4.2f} | in its slot or next {100 * fol:3.0f}% |"
            f" sold in window {100 * sold / len(v):3.0f}%, held med {np.median(held) if held else 0:5.0f} s, under 30 s {100 * sum(1 for h in held if h < 30) / len(v):3.0f}% |"
            f" OUR COPY {sum(nets):+6.2f} SOL {100 * sum(nets) / len(v) / 0.5:+5.1f}% a copy, w/o best 5 {sum(nets[5:]):+6.2f} | A {b['A']:+5.2f} B {b['B']:+5.2f} C {b['C']:+5.2f}"
            f" | on coins we don't copy (w4 under 1.3): {len(alone)} {sum(alone):+5.2f}")
print("== wallet 4 itself (the reference: its buys of 0.9+ SOL on these coins)")
print(row(W4, W[W4]))
print("== every other wallet with 20+ buys, by our copy's total")
for u, v in sorted(((u, v) for u, v in W.items() if len(v) >= 20 and u != W4), key=lambda x: -sum(y["net"] for y in x[1])):
    print(row(u, v))
json.dump({u: v for u, v in W.items() if len(v) >= 10}, gzip.open(f"{SP}/hunt_screen{'_fixed' if FIX else ''}.json.gz", "wt"))
