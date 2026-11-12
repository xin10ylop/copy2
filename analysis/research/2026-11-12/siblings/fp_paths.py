# Wallet 4's fingerprint among every wallet that traded its coins: the cached transactions of the 222 routable coins it
# bought Oct 28 - Nov 12 (since_stop/model.py, SPD/cache/tx_*.json.gz, 31 minutes from its buy). Per fee payer: how
# many transactions, how many tip exactly 1,067,000 or 1,010,000 lamports (its two tip sizes, rare: wallet-check.md),
# how many start with AdvanceNonceAccount, and how many coins it traded.
#   python3 -I fp_paths.py SPD
import sys, os, json, gzip, glob, collections, base64
SPD = sys.argv[1]; W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
SYS = "11111111111111111111111111111111"
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
def b58d(s):
    n = 0
    for c in s: n = n * 58 + B58.index(c)
    b = n.to_bytes((n.bit_length() + 7) // 8, "big")
    return b"\0" * (len(s) - len(s.lstrip("1"))) + b
stats = collections.defaultdict(lambda: dict(tx=0, tip=0, nonce=0, coins=set(), sizes=collections.Counter()))
files = glob.glob(f"{SPD}/cache/tx_*.json.gz")
for fn in files:
    try: t = json.load(gzip.open(fn))
    except Exception: continue
    if not t or t["meta"].get("err"): continue
    m = t["transaction"]["message"]; ks = m["accountKeys"] + (t["meta"].get("loadedAddresses") or {}).get("writable", []) + (t["meta"].get("loadedAddresses") or {}).get("readonly", [])
    payer = ks[0]; s = stats[payer]; s["tx"] += 1
    ix = m["instructions"]
    if ix and ks[ix[0]["programIdIndex"]] == SYS and b58d(ix[0].get("data", "") or "1")[:4] == b"\x04\x00\x00\x00": s["nonce"] += 1
    for i in ix:
        if ks[i["programIdIndex"]] != SYS: continue
        d = b58d(i.get("data", "") or "1")
        if len(d) == 12 and d[:4] == b"\x02\x00\x00\x00" and i["accounts"] and ks[i["accounts"][0]] == payer:
            lam = int.from_bytes(d[4:12], "little")
            if 1_000_000 <= lam <= 1_100_000: s["sizes"][lam] += 1
            if lam in (1_067_000, 1_010_000): s["tip"] += 1
    for b in (t["meta"].get("postTokenBalances") or []):
        if b.get("owner") == payer and b["mint"].endswith("pump"): s["coins"].add(b["mint"])
print(f"{len(files)} cached transactions, {len(stats)} fee payers")
rows = sorted(stats.items(), key=lambda kv: (-kv[1]["tip"], -len(kv[1]["coins"])))
print("payers with any tip of exactly 1,067,000 or 1,010,000 lamports:")
for a, s in rows:
    if s["tip"] == 0: break
    print(f"  {a}  {s['tip']:4d} of {s['tx']:5d} tx, nonce-first {s['nonce']:4d}, coins {len(s['coins']):3d}" + ("   <- wallet 4" if a == W4 else ""))
near = [(a, s) for a, s in rows if s["tip"] == 0 and sum(s["sizes"].values()) >= 5]
print(f"payers tipping 1.00-1.10 M lamports 5+ times, but never wallet 4's two sizes: {len(near)}")
for a, s in sorted(near, key=lambda kv: -sum(kv[1]["sizes"].values()))[:8]:
    print(f"  {a}  sizes {dict(s['sizes'].most_common(3))}  nonce-first {s['nonce']}/{s['tx']}  coins {len(s['coins'])}")
