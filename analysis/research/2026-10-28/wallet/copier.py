# Is 6anjqMeW (and AMDEmVoc) a copier of wallet 4? Their buys in a sample of their newest 2,000 signatures (before
# Oct 28 14:50 UTC): share of the coins that wallet 4 bought too, and the slot gap behind wallet 4's buy.
import sys; sys.path.insert(0, "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/wallet")
sys.path.insert(0, "/home/user/rugsnipe/analysis")
from w4lib import *
from rugsnipe_analysis import events as E
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import random
R = rows(); wb = {}
for r in R:
    for t in r["tr"]:
        if t[1] == W and t[2] == 1 and t[0] not in wb: wb[t[0]] = (r["s"], r["i"], t[5] == 0)
for A in sys.argv[1:]:
    s = []; before = None
    for k in range(3):
        p = tri.sigs(A, before=before, limit=1000); s += p; before = p[-1]["signature"]
    s = [x for x in s if not x.get("err") and x["blockTime"] < 1793199000]
    random.seed(1); smp = random.sample(s, min(400, len(s)))
    with ThreadPoolExecutor(6) as ex: txs = list(ex.map(lambda x: tri.tx(x["signature"]), smp))
    buys = []
    for t in txs:
        if not t: continue
        ks = keys_of(t)
        for grp in t["meta"].get("innerInstructions") or []:
            for ix in grp["instructions"]:
                if ks[ix["programIdIndex"]] != PUMP: continue
                raw = b58d(ix.get("data", ""))
                if raw[:8] == E.EVENT_IX_TAG and raw[8:16] == E.DISC_TRADE:
                    e = E.decode_trade(raw[8:])
                    if e.user == A and e.is_buy: buys.append((e.mint, t["slot"], t.get("transactionIndex"), e.virtual_sol_reserves == 0))
    both = [b for b in buys if b[0] in wb]
    gap = Counter()
    for m, sl, i, oq in both:
        ws, wi, woq = wb[m]; g = sl - ws
        gap["before W" if (g < 0 or (g == 0 and i < wi)) else ("same slot after" if g == 0 else (f"+{g}" if g <= 3 else ">+3"))] += 1
    print(A[:8], "span", ts(s[-1]["blockTime"]), "->", ts(s[0]["blockTime"]), "sampled", len(smp), "buys", len(buys), "other-quote", sum(b[3] for b in buys),
          "| coins wallet 4 also bought:", len(both), f"({100*len(both)/max(1,len(buys)):.0f}%)", "| other-quote buys W also bought:", sum(1 for b in both if b[3]), "of", sum(b[3] for b in buys), "| timing vs W:", dict(gap))
