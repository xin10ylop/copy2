# Where each copied wallet trades (Nov 25): its latest swaps (Helius Enhanced, type SWAP, 2 pages of 100) by source, and
# its buys of 0.5+ SOL by source (a swap whose SOL out of the wallet is 0.5+, from its nativeTransfers and its wSOL), so we
# see what part of its trading our units (pump.fun curve and the routes through it) can follow at all.
#   HELIUS_URL=... python3 -I r3_venues.py
import os, json, time, urllib.request, urllib.parse, collections, datetime as dt
KEY = urllib.parse.parse_qs(urllib.parse.urlparse(os.environ["HELIUS_URL"]).query)["api-key"][0]
W = {"wallet 4": "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg", "CqCAzte8": "CqCAzte8TwCDbCBrhjUpsfG6Au9pZPdrTXrVDidKHGAn",
     "CgyPomTG": "CgyPomTGt9BFqnjBdRS38BCBUZvtMJDf3aKQy8sMTVKX", "3XeFcZKS": "3XeFcZKSn8WzqoDAm5vvgbdfkU82rMmhJfp1q4LXtnX6",
     "6LwMLkCe": "6LwMLkCeEAqYp9Pv33ujrgd9uF987zPXdGKr9Z9sebh5", "6nNzEg86": "6nNzEg86rbY4J1Z6euDn9iQoih8uaSj6ZVZHZVvFxjJf",
     "GqWfqfG6": "GqWfqfG6Mt6RL8BKUWiBkirqzycUc15bgZVtFERQzxJ8", "FatoU1bj": "FatoU1bj1cwMEZ7nNBUu47s8HpJNAFR5ZajGPtP8Fph1",
     "HtHkKxYN": "HtHkKxYN43BdJ8QJU1srMa3bqjpncLFcZgVCX8yU3AJS", "3SiQo8MJ": "3SiQo8MJMzXaZcJexMivmk5CRgrNxDUh4bDbgb3wFAmW"}
WSOL = "So11111111111111111111111111111111111111112"
def enh(a, before):
    for k in range(5):
        try: return json.load(urllib.request.urlopen(f"https://api.helius.xyz/v0/addresses/{a}/transactions?api-key={KEY}&type=SWAP&limit=100" + (f"&before={before}" if before else ""), timeout=60))
        except Exception: time.sleep(2 * (k + 1))
    return []
for name, w in W.items():
    txs, before = [], None
    for _ in range(2):
        p = enh(w, before)
        if not p: break
        txs += p; before = p[-1]["signature"]
        if len(p) < 100: break
    src = collections.Counter(); big = collections.Counter()
    for t in txs:
        s = t.get("source") or "?"; src[s] += 1
        out = sum((x.get("amount") or 0) for x in t.get("nativeTransfers") or [] if x.get("fromUserAccount") == w) / 1e9
        out += sum(float(x.get("tokenAmount") or 0) for x in t.get("tokenTransfers") or [] if x.get("fromUserAccount") == w and x.get("mint") == WSOL)
        if out >= 0.5: big[s] += 1
    span = (txs[0]["timestamp"] - txs[-1]["timestamp"]) / 3600 if len(txs) > 1 else 0
    print(f"{name:9s} {len(txs):3d} swaps over {span:5.1f} h  by source: " + ", ".join(f"{k} {v}" for k, v in src.most_common(5)) +
          f"  |  with 0.5+ SOL out: " + ", ".join(f"{k} {v}" for k, v in big.most_common(5)))
    time.sleep(0.3)
