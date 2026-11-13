# paths_long.py from the cache only: the coins whose 2-hour fetch is already complete (every page of signatures and
# every transaction cached); the others are left out. Writes SPD/paths_2h.json.gz.
#   python3 -I paths_long_partial.py SPD
import sys, os, io, contextlib, json, gzip
SPD = sys.argv[1]; HOLD = 7300
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv = ["x", SPD]; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import model as M
class Missing(Exception): pass
def cached(m, p, key=None):
    path = f"{M.CACHE}/{key}.json.gz"
    if not os.path.exists(path): raise Missing(key)
    return json.load(gzip.open(path))
T_STOP = 1793274720 + 600
def path(r):
    m = M.mints.get((r["slot"], r["mint8"]))
    if not m: return None
    anchor = next((s for bt, s in M.w4 if bt >= r["t"] + HOLD), None)
    sigs, before = [], anchor
    while True:
        p = {"limit": 1000}
        if before: p["before"] = before
        page = cached("getSignaturesForAddress", [m, p], key=f"sigs2h_{m[:12]}_{(before or 'now')[:12]}")
        if not page: break
        sigs += [x for x in page if x["err"] is None and x["slot"] >= r["slot"]]
        if page[-1]["slot"] < r["slot"] or len(page) < 1000: break
        before = page[-1]["signature"]
    txs = [cached("getTransaction", [x["signature"], M.TXO], key=f"tx_{x['signature'][:24]}") for x in sigs]
    tr = [e for tx in txs if tx for e in M.trades(tx, m)]
    order = {}
    for s in (r["slot"], r["slot"] + 1, r["slot"] + 2):
        try: b = cached("getBlock", [], key=f"blk_{s}")
        except Missing: b = None
        if b: order.update({sg: (s, i) for i, sg in enumerate(b["signatures"])})
    tr.sort(key=lambda e: order.get(e["sig"], (e["slot"], 10**6)))
    return m, tr
rows = [r for r in M.rows if r["t"] >= T_STOP]; out = {}
for r in rows:
    try:
        res = path(r)
        if res: out[f"{r['slot']}_{r['mint8']}"] = res
    except Missing: pass
json.dump(out, gzip.open(f"{SPD}/paths_2h.json.gz", "wt"))
print(f"{len(out)} of {len(rows)} coins complete in the cache")
