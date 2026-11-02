# Step 4 (light): what wallet 4 traded lately. Its signatures from now back to Oct 27 00:00 UTC (paged), a seeded
# sample of N landed ones read (Triton), its own pump TradeEvents decoded: the coin, buy or sell, the curve's quote, the
# quote amount. A buy's SOL value: quote amount x the quote's last own-swap price (prices.py, to Oct 27) or, without one,
# Jupiter's price now (out/jup.json: usd / SOL usd); SOL-quoted coins by their lamports. Launch buy = its buy in the
# coin's create slot or the next (the create from the part-A agent's Oct 27 - Nov 1 quote-control read). Scaled to all
# of its landed signatures by day.   python3 -I w1_recent.py [N=2000] -> out/w4_recent.json
import sys, os, time, random, collections
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blib, prices, u1_universe as u1
N = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
F_LO = 1793059200
sp = blib.OUT + "/w4_sigs.json"
if os.path.exists(sp): L = blib.jl(sp)
else:
    L = []; before = None
    while True:
        page = blib.sigs(blib.W4, before=before, limit=1000, cache=False)
        if not page: break
        L += [[p["signature"], p["slot"], p.get("blockTime"), p.get("err") is not None] for p in page]
        before = page[-1]["signature"]
        if (page[-1].get("blockTime") or 0) < F_LO: break
    L = [r for r in L if (r[2] or 0) >= F_LO]; blib.jdump(L, sp)
ok = [r for r in L if not r[3]]
print(f"its signatures since Oct 27 00:00: {len(L)}, landed {len(ok)}, {time.strftime('%F %T', time.gmtime(min(r[2] for r in L)))} .. {time.strftime('%F %T', time.gmtime(max(r[2] for r in L)))} UTC")
byd = collections.Counter(time.strftime("%m-%d", time.gmtime(r[2])) for r in ok)
rnd = random.Random(20261104); pick = rnd.sample(ok, min(N, len(ok)))
FT = {t["mint"]: t for t in blib.jl(blib.OUT + "/fresh_table.json")}
QC = {r["mint"]: r for r in blib.jl(blib.A_OUT + "/qc_creates_1793059200_1793574000.json").values() if r.get("mint")}
J = blib.jl(blib.OUT + "/jup.json")
def sol_value(q, amt, bt):
    if q in blib.SOL_LIKE: return amt / 1e9
    v = prices.lamports_per_raw(q, bt)
    if v: return amt * v / 1e9
    j = J.get(q) or {}
    if j.get("usd") and j.get("sol_usd") and j.get("dec") is not None: return amt / 10 ** j["dec"] * j["usd"] / j["sol_usd"]
    return None
def one(r):
    try: t = blib.tx(r[0])
    except Exception as e: return r, None
    if not t: return r, None
    out = []
    for kind, e in blib.events(t):
        if kind != "trade" or e["user"] != blib.W4: continue
        q = e.get("quote_mint"); q = None if q in blib.SOL_LIKE else q
        amt = e.get("quote_amount") if q else e["sol"]
        out.append(dict(m=e["mint"], buy=int(e["is_buy"]), q=q, amt=amt, slot=t["slot"], bt=t.get("blockTime")))
    return r, out
rows = []
with ThreadPoolExecutor(8) as ex:
    for r, out in ex.map(one, pick):
        for x in out or []:
            x["day"] = time.strftime("%m-%d", time.gmtime(x["bt"])); x["scale"] = byd[x["day"]] / sum(1 for p in pick if time.strftime("%m-%d", time.gmtime(p[2])) == x["day"])
            x["cls"] = "S" if not x["q"] else u1.cls(x["q"]) if x["q"] in u1.POOLS or x["q"] == blib.WBTC else None
            if x["cls"] is None: u1.ensure([x["q"]]); x["cls"] = u1.cls(x["q"])
            x["sol"] = sol_value(x["q"], x["amt"], x["bt"])
            c = QC.get(x["m"]); x["ds"] = (x["slot"] - c["cslot"]) if c else None
            rows.append(x)
blib.jdump(rows, blib.OUT + "/w4_recent.json")
B = [x for x in rows if x["buy"]]
print(f"sampled {len(pick)} landed txs: its trades {len(rows)}, buys {len(B)}; calls {blib.calls()}")
days = sorted(byd)
print("\nits buys a day (scaled from the sample): all / part B (class E) / part B at launch / part B 1.45+ SOL at launch; and other classes")
for d in days:
    D = [x for x in B if x["day"] == d]; s = lambda f: sum(x["scale"] for x in D if f(x))
    print(f"  {d}: all {s(lambda x: True):6.0f}  B {s(lambda x: x['cls'] == 'E'):6.0f}  B launch {s(lambda x: x['cls'] == 'E' and x['ds'] is not None and x['ds'] <= 1):6.0f}"
          f"  B launch 1.45+ {s(lambda x: x['cls'] == 'E' and x['ds'] is not None and x['ds'] <= 1 and (x['sol'] or 0) >= 1.45):5.0f}"
          f"  | A/B/C routable {s(lambda x: x['cls'] in ('A', 'B', 'C')):5.0f}  SOL {s(lambda x: x['cls'] == 'S'):5.0f}")
print("\nits part-B launch buys by quote (scaled), all sizes [1.45+], by day:")
qs = collections.Counter()
for x in B:
    if x["cls"] == "E" and x["ds"] is not None and x["ds"] <= 1: qs[x["q"]] += x["scale"]
for q, n in qs.most_common(15):
    cells = []
    for d in days:
        D = [x for x in B if x["day"] == d and x["q"] == q and x["ds"] is not None and x["ds"] <= 1]
        cells.append(f"{sum(x['scale'] for x in D):4.0f} [{sum(x['scale'] for x in D if (x['sol'] or 0) >= 1.45):3.0f}]")
    print(f"  {u1.sym(q):10s} " + "  ".join(f"{d[3:]}: {c}" for d, c in zip(days, cells)))
