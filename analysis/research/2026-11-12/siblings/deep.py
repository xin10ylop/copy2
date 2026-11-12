# A closer look at candidate wallets (their newest own transactions: tip sizes, nonce-first, nonce authority, what they
# buy) and at the cash-out address's outflows since Nov 9.
#   python3 -I deep.py ADDR [ADDR ...]
import sys, json, os, time, urllib.request, collections, datetime
SP = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad"
R = open(f"{SP}/month/.triton_url").read().strip()
SYS = "11111111111111111111111111111111"; W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
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
f = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d %H:%M")
for A in sys.argv[1:]:
    sigs = [s for s in (rpc("getSignaturesForAddress", [A, {"limit": 300}]) or []) if s["err"] is None]
    own = 0; tips = collections.Counter(); nonce = 0; sizes = []; first = sigs[-1]["blockTime"] if sigs else 0
    for s in sigs[:120]:
        t = rpc("getTransaction", [s["signature"], {"encoding": "json", "maxSupportedTransactionVersion": 1}])
        if not t: continue
        m = t["transaction"]["message"]; ks = m["accountKeys"] + (t["meta"].get("loadedAddresses") or {}).get("writable", []) + (t["meta"].get("loadedAddresses") or {}).get("readonly", [])
        if ks[0] != A: continue
        own += 1; ix = m["instructions"]
        if ix and ks[ix[0]["programIdIndex"]] == SYS and b58d(ix[0].get("data", "") or "1")[:4] == b"\x04\x00\x00\x00": nonce += 1
        for i in ix:
            if ks[i["programIdIndex"]] == SYS:
                d = b58d(i.get("data", "") or "1")
                if len(d) == 12 and d[:4] == b"\x02\x00\x00\x00" and ks[i["accounts"][0]] == A:
                    lam = int.from_bytes(d[4:12], "little")
                    if lam < 50_000_000: tips[lam] += 1
        dsol = (t["meta"]["postBalances"][0] - t["meta"]["preBalances"][0]) / 1e9
        if dsol < -0.3: sizes.append(round(-dsol, 2))
    print(f"== {A}: {len(sigs)} landed signatures (oldest of them {f(first)} Beirut), {own} own of the newest 120")
    print(f"   nonce-first {nonce}/{own}; tips (lamports, top 5) {dict(tips.most_common(5))}; SOL spent per tx over 0.3: {sorted(sizes)[-12:]}")
