# Attention study, H7 step 2: what is in the create transaction itself, the only thing wallet 4 can read when it buys
# (98% of its coins within 2 s of the create, a3_w4_pick.py). Every coin wallet 4 traded in the 48 h, and a random
# sample (seed 7) of the other launches of the same hours; each create transaction (jsonParsed) -> its CreateEvent
# (name, symbol, uri, mayhem, cashback, creator fee, token program), the trades inside it (the dev buy, others in the
# same transaction), the fee payer's SOL before, the priority fee and tips, the programs called.
#   RPC_URL=... LK=SP/attn/lk python3 -I a4_create_tx.py SP [NOTHER=4000]   -> SP/attn/create_tx.json
import sys, os, json, random, collections
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-13/tab_exits"); import lib
SP = sys.argv[1]; NOTHER = int(sys.argv[2]) if len(sys.argv) > 2 else 4000; W4LAST = 1794858000
W4M = json.load(open(f"{SP}/hunt/w4_mints.json")); CR = json.load(open(f"{SP}/market/creates.json")); OUT = json.load(open(f"{SP}/attn/outcomes.json"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import creates
sig_of = {m: s for m, (s, v) in creates.load(SP).items() if OUT.get(m) and v["t"] < W4LAST - 3600}
mine = [m for m in sig_of if m in W4M]; rest = sorted(m for m in sig_of if m not in W4M)
pick = mine + random.Random(7).sample(rest, min(NOTHER, len(rest)))
CB = "ComputeBudget111111111111111111111111111111"; SYS = "11111111111111111111111111111111"
def feat(m):
    try: t = lib.tx(sig_of[m])
    except Exception: return m, None
    if not t: return m, None
    ks = lib.keys_of(t); meta = t["meta"]; ev = lib.events(t)
    cr = next((e for k, e in ev if k == "create"), None)
    tr = [e for k, e in ev if k == "trade" and e.get("mint") == m and e.get("is_buy")]
    progs = []; cu_price = None; tips = 0
    ixs = t["transaction"]["message"]["instructions"]
    for ix in ixs:
        p = ix.get("programId"); progs.append(p)
        if p == CB and ix.get("data"):
            raw = lib.b58d(ix["data"])
            if raw[:1] == b"\x03": cu_price = int.from_bytes(raw[1:9], "little")
        if p == SYS and isinstance(ix.get("parsed"), dict) and ix["parsed"].get("type") == "transfer":
            tips += ix["parsed"]["info"]["lamports"]
    payer = ks[0]
    return m, dict(name=cr["name"] if cr else None, symbol=cr["symbol"] if cr else None, uri=cr["uri"] if cr else None,
                   user=cr["user"] if cr else None, creator=cr["creator"] if cr else None, mayhem=cr.get("mayhem") if cr else None,
                   cashback=cr.get("cashback") if cr else None, cfee=cr.get("creator_fee_bps") if cr else None, tprog=cr.get("token_program") if cr else None,
                   dev_buy=sum(e["sol"] for e in tr if e["user"] == payer) / 1e9, n_buyers=len({e["user"] for e in tr}),
                   other_buy=sum(e["sol"] for e in tr if e["user"] != payer) / 1e9, payer_sol=meta["preBalances"][0] / 1e9,
                   fee=meta["fee"] / 1e9, cu_price=cu_price, transfers=tips / 1e9, n_ix=len(ixs), progs=sorted(set(progs)), n_sig=len(t["transaction"]["signatures"]))
res = {}
with ThreadPoolExecutor(12) as ex:
    for m, f in ex.map(feat, pick): res[m] = f
json.dump(dict(mine=mine, rows=res), open(f"{SP}/attn/create_tx.json", "w"))
print(f"{len(mine)} of wallet 4's coins, {len(pick) - len(mine)} others; read {sum(1 for v in res.values() if v)}")
