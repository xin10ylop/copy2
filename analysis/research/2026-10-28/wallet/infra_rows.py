# Infrastructure from the rows (Oct 19 - Oct 28 14:54): fee, tip, block index for its buys and sells.
import sys; sys.path.insert(0, "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/wallet")
from w4lib import *
R = rows()
def q(v, ps=(10, 50, 90)):
    v = sorted(v); return [v[min(len(v) - 1, int(p / 100 * len(v)))] for p in ps] if v else None
def spent(r): return -(r["d"] + r["tok"].get(WSOL, [0])[0] + r["fee"]) / 1e9
own = [r for r in R if r["signer"]]
buy = [r for r in own if any(t[1] == W and t[2] == 1 for t in r["tr"])]
sell = [r for r in own if any(t[1] == W and t[2] == 0 for t in r["tr"]) and not any(t[1] == W and t[2] == 1 for t in r["tr"])]
bigoq = [r for r in buy if any(t[1] == W and t[2] == 1 and t[5] == 0 for t in r["tr"]) and spent(r) >= 1.45]
solbuy = [r for r in buy if any(t[1] == W and t[2] == 1 and t[5] > 0 for t in r["tr"])]
print("own (self-paid) landed", len(own), " pump-curve buys", len(buy), " sells", len(sell), " 1.45+ other-quote buys", len(bigoq), " SOL-coin buys", len(solbuy))
for name, L in (("all own", own), ("curve buys", buy), ("1.45+ other-quote buys", bigoq), ("SOL-coin buys", solbuy), ("curve sells", sell)):
    tipped = [r for r in L if r["tip"] > 0]
    print(f"{name:24s} n={len(L):5d} fee SOL p10/50/90 {[round(x/1e9, 5) for x in q([r['fee'] for r in L])]}  tipped {len(tipped)} ({100*len(tipped)/max(1,len(L)):.0f}%) tip SOL p10/50/90 {[round(x/1e9, 5) for x in q([r['tip'] for r in tipped])] if tipped else None}  block index p10/50/90 {q([r['i'] for r in L if r['i'] is not None])}")
