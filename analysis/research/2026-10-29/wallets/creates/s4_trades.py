# Step 4: for every frenzy coin of step 3 (>= MINTX landed transactions in its create slot +0..+2), fetch its landed
# transactions in slots +0..+3 (+3 so a +1 buy has its two following slots) and decode the pump TradeEvents of the coin.
#   python3 -I s4_trades.py [THREADS=48] [MINTX=4]  ->  OUT/s4_trades.json {mint: [trade, ...]}
# trade = [sig, slot, dslot, idx, fee_payer, user, is_buy, tok, quote_amount, vquote, vtok, ix, payer_sol_delta, fee, n_top_ix]
#   payer_sol_delta = post - pre lamports of the fee payer (includes the fee); used to price quote tokens (s5).
import sys, os, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crc
TH = int(sys.argv[1]) if len(sys.argv) > 1 else 48; MINTX = int(sys.argv[2]) if len(sys.argv) > 2 else 4
K = crc.json.load(open(crc.OUT + "/s3_coins.json"))
fr = {m: r for m, r in K.items() if "err" not in r and r["s0"] + r["s1"] + r["s2"] >= MINTX}
jobs = []
for m, r in fr.items():
    L = crc.json.load(open(f"{crc.OUT}/s3_sigs/{m}.json"))
    jobs += [(m, sg, sl - r["slot"]) for sg, sl, bt in L if 0 <= sl - r["slot"] <= 3]
    jobs.append((m, r["csig"], 0))
print(time.strftime("%H:%M:%S"), len(fr), "frenzy coins,", len(jobs), "transactions", flush=True)
def one(j):
    m, sg, d = j
    try: t = crc.tx(sg)
    except Exception as e: return m, [[sg, None, d, None, None, None, None, None, None, None, None, "ERR " + crc.red(e)[:60], None, None, None]]
    if not t: return m, []
    ks = crc.keys_of(t); meta = t.get("meta") or {}
    dsol = (meta.get("postBalances") or [0])[0] - (meta.get("preBalances") or [0])[0]
    ntop = len(t["transaction"]["message"]["instructions"])
    out = []
    for k, e in crc.events(t):
        if k == "trade" and e["mint"] == m:
            out.append([sg, t["slot"], d, t.get("transactionIndex"), ks[0], e["user"], e["is_buy"], e["tok"], e.get("quote_amount"),
                        e.get("vquote"), e["vtok"], e.get("ix"), dsol, meta.get("fee"), ntop])
    return m, out
res = {m: [] for m in fr}; t0 = time.time(); n = 0
with ThreadPoolExecutor(TH) as ex:
    for m, out in ex.map(one, jobs):
        res[m] += out; n += 1
        if n % 3000 == 0: print(time.strftime("%H:%M:%S"), n, "/", len(jobs), f"{n/(time.time()-t0):.0f}/s", flush=True)
for m in res: res[m].sort(key=lambda x: (x[1] or 0, x[3] or 0))
crc.jdump(res, crc.OUT + "/s4_trades.json")
nt = sum(len(v) for v in res.values())
print(f"{len(jobs)} tx in {time.time()-t0:.0f} s: {nt} trades of the coin, {sum(1 for v in res.values() for x in v if x[11] and str(x[11]).startswith('ERR'))} errors")
