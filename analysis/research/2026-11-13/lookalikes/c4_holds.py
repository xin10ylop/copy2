# Search 2, step 4: flip or hold. For each wallet, its newest N landed transactions (any coin), its pump curve trades
# in them (TradeEvents with it as the user), and per coin its first buy and first sale: seconds between them. A coin
# with a buy but no sale in the sample is "held past the sample" only if the sample reaches 10 minutes beyond the buy.
#   python3 -I c4_holds.py N WALLET...   ->  LK/c4_holds.json (merged)
import sys, os, json, statistics, collections
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lib, cmodel
N = int(sys.argv[1]); WS = sys.argv[2:]
op = lib.OUT + "/c4_holds.json"; have = json.load(open(op)) if os.path.exists(op) else {}
TXO = {"encoding": "json", "maxSupportedTransactionVersion": 1, "commitment": "confirmed"}
def mytrades(tx, w):
    out = []
    ks = tx["transaction"]["message"]["accountKeys"] + sum(((tx["meta"].get("loadedAddresses") or {}).get(x, []) for x in ("writable", "readonly")), [])
    for g in tx["meta"].get("innerInstructions") or []:
        for ix in g["instructions"]:
            if ks[ix["programIdIndex"]] != lib.PUMP: continue
            raw = lib.b58d(ix.get("data", ""))
            if raw[:8] == cmodel.E.EVENT_IX_TAG and raw[8:16] == cmodel.E.DISC_TRADE:
                try: e = cmodel.decode_trade(raw[16:])
                except Exception: continue
                if e["user"] == w: out.append((e["mint"], e["buy"], tx["blockTime"], e.get("q") or e["sol"], bool(e.get("quote_mint")) and e["quote_mint"] not in lib.SOL_LIKE))
    return out
for w in WS:
    if w in have: continue
    s, before = [], None
    while len(s) < N:
        page = lib.sigs(w, before=before, cache=False)
        if not page: break
        s += [x for x in page if x["err"] is None]; before = page[-1]["signature"]
        if len(page) < 1000: break
    s = s[:N]
    with ThreadPoolExecutor(32) as ex: txs = list(ex.map(lambda x: lib.rpc("getTransaction", [x["signature"], TXO], cache=False), s))
    tr = sorted((t for tx in txs if tx for t in mytrades(tx, w)), key=lambda t: t[2])
    end = max((t[2] for t in tr), default=0); coin = {}
    for m, b, t, q, oq in tr:
        c = coin.setdefault(m, dict(buy=None, sell=None, oq=oq))
        if b and c["buy"] is None: c["buy"] = t
        if not b and c["buy"] is not None and c["sell"] is None: c["sell"] = t
    hs = [c["sell"] - c["buy"] for c in coin.values() if c["buy"] and c["sell"]]
    held = sum(1 for c in coin.values() if c["buy"] and not c["sell"] and end - c["buy"] >= 600)
    hso = [c["sell"] - c["buy"] for c in coin.values() if c["buy"] and c["sell"] and c["oq"]]
    q = lambda v, p: sorted(v)[min(len(v) - 1, int(p * len(v)))] if v else None
    have[w] = dict(n=len(s), span_h=(s[0]["blockTime"] - s[-1]["blockTime"]) / 3600 if s else 0, coins=sum(1 for c in coin.values() if c["buy"]),
                   closed=len(hs), held10=held, h25=q(hs, .25), h50=q(hs, .5), h75=q(hs, .75), ge120=sum(1 for h in hs if h >= 120),
                   oq_closed=len(hso), oq_h50=q(hso, .5), oq_ge120=sum(1 for h in hso if h >= 120))
    json.dump(have, open(op, "w"))
    r = have[w]
    print(f"{w[:8]} {r['n']} tx over {r['span_h']:.1f} h: {r['coins']} coins bought, {r['closed']} with a sale: first sale p25/med/p75 "
          f"{r['h25']}/{r['h50']}/{r['h75']} s, 120 s+ on {r['ge120']}; no sale 10+ min {r['held10']}; other-quote coins: {r['oq_closed']} closed, "
          f"median {r['oq_h50']} s, 120 s+ {r['oq_ge120']}", flush=True)
