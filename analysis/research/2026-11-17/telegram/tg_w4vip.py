# Wallet 4 and the SolHouse VIP (the owner, Nov 17: "you are blindly computing numbers without thinking logically"). The
# money after a VIP alert goes to whoever held the coin before it (75% of the SOL sold in the 2 min after an alert comes
# from earlier holders, tg_vip_why.py), and wallet 4 bought first on 897 of the 905 coins both touched, a median 91 s
# earlier. So our bot, copying wallet 4, often holds a coin when the VIP alerts it: the alert brings a wave of buyers.
# This compares the bot's frozen exits (hunt_lib.model: tp 4, its sale at 30-290 s under 1.5x, sell pressure [5, 60, 30],
# stall 180 s, 600 s) with selling X seconds after the alert (the frozen exits stay; whichever comes first), on the coins
# priced in the bot's floats that wallet 4 bought with 1.3+ SOL and the VIP alerted within 600 s (w4vip/, every trade).
# Two weeks apart: the VIP exports of Nov 1-6 and Nov 10-17; X is picked on one and scored on the other.
#   python3 -I tg_w4vip.py TGDIR > out/tg_w4vip.txt
import sys, os, json, gzip, urllib.request, numpy as np
TG = sys.argv[1]; D = f"{TG}/w4vip"; here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-17/wallet_hunt"); import hunt_lib as H
cns = {}; sys.argv = ["x", TG]; exec(open(os.path.join(here, "tg_channel.py")).read().split("for cj in sorted(glob.glob")[0], cns); order_slots = cns["order_slots"]
W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"; WSOL = "So11111111111111111111111111111111111111112"
FLOATS = {"WBTC": "3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh", "PUMP": "pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn", "SPCX": "SPCXxcqXj6e5dJDVNovHN8744zkbhM2bYudU45BimGb",
          "TTWO": "TTWofwAge91oFhZs7kpQdyrVRkmevgM88xijGvQFbKo", "DJT": "DJTu7vi8norVzdVAffgvb39VP7wjKeTsgaMBJrzfxvoF", "HYPE": "98sMhvDwXj1RQi5c5Mndm3vPe9cBqPrbLaufMXFNMh5g"}
pr = json.load(urllib.request.urlopen(urllib.request.Request(f"https://lite-api.jup.ag/price/v3?ids={','.join(list(FLOATS.values()) + [WSOL])}"), timeout=30))
rate = {s: pr[m]["usdPrice"] / pr[WSOL]["usdPrice"] * 1e9 / 10 ** pr[m]["decimals"] for s, m in FLOATS.items() if m in pr}   # lamports per raw unit (today's prices)
A = json.load(open(f"{D}/alerts.json")); SPLIT = 1794355200   # Nov 10 00:00 UTC: the two VIP exports
rows, cnt = [], {}
def c(k): cnt[k] = cnt.get(k, 0) + 1
for m, (t_alert, t_w4, sym) in A.items():
    if sym not in rate: c("quote not one of the bot's floats"); continue
    f = f"{D}/paths/{m}.json.gz"
    if not os.path.exists(f): c("not fetched"); continue
    tr = order_slots(json.load(gzip.open(f)).get("tr") or [])
    k = next((i for i, e in enumerate(tr) if e["user"] == W4 and e["buy"] and abs(e["t"] - t_w4) <= 3), None)
    if k is None: c("wallet 4's buy not in the path"); continue
    sol = tr[k]["q"] * rate[sym] / 1e9
    if sol < 1.3: c("its buy under 1.3 SOL (the bot skips it)"); continue
    p = H.prep(tr, k, rate[sym], "slot+1")
    if p["refused"]: c("refused (1.25x)"); continue
    c("modelled"); rows.append(dict(m=m, t=t_w4, lead=t_alert - t_w4, p=p, base=H.model(p)[0], why=H.model(p)[1]))
print("coins:", ", ".join(f"{k} {v}" for k, v in sorted(cnt.items(), key=lambda x: -x[1])))
def alt(r, X): return H.model(r["p"], hold=min(600, r["lead"] + X))[0]
for name, R in (("Nov 1-6", [r for r in rows if r["t"] < SPLIT]), ("Nov 10-17", [r for r in rows if r["t"] >= SPLIT]), ("both", rows)):
    if not R: continue
    b = [r["base"] for r in R]
    print(f"\n{name}: {len(R)} copies at 0.5 SOL; the alert came a median {np.median([r['lead'] for r in R]):.0f} s after wallet 4's buy")
    print(f"  the bot's frozen exits:        {sum(b):+6.2f} SOL ({np.mean(b) / 0.5:+6.1%} a copy), won {np.mean([x > 0 for x in b]):.0%}")
    for X in (0, 5, 15, 30, 60, 120):
        a = [alt(r, X) for r in R]
        print(f"  sell {X:3d} s after the alert:     {sum(a):+6.2f} SOL ({np.mean(a) / 0.5:+6.1%} a copy), won {np.mean([x > 0 for x in a]):.0%} | better on {np.mean([x > y + 1e-9 for x, y in zip(a, b)]):.0%}, worse on {np.mean([x < y - 1e-9 for x, y in zip(a, b)]):.0%}")
    print("  the frozen exits' reasons: " + ", ".join(f"{k} {v}" for k, v in sorted({w: sum(r['why'] == w for r in R) for w in {r['why'] for r in R}}.items(), key=lambda x: -x[1])))
