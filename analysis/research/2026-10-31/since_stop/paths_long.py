# Each coin's trades for 2 hours (7,300 s) after wallet 4's buy instead of 31 minutes, for the long-hold test, through
# model.py's fetcher (Triton, cached per transaction in SPD/cache). Writes SPD/paths_2h.json.gz in paths.json.gz's
# format. Only the coins since the stop (Oct 29 12:02 UTC) to the end of the data.
#   python3 -I paths_long.py SPD
import sys, os, io, contextlib, json, gzip, concurrent.futures as cf
SPD = sys.argv[1]; HOLD = 7300
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv = ["x", SPD]; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import model as M
T_STOP = 1793274720 + 600
def path(r):
    m = M.mints.get((r["slot"], r["mint8"]))
    if not m: return None
    anchor = next((s for bt, s in M.w4 if bt >= r["t"] + HOLD), None)
    sigs, before = [], anchor
    while True:
        p = {"limit": 1000}
        if before: p["before"] = before
        page = M.call("getSignaturesForAddress", [m, p], key=f"sigs2h_{m[:12]}_{(before or 'now')[:12]}")
        if not page: break
        sigs += [x for x in page if x["err"] is None and x["slot"] >= r["slot"]]
        if page[-1]["slot"] < r["slot"] or len(page) < 1000: break
        before = page[-1]["signature"]
    with cf.ThreadPoolExecutor(12) as ex:
        txs = list(ex.map(lambda x: M.call("getTransaction", [x["signature"], M.TXO], key=f"tx_{x['signature'][:24]}"), sigs))
    tr = [e for tx in txs if tx for e in M.trades(tx, m)]
    order = {}
    for s in (r["slot"], r["slot"] + 1, r["slot"] + 2):
        b = M.call("getBlock", [s, {"encoding": "json", "transactionDetails": "signatures", "maxSupportedTransactionVersion": 1, "rewards": False}], key=f"blk_{s}")
        if b: order.update({sg: (s, i) for i, sg in enumerate(b["signatures"])})
    tr.sort(key=lambda e: order.get(e["sig"], (e["slot"], 10**6)))
    return m, tr
rows = [r for r in M.rows if r["t"] >= T_STOP]
out = {}
for i, r in enumerate(rows):
    try:
        res = path(r)
        if res: out[f"{r['slot']}_{r['mint8']}"] = res
    except Exception as e: print("failed", r["mint8"], str(e)[:80], flush=True)
    if i % 20 == 0: print(i, "of", len(rows), flush=True)
json.dump(out, gzip.open(f"{SPD}/paths_2h.json.gz", "wt"))
print("done", len(out), "paths", flush=True)
