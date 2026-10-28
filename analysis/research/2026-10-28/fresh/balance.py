# Fresh study: wallet 4's activity per period (signatures and landed transactions) and its SOL over P3 (Oct 27 00:20 UTC
# to the last row): the native SOL change from the rows, the transfers (ledger.py's xfer list: SOL moved with no token),
# wSOL / USD / token holdings changed, and what is left for trading.   python3 -I balance.py
import json, datetime, collections
SP = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad/fresh3"
W = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"; T3 = 1793060400
WSOL = "So11111111111111111111111111111111111111112"
USD = {"EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
       "USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB"}
NAMES = {"3NZ9JMVB": "WBTC", "pumpCmXq": "PUMP", "CARDSccU": "CARDS", "TTWofwAg": "TTWO", "7vfCXTUX": "WETH", "A7bdiYdS": "A7bd"}
def per(t): return "P1" if datetime.datetime.fromtimestamp(t, datetime.timezone.utc).day <= 22 else "P2" if t < T3 else "P3"
def day(t): return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%m-%d")
sg = json.load(open(f"{SP}/h9long/{W[:8]}_sigs.json"))
rows = sorted((json.loads(l) for l in open(f"{SP}/h9long/{W[:8]}.jsonl")), key=lambda r: (r["s"], r["i"] or 0))
print(f"signatures {len(sg)}, landed {sum(not x[3] for x in sg)}, rows {len(rows)}, last row {datetime.datetime.fromtimestamp(rows[-1]['bt'], datetime.timezone.utc):%m-%d %H:%M:%S} UTC")
a, b = collections.Counter(), collections.Counter(); hrs = {}
for s, slot, bt, err in sg: a[(per(bt), day(bt))] += 1; b[(per(bt), day(bt))] += not err
print("activity by UTC day: period day  signatures  landed (failed)")
for k in sorted(a): print(f"   {k[0]} {k[1]}  {a[k]:6d} {b[k]:6d} ({a[k] - b[k]})")
for p in ("P1", "P2", "P3"):
    ts = [x[2] for x in sg if per(x[2]) == p]; h = (max(ts) - min(ts)) / 3600
    n = sum(1 for x in sg if per(x[2]) == p and not x[3])
    print(f"   {p}: {len(ts)} signatures, {n} landed over {h:.1f} h: {n / h * 24:.0f} landed a day")
# P3: SOL legs
L = json.load(open(f"{SP}/h9long/{W[:8]}_ledger.json"))
x3 = [x for x in L["xfer"] if x[0] >= T3]
R3 = [r for r in rows if r["bt"] >= T3]
nat = sum(r["d"] for r in R3) / 1e9
fee = sum(((r["fee"] or 0) + (r["tip"] or 0)) for r in R3 if r["signer"]) / 1e9
ws = sum(r["tok"].get(WSOL, [0])[0] for r in R3) / 1e9
usd = sum(v[0] / 10 ** v[1] for r in R3 for m, v in r["tok"].items() if m in USD)
print(f"\nP3 ({len(R3)} landed rows): native SOL {nat:+.3f}, wSOL {ws:+.3f}, USD {usd:+.2f}; fees + tips paid {fee:.3f}")
xin = [x for x in x3 if x[1] > 0]; xout = [x for x in x3 if x[1] < 0]
print(f"   transfers (no token moved, > 0.003 SOL): {len(x3)} net {sum(x[1] for x in x3):+.3f}: in {len(xin)} {sum(x[1] for x in xin):+.3f}, out {len(xout)} {sum(x[1] for x in xout):+.3f}")
for x in sorted(x3, key=lambda x: -abs(x[1]))[:8]:
    print(f"      {datetime.datetime.fromtimestamp(x[0], datetime.timezone.utc):%m-%d %H:%M} UTC  {x[1]:+9.4f}  signed by it {x[2]}")
print("   native SOL change in the first minutes of P3 (its swing around the docs' 467.7 SOL reading): " + "  ".join(
    f"{k} min {sum(r['d'] for r in R3 if r['bt'] < T3 + 60 * k) / 1e9:+.3f}" for k in (10, 20, 30, 40, 60, 90, 120)))
print(f"   native SOL change before P3 (Oct 19 00:00 to Oct 27 00:20): {sum(r['d'] for r in rows if r['bt'] < T3) / 1e9:+.3f}")
K = collections.Counter(); S = collections.Counter()
for r in R3:
    if r["tok"] or abs(r["d"]) <= 3e6: continue
    k = ("in" if r["d"] > 0 else "out", "signed by it" if r["signer"] else "not signed by it", ",".join(p[:8] for p in r["progs"]) or "no program")
    K[k] += 1; S[k] += r["d"] / 1e9
print("   the transfers by program (Tokenkeg / TokenzQd: token-account closings, the rent comes back):")
for k in sorted(K, key=lambda k: S[k]): print(f"      {k[0]:3s} {k[1]:16s} {k[2]:28s} {K[k]:3d}  {S[k]:+.4f}")
print(f"   native SOL change less transfers: {nat - sum(x[1] for x in x3):+.3f}")
# token holdings changed over P3 (the floats), at the ledger's last price
dq = collections.Counter()
for r in R3:
    for m, v in r["tok"].items():
        if m != WSOL and m not in USD: dq[m] += v[0] / 10 ** v[1]
pos = {p["m"]: p for p in L["pos"]}
print("   token holdings changed over P3 (largest by value at the ledger's last price):")
import bisect
vals = []
for m, q in dq.items():
    p = pos.get(m)
    if not p or abs(q) < 1e-12: continue
    # last price: the ledger's SOL per token from its trades (tr: [slot, bt, isbuy, v, q])
    tr = [t for t in p["tr"] if t[4]]
    px = abs(tr[-1][3] / tr[-1][4]) if tr else 0
    vals.append((q * px, m, q, px))
for v, m, q, px in sorted(vals, key=lambda z: -abs(z[0]))[:6]:
    print(f"      {NAMES.get(m[:8], m[:8]):8s} {q:+.6g} tokens  about {v:+.3f} SOL")
print(f"      all tokens: about {sum(v for v, *_ in vals):+.3f} SOL")
