# The paper run's skips (05-live/long-paper-history-and-journal-2026-10-28.txt, Oct 27 16:11 -> Oct 28 13:13 UTC) matched
# to its transactions (H9kuqGKN.jsonl, re-fetched to Oct 28 14:54): the token it paid with, the size of the buy in SOL
# (the quote it paid the curve, or its route's input, at the token's price: its own swaps of that token against SOL in
# the rows, ledger.py's way, else Jupiter's price now), and whether a PumpSwap pool from wSOL reaches the token
# (SPX/pools.json).   python3 -I skips.py
import sys, os, json, re, datetime, collections, bisect, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim
SPX = "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/more"
J = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "05-live", "long-paper-history-and-journal-2026-10-28.txt")
W, WSOL = sim.W, sim.WSOL
PL = json.load(open(f"{SPX}/pools.json"))["tokens"]
rows = sorted(sim.ROWS, key=lambda r: (r["s"], r["i"] or 0))
# SOL per token from its own one-token swaps against SOL (ledger.py's tokp)
tokp = collections.defaultdict(list)
for r in rows:
    sol = r["d"] + r["tok"].get(WSOL, [0])[0]
    tk = {m: v[0] / 10 ** v[1] for m, v in r["tok"].items() if m != WSOL}
    fee = ((r["fee"] or 0) + (r["tip"] or 0)) if r["signer"] else 0
    if len(tk) == 1:
        (m, q), = tk.items(); s = (sol + fee) / 1e9
        if q and abs(s) > 0.01 and s * q < 0: tokp[m].append((r["bt"], -s / q))
def near(m, t):
    ser = tokp.get(m)
    if not ser: return None
    k = bisect.bisect_left([x[0] for x in ser], t)
    c = [ser[j] for j in (k - 1, k) if 0 <= j < len(ser)]
    best = min(c, key=lambda x: abs(x[0] - t))
    return best[1] if abs(best[0] - t) < 6 * 3600 else None
skips = []
for line in open(J):
    mm = re.search(r"^(\w+ \d+ [\d:]+) .*long (skip|paper-buy) #?(\d+ )?(\w{8}) its ([\d.?]+) SOL( route| \((\w+)\): (.*))?", line)
    if not mm: continue
    t = datetime.datetime.strptime("2026 " + mm.group(1), "%Y %b %d %H:%M:%S").replace(tzinfo=datetime.timezone.utc).timestamp()
    skips.append(dict(t=t, what=mm.group(2), pre=mm.group(4), its=mm.group(5), kind=mm.group(7), why=(mm.group(8) or "").strip()))
ids = sorted({m for r in rows for m in r["tok"]} - {WSOL})
need = set()
out = []
for k in skips:
    if k["what"] != "skip": continue
    cand = [(abs(r["bt"] - k["t"]), r, t) for r in rows if abs(r["bt"] - k["t"]) < 120 for t in r["tr"] if t[1] == W and t[2] == 1 and t[0].startswith(k["pre"])]
    if not cand: out.append(dict(k, found=False)); continue
    _, r, t = min(cand, key=lambda c: c[0])
    others = {m: v for m, v in r["tok"].items() if m not in (t[0], WSOL)}
    pay = min(others, key=lambda m: others[m][0]) if others else None   # the token it spent most of
    amt = -others[pay][0] / 10 ** others[pay][1] if pay else None
    out.append(dict(k, found=True, mint=t[0], pay=pay, amt=amt, sig=r["sig"], quote_raw=t[3])); need.add(pay)
px = {}
idl = sorted(x for x in need if x) + [WSOL]
for i in range(0, len(idl), 50):
    with urllib.request.urlopen("https://lite-api.jup.ag/price/v3?ids=" + ",".join(idl[i:i + 50]), timeout=30) as f: px.update(json.load(f))
solusd = px[WSOL]["usdPrice"]
for o in out:
    if not o.get("found") or not o["pay"]: continue
    p = near(o["pay"], o["t"]); o["src"] = "its swaps" if p else "jupiter now"
    if p is None and (px.get(o["pay"]) or {}).get("usdPrice"): p = px[o["pay"]]["usdPrice"] / solusd
    o["sol"] = o["amt"] * p if (p and o["amt"] and o["amt"] > 0) else None
for o in out:                                      # the bot's own value when it had one (a Jupiter leg, wSOL)
    if o.get("found") and o["its"] != "?": o["sol"], o["src"] = float(o["its"]), "journal"
json.dump(out, open(f"{SPX}/skips.json", "w"))
NAMES = {"pumpCmXq": "PUMP", "CARDSccU": "CARDS", "TTWofwAg": "TTWO", "EPjFWdd5": "USDC", "A7bdiYdS": "A7bd", "WXMRyRZh": "WXMR", "6GmAFSYs": "6GmA"}
print(f"journal skips {len(out)}: " + ", ".join(f"{k} {v}" for k, v in collections.Counter(o['why'][:40] for o in out).items()))
print(f"matched to its transaction: {sum(o.get('found', False) for o in out)}")
g = collections.defaultdict(list)
for o in out:
    if not o.get("found"): continue
    tier = "?" if o.get("sol") is None else ("1.45+" if o["sol"] >= 1.45 else "0.8-1.45" if o["sol"] >= 0.8 else "<0.8")
    g[(o["why"][:28], NAMES.get((o["pay"] or "SOL")[:8], (o["pay"] or "SOL")[:8]))].append(tier)
print(f"   {'why':30s} {'paid in':8s} {'n':>3s}  {'1.45+':>5s} {'0.8-1.45':>8s} {'<0.8':>5s} {'?':>3s}  wSOL pool (best SOL side)")
for (why, pay), v in sorted(g.items(), key=lambda kv: -len(kv[1])):
    full = next((m for m in PL if m.startswith(pay) or NAMES.get(m[:8]) == pay), None)
    ws = (PL.get(full) or {}).get("pools", {}).get("wsol") or []
    c = collections.Counter(v)
    print(f"   {why:30s} {pay:8s} {len(v):3d}  {c['1.45+']:5d} {c['0.8-1.45']:8d} {c['<0.8']:5d} {c['?']:3d}  "
          f"{(f'{len(ws)} pools, {ws[0][chr(115)+chr(111)+chr(108)+chr(95)+chr(115)+chr(105)+chr(100)+chr(101)]:.1f} SOL' if ws else 'none')}")
big = [o for o in out if o.get("sol") and o["sol"] >= 1.45]
print(f"skips of 1.45+ SOL buys: {len(big)} in {(skips[-1]['t'] - skips[0]['t']) / 3600:.1f} h; sizes: " + ", ".join(f"{o['sol']:.2f}" for o in big))
