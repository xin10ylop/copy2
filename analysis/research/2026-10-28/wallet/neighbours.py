# Who trades next to wallet 4: 40 of its 1.45+ SOL buys of other-quote coins (4 a day, Oct 19-28, random, seed 5).
# For each: every transaction on the coin's bonding curve in slots S-2 .. S+2 (S = its buy slot), via
# getSignaturesForAddress(curve, before = first signature of block S+3), then getTransaction for each.
# Output: wallet/neigh.json (one entry per buy: list of txs with slot offset, index, payer, pump trades, tips).
import sys; sys.path.insert(0, "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/wallet")
sys.path.insert(0, "/home/user/rugsnipe/analysis")
from w4lib import *
from pda import bonding_curve
from rugsnipe_analysis import events as E
import random
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
R = sorted(rows(), key=lambda r: (r["s"], r["i"] or 0))
def spent(r): return -(r["d"] + r["tok"].get(WSOL, [0])[0] + r["fee"]) / 1e9
B = [r for r in R if any(t[1] == W and t[2] == 1 and t[5] == 0 for t in r["tr"]) and spent(r) >= 1.45]
byday = defaultdict(list)
for r in B: byday[time.strftime("%m-%d", time.gmtime(r["bt"]))].append(r)
random.seed(5); pick = []
for d in sorted(byday): pick += random.sample(byday[d], min(4, len(byday[d])))
print("buys >= 1.45 other-quote:", len(B), "by day", {d: len(v) for d, v in sorted(byday.items())}, "picked", len(pick), flush=True)
def first_sig_of_block(slot):
    for s in range(slot, slot + 8):
        try:
            b = tri.rpc("getBlock", [s, {"transactionDetails": "signatures", "rewards": False, "maxSupportedTransactionVersion": 1}], cache=True)
        except Exception as e:
            continue
        if b and b.get("signatures"): return b["signatures"][0], s
    return None, None
def trades(t, ks):
    out = []
    for grp in t["meta"].get("innerInstructions") or []:
        for ix in grp["instructions"]:
            if ks[ix["programIdIndex"]] != PUMP: continue
            raw = b58d(ix.get("data", ""))
            if raw[:8] == E.EVENT_IX_TAG and raw[8:16] == E.DISC_TRADE:
                try: e = E.decode_trade(raw[8:]); out.append([e.mint, e.user, int(e.is_buy), e.sol_amount, e.token_amount, e.virtual_sol_reserves, e.virtual_token_reserves])
                except Exception: pass
    return out
res = []
for k, r in enumerate(pick):
    mint = [t[0] for t in r["tr"] if t[1] == W and t[2] == 1][0]; curve = bonding_curve(mint); S = r["s"]
    anchor, aslot = first_sig_of_block(S + 3)
    got = []; before = anchor
    while True:
        p = tri.sigs(curve, before=before, limit=1000)
        got += [x for x in p if S - 2 <= x["slot"] <= S + 2]
        if len(p) < 1000 or p[-1]["slot"] < S - 2: break
        before = p[-1]["signature"]
    with ThreadPoolExecutor(6) as ex: txs = list(ex.map(lambda x: tri.tx(x["signature"]), got))
    L = []
    for x, t in zip(got, txs):
        if not t: continue
        ks = keys_of(t); tips = [(TIPS[b], l) for kk, a, b, l, m, d, inn in transfers(t) if b in TIPS]
        L.append(dict(sig=x["signature"], off=x["slot"] - S, i=t.get("transactionIndex"), payer=ks[0], err=t["meta"]["err"] is not None,
                      tr=trades(t, ks), tips=tips, ver=str(t.get("version")), nonce=(ks[t["transaction"]["message"]["instructions"][0]["programIdIndex"]] == SYS and b58d(t["transaction"]["message"]["instructions"][0].get("data", ""))[:4] == b"\x04\x00\x00\x00")))
    res.append(dict(sig=r["sig"], slot=S, i=r["i"], bt=r["bt"], mint=mint, curve=curve, spent=spent(r), anchor_slot=aslot, txs=L))
    print(k, ts(r["bt"]), mint[:8], "slot", S, "idx", r["i"], "curve txs in S-2..S+2:", len(L), flush=True)
json.dump(res, open(OUT + "/neigh.json", "w"))
