# The routes of its big buys from the chain: for every buy in SPX/quotes.json with a multi_hop_swap (and every buy of
# class E), its transaction (Triton, getTransaction, version 1), the multi_hop_swap's hops (16 fixed accounts, then
# base_mint, quote_mint, market, base_vault, quote_vault per hop; a market that is the base mint's bonding curve is a
# curve, anything else a PumpSwap pool), its input mint, the curve's quote, and the transaction's size in bytes and
# version.   python3 -I routes.py   ->  SPX/routes.json (resumable)
import sys, os, json, base64
from concurrent.futures import ThreadPoolExecutor
SP = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad"
SPX = "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/more"
sys.path.insert(0, SP + "/month"); sys.path.insert(0, SP + "/rivalpnl")
import tri, common as C
PAMM = "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"; DISC = bytes.fromhex("2b644913e9f66f94")
W = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
Qs = json.load(open(f"{SPX}/quotes.json"))
OUT = f"{SPX}/routes.json"
have = json.load(open(OUT)) if os.path.exists(OUT) else {}
todo = [q for q in Qs if (q["mh"] or q["cls"] == "E") and q["sig"] not in have]
def one(q):
    o = {"version": None}
    for k in range(3):
        try:
            tx = tri.rpc("getTransaction", [q["sig"], {"encoding": "json", "maxSupportedTransactionVersion": 1, "commitment": "confirmed"}], cache=False)
            raw = tri.rpc("getTransaction", [q["sig"], {"encoding": "base64", "maxSupportedTransactionVersion": 1, "commitment": "confirmed"}], cache=False)
            break
        except Exception as e:
            tx = None; err = str(e)[:80]
    if not tx: return q["sig"], dict(err=err)
    m = tx["transaction"]["message"]
    ks = m["accountKeys"] + (tx["meta"].get("loadedAddresses") or {}).get("writable", []) + (tx["meta"].get("loadedAddresses") or {}).get("readonly", [])
    ixs = [(ix["programIdIndex"], ix["accounts"], ix["data"]) for ix in m["instructions"]]
    for g in tx["meta"].get("innerInstructions") or []:
        ixs += [(ix["programIdIndex"], ix["accounts"], ix["data"]) for ix in g["instructions"]]
    hops = None
    for p, acc, data in ixs:
        if ks[p] != PAMM: continue
        d = C.b58d(data)
        if d[:8] != DISC: continue
        a = [ks[i] for i in acc]
        hops = []
        for h in range((len(a) - 16) // 5):
            base, quote, market = a[16 + 5 * h], a[17 + 5 * h], a[18 + 5 * h]
            hops.append(["curve" if market == C.bonding_curve(base) else "pool", base, quote, market])
        o["user_in"] = a[1]
        break
    # the input mint: the token account a[1]'s mint from the balances, else the first hop's mint the second lacks
    inp = None
    if hops:
        for bl in (tx["meta"].get("preTokenBalances") or []) + (tx["meta"].get("postTokenBalances") or []):
            if ks[bl["accountIndex"]] == o["user_in"]: inp = bl["mint"]
        if not inp:
            h0 = hops[0]; h1 = hops[1] if len(hops) > 1 else None
            inp = h0[2] if (not h1 or h0[1] in h1[1:3]) else h0[1]
    curve = [h for h in (hops or []) if h[0] == "curve"]
    o.update(hops=hops, input=inp, curve_quote=curve[-1][2] if curve else None, version=tx.get("version"),
             bytes=len(base64.b64decode(raw["transaction"][0])), nkeys=len(m["accountKeys"]), nix=len(m["instructions"]),
             alts=len(m.get("addressTableLookups") or []))
    return q["sig"], o
with ThreadPoolExecutor(8) as ex:
    for n, (s, o) in enumerate(ex.map(one, todo)):
        have[s] = o
        if n % 50 == 0: json.dump(have, open(OUT, "w")); print(n, "/", len(todo), flush=True)
json.dump(have, open(OUT, "w"))
print("done", len(have), "transactions;", sum(1 for v in have.values() if v.get("err")), "errors")
