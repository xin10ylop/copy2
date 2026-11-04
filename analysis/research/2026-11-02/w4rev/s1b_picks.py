# Step 1b: wallet 4's other-quote pump buys (H9kuqGKN_trips.json, Oct 19 - Oct 27 00:40 UTC), each tied to its coin's
# create: the landed + failed signatures on the mint before its buy (getSignaturesForAddress, before = its buy), the
# oldest of them read and decoded (CreateEvent: quote, creator, name, symbol, uri; the trades in the create tx).
#   python3 -I s1b_picks.py [THREADS=8] -> out/picks.json {mint: row}
import sys, os, time, collections
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
from s1b_crow import crow
TH = int(sys.argv[1]) if len(sys.argv) > 1 else 8
T = lib.jl(lib.H9 + "/H9kuqGKN_trips.json")
rows = [lib.json.loads(l) for l in open(lib.H9 + "/H9kuqGKN.jsonl")]
by = {(t[0], r["s"], t[2]): r for r in rows for t in r["tr"] if t[1] == lib.W4}
oq = [x for x in T if x["kind"] == "pump, other quote" and x["tr"][0]["buy"] == 1]
op = lib.OUT + "/picks.json"; have = lib.jl(op) if os.path.exists(op) else {}
def one(x):
    m = x["m"]
    if m in have and "err" not in have[m]: return m, have[m]
    b = x["tr"][0]; r = by.get((m, b["s"], 1))
    out = dict(bslot=b["s"], bidx=b["i"], bbt=b["bt"], v=b["v"], vt=b["vt"], ix=b["ix"], tip=b["tip"], net=x["net"])
    if not r: out["err"] = "no row"; return m, out
    out["bsig"] = r["sig"]
    try:
        page = lib.sigs(m, before=r["sig"], limit=1000)
        out["n_before"] = len(page); out["n_before_landed"] = sum(1 for p in page if p.get("err") is None)
        if len(page) == 1000: out["far"] = True; return m, out
        old = [p for p in page if p.get("err") is None]
        if not old: out["err"] = "no landed before"; return m, out
        c = None
        for p in reversed(old[-8:]):            # the oldest landed one is the create, or one of the next few (a transfer to the mint first)
            cs = p["signature"]; t = lib.tx(cs)
            c = crow(t, cs) if t else None
            if c and c["mint"] == m: break
            c = None
        if not c: out["err"] = "no create among the 8 oldest"; return m, out
        old = [p for p in old if p["slot"] >= c["cslot"]]
        out.update(c); out["ds"] = b["s"] - c["cslot"]
        out["before"] = [[p["signature"], p["slot"]] for p in reversed(old)]
    except Exception as e:
        out["err"] = lib.red(e)[:160]
    return m, out
t0 = time.time(); n = 0
with ThreadPoolExecutor(TH) as ex:
    for m, row in ex.map(one, oq):
        have[m] = row; n += 1
        if n % 500 == 0: print(time.strftime("%H:%M:%S"), n, "/", len(oq), f"calls {lib.crc.NCALLS[0]}", flush=True); lib.jdump(have, op)
lib.jdump(have, op)
G = [have[x["m"]] for x in oq]
print(f"{len(G)} buys; errors {collections.Counter(g.get('err') for g in G if 'err' in g)}; far {sum(1 for g in G if g.get('far'))}; calls {lib.crc.NCALLS[0]} in {time.time()-t0:.0f} s")
ok = [g for g in G if "ds" in g]
print("its buy slot - create slot:", sorted(collections.Counter(min(g["ds"], 10) for g in ok).items()))
