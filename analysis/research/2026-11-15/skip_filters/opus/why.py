# Step 5. Why would a low curve fee mark a losing copy? What the coin does after wallet 4's buy, low-fee coins
# (bps < 125: the curve's protocol + creator fee, as the bot reads it from its trade event) against the rest: the
# highest price within 600 s (as a multiple of the price its buy left), how many reach 1.5x / 2x / 3x, trades and
# distinct traders in the first 60 s, how fast wallet 4 sells, and wallet 4's own result on the coin.
#   python3 -I why.py SPD > out/why.txt
import sys, os, json, gzip, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import common as C
SPD = sys.argv[1]; W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
P = json.load(gzip.open(f"{SPD}/paths.json.gz"))
def info(r):
    m, tr = P[r["key"]]
    k = next(i for i, e in enumerate(tr) if e["user"] == W4 and e["buy"] and e["slot"] == r["slot"])
    vt0 = tr[k]["vt"]; t0 = tr[k]["t"]; rest = tr[k + 1:]
    px = [(vt0 / e["vt"]) ** 2 for e in rest if e["t"] - t0 <= 600]
    first = [e for e in rest if e["t"] - t0 <= 60]
    sell = next((e["t"] - t0 for e in rest if e["user"] == W4 and not e["buy"]), None)
    return dict(peak=max(px) if px else 1.0, n60=len(first), u60=len({e["user"] for e in first}),
                buyq60=sum(e["q"] for e in first if e["buy"]) / max(1, sum(e["q"] for e in first)), sell=sell, w4=r["w4own"][1])
if __name__ == "__main__":
    G = {"bps < 125": [r for r in C.R if r["f"]["bps"] < 125], "bps >= 125": [r for r in C.R if r["f"]["bps"] >= 125]}
    for a in (None, "SOL", "WBTC"):
        print(f"== {'all kinds' if a is None else a + '-paid only'}")
        for g, rs in G.items():
            rs = [r for r in rs if a is None or r["anchor"] == a]; I = [info(r) for r in rs]; n = len(I)
            med = lambda k: statistics.median(x[k] for x in I)
            print(f"   {g:10s} {n:3d} coins | peak in 600 s: median {med('peak'):.2f}x, reach 1.5x {100 * sum(x['peak'] >= 1.5 for x in I) / n:4.1f}%, 2x {100 * sum(x['peak'] >= 2 for x in I) / n:4.1f}%, "
                  f"3x {100 * sum(x['peak'] >= 3 for x in I) / n:4.1f}% | first 60 s: trades {med('n60'):.0f}, traders {med('u60'):.0f}, buy share of volume {med('buyq60'):.2f} | "
                  f"wallet 4 sells by 60 s {100 * sum(1 for x in I if x['sell'] is not None and x['sell'] <= 60) / n:4.1f}%, by 300 s {100 * sum(1 for x in I if x['sell'] is not None and x['sell'] <= 300) / n:4.1f}% | "
                  f"its own result median {100 * med('w4'):+.1f}%, mean {100 * statistics.mean(x['w4'] for x in I):+.1f}%")
    print("\n== the fee values among the low-fee coins (bps: coins)")
    import collections; print("   " + ", ".join(f"{k}: {v}" for k, v in sorted(collections.Counter(r["f"]["bps"] for r in G["bps < 125"]).items())))
    print("== the low-fee coins by quote token (top 8) and by block")
    print("   " + ", ".join(f"{k}: {v}" for k, v in collections.Counter(r["f"]["quote"] for r in G["bps < 125"]).most_common(8)))
    print("   " + ", ".join(f"{'ABC'[k]}: {v}" for k, v in sorted(collections.Counter(r["blk"] for r in G["bps < 125"]).items())) + "   (all buys: " +
          ", ".join(f"{'ABC'[k]}: {v}" for k, v in sorted(collections.Counter(r["blk"] for r in C.R).items())) + ")")
