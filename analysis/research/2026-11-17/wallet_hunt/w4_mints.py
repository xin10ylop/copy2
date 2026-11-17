# Every coin wallet 4 traded since Nov 3 00:00 UTC (or env T0) (any token it held in a transaction of its own; its quote tokens
# and floats drop out by the count), from its transactions on disk. -> OUT (json: mint -> first time)
#   python3 -I w4_mints.py OUT TXDIR [TXDIR ...]
import sys, os, json, datetime
OUT, DIRS = sys.argv[1], sys.argv[2:]; W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
T0 = float(os.environ.get("T0", datetime.datetime(2026, 11, 3, tzinfo=datetime.timezone.utc).timestamp())); M = {}; n = 0; last = 0
for D in DIRS:
    for f in os.listdir(D):
        t = json.load(open(f"{D}/{f}")); bt = t.get("blockTime") or 0; last = max(last, bt)
        if bt < T0: continue
        n += 1
        for b in (t["meta"].get("postTokenBalances") or []) + (t["meta"].get("preTokenBalances") or []):
            if b.get("owner") == W4: M[b["mint"]] = min(M.get(b["mint"], bt), bt)
json.dump(M, open(OUT, "w"))
print(f"{n} of its transactions since {datetime.datetime.fromtimestamp(T0, datetime.timezone.utc):%m-%d %H:%M} UTC, last {datetime.datetime.fromtimestamp(last, datetime.timezone.utc):%m-%d %H:%M} UTC; {len(M)} mints")
