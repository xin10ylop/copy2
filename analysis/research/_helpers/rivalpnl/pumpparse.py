# Decode pump TradeEvent/CreateEvent from a tx (json or jsonParsed encoding), compute budget, tips.
import sys, os, json, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
TAG = bytes.fromhex("e445a52e51cb9a1d"); TRADE = bytes.fromhex("bddb7fd34ee661ee"); CREATEV = bytes.fromhex("1b72a94ddeeb6376")
IX = {k: bytes.fromhex(v) for k, v in dict(create="181ec828051c0777", create_v2="d6904cec5f8b31b4", buy="66063d1201daebea",
      buy_exact_sol_in="38fc74089edfcd5f", sell="33e685a4017f83ad", buy_v2="b817ee6167c5d33d", sell_v2="5df6823ce7e940b2",
      buy_exact_quote_in_v2="c2ab1c46684d5b2f", buy_v3="07051dc4f5176550", sell_v3="1c92de7726c469d5",
      buy_exact_quote_in_v3="e1f7501ed5b38488").items()}
IXR = {v: k for k, v in IX.items()}
TIPS = json.load(open(os.path.join(C.OUTD, "tip_accounts.json")))
SYS = "11111111111111111111111111111111"; CB = "ComputeBudget111111111111111111111111111111"
WANT = {SYS, CB, C.PUMP}
def keys_of(tx):
    m = tx["transaction"]["message"]; ks = [k["pubkey"] if isinstance(k, dict) else k for k in m["accountKeys"]]
    la = (tx.get("meta") or {}).get("loadedAddresses") or {}
    if ks and len(ks) == len(m["accountKeys"]) and isinstance(m["accountKeys"][0], dict): return ks  # jsonParsed already includes loaded
    return ks + la.get("writable", []) + la.get("readonly", [])
def _ixs(tx, ks):
    """yield (program, accounts(list of str), data bytes, outer_index, inner?) for outer and inner ixs."""
    m = tx["transaction"]["message"]
    def norm(ix):
        if "programIdIndex" in ix:
            prog = ks[ix["programIdIndex"]]
            if prog not in WANT: return prog, [], b"", None
            accs = [ks[a] for a in ix.get("accounts", [])]; data = C.b58d(ix.get("data", ""))
            return prog, accs, data, None
        prog = ix.get("programId"); accs = ix.get("accounts", []) or []
        if "parsed" in ix: return prog, accs, b"", ix["parsed"]
        return prog, accs, (C.b58d(ix.get("data", "")) if prog in WANT else b""), None
    for i, ix in enumerate(m["instructions"]): yield (*norm(ix), i, False)
    for grp in (tx.get("meta") or {}).get("innerInstructions") or []:
        for ix in grp["instructions"]: yield (*norm(ix), grp["index"], True)
def u64(b, o): return struct.unpack_from("<Q", b, o)[0]
def decode_trade(d):
    # d starts after TAG+TRADE
    mint = C.b58e(d[0:32]); sol = u64(d, 32); tok = u64(d, 40); isbuy = d[48] == 1; user = C.b58e(d[49:81])
    ts = struct.unpack_from("<q", d, 81)[0]; vsol = u64(d, 89); vtok = u64(d, 97)
    return dict(mint=mint, sol=sol, tok=tok, is_buy=isbuy, user=user, ts=ts, vsol=vsol, vtok=vtok)
def analyze(tx):
    ks = keys_of(tx); meta = tx.get("meta") or {}
    r = dict(signer=ks[0], err=meta.get("err") is not None, fee=meta.get("fee", 0), trades=[], creates=[], pump_ix=[],
             cu_price=None, cu_limit=None, tips={}, tip_total=0, has_pump=C.PUMP in ks, sysxfers=[])
    for prog, accs, data, parsed, oi, inner in _ixs(tx, ks):
        if prog == CB and data:
            if data[0] == 3 and len(data) >= 9: r["cu_price"] = u64(data, 1)
            if data[0] == 2 and len(data) >= 5: r["cu_limit"] = struct.unpack_from("<I", data, 1)[0]
        elif prog == SYS:
            if parsed and parsed.get("type") == "transfer":
                src, dst, lam = parsed["info"]["source"], parsed["info"]["destination"], parsed["info"]["lamports"]
            elif data[:4] == b"\x02\x00\x00\x00" and len(data) >= 12 and len(accs) >= 2:
                src, dst, lam = accs[0], accs[1], u64(data, 4)
            else: continue
            r["sysxfers"].append((src, dst, lam, inner))
            if dst in TIPS:
                r["tips"][TIPS[dst]] = r["tips"].get(TIPS[dst], 0) + lam; r["tip_total"] += lam
        elif prog == C.PUMP and data:
            if data[:8] == TAG and data[8:16] == TRADE: r["trades"].append(decode_trade(data[16:]))
            elif data[:8] == TAG and data[8:16] == CREATEV: r["creates"].append(1)
            elif not inner and data[:8] in IXR:
                n = IXR[data[:8]]; r["pump_ix"].append(n)
                if n.startswith("create"): r["create_mint"] = accs[0] if accs else None
    return r
