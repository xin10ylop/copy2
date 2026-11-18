# Attention study, the signals as a filter on wallet 4's own buys (Nov 18; the money test showed the signals alone do not
# pay). Wallet 4's 1,559 copyable buys of Oct 21 - Nov 16 with our modelled copy of each (SP/hunt_screen.json.gz, the
# frozen live setup, 0.0026 SOL a round trip; the report also at 0.0345); each coin's create transaction (its bonding
# curve's signatures paged back to the first, at most PAGES pages): the dev buy, tips, mayhem, the creator fee, the payer.
# Pre-registered: groups fixed below; pick on the first half of its buys by time, score on the second; a filter is only
# proposed if its removed copies lose in both halves and it has a reason. A live change is the owner's call.
#   RPC_URL=... LK=SP/attn/lk python3 -I a9_w4_filter.py SP [PAGES=15]   -> SP/attn/w4_create.json, then the report
import sys, os, json, gzip
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-13/tab_exits"); import lib
from solders.pubkey import Pubkey as P
SP = sys.argv[1]; PAGES = int(sys.argv[2]) if len(sys.argv) > 2 else 15
curve = lambda m: str(P.find_program_address([b"bonding-curve", bytes(P.from_string(m))], P.from_string(lib.PUMP))[0])
W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"; ROWS = json.load(gzip.open(f"{SP}/hunt_screen.json.gz"))[W4]
SYS = "11111111111111111111111111111111"; OUTF = f"{SP}/attn/w4_create.json"
def feat(m):
    before = None; last = None
    for _ in range(PAGES):
        s = lib.sigs(curve(m), before=before, limit=1000)
        if not s: break
        last = s[-1]["signature"]; before = last
        if len(s) < 1000: break
    else: return m, None
    if not last: return m, None
    try: t = lib.tx(last)
    except Exception: return m, None
    if not t: return m, None
    ks = lib.keys_of(t); ev = lib.events(t); cr = next((e for k, e in ev if k == "create"), None)
    if not cr or cr.get("mint") != m: return m, None
    tr = [e for k, e in ev if k == "trade" and e.get("mint") == m and e.get("is_buy")]
    tips = sum(ix["parsed"]["info"]["lamports"] for ix in t["transaction"]["message"]["instructions"]
               if ix.get("programId") == SYS and isinstance(ix.get("parsed"), dict) and ix["parsed"].get("type") == "transfer")
    return m, dict(t=t["blockTime"], dev_buy=sum(e["sol"] for e in tr if e["user"] in (cr["user"], cr["creator"], ks[0])) / 1e9, tips=tips / 1e9,
                   mayhem=cr.get("mayhem"), cfee=cr.get("creator_fee_bps"), payer_is_creator=cr["user"] == cr["creator"], creator=cr["creator"],
                   payer_sol=t["meta"]["preBalances"][0] / 1e9, name=cr["name"], symbol=cr["symbol"])
if not os.path.exists(OUTF):
    with ThreadPoolExecutor(16) as ex: F = dict(ex.map(feat, sorted({r["m"] for r in ROWS})))
    json.dump(F, open(OUTF, "w"))
print(f"{len(ROWS)} buys; creates read {sum(1 for v in json.load(open(OUTF)).values() if v)}")
