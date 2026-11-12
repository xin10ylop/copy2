# Who else pays wallet 4's exact tip sizes (1,067,000 or 1,010,000 lamports), on any coin: the newest transactions sent to
# the tip accounts wallet 4 paid in its own recent transactions (from SPD/w4tx), each account's newest N signatures.
#   python3 -I tipscan.py SPD N
import sys, os, json, gzip, time, urllib.request, collections, concurrent.futures as cf, datetime
SPD = sys.argv[1]; N = int(sys.argv[2]); W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
SP = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad"
R = open(f"{SP}/month/.triton_url").read().strip(); SYS = "11111111111111111111111111111111"
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
def b58d(s):
    n = 0
    for c in s: n = n * 58 + B58.index(c)
    b = n.to_bytes((n.bit_length() + 7) // 8, "big"); return b"\0" * (len(s) - len(s.lstrip("1"))) + b
def rpc(m, p):
    for k in range(6):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(R, json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), {"content-type": "application/json"}), timeout=60))
            if "result" in r: return r["result"]
        except Exception: pass
        time.sleep(1.5 * (k + 1))
def tips_of(t):
    m = t["transaction"]["message"]; ks = m["accountKeys"] + (t["meta"].get("loadedAddresses") or {}).get("writable", []) + (t["meta"].get("loadedAddresses") or {}).get("readonly", [])
    out = []
    for i in m["instructions"] + [x for g in (t["meta"].get("innerInstructions") or []) for x in g["instructions"]]:
        if ks[i["programIdIndex"]] != SYS: continue
        d = b58d(i.get("data", "") or "1")
        if len(d) == 12 and d[:4] == b"\x02\x00\x00\x00" and len(i["accounts"]) >= 2:
            out.append((ks[i["accounts"][0]], ks[i["accounts"][1]], int.from_bytes(d[4:12], "little")))
    return ks, out
# the tip accounts wallet 4 itself paid, from its newest 2,000 transactions
used = collections.Counter()
files = sorted(os.listdir(f"{SPD}/w4tx"))[-2000:]
for fn in files:
    t = json.load(open(f"{SPD}/w4tx/{fn}")); ks, tr = tips_of(t)
    for a, b, lam in tr:
        if a == W4 and lam in (1_067_000, 1_010_000): used[b] += 1
accts = [a for a, _ in used.most_common()]
print(f"wallet 4 paid its two tip sizes to {len(accts)} accounts in its newest 2,000 transactions")
def scan(acct):
    sigs = [s for s in (rpc("getSignaturesForAddress", [acct, {"limit": N}]) or []) if s["err"] is None]
    hits = collections.Counter(); n = 0; t0 = t1 = None
    for s in sigs:
        t = rpc("getTransaction", [s["signature"], {"encoding": "json", "maxSupportedTransactionVersion": 1}])
        if not t: continue
        n += 1; t0 = min(t0 or s["blockTime"], s["blockTime"]); t1 = max(t1 or 0, s["blockTime"])
        ks, tr = tips_of(t)
        for a, b, lam in tr:
            if b == acct and lam in (1_067_000, 1_010_000): hits[a] += 1
    return acct, n, t0, t1, hits
total = collections.Counter(); spans = []
with cf.ThreadPoolExecutor(8) as ex:
    for acct, n, t0, t1, hits in ex.map(scan, accts):
        total.update(hits); spans.append((n, t0, t1))
f = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d %H:%M")
print(f"scanned {sum(n for n, _, _ in spans)} transactions to those accounts, from {f(min(t for _, t, _ in spans if t))} to {f(max(t for _, _, t in spans if t))} Beirut")
print("payers of exactly 1,067,000 or 1,010,000 lamports to them:")
for a, c in total.most_common(15): print(f"  {a}  {c}" + ("   <- wallet 4" if a == W4 else ""))
