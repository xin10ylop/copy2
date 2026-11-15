# Top holders selling, with their real bags (Nov 15 night)

The owner, on the one gap left after `../signals/` round 3 ("what the top holders held before his buy"): "isn't there
an efficient way to do it?" There is, with no new fetch: `model.py`'s cache keeps every trade transaction of every path
whole (963,971 of them), and a transaction's meta gives the trader's balance of the coin before and after it. So for
every sell after wallet 4's buy the seller's bag is known, whether it was bought before wallet 4's buy or after
(`build.py` -> `bags.json.gz`; 187,111 sells by others at landing 4, the bag not found for 5,735 = 3%, a router's
account: those count as at least what they sold). Holders who never trade while we hold stay unseen; they cannot
fire a sell signal.

    python3 -I build.py CQ ALL CACHE OUT          # 3 minutes, from the cache
    python3 -I holders.py CQ ALL OUT > out/holders.txt

**Result (`out/holders.txt`): every one of the 33 rules loses, added to the live setup** (+75.29 SOL, 1,238 buys, 0.5
SOL):

| signal | settings ahead | the best | the worst |
|---|---|---|---|
| a 1-5% holder sells (any part) | 0 of 8 | −7.37 (5%+, under 1.5x) | −30.61 |
| a 0.5-3% holder sells its whole bag | 0 of 8 | −8.43 (3%+, under 1.5x) | −31.97 |
| one of the 1 / 3 / 5 / 10 biggest known bags sells half+ | 0 of 8 | −7.69 (the biggest, under 1.5x) | −34.65 |
| 2-5 whole-bag exits (0.5%+ bags) in 60-120 s | 0 of 6 | −33.92 | −38.69 |
| 2-4 of the 10 biggest known bags sell half+ in 120 s | 0 of 3 | −31.16 | −33.32 |

Picked on two blocks, scored on the third: −11.48 SOL.

**Why:** in these coins a top-holder-sized sale is the normal churn, not a warning. 21.6% of all sells come from bags
of 1%+ of the supply, and most sellers sell their whole bag at once (69% of the 1-2% bags, 56% of the 2-5% bags): they
are flippers going in and out. "A 1%+ holder sells" fires on 755 of the copies, most of them before the coin runs.
What does carry information is the balance of sells against buys over a minute (`sell_pressure`) and the price no
longer making highs (`stall_s`), both live since Nov 15 19:29 UTC. Holder signals: closed.
