# Pull Enhanced-API history for a wallet back to a cutoff timestamp. Usage: pull_hist.py WALLET CUTOFF_TS [MAXPAGES]
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
def pull(addr, cutoff, maxpages=10, verbose=True):
    out, before = [], None
    for page in range(maxpages):
        try:
            j = C.enhanced(addr, before=before)
        except Exception as e:
            if verbose: print("  enhanced error:", e, file=sys.stderr)
            return out, "error"
        if not j: return out, "end"
        out += j; before = j[-1]["signature"]
        if verbose: print(f"  {addr[:8]} page {page} n={len(j)} oldest ts={j[-1]['timestamp']} slot={j[-1]['slot']}", file=sys.stderr)
        if j[-1]["timestamp"] < cutoff: return out, "cutoff"
    return out, "maxpages"
if __name__ == "__main__":
    addr, cutoff = sys.argv[1], int(sys.argv[2]); mp = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    txs, why = pull(addr, cutoff, mp)
    txs = [t for t in txs if t["timestamp"] >= cutoff]
    json.dump({"wallet": addr, "stop": why, "txs": txs}, open(os.path.join(C.OUTD, f"hist_{addr}.json"), "w"))
    print(addr, why, len(txs))
