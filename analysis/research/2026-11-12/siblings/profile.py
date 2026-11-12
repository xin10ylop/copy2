# What a candidate wallet does: per own transaction, the programs it calls, its SOL and token changes (pump coins, quote
# tokens), and its first transactions (funding).
#   python3 -I profile.py ADDR [N]
import sys, json, time, urllib.request, collections, datetime
SP = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad"
R = open(f"{SP}/month/.triton_url").read().strip(); A = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 60
NAMES = {"6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "pump", "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA": "pumpswap",
         "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUJw2dS3Wdpc4": "jupiter", "11111111111111111111111111111111": "system",
         "ComputeBudget111111111111111111111111111111": "", "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA": "token",
         "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb": "token22", "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL": "ata"}
def rpc(m, p):
    for k in range(6):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(R, json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), {"content-type": "application/json"}), timeout=60))
            if "result" in r: return r["result"]
        except Exception: pass
        time.sleep(1.5 * (k + 1))
f = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d %H:%M:%S")
allsigs, before = [], None
while True:
    p = {"limit": 1000}
    if before: p["before"] = before
    page = rpc("getSignaturesForAddress", [A, p]) or []
    allsigs += page
    if len(page) < 1000: break
    before = page[-1]["signature"]
ok = [s for s in allsigs if s["err"] is None]
print(f"{A}: {len(allsigs)} signatures ({len(ok)} landed), {f(allsigs[-1]['blockTime'])} -> {f(allsigs[0]['blockTime'])} Beirut")
progs = collections.Counter(); mints = collections.Counter()
def show(s, label=""):
    t = rpc("getTransaction", [s["signature"], {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 1}])
    if not t: return
    ks = [k["pubkey"] for k in t["transaction"]["message"]["accountKeys"]]
    i = ks.index(A) if A in ks else None
    d = (t["meta"]["postBalances"][i] - t["meta"]["preBalances"][i]) / 1e9 if i is not None else 0
    pr = sorted({NAMES.get(ks[j] if False else (ix.get("programId") or ""), (ix.get("programId") or "")[:6]) for ix in t["transaction"]["message"]["instructions"]} - {""})
    inner = {NAMES.get(ix.get("programId") or "", "") for g in (t["meta"].get("innerInstructions") or []) for ix in g["instructions"]} - {"", "token", "token22", "system", "ata"}
    tok = collections.defaultdict(float)
    for b in t["meta"].get("preTokenBalances") or []:
        if b.get("owner") == A: tok[b["mint"]] -= float(b["uiTokenAmount"]["uiAmountString"] or 0)
    for b in t["meta"].get("postTokenBalances") or []:
        if b.get("owner") == A: tok[b["mint"]] += float(b["uiTokenAmount"]["uiAmountString"] or 0)
    tk = {m[:8]: round(v, 6) for m, v in tok.items() if abs(v) > 0}
    for m in tok:
        if m.endswith("pump"): mints[m] += 1
    progs.update(pr); progs.update(inner)
    print(f"  {label}{f(s['blockTime'])} signer {ks[0][:8]} {d:+.4f} SOL  {pr}{' via ' + str(sorted(inner)) if inner else ''}  {tk}")
print("its first 6 transactions:")
for s in list(reversed(ok))[:6]: show(s, "first ")
print(f"its newest {N} landed transactions:")
for s in ok[:N]: show(s)
print("programs:", dict(progs.most_common(10)))
print("pump coins touched:", len(mints))
