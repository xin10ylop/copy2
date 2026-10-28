# Compare how two wallets build their transactions: a random sample of each one's own (self-paid, landed) transactions.
# Features: top-level program sequence, durable nonce (AdvanceNonceAccount first), CU price / limit, tip service and
# size, plain wrap amounts, pump buy sizes. Usage: fingerprint.py N ADDR [ADDR...]   (signatures from sigs_<a8>.json
# if present, else the newest 2,000)
import sys; sys.path.insert(0, "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/wallet")
sys.path.insert(0, "/home/user/rugsnipe/analysis")
from w4lib import *
from rugsnipe_analysis import events as E
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import random, os
N = int(sys.argv[1])
def sigs_for(A):
    p = OUT + f"/sigs_{A[:8]}.json"
    if A == W: return [[x[0], x[1], x[2], x[3]] for x in json.load(open(SP + "/h9long/H9kuqGKN_sigs.json"))]
    if os.path.exists(p): return json.load(open(p))
    s = []; before = None
    for k in range(2):
        q = tri.sigs(A, before=before, limit=1000); s += [[x["signature"], x["slot"], x["blockTime"], bool(x.get("err"))] for x in q]
        if len(q) < 1000: break
        before = q[-1]["signature"]
    return s
for A in sys.argv[2:]:
    S = [x for x in sigs_for(A) if not x[3]]; S = S[:3000]; random.seed(11); smp = random.sample(S, min(N, len(S)))
    with ThreadPoolExecutor(6) as ex: txs = list(ex.map(lambda x: tri.tx(x[0]), smp))
    seq = Counter(); nonce = 0; cup = Counter(); cul = Counter(); tips = Counter(); tipamt = Counter(); wraps = Counter(); buys = Counter(); n = 0; mem = Counter()
    for t in txs:
        if not t: continue
        ks = keys_of(t)
        if ks[0] != A: continue
        n += 1; m = t["transaction"]["message"]
        top = [ks[ix["programIdIndex"]] for ix in m["instructions"]]
        seq[" ".join(p[:4] for p in top)] += 1
        ix0 = m["instructions"][0]; d0 = b58d(ix0.get("data", ""))
        if ks[ix0["programIdIndex"]] == SYS and d0[:4] == b"\x04\x00\x00\x00": nonce += 1
        cfg = m.get("transactionConfig") or {}
        for ix in m["instructions"]:
            if ks[ix["programIdIndex"]] == CB:
                d = b58d(ix.get("data", ""))
                if d[:1] == b"\x03": cup[u64(d, 1)] += 1
                if d[:1] == b"\x02": cul[struct.unpack_from("<I", d, 1)[0]] += 1
        if cfg.get("priorityFee") is not None: cup["cfg:" + str(cfg.get("priorityFee"))] += 1
        if cfg.get("computeUnitLimit") is not None: cul["cfg:" + str(cfg.get("computeUnitLimit"))] += 1
        for k, a, b, l, mt, dd, inn in transfers(t):
            if b in TIPS and a == A: tips[TIPS[b]] += 1; tipamt[l] += 1
            if k == "sys" and a == A and b == A and not inn: wraps[round(l / 1e9, 4)] += 1
        for x in ("MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr",):
            if x in ks: mem["memo"] += 1
    print(f"\n{A}: sampled {len(smp)}, self-paid {n}, durable nonce first {nonce}")
    print("  top-level sequences:", seq.most_common(6))
    print("  cu price:", cup.most_common(6)); print("  cu limit:", cul.most_common(5))
    print("  tips by service:", tips.most_common(8)); print("  tip lamports:", tipamt.most_common(6))
    print("  wrap amounts (SOL to own wSOL):", wraps.most_common(8))
