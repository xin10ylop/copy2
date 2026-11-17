# Winners first, step 4b: each candidate's own money on its copyable buys (step 4's coins), from its own trades in its
# history: per coin, what its sales brought minus what its buys cost, in SOL (other quotes at Jupiter's price, fees in),
# tokens still held valued at 0 (cautious: a coin still on its curve, or graduated and not sold, counts as lost). Also how
# long it holds (its first sale after its first buy) and how often it sells before graduation.
#   python3 -I w4b_ownpnl.py SP > out/w4b_ownpnl.txt
import sys, os, json, collections, statistics as st
SP = sys.argv[1]; W = f"{SP}/winners"
WSOL = "So11111111111111111111111111111111111111112"; SOLQ = {WSOL, "11111111111111111111111111111111", None}
PR = json.load(open(f"{SP}/market/prices.json")); sol_usd = PR[WSOL]["usdPrice"]
def rate_of(q):
    if q in SOLQ: return 1.0
    return PR[q]["usdPrice"] / sol_usd * 1e9 / 10 ** PR[q]["decimals"] if q in PR else None
res = json.load(open(f"{W}/w4_res.json")) if os.path.exists(f"{W}/w4_res.json") else {}
print("wallet   | period: coins, its net SOL, a coin, won share, best coin | without its best 5 | first sale med s, held at end")
for w in sorted(os.listdir(f"{W}/hist")):
    w = w[:-5]; h = json.load(open(f"{W}/hist/{w}.json")); by = collections.defaultdict(list)
    for e in h["trades"]: by[e["m"]].append(e)
    per = res.get(w)
    if per is None: continue
    out = []
    for k in ("before", "screen", "after"):
        rows = []
        for x in per.get(k, []):
            tr = sorted(by[x["m"]], key=lambda e: e["t"]); rate = rate_of(tr[0]["quote"])
            if rate is None: continue
            cost = sum(e["q"] * (1 + e["bps"] / 1e4) for e in tr if e["buy"]) * rate / 1e9
            got = sum(e["q"] * (1 - e["bps"] / 1e4) for e in tr if not e["buy"]) * rate / 1e9
            tok = sum(e["tok"] for e in tr if e["buy"]) - sum(e["tok"] for e in tr if not e["buy"])
            s1 = next((e["t"] for e in tr if not e["buy"]), None)
            rows.append(dict(net=got - cost, cost=cost, g=x["g"], hold=(s1 - tr[0]["t"]) if s1 else None, left=tok > 0.01 * sum(e["tok"] for e in tr if e["buy"])))
        if not rows: out.append(f"{k}: 0"); continue
        nets = sorted((r["net"] for r in rows), reverse=True); net = sum(nets)
        hold = [r["hold"] for r in rows if r["hold"] is not None]
        out.append(f"{k}: {len(rows)}, {net:+7.2f}, {net / sum(r['cost'] for r in rows):+6.1%}, {sum(r['net'] > 0 for r in rows) / len(rows):3.0%}, best {nets[0]:+.2f} | w/o 5 {sum(nets[5:]):+7.2f} | "
                   f"{st.median(hold) if hold else 0:5.0f} s, {sum(r['left'] for r in rows) / len(rows):3.0%}")
    print(f"{w[:8]} | " + " || ".join(out), flush=True)
