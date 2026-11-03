# Wallet tracking: a trader that looks empty may trade from sub-accounts, or have moved its money to another address
# or into a vault. For each candidate picked and copyable in rank.json: its sub-accounts, its vault equities, and its
# ledger of the last 120 days (sends, transfers, withdrawals); every other address it moved money to or from (not its
# own dex-to-dex moves, not the system bridge 0x2000...0000 to HyperEVM) is listed with the USD amounts, then every
# sub-account and counterparty is fetched (portfolio) so rank.py can test it like any candidate.
#   python3 -I track.py DATA_DIR
import json, os, sys, time, urllib.request, collections

D = sys.argv[1]; API = "https://api.hyperliquid.xyz/info"; GAP = 1.1; last = [0.0]; DAY = 86400 * 1000
def info(body):
    for i in range(8):
        dt = time.time() - last[0]
        if dt < GAP: time.sleep(GAP - dt)
        last[0] = time.time()
        try:
            req = urllib.request.Request(API, json.dumps(body).encode(), {"Content-Type": "application/json"})
            return json.loads(urllib.request.urlopen(req, timeout=60).read())
        except Exception as e:
            time.sleep(15 * (i + 1) if "429" in str(e) else 3 * (i + 1))
    return None
SYSTEM = {"0x2000000000000000000000000000000000000000", "0x0000000000000000000000000000000000000000"}
rank = json.load(open(f"{D}/rank.json"))
cands = [o for o in rank if o["pick"] and o["copyable"]]
os.makedirs(f"{D}/ledger", exist_ok=True); os.makedirs(f"{D}/port", exist_ok=True)
now = int(time.time() * 1000)
links = []                          # (candidate, other address, relation, usd out, usd in)
for o in cands:
    a = o["a"]
    lf, sf, vf = f"{D}/ledger/{a}.json", f"{D}/ledger/sub_{a}.json", f"{D}/ledger/vault_{a}.json"
    if not os.path.exists(lf): json.dump(info({"type": "userNonFundingLedgerUpdates", "user": a, "startTime": now - 120 * DAY}), open(lf, "w"))
    if not os.path.exists(sf): json.dump(info({"type": "subAccounts", "user": a}), open(sf, "w"))
    if not os.path.exists(vf): json.dump(info({"type": "userVaultEquities", "user": a}), open(vf, "w"))
    L = json.load(open(lf)) or []; S = json.load(open(sf)) or []; V = json.load(open(vf)) or []
    for s in S:
        links.append((a, s["subAccountUser"].lower(), "sub-account", 0.0, 0.0))
    for v in V:
        links.append((a, v["vaultAddress"].lower(), f"vault deposit ${float(v.get('equity') or 0):,.0f}", 0.0, 0.0))
    flow = collections.defaultdict(lambda: [0.0, 0.0, collections.Counter()])
    wd = 0.0
    for x in L:
        dl = x["delta"]; t = dl["type"]
        usd = float(dl.get("usdcValue") or dl.get("usdc") or dl.get("amount") or 0)
        if t == "withdraw": wd += usd; continue
        src, dst = (dl.get("user") or "").lower(), (dl.get("destination") or dl.get("vault") or "").lower()
        if not dst or src == dst: continue
        other = dst if src == a.lower() else src
        if other in SYSTEM or other == a.lower(): continue
        f = flow[other]; f[2][t] += 1
        if src == a.lower(): f[0] += usd
        else: f[1] += usd
    for other, (out_, in_, kinds) in flow.items():
        links.append((a, other, "+".join(sorted(kinds)), out_, in_))
    if wd: links.append((a, "(withdrawn to its own chain address)", "withdraw", wd, 0.0))
json.dump(links, open(f"{D}/links.json", "w"))
others = sorted({l[1] for l in links if l[1].startswith("0x")})
print(f"{len(cands)} candidates; {len(links)} links; {len(others)} other addresses to test", flush=True)
for k, b in enumerate(others):
    if not os.path.exists(f"{D}/port/{b}.json"):
        p = info({"type": "portfolio", "user": b})
        if p is not None: json.dump(p, open(f"{D}/port/{b}.json", "w"))
print("done", flush=True)
