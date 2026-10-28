# Step 4: entry mechanics of top profitable wallets from sampled buys located in their blocks.
import sys, os, json, random, collections, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C, blocks as B, rival_stats as R
W = sys.argv[1:]; random.seed(3); res = {}
for w in W:
    h = json.load(open(os.path.join(C.OUTD, f"hist_{w}.json")))
    P = [R.parse(w, t) for t in sorted(reversed(h["txs"]), key=lambda t: t["slot"])]
    buys = [p for p in P if len(p["legs"]) == 1 and list(p["legs"].values())[0] > 0 and p["pumpfee"]]
    first_sell = {}
    for p in P:
        if len(p["legs"]) == 1:
            m, v = list(p["legs"].items())[0]
            if v < 0 and m not in first_sell: first_sell[m] = p["slot"]
    smp = random.sample(buys, min(20, len(buys))); rows = []
    for p in smp:
        mint = list(p["legs"])[0]; b = B.summarize(p["slot"])
        me = [x for x in b["txs"] if x["sig"] == p["sig"]] if b else []
        if not me: continue
        me = me[0]; tr = [t for t in me["trades"] if t["mint"] == mint and t["user"] == w]
        cs = ci = None
        for s in range(p["slot"], p["slot"] - 8, -1):
            bb = B.summarize(s)
            if not bb: continue
            c = [x for x in bb["txs"] if x["create_mint"] == mint]
            if c: cs, ci = s, c[0]["idx"]; break
        sol_ahead = (tr[0]["vsol"] - tr[0]["sol"]) / 1e9 - 30 if tr else None
        rows.append(dict(idx=me["idx"], n=b["n"], doff=(p["slot"] - cs) if cs is not None else ">7", ridx=(me["idx"] - ci) if cs == p["slot"] else None,
                         fee=me["fee"], cu=me["cu_price"], tips=me["tips"], tip=me["tip_total"], ix=me["pump_ix"], sol=tr[0]["sol"] / 1e9 if tr else None,
                         sol_ahead=sol_ahead, exit_slots=(first_sell[mint] - p["slot"]) if mint in first_sell else None))
    hrs = collections.Counter(p["ts"] // 3600 for p in buys)
    exits = [first_sell[m] - p["slot"] for p in buys for m in p["legs"] if m in first_sell and first_sell[m] >= p["slot"]]
    res[w] = dict(rows=rows, buys_per_active_h=st.median(hrs.values()), active_h=len(hrs), exit_slots_med=st.median(exits) if exits else None,
                  exit_slots_p25=sorted(exits)[len(exits)//4] if exits else None, exit_slots_p75=sorted(exits)[3*len(exits)//4] if exits else None)
    r = rows
    print(f"\n{w}  sampled {len(r)}  buys/active-h median {res[w]['buys_per_active_h']} over {len(hrs)} h  exit slots p25/med/p75 {res[w]['exit_slots_p25']}/{res[w]['exit_slots_med']}/{res[w]['exit_slots_p75']}")
    print("  doff", dict(collections.Counter(x["doff"] for x in r)), " ridx(same-slot) med", st.median([x["ridx"] for x in r if x["ridx"] is not None] or [-1]),
          " idx med", st.median([x["idx"] for x in r]), " fee med %.2fM" % (st.median([x["fee"] for x in r]) / 1e6), " cu med", st.median([x["cu"] or 0 for x in r]),
          " tip med %.2fM" % (st.median([x["tip"] for x in r]) / 1e6), " tipped share", sum(1 for x in r if x["tip"]) / len(r))
    print("  tip providers", dict(collections.Counter(k for x in r for k in x["tips"])), " ix", dict(collections.Counter(tuple(x["ix"]) for x in r)))
    print("  SOL in curve ahead of them: med", st.median([x["sol_ahead"] for x in r if x["sol_ahead"] is not None]), " size med", st.median([x["sol"] for x in r if x["sol"]]))
    for x in r[:6]: print("   ", {k: x[k] for k in ("doff", "idx", "ridx", "fee", "tip", "sol", "sol_ahead", "exit_slots")})
json.dump(res, open(os.path.join(C.OUTD, "mech.json"), "w"))
