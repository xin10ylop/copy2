# The bags behind the trades, with no new fetch (the owner, Nov 15 night: "isn't there an efficient way?"). model.py's
# cache keeps every trade transaction of every path whole (CACHE/tx_<sig[:24]>.json.gz), and a transaction's meta gives
# the trader's balance of the coin before and after it (pre/postTokenBalances, owner = the trader). So for every trade
# after wallet 4's buy: the trader's bag before and after, in tokens.
#   python3 -I build.py CQ ALL CACHE OUT     -> OUT/bags.json.gz  {key: [[pre, post] per trade of the path, in order]}
import sys, os, json, gzip, concurrent.futures as cf
CQ, ALL, CACHE, OUT = sys.argv[1:5]
P = {}
for SPD in (ALL, CQ): P.update({k: v for k, v in json.load(gzip.open(f"{SPD}/paths.json.gz")).items() if v and k not in P})
def bags(key):
    m, tr = P[key]; out = []; memo = {}
    for e in tr:
        s = e["sig"]
        if s not in memo:
            try: memo[s] = json.load(gzip.open(f"{CACHE}/tx_{s[:24]}.json.gz"))["meta"]
            except Exception: memo[s] = None
        mt = memo[s]
        if mt is None: out.append([-1, -1]); continue
        f = lambda lst: sum(int(b["uiTokenAmount"]["amount"]) for b in lst or [] if b.get("owner") == e["user"] and b["mint"].startswith(m))
        out.append([f(mt.get("preTokenBalances")), f(mt.get("postTokenBalances"))])
    return key, out
with cf.ProcessPoolExecutor(8) as ex: res = dict(ex.map(bags, list(P), chunksize=8))
json.dump(res, gzip.open(f"{OUT}/bags.json.gz", "wt"))
n = sum(len(v) for v in res.values()); miss = sum(1 for v in res.values() for a, b in v if a < 0)
print(f"{len(res)} paths, {n} trades, {miss} without a cached transaction")
