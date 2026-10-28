# Step 6: do the top wallets flip or hold? For each top wallet (s5 order) and each frenzy coin it bought at +0/+1
# (up to CAPC a wallet, newest first), its token account for the coin is read from the buy's postTokenBalances,
# that account's signatures are listed, and every later transaction is read for the account's token change (any
# decrease = a sale or a transfer out) and the wallet's pump TradeEvents of the coin (quote in and out).
#   python3 -I s6_holds.py [TOP=20] [CAPC=25] [THREADS=32]  ->  OUT/s6_holds.json, stdout table
import sys, os, time, collections, statistics as st
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crc
TOP = int(sys.argv[1]) if len(sys.argv) > 1 else 20; CAPC = int(sys.argv[2]) if len(sys.argv) > 2 else 25
TH = int(sys.argv[3]) if len(sys.argv) > 3 else 32
R = crc.json.load(open(crc.OUT + "/s5_rank.json")); K = crc.json.load(open(crc.OUT + "/s3_coins.json"))
users = [r["user"] for r in R["rows"][:TOP]]
if crc.W4 not in users and crc.W4 in R["coins"]: users.append(crc.W4)
extra = [u for u in sys.argv[4:]] if len(sys.argv) > 4 else []
users += [u for u in extra if u not in users and u in R["coins"]]
pq = R["pq"]; corr = R["corr"]
def lam(q, qa): return qa * pq[q] * corr.get(q, 1.0)
def tokbal(t, acct):
    ks = crc.keys_of(t); meta = t.get("meta") or {}
    def amt(lst):
        for b in lst or []:
            if ks[b["accountIndex"]] == acct: return int(b["uiTokenAmount"]["amount"])
        return 0
    return amt(meta.get("preTokenBalances")), amt(meta.get("postTokenBalances"))
def one(job):
    u, m, c = job; q = K[m]["quote"]
    t = crc.tx(c["sig"])
    if not t: return u, m, dict(err="no buy tx")
    ks = crc.keys_of(t); acct = None
    for b in (t.get("meta") or {}).get("postTokenBalances") or []:
        if b.get("mint") == m and b.get("owner") == u: acct = ks[b["accountIndex"]]
    if not acct: return u, m, dict(err="no token account")
    S = sorted(crc.sigs(acct, limit=1000), key=lambda p: (p["slot"], p["signature"]))
    t_buy = t["blockTime"]; s_buy = t["slot"]
    after = [p for p in S if p.get("err") is None and p["signature"] != c["sig"] and p["slot"] >= s_buy][:20]
    pre, held = tokbal(t, acct); q_in = 0; q_out = 0; ev = []; maxheld = held
    for e in [e for k, e in crc.events(t) if k == "trade" and e["mint"] == m and e["user"] == u and e["is_buy"]]:
        q_in += e.get("quote_amount") or 0
    for p in after:
        x = crc.tx(p["signature"])
        if not x: continue
        a, b = tokbal(x, acct)
        tr = [e for k, e in crc.events(x) if k == "trade" and e["mint"] == m and e["user"] == u]
        for e in tr:
            if e["is_buy"]: q_in += e.get("quote_amount") or 0
            else: q_out += e.get("quote_amount") or 0
        ev.append([x["blockTime"] - t_buy, x["slot"] - s_buy, b - a, bool(tr), any(not e["is_buy"] for e in tr)])
        maxheld = max(maxheld, b)
    dec = [e for e in ev if e[2] < 0]
    first = dec[0][0] if dec else None
    gone = next((e[0] for e in ev if e[2] < 0 and sum(z[2] for z in ev[:ev.index(e) + 1]) + held <= 0.01 * maxheld), None)
    curve_sold = sum(-e[2] for e in dec if e[4]); all_sold = sum(-e[2] for e in dec)
    return u, m, dict(first=first, gone=gone, n_after=len(after), n_sigs=len(S), held=held, q_in=q_in, q_out=q_out,
                      sol_in=lam(q, q_in) / 1e9, sol_out=lam(q, q_out) / 1e9, curve_share=curve_sold / all_sold if all_sold else None,
                      first_slots=dec[0][1] if dec else None, bt=t_buy)
jobs = []
for u in users:
    cs = sorted(R["coins"][u].items(), key=lambda kv: -kv[1]["bt"])[:CAPC]
    jobs += [(u, m, c) for m, c in cs]
op = crc.OUT + "/s6_holds.json"; out = collections.defaultdict(dict)
print(time.strftime("%H:%M:%S"), len(users), "wallets,", len(jobs), "coins", flush=True)
with ThreadPoolExecutor(TH) as ex:
    def safe(j):
        try: return one(j)
        except Exception as e: return j[0], j[1], dict(err=crc.red(e)[:120])
    for u, m, r in ex.map(safe, jobs):
        out[u][m] = r
crc.jdump(out, op)
now = max(K[m]["bt"] for m in K if "bt" in K[m])
print("wallet                                         coins  sold  1st-sale med  <=10s  >=60s  out med  closed  net SOL-eq  won")
for u in users:
    v = [r for r in out[u].values() if "err" not in r]
    sold = [r for r in v if r["first"] is not None]
    fs = [r["first"] for r in sold]
    closed = [r for r in v if r["gone"] is not None and r["curve_share"] and r["curve_share"] > 0.99]
    net = sum(r["sol_out"] - r["sol_in"] for r in closed)
    print(f"{u:44s} {len(v):5d} {len(sold):5d} {st.median(fs) if fs else float('nan'):10.0f}s {sum(1 for x in fs if x <= 10):6d} {sum(1 for x in fs if x >= 60):6d}"
          f" {st.median(r['gone'] for r in v if r['gone'] is not None) if any(r['gone'] is not None for r in v) else float('nan'):7.0f}s"
          f" {len(closed):7d} {net:+10.2f} {sum(1 for r in closed if r['sol_out'] > r['sol_in']):5d}")
