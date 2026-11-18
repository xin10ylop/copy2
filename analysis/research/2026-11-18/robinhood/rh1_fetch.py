# Robinhood Chain (4663), Pons V2 launchpad: every bonding-curve trade and launch for the last DAYS days, from the
# official public RPC (rate-limited; logs reach back at least 36 days; 30,000 blocks a request at most). Pons V2 =
# pump.fun's design on an EVM chain: one curve contract per token, 1B supply, graduation into a Uniswap v4 pool
# (docs.bitquery.io, Pons Launchpad API). Out: OUT/logs_<from>_<to>.json.gz per chunk, OUT/blocks.json (block -> time).
#   python3 -I rh1_fetch.py OUT DAYS
import sys, os, json, gzip, time, requests
from Crypto.Hash import keccak
OUT, DAYS = sys.argv[1], float(sys.argv[2]); os.makedirs(OUT, exist_ok=True)
U = "https://rpc.mainnet.chain.robinhood.com"; S = requests.Session()
K = lambda s: "0x" + keccak.new(digest_bits=256, data=s.encode()).hexdigest()
T = {n: K(s) for n, s in (("CurveBuy", "CurveBuy(address,address,uint256,uint256,uint256,uint256)"), ("CurveSell", "CurveSell(address,address,uint256,uint256,uint256,uint256)"),
                           ("TokenLaunched", "TokenLaunched(address,address,address,address,uint256,uint256)"), ("LaunchSwept", "LaunchSwept(address,uint256,uint256)"))}
json.dump(T, open(f"{OUT}/topics.json", "w"))
def call(m, p):
    for i in range(8):
        try:
            r = S.post(U, json={"jsonrpc": "2.0", "id": 1, "method": m, "params": p}, timeout=90).json()
            if isinstance(r.get("error"), dict):
                if r["error"].get("code") == 429: time.sleep(1.5 * (i + 1)); continue
                raise RuntimeError(r["error"])
            return r["result"]
        except (requests.RequestException, ValueError): time.sleep(2 * (i + 1))
    raise RuntimeError("gave up")
tip = int(call("eth_blockNumber", []), 16); B = {}
def btime(n):
    if n not in B: B[n] = int(call("eth_getBlockByNumber", [hex(n), False])["timestamp"], 16)
    return B[n]
def get_logs(lo, hi):
    """eth_getLogs, split in halves when the range holds more than the RPC's 10,000 logs."""
    try: return call("eth_getLogs", [{"fromBlock": hex(lo), "toBlock": hex(hi), "topics": [list(T.values())]}])
    except RuntimeError as e:
        if "exceeds limit" not in str(e) or hi <= lo: raise
        mid = (lo + hi) // 2; return get_logs(lo, mid) + get_logs(mid + 1, hi)
span = 30_000; t_tip = btime(tip); n_chunks = int(DAYS * 86400 / (span * 0.1026)) + 1
top = tip // span * span                      # fixed chunk boundaries (multiples of span): a restart skips what is on disk
for i in range(n_chunks):
    lo = top - (i + 1) * span; hi = lo + span - 1; f = f"{OUT}/logs_{lo}_{hi}.json.gz"
    btime(lo)
    if os.path.exists(f): continue
    logs = get_logs(lo, hi)
    with gzip.open(f + ".tmp", "wt") as fh: json.dump(logs, fh)
    os.replace(f + ".tmp", f)
    if i % 20 == 0:
        json.dump(B, open(f"{OUT}/blocks.json", "w")); print(f"{i + 1}/{n_chunks} chunks, back to {time.strftime('%m-%d %H:%M', time.gmtime(B[lo]))} UTC, {len(logs)} logs", flush=True)
    time.sleep(0.4)
json.dump(B, open(f"{OUT}/blocks.json", "w")); print("done", n_chunks, "chunks")
