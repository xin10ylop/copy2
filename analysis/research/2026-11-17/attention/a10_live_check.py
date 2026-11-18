# The live check of the pre-registered filter (README): our bot wallet's coins after the backtest window (Nov 16 14:25:07
# UTC), from its own transactions on chain (the mints it received), each coin's create (its bonding curve paged back)
# and the SOL its fee payer held before. The result of each trade comes from the bot's journal ("long closed" lines, the
# owner's paste in out/live_closed.txt), matched by the mint's first 8 characters.
#   RPC_URL=... LK=SP/attn/lk python3 -I a10_live_check.py SP
import sys, os, re, json
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-13/tab_exits"); import lib
from solders.pubkey import Pubkey as P
SP = sys.argv[1]; BOT = "Eao8T2Pk2aDzPWUFCA8si7oWd5ndFKfnX3HjYMpERst6"; T0 = 1794839107
curve = lambda m: str(P.find_program_address([b"bonding-curve", bytes(P.from_string(m))], P.from_string(lib.PUMP))[0])
sigs, before = [], None
while True:
    s = lib.sigs(BOT, before=before, limit=1000, cache=False)
    if not s: break
    sigs += [x for x in s if x.get("blockTime") and x["blockTime"] >= T0 and x.get("err") is None]; before = s[-1]["signature"]
    if s[-1].get("blockTime", 0) < T0 or len(s) < 1000: break
mints = {}
def got(x):
    t = lib.tx(x["signature"])
    if not t: return []
    pre = {(b["mint"], b["owner"]): float(b["uiTokenAmount"]["uiAmount"] or 0) for b in t["meta"].get("preTokenBalances") or []}
    return [(b["mint"], x["blockTime"]) for b in t["meta"].get("postTokenBalances") or []
            if b.get("owner") == BOT and float(b["uiTokenAmount"]["uiAmount"] or 0) > pre.get((b["mint"], BOT), 0) and b["mint"].endswith("pump")]
with ThreadPoolExecutor(16) as ex:
    for L in ex.map(got, sigs):
        for m, t in L: mints.setdefault(m, t)
def payer(m):
    before = last = None
    for _ in range(15):
        s = lib.sigs(curve(m), before=before, limit=1000)
        if not s: break
        last = s[-1]["signature"]; before = last
        if len(s) < 1000: break
    t = lib.tx(last) if last else None
    if not t: return m, None
    ev = lib.events(t); cr = next((e for k, e in ev if k == "create"), None)
    return m, (t["meta"]["preBalances"][0] / 1e9 if cr and cr.get("mint") == m else None)
with ThreadPoolExecutor(16) as ex: PS = dict(ex.map(payer, list(mints)))
json.dump({m: dict(t=mints[m], payer_sol=PS[m]) for m in mints}, open(f"{SP}/attn/live_coins.json", "w"))
print(f"{len(sigs)} bot transactions since Nov 16 14:25 UTC; {len(mints)} coins bought; payer read for {sum(1 for v in PS.values() if v is not None)}")
CL = f"{os.path.dirname(os.path.abspath(__file__))}/out/live_closed.txt"
if os.path.exists(CL):
    net = {}
    for l in open(CL):
        g = re.search(r"long closed #(\d+) (\w{8}) \S+ net ([+-][\d.]+) SOL", l)
        if g: net[g.group(2)] = net.get(g.group(2), 0) + float(g.group(3))
    rows = [(m, PS.get(m), net[m[:8]]) for m in mints if m[:8] in net]
    for name, f in (("payer held 0.5 SOL or less (the filter would skip)", lambda p: p is not None and p <= 0.5), ("payer held more", lambda p: p is not None and p > 0.5), ("payer unknown", lambda p: p is None)):
        X = [n for _, p, n in rows if f(p)]; print(f"   {name:52s} {len(X):3d} trades, net {sum(X):+.4f} SOL")
