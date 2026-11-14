# Are the PUMP- and SPCX-priced coins' trade events read right? Wallet 4's own result per coin from the events in the
# path (its buys: quote in plus the fee; its sales: quote out less the fee) against its token balances in its own
# transactions (the chain's truth), for coins it bought once and sold out within the 31 minutes.
#   python3 -I decode_check.py SPD
import sys, os, json, collections, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lib as L
SPD = sys.argv[1]; rows, P, info = L.load(SPD)
want = {r["slot"]: r for r in rows if r["anchor"] in ("PUMP", "SPCX") and r["hops"] == 1}
QUOTE = {"PUMP": "pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn", "SPCX": "SPCXxcqXj6e5dJDVNovHN8744zkbhM2bYudU45BimGb"}
chain = collections.defaultdict(lambda: [0, 0, 0])       # mint -> quote out, quote back, coin held (from its transactions)
mint_of = {}
for f in os.listdir(f"{SPD}/w4tx"):
    t = json.load(open(f"{SPD}/w4tx/{f}")); m = t["meta"]
    if m.get("err"): continue
    d = collections.defaultdict(int)
    for k, s in (("preTokenBalances", -1), ("postTokenBalances", 1)):
        for b in m.get(k) or []:
            if b.get("owner") == L.W4: d[b["mint"]] += s * int(b["uiTokenAmount"]["amount"])
    d = {k: v for k, v in d.items() if v}
    q = [k for k in d if k in QUOTE.values()]; c = [k for k in d if k not in QUOTE.values() and not k.startswith("So1111")]
    if len(q) != 1 or len(c) != 1: continue
    x = chain[c[0]]; x[2] += d[c[0]]
    if d[c[0]] > 0: x[0] += -d[q[0]]
    else: x[1] += d[q[0]]
    if t["slot"] in want and c[0].startswith(want[t["slot"]]["mint8"]): mint_of[t["slot"]] = c[0]
out = collections.defaultdict(list); bps = collections.defaultdict(list)
for slot, r in want.items():
    m = mint_of.get(slot)
    if not m or chain[m][2] != 0 or chain[m][0] <= 0: continue
    tr = P[r["key"]][1]; sp = bk = 0; held = 0
    for e in tr:
        if e["user"] != L.W4: continue
        if e["buy"]: sp += e["q"] * (1 + e["bps"] / 1e4); held += e["tok"]
        else: bk += e["q"] * (1 - e["bps"] / 1e4); held -= e["tok"]
        bps[r["anchor"]].append(e["bps"])
    if held != 0 or sp <= 0: continue
    out[r["anchor"]].append((100 * (bk - sp) / sp, 100 * (chain[m][1] - chain[m][0]) / chain[m][0], sp / chain[m][0]))
for a, v in out.items():
    d = [x[0] - x[1] for x in v]
    print(f"{a}: {len(v)} coins; its result from the events {statistics.mean(x[0] for x in v):+.1f}% a coin, from its balances {statistics.mean(x[1] for x in v):+.1f}%; "
          f"difference per coin: median {statistics.median(d):+.2f} points, worst {max(d, key=abs):+.2f}; its spend, events / balances: median {statistics.median(x[2] for x in v):.4f}; "
          f"fee in its events: {collections.Counter(bps[a]).most_common(3)} bps")
