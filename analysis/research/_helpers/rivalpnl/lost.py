# Step 1b: for each failed buy, who bought that mint ahead of us (create slot .. our slot/index).
import sys, os, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C, blocks as B
rows = json.load(open(os.path.join(C.OUTD, "our_rows.json")))
which = sys.argv[1] if len(sys.argv) > 1 else "fail"
sel = [r for r in rows if r["kind"] == "buy" and (r["err"] if which == "fail" else not r["err"])]
out = []
for r in sel:
    mint, slot = r["mint"], r["slot"]
    b = B.summarize(slot)
    me = [x for x in b["txs"] if x["sig"] == r["sig"]]
    myidx = me[0]["idx"] if me else None
    # find create slot
    cslot, cidx, creator = None, None, None
    for s in range(slot, slot - 6, -1):
        bb = b if s == slot else B.summarize(s)
        if not bb: continue
        c = [x for x in bb["txs"] if x["create_mint"] == mint]
        if c: cslot, cidx, creator = s, c[0]["idx"], c[0]["signer"]; break
    ahead = []
    if cslot is not None:
        for s in range(cslot, slot + 1):
            bb = B.summarize(s)
            if not bb: continue
            for x in bb["txs"]:
                if x["err"]: continue
                if s == cslot and x["idx"] < cidx: continue
                if s == slot and myidx is not None and x["idx"] >= myidx: continue
                for t in x["trades"]:
                    if t["mint"] != mint or not t["is_buy"]: continue
                    ahead.append(dict(user=t["user"], signer=x["signer"], sol=t["sol"] / 1e9, vsol=t["vsol"], slot=s, doff=s - cslot, idx=x["idx"],
                                      ridx=(x["idx"] - cidx) if s == cslot else None, fee=x["fee"], cu_price=x["cu_price"], tips=x["tips"],
                                      is_create=x["create_mint"] == mint, is_creator=t["user"] == creator, ix=x["pump_ix"]))
    out.append(dict(sig=r["sig"], mint=mint, slot=slot, myidx=myidx, cslot=cslot, cidx=cidx, creator=creator, late=(slot - cslot) if cslot else None,
                    errv=r["errv"], my_fee=r["fee"], my_cu=r["cu_price"], my_tips=r["tips"], ahead=ahead, n_block=b["n"]))
json.dump(out, open(os.path.join(C.OUTD, f"lost_{which}.json"), "w"))
print(which, "n", len(out), "create found", sum(1 for o in out if o["cslot"] is not None), "late dist", collections.Counter(o["late"] for o in out))
print("err codes", collections.Counter(str(o["errv"]) for o in out).most_common(5))
