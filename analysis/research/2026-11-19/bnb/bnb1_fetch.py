# BNB Chain, four.meme (Nov 19; the owner: "check bnb"): every log of four.meme's contract 0x5c952063... (Bitquery's
# four.meme proxy; TokenCreate / TokenPurchase / TokenSale / LiquidityAdded) for the last DAYS days, from PublicNode's
# public BSC RPC (5,000 blocks a request; BSC blocks are 0.45 s). Out: OUT/logs_<from>_<to>.json.gz, OUT/blocks.json
# (a timestamp every 2,000 blocks, for interpolation). Re-runnable: chunks already fetched are skipped.
#   python3 -I bnb1_fetch.py OUT DAYS
import sys, os, json, gzip, time, urllib.request
OUT, DAYS = sys.argv[1], float(sys.argv[2]); os.makedirs(OUT, exist_ok=True)
U = "https://bsc-rpc.publicnode.com"; ADDR = "0x5c952063c7fc8610FFDB798152D69F0B9550762b"; STEP = 5000
def q(m, p, tries=6):
    for i in range(tries):
        try:
            r = urllib.request.Request(U, json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), {"content-type": "application/json", "user-agent": "curl/8"})
            j = json.load(urllib.request.urlopen(r, timeout=90))
            if "error" in j: raise RuntimeError(j["error"])
            return j["result"]
        except Exception as e:
            err = e; time.sleep(2 * (i + 1))
    raise RuntimeError(err)
B = int(q("eth_blockNumber", []), 16); start = B - int(DAYS * 86400 / 0.45)
bf = f"{OUT}/blocks.json"; blocks = json.load(open(bf)) if os.path.exists(bf) else {}
done = 0
for a in range(start - start % STEP, B, STEP):
    b = min(a + STEP - 1, B); f = f"{OUT}/logs_{a}_{b}.json.gz"
    if b == a + STEP - 1 and os.path.exists(f): continue
    try: L = q("eth_getLogs", [{"fromBlock": hex(a), "toBlock": hex(b), "address": ADDR}])
    except Exception as e:   # too many results: halves
        L = []
        for h in (a, a + STEP // 2):
            L += q("eth_getLogs", [{"fromBlock": hex(h), "toBlock": hex(min(h + STEP // 2 - 1, b)), "address": ADDR}])
    json.dump(L, gzip.open(f, "wt"))
    for n in range(a, b + 1, 2000):
        if str(n) not in blocks: blocks[str(n)] = int(q("eth_getBlockByNumber", [hex(n), False])["timestamp"], 16)
    done += 1
    if done % 50 == 0: json.dump(blocks, open(bf, "w")); print(f"{done} chunks, at block {b} ({(B - b) * 0.45 / 86400:.1f} days left)", flush=True)
json.dump(blocks, open(bf, "w")); print("done", done, "chunks")
