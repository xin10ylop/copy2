import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
def sigs(addr, cutoff, maxpages=20):
    out, before = [], None
    for _ in range(maxpages):
        p = {"limit": 1000}
        if before: p["before"] = before
        r = C.rpc("getSignaturesForAddress", [addr, p], cache=bool(before))
        if not r: break
        out += r; before = r[-1]["signature"]
        if (r[-1].get("blockTime") or 0) < cutoff: break
    return [s for s in out if (s.get("blockTime") or 0) >= cutoff]
if __name__ == "__main__":
    addr, cutoff = sys.argv[1], int(sys.argv[2])
    s = sigs(addr, cutoff)
    json.dump(s, open(os.path.join(C.OUTD, f"sigs_{addr}.json"), "w"))
    import collections, datetime
    print(len(s), "ok", sum(1 for x in s if not x["err"]), "err", sum(1 for x in s if x["err"]))
    h = collections.Counter((datetime.datetime.utcfromtimestamp(x["blockTime"]).hour, bool(x["err"])) for x in s)
    for hr in sorted({k[0] for k in h}): print(f"  {hr:02d}h ok {h[(hr,False)]:4d} err {h[(hr,True)]:4d}")
