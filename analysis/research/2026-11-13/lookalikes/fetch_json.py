# A wallet's landed transactions from T0 to T1 (UTC seconds), one RPC "json"-encoded file each (the format of
# crates/rugsnipe-long/examples/scan.rs; since_stop/fetch_w4.py's), from the signature list of the score data.
#   SP=<score data> python3 -I fetch_json.py WALLET T0 T1 OUTDIR
import sys, os, json
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lib
W, T0, T1, OUT = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]; os.makedirs(OUT, exist_ok=True)
S = [s for s in json.load(open(f"{os.environ['SP']}/h9long/{W[:8]}_sigs.json")) if not s[3] and T0 <= s[2] < T1]
have = {f.split("_")[1][:12] for f in os.listdir(OUT)}
TXO = {"encoding": "json", "maxSupportedTransactionVersion": 1, "commitment": "confirmed"}
def get(s):
    if s[0][:12] in have: return 0
    t = lib.rpc("getTransaction", [s[0], TXO], cache=False)
    if t is None: return 1
    json.dump(t, open(f"{OUT}/{t['slot']}_{s[0][:12]}.json", "w")); return 0
with ThreadPoolExecutor(32) as ex: bad = sum(ex.map(get, S))
print(len(S), "landed in the window; failed to fetch", bad, "; files", len(os.listdir(OUT)))
