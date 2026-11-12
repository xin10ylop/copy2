# Who funded a wallet, and where its big SOL transfers went: the wallet's native SOL moves of MIN+ SOL with no token
# change (from its own signatures in the score data), each transaction's other accounts whose SOL moved the other way.
#   SP=<score data> python3 -I funding.py WALLET [MIN=1]
import sys, os, json, datetime
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lib
W = sys.argv[1]; MIN = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0; SP = os.environ["SP"]
rows = [json.loads(l) for l in open(f"{SP}/h9long/{W[:8]}.jsonl")]
sig = [r["sig"] for r in rows if abs(r.get("d") or 0) >= MIN * 1e9 and not r.get("tok")]
if sig is None:          # pull.py's row keys: find the SOL change field
    print("row keys:", sorted(rows[0].keys())); sys.exit()
TXO = {"encoding": "json", "maxSupportedTransactionVersion": 1, "commitment": "confirmed"}
with ThreadPoolExecutor(16) as ex: txs = list(ex.map(lambda s: lib.rpc("getTransaction", [s, TXO], cache=False), sig))
for t in sorted((t for t in txs if t), key=lambda t: t["blockTime"]):
    m = t["meta"]; ks = t["transaction"]["message"]["accountKeys"] + sum(((m.get("loadedAddresses") or {}).get(x, []) for x in ("writable", "readonly")), [])
    i = ks.index(W); d = (m["postBalances"][i] - m["preBalances"][i]) / 1e9
    other = [(ks[j], round((m["postBalances"][j] - m["preBalances"][j]) / 1e9, 3)) for j in range(len(ks)) if j != i and j < len(m["postBalances"]) and abs(m["postBalances"][j] - m["preBalances"][j]) >= 0.5e9]
    print(datetime.datetime.fromtimestamp(t["blockTime"], datetime.timezone.utc).strftime("%m-%d %H:%M UTC"), f"{d:+.3f}", other)
