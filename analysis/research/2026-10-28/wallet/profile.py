# Quick profile of wallets: signatures (up to CAP), span, a sample of up to N transactions: programs, pump trades by
# the wallet (buys: count, SOL size from its SOL+wSOL change, quote other-than-SOL share), plain SOL in/out >= 0.5.
# Usage: profile.py CAP N ADDR [ADDR ...]   -> wallet/profile_<addr8>.json
import sys; sys.path.insert(0, "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/wallet")
sys.path.insert(0, "/home/user/rugsnipe/analysis")
from w4lib import *
from rugsnipe_analysis import events as E
from rugsnipe_analysis import labels as L
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import random
CAP, N = int(sys.argv[1]), int(sys.argv[2])
def pump_trades(t, ks):
    out = []
    for grp in t["meta"].get("innerInstructions") or []:
        for ix in grp["instructions"]:
            if ks[ix["programIdIndex"]] != PUMP: continue
            raw = b58d(ix.get("data", ""))
            if raw[:8] == E.EVENT_IX_TAG and raw[8:16] == E.DISC_TRADE:
                try: out.append(E.decode_trade(raw[8:]))
                except Exception: pass
    return out
def profile(A):
    s = []; before = None
    while True:
        p = tri.sigs(A, before=before, limit=1000); s += p
        if len(p) < 1000 or len(s) >= CAP: break
        before = p[-1]["signature"]
    if not s: return dict(addr=A, n=0)
    span = (s[-1]["blockTime"], s[0]["blockTime"])
    ok = [x for x in s if not x.get("err")]; random.seed(3)
    smp = ok if len(ok) <= N else random.sample(ok, N)
    with ThreadPoolExecutor(6) as ex: txs = list(ex.map(lambda x: tri.tx(x["signature"]), smp))
    pr = Counter(); buys = []; sells = 0; payer_self = 0; plain = []; ver = Counter(); idx = []
    for x, t in zip(smp, txs):
        if not t: continue
        ks = keys_of(t); ver[str(t.get("version"))] += 1
        if ks[0] == A: payer_self += 1
        for p in progs_of(t): pr[p] += 1
        tr = [e for e in pump_trades(t, ks) if e.user == A]
        if A in ks:
            i = ks.index(A); d = t["meta"]["postBalances"][i] - t["meta"]["preBalances"][i]
            w = sum((1 if side == "postTokenBalances" else -1) * int(b["uiTokenAmount"]["amount"]) for side in ("preTokenBalances", "postTokenBalances") for b in t["meta"].get(side) or [] if b.get("owner") == A and b["mint"] == WSOL)
            net = d + w + (t["meta"]["fee"] if ks[0] == A else 0)
            for e in tr:
                if e.is_buy: buys.append((round(-net / 1e9, 3), e.virtual_sol_reserves == 0)); idx.append(t.get("transactionIndex"))
                else: sells += 1
        for k, a, b, l, m, dd, inn in transfers(t):
            if m in ("SOL", WSOL) and a != b and A in (a, b) and l >= 5e8 and set(progs_of(t)) <= {TOK, T22, "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"}:
                plain.append(("IN" if b == A else "OUT", a if b == A else b, round(l / 1e9, 3), x["blockTime"]))
    lab = L.get_label(A)
    bs = sorted(b[0] for b in buys)
    return dict(addr=A, n=len(s), capped=len(s) >= CAP, first=span[0], last=span[1], sampled=len(smp), payer_self=payer_self,
                progs=[(p, c) for p, c in pr.most_common(8)], nbuys=len(buys), nsells=sells, other_quote=sum(b[1] for b in buys),
                buy_p50=bs[len(bs) // 2] if bs else None, buy_p10=bs[len(bs) // 10] if bs else None, buy_p90=bs[9 * len(bs) // 10] if bs else None,
                big_other=sum(1 for b in buys if b[1] and 1.45 <= b[0] <= 1.6), plain=plain[:30], ver=dict(ver), label=(lab.entity + "/" + lab.category) if lab else None)
for A in sys.argv[3:]:
    r = profile(A); json.dump(r, open(OUT + f"/profile_{A[:8]}.json", "w"))
    if r["n"] == 0: print(A, "no signatures"); continue
    print(f"{A} sigs {r['n']}{'+' if r['capped'] else ''} {ts(r['first'])} -> {ts(r['last'])} label {r['label']} sampled {r['sampled']} self-paid {r['payer_self']} ver {r['ver']}")
    print(f"   pump buys {r['nbuys']} (other-quote {r['other_quote']}, 1.45-1.6 SOL other-quote {r['big_other']}) sells {r['nsells']} buy SOL p10/50/90 {r['buy_p10']}/{r['buy_p50']}/{r['buy_p90']}")
    print("   progs", [(p[:8], c) for p, c in r["progs"]])
    if r["plain"]: print("   plain >=0.5:", [(d, c[:8], v, ts(t)[5:16]) for d, c, v, t in r["plain"][:8]])
