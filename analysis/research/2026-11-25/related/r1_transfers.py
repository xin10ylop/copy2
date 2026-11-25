# Money links of each copied wallet (Nov 25; the owner: "check every single wallet we have, if they have any other wallet
# related trading with, on chain tracking"). Helius Enhanced Transactions (type TRANSFER, newest first, PAGES x 100): every
# plain SOL transfer of 0.05+ SOL between the wallet and another account, summed by counterparty (in, out, count, first
# and last time). The key comes from HELIUS_URL, never printed.
#   HELIUS_URL=... python3 -I r1_transfers.py OUT.json [PAGES=5]
import os, sys, json, time, urllib.request, urllib.parse, collections, datetime as dt
OUT = sys.argv[1]; PAGES = int(sys.argv[2]) if len(sys.argv) > 2 else 5
KEY = urllib.parse.parse_qs(urllib.parse.urlparse(os.environ["HELIUS_URL"]).query)["api-key"][0]
W = {"wallet 4": "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg", "CqCAzte8": "CqCAzte8TwCDbCBrhjUpsfG6Au9pZPdrTXrVDidKHGAn",
     "CgyPomTG": "CgyPomTGt9BFqnjBdRS38BCBUZvtMJDf3aKQy8sMTVKX", "3XeFcZKS": "3XeFcZKSn8WzqoDAm5vvgbdfkU82rMmhJfp1q4LXtnX6",
     "6LwMLkCe": "6LwMLkCeEAqYp9Pv33ujrgd9uF987zPXdGKr9Z9sebh5", "6nNzEg86": "6nNzEg86rbY4J1Z6euDn9iQoih8uaSj6ZVZHZVvFxjJf",
     "GqWfqfG6": "GqWfqfG6Mt6RL8BKUWiBkirqzycUc15bgZVtFERQzxJ8", "FatoU1bj": "FatoU1bj1cwMEZ7nNBUu47s8HpJNAFR5ZajGPtP8Fph1",
     "HtHkKxYN": "HtHkKxYN43BdJ8QJU1srMa3bqjpncLFcZgVCX8yU3AJS", "3SiQo8MJ": "3SiQo8MJMzXaZcJexMivmk5CRgrNxDUh4bDbgb3wFAmW"}
def get(url):
    for a in range(6):
        try: return json.load(urllib.request.urlopen(url, timeout=60))
        except Exception: time.sleep(2 * (a + 1))
    return []
res = {}
for name, w in W.items():
    cp = collections.defaultdict(lambda: dict(inn=0.0, out=0.0, n=0, first=9e12, last=0)); before = None; ntx = 0
    for _ in range(PAGES):
        url = f"https://api.helius.xyz/v0/addresses/{w}/transactions?api-key={KEY}&type=TRANSFER&limit=100" + (f"&before={before}" if before else "")
        page = get(url)
        if not page: break
        for tx in page:
            ntx += 1
            for t in tx.get("nativeTransfers") or []:
                a, b, amt = t.get("fromUserAccount"), t.get("toUserAccount"), (t.get("amount") or 0) / 1e9
                if amt < 0.05 or a == b or w not in (a, b): continue
                o = b if a == w else a; c = cp[o]
                c["out" if a == w else "inn"] += amt; c["n"] += 1; c["first"] = min(c["first"], tx["timestamp"]); c["last"] = max(c["last"], tx["timestamp"])
        before = page[-1]["signature"]
        if len(page) < 100: break
        time.sleep(0.3)
    top = sorted(cp.items(), key=lambda kv: -(kv[1]["inn"] + kv[1]["out"]))[:8]
    res[name] = dict(wallet=w, transfer_txs=ntx, top=[dict(acct=k, **v) for k, v in top])
    print(f"== {name} ({ntx} transfer transactions read)")
    for k, v in top:
        f = lambda t: dt.datetime.fromtimestamp(t, dt.UTC).strftime("%m-%d")
        print(f"   {k:44s} in {v['inn']:9.2f}  out {v['out']:9.2f}  x{v['n']:3d}  {f(v['first'])} to {f(v['last'])}")
json.dump(res, open(OUT, "w"))
