# Its early sells over every period: the copies the backtest closes behind its early sale ("its early sell, we follow"
# in sim.KIND; the bot's set of p3.py, DATA=fresh3, at most 4 open), priced again as if the engine ignored its sale and
# kept to its own exits (TP 2.0 / stop 0.8 / 1790 s from its buy). The path after its sale: the bonding curve's trades to
# 1,800 s after its buy (Triton), the first 25 transactions after its sale and an even sample of the rest (at most 80;
# full_paths.py samples the same way); its own 2.5x cannot fire after it sold.
#   python3 -I early2.py   ->  SPX/early2_paths.json (cached)
import os, sys, json, collections
os.environ["DATA"] = "fresh3"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim
from concurrent.futures import ThreadPoolExecutor
SP = sim.SP; SPX = "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/more"
sys.path.insert(0, SP + "/month"); sys.path.insert(0, SP + "/rivalpnl"); sys.path.insert(0, "/home/user/rugsnipe/analysis")
import tri, common as C
from rugsnipe_analysis import events as E
THREE = ("AvcwGFaF", "2FSWwQwj", "6dp2JZAY", "CCci2Fr6", "CcLYZCSg", "EkvZsJuJ", "NotmcxBN")
TR = sim.trips(lo=1.45, grad=True, nots=THREE)
_, got = sim.score(TR, cap=4)
taken = {m for p in got for r, m in got[p]}
early = [(m, x, p) for m, x, p in TR if m in taken and sim.KIND.get(m) == "its early sell, we follow"]
OUT = f"{SPX}/early2_paths.json"
have = json.load(open(OUT)) if os.path.exists(OUT) else {}
TXO = {"encoding": "json", "maxSupportedTransactionVersion": 1, "commitment": "confirmed"}
def trades(tx, m):
    out = []
    ks = tx["transaction"]["message"]["accountKeys"] + (tx["meta"].get("loadedAddresses") or {}).get("writable", []) + (tx["meta"].get("loadedAddresses") or {}).get("readonly", [])
    for g in tx["meta"].get("innerInstructions") or []:
        for ix in g["instructions"]:
            if ks[ix["programIdIndex"]] != C.PUMP: continue
            raw = C.b58d(ix.get("data", ""))
            if raw[:8] == E.EVENT_IX_TAG and raw[8:16] == E.DISC_TRADE:
                try: e = E.decode_trade(raw[8:])
                except Exception: continue
                if e.mint == m: out.append([tx["slot"], tx.get("transactionIndex") or 0, e.user[:8], int(e.is_buy), e.token_amount, e.virtual_token_reserves, tx.get("blockTime")])
    return out
def fetch(item):
    m, x, path = item
    if m in have: return m, have[m]
    b, s = x["tr"]
    ssig = sim.ROWS_BY.get((m, s["s"], 0), {}).get("sig")
    if not ssig: return m, None
    bc = C.bonding_curve(m); sigs, before = [], None
    for _ in range(60):
        o = {"limit": 1000, "until": ssig}
        if before: o["before"] = before
        page = tri.rpc("getSignaturesForAddress", [bc, o], cache=False) or []
        sigs += [(p["signature"], p.get("blockTime") or 0) for p in page if not p.get("err")]
        if len(page) < 1000: break
        before = page[-1]["signature"]
    win = [sg for sg, t in sigs if t <= b["bt"] + 1830][::-1]
    keep = win if len(win) <= 80 else win[:25] + win[25::max(1, (len(win) - 25) // 55)]
    tr = []
    for sg in keep:
        tx = tri.rpc("getTransaction", [sg, TXO], cache=False)
        if tx: tr += trades(tx, m)
    tr.sort(key=lambda r: (r[0], r[1]))
    return m, dict(after=tr, n=len(win), sampled=len(win) > 80)
with ThreadPoolExecutor(6) as ex:
    for m, v in ex.map(fetch, early): have[m] = v
json.dump(have, open(OUT, "w"))
print(f"copies the bot's set closes behind its early sale (at most 4 open): {len(early)}")
g = collections.defaultdict(lambda: [0, 0.0, 0.0, collections.Counter()])
rows = []
for m, x, path in early:
    v = have.get(m)
    if not v: continue
    b, s = x["tr"]
    r_f = sim.one(x, path)[2]
    full = sorted([r for r in path if (r[0], r[1]) <= (s["s"], s["i"] or 0)] + v["after"], key=lambda r: (r[0], r[1]))
    last = full[-1]
    x2 = dict(x, tr=[b, dict(s=last[0] + 1, i=0, bt=b["bt"] + 1800, tok=0, vt=last[5])])
    r_i = sim.one(x2, full, lift=False)[2]; k = sim.KIND.get(m)
    p = sim.per(b["bt"]); g[p][0] += 1; g[p][1] += r_f; g[p][2] += r_i; g[p][3][k] += 1
    rows.append((p, m, s["bt"] - b["bt"], (b["vt"] / s["vt"]) ** 2, r_f, r_i, k, v["n"]))
print(f"{'':3s} {'coin':9s} {'sold after':>10s} {'its x':>6s} {'follow':>7s} {'ignore':>7s}  ignore's exit")
for p, m, held, mult, a, c, k, n in sorted(rows):
    print(f"{p:3s} {m[:8]:9s} {held:9d}s {mult:6.2f} {a:+7.3f} {c:+7.3f}  {k} ({n} txs after its sale)")
for p in sim.PERIODS:
    if p in g:
        n, a, c, ks = g[p]
        print(f"   {p}: {n} copies; follow its sale {a:+.2f}, ignore it {c:+.2f} (difference {c - a:+.2f}); ignore's exits {dict(ks)}")
# the bot's set with every one of these copies priced the "ignore" way instead (the close times are not re-capped:
# in P3 the cap never binds, ../fresh/ README section 3)
IGN = {m: c for p, m, held, mult, a, c, k, n in rows}
for P in sim.PERIODS:
    base = sorted((r for r, m in got[P]), reverse=True)
    alt = sorted((IGN.get(m, r) for r, m in got[P]), reverse=True)
    print(f"   {P} the bot's set, 4 open: follow its sale {sum(base):+.2f} ({sum(base[2:]):+.2f}); ignore it {sum(alt):+.2f} ({sum(alt[2:]):+.2f}) on {len(alt)} copies")
