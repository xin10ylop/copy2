# Each listed wallet's own recent activity: its newest 1,000 signatures (getSignaturesForAddress, as of the run): the
# newest and oldest time in the page, signatures an hour over the page, the failed share, and the signatures per UTC day.
# A wallet that answers the same 1,000 signatures for days is quiet. Wallets: rank.py's top 15 and the four named ones.
#   python3 -I activity.py   ->  OUT/activity.json (printed)
import sys, os, json, datetime, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nlib as L
R = json.load(open(L.OUT + "/rank.json"))
ws = list(dict.fromkeys(R["top"] + list(R["named"].values())))
def ts(t): return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%m-%d %H:%M")
out = {}
print(f"{'wallet':44s} {'newest UTC':11s} {'oldest UTC':11s} {'sigs':>5s} {'/hour':>6s} {'failed':>7s}  per day (UTC)")
for w in ws:
    pg = L.sigs(w, limit=1000, cache=False)
    if not pg: print(f"{w:44s} no signatures"); continue
    bts = [p["blockTime"] for p in pg if p.get("blockTime")]
    new, old = max(bts), min(bts); h = max((new - old) / 3600, 1 / 60)
    fail = sum(1 for p in pg if p.get("err"))
    day = collections.Counter(datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%m-%d") for t in bts)
    out[w] = dict(newest=new, oldest=old, n=len(pg), per_hour=len(pg) / h, failed=fail / len(pg), days=dict(day))
    print(f"{w:44s} {ts(new):11s} {ts(old):11s} {len(pg):5d} {len(pg) / h:6.1f} {fail / len(pg):7.1%}  " + " ".join(f"{d} {c}" for d, c in sorted(day.items())))
json.dump(out, open(L.OUT + "/activity.json", "w"))
