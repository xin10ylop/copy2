# c1 (Nov 19): pump_pair/p1_fetch.py for any wallets (WALLETS=a,b,...) into SP/SUB (the m16 candidates' own histories).
# One trader, two wallets (Nov 19; m12_clusters: 8zqsUMty + FDhoU1DE buy the same coins within 1 slot; on the 4 days
# their copy +19.6% a copy and up on the blind days). Their OWN pump trades over the last DAYS days, from Solana's free
# public node or Triton (RPC_URL; batches of 100; resumable: signatures and decoded trades are cached in SP/pair/).
#   RPC_URL=https://api.mainnet-beta.solana.com python3 -I p1_fetch.py SP DAYS
import sys, os, json, time
SP, DAYS = sys.argv[1], float(sys.argv[2]); O = f"{SP}/" + os.environ.get("SUB", "pair"); os.makedirs(O, exist_ok=True)
src = open("/home/user/copy2/analysis/research/2026-11-17/winners/w4_history.py").read().split("def history")[0]
ns = {"__file__": "w4_history.py"}; sys.argv = ["x", SP]; exec(compile(src, "w4_history.py", "exec"), ns)
WALLETS = os.environ["WALLETS"].split(",")   # comma-separated (candidates/c1_fetch.py)
since = time.time() - DAYS * 86400
for w in WALLETS:
    fs = f"{O}/{w[:8]}_sigs.json"
    if os.path.exists(fs): sigs = json.load(open(fs))
    else:
        sigs, before, pages, failed = [], None, 0, 0
        # MAXPAGES (Nov 22): a wallet whose address carries thousands of failed transactions a minute (4vw54BmA) would page
        # for hours; stop after MAXPAGES pages of 1,000 and keep what was read (its newest days only), saying so
        MAXP = int(os.environ.get("MAXPAGES", 10**9))
        while True:
            pg = ns["call"]("getSignaturesForAddress", [w, {"limit": 1000, **({"before": before} if before else {})}])
            if not pg: break
            pages += 1; failed += sum(1 for s in pg if s["err"] is not None)
            sigs += [[s["signature"], s.get("blockTime") or 0] for s in pg if s["err"] is None]; before = pg[-1]["signature"]
            if len(pg) < 1000 or (pg[-1].get("blockTime") or 0) < since: break
            if pages >= MAXP:
                print(f"{w[:8]}: stopped at {pages} pages ({failed:,} failed transactions); history from "
                      f"{time.strftime('%m-%d %H:%M', time.gmtime(pg[-1].get('blockTime') or 0))} UTC only", flush=True); break
        sigs = [s for s in sigs if s[1] >= since]; json.dump(sigs, open(fs, "w"))
    ft = f"{O}/{w[:8]}_trades.jsonl"; done = set()
    if os.path.exists(ft):
        for l in open(ft): done.add(json.loads(l)["sig"])
    print(f"{w[:8]}: {len(sigs)} transactions in {DAYS:g} days, {len(done)} already read", flush=True)
    todo = [x for x in sigs if x[0] not in done]; ch = [todo[i:i + 100] for i in range(0, len(todo), 100)]
    with open(ft, "a") as f:
        for n, part in enumerate(ns["POOL"].map(lambda c: (c, ns["_batch"]([x[0] for x in c])), ch)):
            c, txs = part
            for (s, bt), tx in zip(c, txs): f.write(json.dumps({"sig": s, "t": bt, "trades": ns["own_trades"](tx, w) if tx else None}) + "\n")
            f.flush(); print(f"   {w[:8]} {min((n + 1) * 100, len(todo))}/{len(todo)}", flush=True)
print("done")
