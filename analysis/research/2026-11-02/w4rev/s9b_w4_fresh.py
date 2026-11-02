# Step 4b: wallet 4's curve buys of Oct 28 00:00 - Nov 1 21:30 UTC from its own signatures (Triton): each landed
# transaction read, its pump TradeEvents with user = wallet 4 and a buy; the coin's create from the fresh universe
# (slot gap ds) and the buy's SOL value at pump's price of the quote x the class factor (as s5_sim.py).
#   python3 -I s9b_w4_fresh.py [THREADS=10] -> out/w4_fresh.json {mint: {slot, ds, v, ix}}
import sys, os, time, calendar, collections
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib, routes
TH = int(sys.argv[1]) if len(sys.argv) > 1 else 10; lib.crc.MIN_GAP = 0.03
LO, HI = calendar.timegm((2026, 10, 28, 0, 0, 0)), calendar.timegm((2026, 11, 1, 21, 30, 0))
U = {r["mint"]: r for r in lib.jl(lib.OUT + "/qc_creates_1793059200_1793574000.json").values() if r.get("mint")}
rows = lib.sigs(lib.W4, limit=1000)
while rows and rows[-1]["blockTime"] >= LO:
    page = lib.sigs(lib.W4, before=rows[-1]["signature"], limit=1000)
    if not page: break
    rows += page
S = [r for r in rows if r.get("err") is None and LO <= (r.get("blockTime") or 0) < HI]
print(time.strftime("%H:%M:%S"), f"wallet 4: {len(rows)} signatures listed, {len(S)} landed in the window", flush=True)
FACT = {"C": 1.130, "A": 0.892, "B": 0.892}
def one(r):
    t = lib.tx(r["signature"])
    if not t: return []
    out = []
    for k, e in lib.events(t):
        if k == "trade" and e["user"] == lib.W4 and e["is_buy"]: out.append((e["mint"], t["slot"], e))
    return out
B = {}
with ThreadPoolExecutor(TH) as ex:
    for res in ex.map(one, S):
        for m, slot, e in res:
            if m in B and B[m]["slot"] <= slot: continue
            c = U.get(m); cls = routes.cls(c["quote"]) if c else None
            v = None
            if c and cls in FACT and c.get("vquote"): v = (e.get("quote_amount") or 0) * 30 * FACT[cls] / c["vquote"]
            elif e.get("quote_mint") in lib.SOL_LIKE or not e.get("vquote"): v = e["sol"] / 1e9
            B[m] = dict(slot=slot, ds=(slot - c["cslot"]) if c else None, v=v, cls=cls, ix=e.get("ix"))
lib.jdump(B, lib.OUT + "/w4_fresh.json")
c = collections.Counter((b["cls"], b["ds"] is not None and b["ds"] <= 1, (b["v"] or 0) >= 1.45) for b in B.values())
print(f"{len(B)} coins bought; (class, at +0/+1, 1.45+) -> count:", sorted(c.items(), key=str))
print("calls", lib.crc.NCALLS[0])
