# Estimate pump creates/hour from a random sample of blocks between 07:00 UTC and now.
import sys, os, json, random, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C, blocks as B
cur = C.rpc("getSlot", [{"commitment": "confirmed"}], cache=False)
t_now = C.rpc("getBlockTime", [cur - 50], cache=False)
lo = cur - int(10.5 * 3600 / 0.4)
random.seed(7); slots = sorted(random.sample(range(lo, cur - 100), 80))
n = 0; cr = 0; got = []
for s in slots:
    b = B.summarize(s)
    if not b: continue
    c = sum(1 for x in b["txs"] if x["create_mint"] and not x["err"]); got.append(c)
t_lo = C.rpc("getBlockTime", [lo], cache=False)
slots_per_h = (cur - 50 - lo) / ((t_now - t_lo) / 3600)
res = dict(sampled=len(got), creates_per_block=sum(got) / len(got), slots_per_hour=slots_per_h, creates_per_hour=sum(got) / len(got) * slots_per_h,
           stdev_blk=st.pstdev(got))
json.dump(res, open(os.path.join(C.OUTD, "create_rate.json"), "w")); print(res)
