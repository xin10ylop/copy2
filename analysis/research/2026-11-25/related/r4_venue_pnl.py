# Each copied wallet's own result by venue (Nov 25; the owner: "go", on measuring its LaunchLab and PumpSwap trading).
# Helius Enhanced Transactions, type SWAP, newest first, up to PAGES x 100 (it lists LaunchLab, PumpSwap, Jupiter ...
# swaps; plain pump.fun curve buys mostly are not in it). Per transaction the wallet's SOL change (its native balance
# change, fees in, plus wSOL moved) and its token moves; per coin (mint) the venue of its first buy here, its SOL in and
# out, and whether it sold what it bought (90%+). Per venue: coins sold out, its own result, buys of 0.5+ SOL a day, the
# share of winning coins, days up.
#   HELIUS_URL=... python3 -I r4_venue_pnl.py [CALLS=30] [DAYS=14]
import os, sys, json, time, urllib.request, urllib.parse, collections, datetime as dt
KEY = urllib.parse.parse_qs(urllib.parse.urlparse(os.environ["HELIUS_URL"]).query)["api-key"][0]
PAGES = int(sys.argv[1]) if len(sys.argv) > 1 else 30; DAYS = float(sys.argv[2]) if len(sys.argv) > 2 else 14   # calls a wallet, days back
W = {"HtHkKxYN": "HtHkKxYN43BdJ8QJU1srMa3bqjpncLFcZgVCX8yU3AJS", "CqCAzte8": "CqCAzte8TwCDbCBrhjUpsfG6Au9pZPdrTXrVDidKHGAn",
     "CgyPomTG": "CgyPomTGt9BFqnjBdRS38BCBUZvtMJDf3aKQy8sMTVKX", "3SiQo8MJ": "3SiQo8MJMzXaZcJexMivmk5CRgrNxDUh4bDbgb3wFAmW",
     "6LwMLkCe": "6LwMLkCeEAqYp9Pv33ujrgd9uF987zPXdGKr9Z9sebh5", "3XeFcZKS": "3XeFcZKSn8WzqoDAm5vvgbdfkU82rMmhJfp1q4LXtnX6",
     "GqWfqfG6": "GqWfqfG6Mt6RL8BKUWiBkirqzycUc15bgZVtFERQzxJ8"}
WSOL = "So11111111111111111111111111111111111111112"
STABLE = {"EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB"}
import re, urllib.error
def enh(a, before):
    """one call: (transactions, where to continue). With a type filter Helius returns partial pages, or an error naming
    the signature to continue from when a stretch has none of that type (Nov 25: stopping at the first short page read
    one page only)."""
    for k in range(6):
        try:
            p = json.load(urllib.request.urlopen(f"https://api.helius.xyz/v0/addresses/{a}/transactions?api-key={KEY}&type=SWAP&limit=100" + (f"&before={before}" if before else ""), timeout=60))
            return p, (p[-1]["signature"] if p else None)
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")
            m = re.search(r"`before` parameter set to ([1-9A-HJ-NP-Za-km-z]{60,90})", body)
            if m: return [], m.group(1)
            time.sleep(2 * (k + 1))
        except Exception: time.sleep(2 * (k + 1))
    return [], None
out = {}
for name, w in W.items():
    txs, before = [], None
    stop = time.time() - DAYS * 86400
    for _ in range(PAGES):
        p, nxt = enh(w, before)
        txs += p
        if not nxt or (p and p[-1]["timestamp"] < stop): break
        before = nxt; time.sleep(0.25)
    txs.sort(key=lambda t: t["timestamp"])
    coin = {}
    for t in txs:
        ad = next((a for a in t.get("accountData") or [] if a.get("account") == w), None)
        sol = (ad.get("nativeBalanceChange") or 0) / 1e9 if ad else 0.0
        sol += sum(float(x.get("tokenAmount") or 0) * (1 if x.get("toUserAccount") == w else -1) for x in t.get("tokenTransfers") or []
                   if x.get("mint") == WSOL and w in (x.get("toUserAccount"), x.get("fromUserAccount")))
        moves = collections.defaultdict(float)
        for x in t.get("tokenTransfers") or []:
            m = x.get("mint")
            if m in (WSOL,) or m in STABLE or w not in (x.get("toUserAccount"), x.get("fromUserAccount")): continue
            moves[m] += float(x.get("tokenAmount") or 0) * (1 if x.get("toUserAccount") == w else -1)
        if len(moves) != 1: continue                      # one coin a swap (a token-for-token swap is left out)
        m, d = next(iter(moves.items()))
        c = coin.setdefault(m, dict(venue=t.get("source") or "?", t=t["timestamp"], tin=0.0, tout=0.0, sin=0.0, sout=0.0, first_buy=None))
        if d > 0:
            c["tin"] += d; c["sout"] += max(0.0, -sol)
            if c["first_buy"] is None: c["first_buy"] = max(0.0, -sol); c["venue"] = t.get("source") or "?"
        else:
            c["tout"] += -d; c["sin"] += max(0.0, sol)
    span_d = (txs[-1]["timestamp"] - txs[0]["timestamp"]) / 86400 if len(txs) > 1 else 0
    by = collections.defaultdict(list)
    for m, c in coin.items():
        if c["first_buy"] is None or c["tin"] <= 0 or c["tout"] < 0.9 * c["tin"]: continue
        by[c["venue"]].append(c)
    print(f"== {name}: {len(txs)} swaps over {span_d:.1f} days")
    for v, cs in sorted(by.items(), key=lambda kv: -len(kv[1])):
        res = [c["sin"] - c["sout"] for c in cs]; big = [c for c in cs if c["first_buy"] >= 0.5]
        days = collections.defaultdict(float)
        for c, r in zip(cs, res): days[dt.datetime.fromtimestamp(c["t"], dt.UTC).strftime("%m-%d")] += r
        rb = [c["sin"] - c["sout"] for c in big]
        print(f"   {v:20s} {len(cs):4d} coins sold out, own {sum(res):+8.2f} SOL, wins {sum(1 for r in res if r > 0) / len(res):4.0%}, days up "
              f"{sum(1 for x in days.values() if x > 0)}/{len(days)} | first buy 0.5+ SOL: {len(big):3d} coins "
              f"({len(big) / span_d if span_d else 0:.1f} a day), own {sum(rb):+7.2f} SOL")
    out[name] = {v: dict(n=len(cs), own=sum(c["sin"] - c["sout"] for c in cs)) for v, cs in by.items()}
    time.sleep(0.3)
json.dump(out, open("venue_pnl.json", "w"))
