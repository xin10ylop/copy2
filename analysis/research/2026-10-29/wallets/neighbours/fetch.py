# For each coin of wallet 4's 1.45+ SOL buys (the trips of full_paths.py / grad_paths.py: _fpaths.json + _gpaths.json),
# read every transaction on the coin's bonding curve from its create up to slot max(C + 3, S + 2), C = the create slot,
# S = wallet 4's buy slot, landed and failed:
#   before its buy: getSignaturesForAddress(curve, before = its buy sig), paged back to the curve's first signature;
#   after its buy:  getSignaturesForAddress(curve, until = its buy sig, before = its sell sig), all pages, kept up to the
#                   window's end; then getTransaction for each signature in the window.
# Failed transactions are read up to slot C + 1 only.
# C = the slot of the transaction carrying the coin's CreateEvent (else the oldest landed signature).
#   python3 -I fetch.py [N]   ->  OUT/win.json  (one entry per coin; resumable through the response cache)
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from concurrent.futures import ThreadPoolExecutor
import nlib as L
T = {x["m"]: x for x in json.load(open(f"{L.SP}/H9kuqGKN_trips.json"))}
P = json.load(open(f"{L.SP}/H9kuqGKN_fpaths.json")); G = json.load(open(f"{L.SP}/H9kuqGKN_gpaths.json"))
LED = {p["m"]: p for p in json.load(open(f"{L.SP}/H9kuqGKN_ledger.json"))["pos"]}
sig_of = {}
for l in open(f"{L.SP}/H9kuqGKN.jsonl"):
    r = json.loads(l)
    for t in r["tr"]:
        if t[1] == L.W: sig_of.setdefault((t[0], r["s"], t[2]), r["sig"])
coins = [m for m in list(P) + list(G) if (P.get(m) or G.get(m)) and (T[m]["tr"][0]["v"] or 0) >= 1.45
         and T[m]["kind"] in ("pump, other quote", "pump, SOL quote")]
coins = sorted(set(coins), key=lambda m: T[m]["tr"][0]["bt"])
if len(sys.argv) > 1: coins = coins[:int(sys.argv[1])]
def one(m):
    x = T[m]; b = x["tr"][0]; S = b["s"]
    bs = sig_of.get((m, S, 1))
    if m in G:   # graduated before its sale: its sell is off the curve; no upper anchor (page from the newest)
        ss = None
    else:
        ss = sig_of.get((m, x["tr"][1]["s"], 0))
    if not bs: return m, dict(err="no buy sig")
    curve = L.bonding_curve(m)
    pre, before = [], bs
    for _ in range(6):
        pg = L.sigs(curve, before=before)
        pre += pg
        if len(pg) < 1000: break
        before = pg[-1]["signature"]
    post, before = [], ss
    for _ in range(8):
        pg = L.sigs(curve, before=before, until=bs)
        post += pg
        if len(pg) < 1000: break
        before = pg[-1]["signature"]
    landed_pre = [p for p in pre if not p.get("err")]
    if not landed_pre: return m, dict(err="nothing before its buy", n_pre=len(pre))
    C0 = landed_pre[-1]["slot"]
    end = max(C0 + 3, S + 2)
    # failed transactions only up to C + 1 (where the early buyers fire; later ones are mostly spam retries)
    want = [p for p in pre if p["slot"] >= C0 - 2] + [p for p in post if p["slot"] <= end and (not p.get("err") or p["slot"] <= C0 + 1)]
    rec = []
    for p in want:
        t = L.tx(p["signature"])
        if not t: continue
        r = L.parse(t, m); r["sig"] = p["signature"]; rec.append(r)
    cr = [r for r in rec if r["create"]]
    C = cr[0]["s"] if cr else C0
    rec.sort(key=lambda r: (r["s"], r["i"] if r["i"] is not None else 0))
    return m, dict(C=C, C_from="create event" if cr else "oldest landed sig", S=S, i=b["i"], bt=b["bt"], v=b["v"],
                   tok=b["tok"], vt=b["vt"], kind=x["kind"], grad=m in G, n_pre=len(pre), n_post=len(post),
                   pre_capped=len(pre) >= 6000, end=end, buy_sig=bs, tx=rec)
OUTF = L.OUT + "/win.json"
have = json.load(open(OUTF)) if os.path.exists(OUTF) else {}
todo = [m for m in coins if m not in have or "err" in have[m]]
print(time.strftime("%H:%M:%S"), len(coins), "coins,", len(todo), "to do", flush=True)
n = 0
with ThreadPoolExecutor(int(os.environ.get("THREADS", "12"))) as ex:
    for m, v in ex.map(one, todo):
        have[m] = v; n += 1
        if n % 50 == 0:
            print(time.strftime("%H:%M:%S"), n, "/", len(todo), flush=True); json.dump(have, open(OUTF, "w"))
json.dump(have, open(OUTF, "w"))
print(time.strftime("%H:%M:%S"), "done", n, "errors", sum(1 for v in have.values() if "err" in v), flush=True)
