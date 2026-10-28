# A wallet's landed transactions from <w8>_sigs.json -> SP/h9long/<w8>.jsonl. Each row: slot, block index, time, fee,
# the wallet's SOL change (native) and token changes by mint (wSOL included, so a swap through wSOL nets), the pump
# curve trades (TradeEvent, every user), the programs called (top level and inner), tips. Any venue: a PumpSwap or
# router swap shows as token deltas and its program ids. Raw transactions are not kept.
# Copy of ../../../2026-10-27/h9long/pull.py. Changed: SP from the environment (data under this session's scratchpad);
# each row also keeps "qm" = {coin: the curve's quote mint} for every pump curve the transaction traded: the mint of the
# token account the bonding curve owns besides the coin (none for SOL-priced curves). Used by route_q.py.
# SHARD=k/n (optional) fetches every n-th of the missing transactions into <w8>.jsonl.k, so several processes can share
# the work; merge.py then folds the shard files into <w8>.jsonl (deduplicated, broken last lines dropped).
#   python3 -I pull.py WALLET            SHARD=0/3 python3 -I pull.py WALLET
import sys, os, json, time
from concurrent.futures import ThreadPoolExecutor
SP0 = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad"      # helpers: tri, rivalpnl
SP = os.environ.get("SP", "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/score")
sys.path.insert(0, SP0 + "/month"); sys.path.insert(0, SP0 + "/rivalpnl"); sys.path.insert(0, "/home/user/rugsnipe/analysis")
import tri, common as C, pumpparse as PP
from rugsnipe_analysis import events as E
W = sys.argv[1]
OUT = f"{SP}/h9long/{W[:8]}.jsonl"
sigs = [x for x in json.load(open(f"{SP}/h9long/{W[:8]}_sigs.json")) if not x[3]]
done = set()
import glob
for fn in [f for f in [OUT] + glob.glob(OUT + ".*") if os.path.exists(f)]:
    for l in open(fn):
        try: done.add(json.loads(l)["sig"])
        except Exception: pass
todo = [s for s, *_ in sigs if s not in done]
if os.environ.get("SHARD"):
    k, n = map(int, os.environ["SHARD"].split("/")); todo = todo[k::n]; OUT = f"{OUT}.{k}"
print(time.strftime("%H:%M:%S"), len(sigs), "landed,", len(todo), "to fetch", flush=True)
BC = {}
def bcurve(m):
    if m not in BC: BC[m] = C.bonding_curve(m)
    return BC[m]
def row(tx):
    ks = PP.keys_of(tx); a = PP.analyze(tx); meta = tx.get("meta") or {}; m = tx["transaction"]["message"]
    i = ks.index(W) if W in ks else None
    tr = []
    progs = set()
    for ix in m["instructions"]: progs.add(ks[ix["programIdIndex"]])
    for grp in meta.get("innerInstructions") or []:
        for ix in grp["instructions"]:
            p = ks[ix["programIdIndex"]]; progs.add(p)
            if p != C.PUMP: continue
            raw = C.b58d(ix.get("data", ""))
            if raw[:8] == E.EVENT_IX_TAG and raw[8:16] == E.DISC_TRADE:
                try:
                    e = E.decode_trade(raw[8:])
                    tr.append([e.mint, e.user, int(e.is_buy), e.sol_amount, e.token_amount, e.virtual_sol_reserves,
                               e.virtual_token_reserves, e.real_sol_reserves, e.creator, e.fee or 0, e.creator_fee or 0, e.ix_name])
                except Exception: pass
    tok = {}
    for side, sgn in (("preTokenBalances", -1), ("postTokenBalances", 1)):
        for b in meta.get(side) or []:
            if b.get("owner") != W: continue
            mt = b["mint"]; amt = int(b["uiTokenAmount"]["amount"])
            t = tok.setdefault(mt, [0, b["uiTokenAmount"].get("decimals", 0), b.get("programId", "")])
            t[0] += sgn * amt
    tok = {k: v for k, v in tok.items() if v[0] != 0}
    qm = {}
    for mt in {t[0] for t in tr}:
        bc = bcurve(mt)
        q = [b["mint"] for b in (meta.get("postTokenBalances") or []) if b.get("owner") == bc and b["mint"] != mt]
        if q: qm[mt] = q[0]
    return dict(sig=tx["transaction"]["signatures"][0], s=tx["slot"], i=tx.get("transactionIndex"), bt=tx.get("blockTime"),
                fee=meta.get("fee"), d=(meta["postBalances"][i] - meta["preBalances"][i]) if i is not None else 0,
                tok=tok, tr=tr, progs=sorted(progs - {"11111111111111111111111111111111", "ComputeBudget111111111111111111111111111111"}),
                tip=a["tip_total"], cup=a["cu_price"], signer=ks[0] == W, qm=qm)
def one(s):
    for k in range(3):
        try:
            tx = tri.rpc("getTransaction", [s, {"encoding": "json", "maxSupportedTransactionVersion": 1, "commitment": "confirmed"}], cache=False)
            return json.dumps(row(tx), separators=(",", ":")) if tx else None
        except Exception as e:
            err = e
    return None
n = 0
with ThreadPoolExecutor(10) as ex, open(OUT, "a") as f:
    for line in ex.map(one, todo):
        n += 1
        if line: f.write(line + "\n")
        if n % 2000 == 0: print(time.strftime("%H:%M:%S"), n, flush=True); f.flush()
print(time.strftime("%H:%M:%S"), "done", flush=True)
