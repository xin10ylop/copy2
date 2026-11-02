# The create-row decoder shared by s1b_picks.py and s2_sample.py.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
def top_progs(t):
    out = []
    for ix in t["transaction"]["message"]["instructions"]:
        p = ix.get("programId")
        if p and p not in out: out.append(p)
    return out
def crow(t, sig):
    ev = lib.events(t); cr = [e for k, e in ev if k == "create"]
    if not cr: return None
    c = cr[0]; m = c["mint"]; ks = lib.keys_of(t)
    return dict(csig=sig, cslot=t["slot"], cbt=t.get("blockTime"), cidx=t.get("transactionIndex"), payer=ks[0],
                mint=m, quote=c.get("quote_mint"), user=c["user"], creator=c["creator"], name=c["name"][:64], sym=c["symbol"][:32],
                uri=c["uri"][:200], vquote=c.get("vquote"), vsol=c["vsol"], vtok=c["vtok"], depth=c.get("depth"),
                mayhem=c.get("mayhem"), cashback=c.get("cashback"), cfee=c.get("creator_fee_bps"), token_program=c.get("token_program"),
                dev=[[e["user"], e["is_buy"], e["sol"], e["tok"], e.get("quote_amount"), e["vtok"]] for k, e in ev if k == "trade" and e["mint"] == m],
                fee=(t.get("meta") or {}).get("fee"), progs=top_progs(t), nsig=len(t["transaction"].get("signatures") or []),
                cu=(t.get("meta") or {}).get("computeUnitsConsumed"))
