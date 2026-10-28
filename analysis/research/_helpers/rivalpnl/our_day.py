# Step 1a: our day from chain. getTransaction(jsonParsed) for every signature since 00:00 UTC.
import sys, os, json, collections, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C, pumpparse as P
sigs = json.load(open(os.path.join(C.OUTD, f"sigs_{C.OUR}.json")))
rows = []
for s in sigs:
    tx = C.rpc("getTransaction", [s["signature"], {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0, "commitment": "confirmed"}])
    if tx is None: print("missing", s["signature"][:12]); continue
    r = P.analyze(tx); meta = tx["meta"]; ks = P.keys_of(tx)
    i = ks.index(C.OUR); delta = meta["postBalances"][i] - meta["preBalances"][i]
    payer = ks[0] == C.OUR
    # rent: createAccount funded by us; closeAccount refunds to us
    rent_paid = rent_ref = 0
    pre = dict(zip(ks, meta["preBalances"]))
    if not r["err"]:
        for grp in [tx["transaction"]["message"]["instructions"]] + [g["instructions"] for g in meta.get("innerInstructions") or []]:
            for ix in grp:
                p = ix.get("parsed")
                if not isinstance(p, dict): continue
                t, inf = p.get("type"), p.get("info", {})
                if t in ("createAccount", "createAccountWithSeed") and inf.get("source") == C.OUR: rent_paid += inf["lamports"]
                if t == "closeAccount" and inf.get("destination") == C.OUR: rent_ref += pre.get(inf["account"], 0)
    kind = "other"
    names = r["pump_ix"]
    if any(n.startswith("buy") for n in names): kind = "buy"
    elif any(n.startswith("sell") for n in names): kind = "sell"
    elif r["has_pump"] or C.PUMPSWAP in ks: kind = "pump_other"
    mints = sorted({t["mint"] for t in r["trades"] if t["user"] == C.OUR})
    # failed txs: mint from token balances / account list (pump buy accounts: mint is accounts[2] in buy layouts; fall back to *pump key)
    if not mints:
        mints = sorted({k for k in ks if k.endswith("pump")})[:1]
    tsol = sum(t["sol"] for t in r["trades"] if t["user"] == C.OUR)
    tips_paid = 0 if r["err"] else r["tip_total"]
    rows.append(dict(sig=s["signature"], slot=s["slot"], ts=s["blockTime"], kind=kind, err=r["err"], errv=meta["err"], fee=meta["fee"] if payer else 0,
                     delta=delta, tips_paid=tips_paid, tips=r["tips"], rent_paid=rent_paid, rent_ref=rent_ref, mint=mints[0] if mints else None,
                     trade_sol=tsol, cu_price=r["cu_price"], cu_limit=r["cu_limit"], ix=names,
                     sysx=[x for x in r["sysxfers"] if x[1] not in P.TIPS] if kind == "other" else []))
json.dump(rows, open(os.path.join(C.OUTD, "our_rows.json"), "w"))
L = 1e9
def S(f, k): return sum(f(r) for r in rows if k(r)) / L
cnt = collections.Counter((r["kind"], r["err"]) for r in rows)
print("counts:", dict(cnt))
lb = [r for r in rows if r["kind"] == "buy" and not r["err"]]; fb = [r for r in rows if r["kind"] == "buy" and r["err"]]
ls = [r for r in rows if r["kind"] == "sell" and not r["err"]]; fs = [r for r in rows if r["kind"] == "sell" and r["err"]]
# decomposition (residual-based so it sums to the delta exactly)
buy_spend = sum(-(r["delta"]) - r["fee"] - r["tips_paid"] - r["rent_paid"] + r["rent_ref"] for r in lb) / L
sell_proc = sum(r["delta"] + r["fee"] + r["tips_paid"] + r["rent_paid"] - r["rent_ref"] for r in ls) / L
print(f"landed buys {len(lb)}  failed buys {len(fb)}  sells {len(ls)}  failed sells {len(fs)}  other {sum(1 for r in rows if r['kind'] in ('other','pump_other'))}")
print(f"buy spend (curve+pump fees)  {-buy_spend:+.4f}   (TradeEvent sol_amount sum {sum(r['trade_sol'] for r in lb)/L:.4f})")
print(f"sell proceeds                {sell_proc:+.4f}   (TradeEvent sol_amount sum {sum(r['trade_sol'] for r in ls)/L:.4f})")
print(f"fees landed buys             {-S(lambda r:r['fee'], lambda r:r in lb):+.4f}  median {st.median([r['fee'] for r in lb])/L if lb else 0:.5f}")
print(f"fees failed buys             {-S(lambda r:r['fee'], lambda r:r in fb):+.4f}  median {st.median([r['fee'] for r in fb])/L if fb else 0:.5f}")
print(f"fees sells                   {-S(lambda r:r['fee'], lambda r:r in ls):+.4f}")
print(f"fees failed sells            {-S(lambda r:r['fee'], lambda r:r in fs):+.4f}")
tp = collections.Counter()
for r in rows:
    for k, v in (r["tips"].items() if not r["err"] else []): tp[(r["kind"], k)] += v
print("tips paid by kind/provider:", {f"{a}/{b}": round(v / L, 4) for (a, b), v in tp.items()})
print(f"tips total                   {-S(lambda r:r['tips_paid'], lambda r:True):+.4f}")
print(f"rent paid {-S(lambda r:r['rent_paid'], lambda r:True):+.4f}   rent refunded {S(lambda r:r['rent_ref'], lambda r:True):+.4f}")
pumpnet = S(lambda r: r["delta"], lambda r: r["kind"] in ("buy", "sell", "pump_other"))
print(f"NET SOL on pump txs (chain)  {pumpnet:+.4f}")
print(f"other txs net {S(lambda r: r['delta'], lambda r: r['kind']=='other'):+.4f}  n={sum(1 for r in rows if r['kind']=='other')}")
for r in rows:
    if r["kind"] in ("other", "pump_other"): print("   other", r["slot"], r["delta"] / L, r["ix"], [(a[:6], b[:6], c / L) for a, b, c, _ in r["sysx"]][:3])
ledger = buy_spend * 0  # placeholder
led = sell_proc - buy_spend - S(lambda r: r["fee"], lambda r: r in fb)
print(f"ledger-style (sell proceeds - buy spend - failed-attempt fees) {led:+.4f}  vs chain {pumpnet:+.4f}")
# token positions still held
held = collections.Counter()
for r in lb: held[r["mint"]] += 1
for r in ls: held[r["mint"]] -= 1
print("mints bought but no sell:", sum(1 for m, v in held.items() if v > 0), "distinct mints bought", len({r['mint'] for r in lb}))
import datetime
print("first/last pump tx:", datetime.datetime.utcfromtimestamp(min(r['ts'] for r in lb+fb)), datetime.datetime.utcfromtimestamp(max(r['ts'] for r in rows)))
