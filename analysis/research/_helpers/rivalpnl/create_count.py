# Count pump creates per UTC hour via signatures of the pump mint-authority PDA (touched by create/create_v2).
import sys, os, json, collections, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
MA = "TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM"
before = None; hours = collections.Counter(); herr = collections.Counter(); n = 0
for page in range(60):
    p = {"limit": 1000}
    if before: p["before"] = before
    r = C.rpc("getSignaturesForAddress", [MA, p], cache=False)
    if not r: break
    for s in r:
        h = datetime.datetime.fromtimestamp(s["blockTime"], datetime.timezone.utc).strftime("%H")
        (herr if s["err"] else hours)[h] += 1
    before = r[-1]["signature"]; n += len(r)
    if r[-1]["blockTime"] < 1792713600 + 7 * 3600: break
json.dump(dict(ok=hours, err=herr), open(os.path.join(C.OUTD, "create_count.json"), "w"))
print("pages", page + 1, "sigs", n); print(sorted(hours.items()))
