# The clean test of the consensus (k1 is in-sample: most pickers were chosen on the 48 h's graduations). Their buys on
# coins created OUTSIDE Nov 15 01:07 - Nov 17 01:07 UTC (the histories go back to Nov 3 and on to Nov 17-18): each coin's
# outcome read now from its bonding curve (getMultipleAccounts), then the same table. Coins younger than 2 h at the read are
# left out (not yet decided). RPC from RPC_URL, never printed.
#   RPC_URL=... python3 -I k2_clean.py SP > out/k2_clean.txt
import sys, os, json, glob, time, base64, collections, urllib.request
from concurrent.futures import ThreadPoolExecutor
from solders.pubkey import Pubkey as P
SP = sys.argv[1]; URL = os.environ["RPC_URL"]; A, B = 1794790020, 1794877620; NOW = time.time()
SKIP = {"H9kuqGKN", "4sgdNABj", "AsDCYFPT", "8QzUkGJi", "B4BMZH3T", "HbovEh3L", "64Dn57gX", "H2nsBdjF", "EhS8bGVC", "Gf9gk8sZ", "DHLAr4dH", "91Wu2yN6", "G8hmNBej", "7zvP2xFF"}
buys = collections.defaultdict(list)
for f in glob.glob(f"{SP}/winners/hist/*.json"):
    w = os.path.basename(f)[:8]
    if w in SKIP: continue
    try: T = json.load(open(f))["trades"]
    except Exception: continue
    first = {}
    for e in sorted(T, key=lambda e: e["t"]):
        if e["buy"] and e["m"].endswith("pump"): first.setdefault(e["m"], e)
    for m, e in first.items():
        if not (A <= e["t"] < B) and NOW - e["t"] > 7200 and e["real"] > 0: buys[m].append((e["t"], w))
ms = sorted(buys); PUMP = P.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
def call(m, p):
    for i in range(6):
        try:
            rq = urllib.request.Request(URL, json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), {"Content-Type": "application/json"})
            return json.load(urllib.request.urlopen(rq, timeout=60))["result"]
        except Exception: time.sleep(1.5 * (i + 1))
pda = lambda m: str(P.find_program_address([b"bonding-curve", bytes(P.from_string(m))], PUMP)[0])
def batch(x):
    r = call("getMultipleAccounts", [[pda(m) for m in x], {"encoding": "base64"}]); out = {}
    for m, a in zip(x, (r or {}).get("value") or []):
        d = base64.b64decode(a["data"][0]) if a else b""; out[m] = bool(d[48]) if len(d) > 48 else None
    return out
OC = {}
with ThreadPoolExecutor(8) as ex:
    for o in ex.map(batch, [ms[i:i + 100] for i in range(0, len(ms), 100)]): OC.update(o)
for name, sel in (("BEFORE the screen (Nov 3 - Nov 15)", lambda t: t < A), ("AFTER the screen (Nov 17 01:07 on)", lambda t: t >= B)):
    rows = []
    for m, v in buys.items():
        v.sort(); t0 = v[0][0]
        if not sel(t0) or OC.get(m) is None: continue
        ws = []
        for t, w in v:
            if t - t0 <= 300 and w not in ws: ws.append(w)
        rows.append((len(ws), OC[m]))
    print(f"\n{name}: {len(rows)} coins with an outcome")
    for lo, hi in ((1, 1), (2, 3), (4, 5), (6, 8), (9, 99)):
        X = [g for n, g in rows if lo <= n <= hi]
        if X: print(f"   {lo}-{hi} pickers: {len(X):6d} coins, graduated {sum(X):5d} ({sum(X) / len(X):6.1%})")
