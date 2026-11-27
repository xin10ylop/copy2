# The floats' sizes again (Nov 27, ../../2026-11-26/uncopied2/u5_floats.py on fresh 7-day histories histfl_, the 12 units
# running on Nov 27 at their stakes and floors, the sizes since Nov 26). From Nov 26: the owner: "lets add floats, and the floats balances, review them, we have 7 sol free").
# Every copyable coin over the last DAYS days of the ten wallets' histories (first buy at the unit's floor, the unit's coin
# kind) priced in each float or candidate token, the units' stakes as they run (qqq and uuu 1.0 SOL, the rest 0.5), each
# copy holding the float's SOL for the unit's longest hold (qqq 600 s, ppp 120 s, the rest 420 s: an upper bound). Per
# token: copies, the most SOL tied up at once, and how many copies a float of each size would skip (under
# float_min_frac = 0.5 of the stake left) or shrink (part of the stake).
#   python3 -I u5_floats.py SP DAYS
import sys, json, collections, time
SP, DAYS = sys.argv[1], float(sys.argv[2]); T0 = time.time() - DAYS * 86400
UNITS = [("qqq", "H9kuqGKN", "token", 1.3, 1.0, 600), ("eee", "CgyPomTG", "all", 0.5, 0.5, 420), ("rrr", "3XeFcZKS", "token", 0.5, 0.5, 420),
         ("ttt", "6LwMLkCe", "token", 0.5, 0.5, 420), ("yyy", "6nNzEg86", "token", 0.25, 0.5, 420), ("uuu", "GqWfqfG6", "all", 0.5, 1.0, 420),
         ("iii", "Bing35WC", "all", 0.5, 1.0, 420), ("ooo", "HtHkKxYN", "all", 0.5, 0.5, 420), ("ppp", "3SiQo8MJ", "token", 0.1, 0.25, 120),
         ("ddd", "E2XwSeqe", "all", 0.5, 0.5, 420), ("fff", "E5CLHHz6", "all", 0.5, 0.5, 420), ("hhh", "2GJUPUrk", "all", 0.5, 0.5, 420)]
TOK = {"SQQQAa3g": "SQQQ", "3NZ9JMVB": "WBTC", "pumpCmXq": "PUMP", "SPCXxcqX": "SPCX", "TTWofwAg": "TTWO", "he1iusmf": "hSOL", "98kfF7rm": "PAID",
       "Xsc9qvGR": "NVDAx", "EPjFWdd5": "USDC", "ANTBTZQ1": "ANT", "GTA6ot7g": "GTA6", "XsDoVfqe": "TSLAx", "B34nXKzC": "B34nXKzC"}
LEVEL = {"WBTC": 0.5, "PUMP": 1.0, "SPCX": 1.0, "TTWO": 2.5, "hSOL": 2.0, "PAID": 0.6, "NVDAx": 1.5, "USDC": 1.0}   # config/float-levels.live, Nov 26
# the coin's quote for each wallet's first buy, its size in SOL: the price of each quote at its trade, from its own buy
ev = collections.defaultdict(list)
for lab, w8, kind, mn, stake, hold in UNITS:
    seen, tr = set(), []
    for l in open(f"{SP}/histfl_{w8}/{w8}_trades.jsonl"):
        for e in json.loads(l)["trades"] or []:
            k = (e["m"], e["slot"], e["buy"], e["q"], e["tok"])
            if k not in seen: seen.add(k); tr.append(e)
    by = collections.defaultdict(list)
    for e in tr: by[e["m"]].append(e)
    for m, es in by.items():
        es.sort(key=lambda e: (e["slot"], not e["buy"]))
        f = es[0]; q = (f["quote"] or "")[:8]
        if not f["buy"] or q not in TOK or f["t"] < T0: continue
        sol = f.get("sol") if f.get("sol") is not None else None
        ev[TOK[q]].append((f["t"], lab, stake, hold, f["q"], m))
# sizes: the buy's SOL value is not in the history for token quotes; count every first buy of a coin in these tokens that
# its unit's kind takes, and its floor through the token's SOL price now (Jupiter)
import urllib.request
SOLM = "So11111111111111111111111111111111111111112"
full = {}
for l in open(f"{SP}/quiet/quotes.txt"): full[l.strip()[:8]] = l.strip()
ids = [full[k] for k in TOK if k in full] + [SOLM]
P = {}
for a in range(5):
    try: P = json.load(urllib.request.urlopen("https://lite-api.jup.ag/price/v3?ids=" + ",".join(ids), timeout=20)); break
    except Exception: time.sleep(3 * (a + 1))
su = P[SOLM]["usdPrice"]
rate = {TOK[k]: P[full[k]]["usdPrice"] / su / 10 ** P[full[k]]["decimals"] for k in TOK if k in full and full[k] in P}
FLOOR = {lab: mn for lab, _, _, mn, _, _ in UNITS}
print(f"the last {DAYS:.0f} days: copyable coins priced in each token (first buy at its unit's floor), SOL a copy ties up, and a float's size")
print(f"  {'token':9s} {'now':>5s} {'copies':>6s} {'a day':>6s} {'most at once':>12s}   skipped / shrunk at: now | SIZES    by unit")
for tk in sorted(ev, key=lambda k: -len(ev[k])):
    rows = sorted((t, lab, stake, hold) for t, lab, stake, hold, qty, m in ev[tk] if tk in rate and qty * rate[tk] >= FLOOR[lab])
    if not rows: continue
    peak, opens = 0.0, []
    for t, lab, stake, hold in rows:
        opens = [(e, s) for e, s in opens if e > t]; opens.append((t + hold, stake)); peak = max(peak, sum(s for _, s in opens))
    def sim(level):
        sk = sh = 0; opens = []
        for t, lab, stake, hold in rows:
            opens = [(e, s) for e, s in opens if e > t]; free = level - sum(s for _, s in opens)
            if free < 0.5 * stake: sk += 1; continue
            use = min(stake, free); sh += use < stake; opens.append((t + hold, use))
        return f"{sk}/{sh}"
    units = collections.Counter(lab for _, lab, _, _ in rows)
    print(f"  {tk:9s} {LEVEL.get(tk, 0):5.1f} {len(rows):6d} {len(rows) / DAYS:6.1f} {peak:10.1f} SOL   " + " | ".join(sim(x) for x in (LEVEL.get(tk, 0),) + tuple(float(v) for v in __import__("os").environ.get("SIZES", "1.0,1.5,2.0").split(",")))
          + "    " + ", ".join(f"{k} {v}" for k, v in units.most_common()))

rows = []
for lab, w8, kind, mn, stake, hold in UNITS:
    if kind != "all": continue
    seen = set(); tr = []
    for l in open(f"{SP}/histfl_{w8}/{w8}_trades.jsonl"):
        for e in json.loads(l)["trades"] or []:
            k = (e["m"], e["slot"], e["buy"], e["q"], e["tok"])
            if k not in seen: seen.add(k); tr.append(e)
    first = {}
    for e in sorted(tr, key=lambda e: (e["slot"], not e["buy"])): first.setdefault(e["m"], e)
    for f in first.values():
        if f["buy"] and (not f["quote"] or f["quote"].startswith("1111")) and f["t"] >= T0 and f["q"] / 1e9 >= mn: rows.append((f["t"], stake, hold))
rows.sort(); opens = []; peak = 0; over = collections.Counter()
for t, stake, hold in rows:
    opens = [(e, s) for e, s in opens if e > t]; opens.append((t + hold, stake)); n = sum(s for _, s in opens); peak = max(peak, n)
    for x in (1.5, 2.0, 2.5, 3.0): over[x] += n > x
print(f"SOL coins (paid with SOL): {len(rows)} copies, the most SOL tied up at once {peak:.1f}; copies that found more than X tied up: " + ", ".join(f"{x} SOL {over[x]}" for x in (1.5, 2.0, 2.5, 3.0)))
