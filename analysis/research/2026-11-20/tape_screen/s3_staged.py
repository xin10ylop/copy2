# The full copy test of one candidate, staged so a bad wallet costs little Triton (Nov 21; the owner: "be smart about
# it: if the first half looks bad, just stop"). Reads the wallet's own trades from s2_history.py's cache (part 1 must
# have run: SP/hist_W8/), then our copy on its past first buys of 0.5+ SOL (STAKE SOL landing in the slot after its
# buy, refused over 1.5x, COST a round trip, the screen's five fixed exits; s2_history.exits):
#   seen   = its OLDER half of buys: batches of 10 coins at random, up to NSEEN; the exit best on them is picked
#   unseen = its NEWER half: batches of 10, up to NUNSEEN, scored with the exit picked on the seen half (blind)
# Stops early: after the first seen batch if every exit is under STOP1 (default -15%), after the seen half if the best
# exit is not above 0, after the first unseen batch if the picked exit is under STOP1.
# Each coin's trades are fetched only to MAXAGE s after its buy (default 640: the longest exit holds 600 s), not the
# 31 minutes s2_history fetches: about a third of the transactions.
#   RPC_URL=... LK=SP/lk COST=0.0064 python3 -I s3_staged.py SP WALLET [NSEEN=20] [NUNSEEN=20]
import sys, os, json, random, collections, datetime as dt, numpy as np, concurrent.futures as cf
SP, W = sys.argv[1], sys.argv[2]; NSEEN = int(sys.argv[3]) if len(sys.argv) > 3 else 20; NUNSEEN = int(sys.argv[4]) if len(sys.argv) > 4 else 20
STOP1 = float(os.environ.get("STOP1", -15)); MAXAGE = float(os.environ.get("MAXAGE", 640))
sys.argv = [sys.argv[0], SP, W, "14", "0"]          # s2_history's own argument shape; its main loop is not run (below)
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "s2_history.py")).read()
exec(src.split("for W in WS:")[0])                  # imports, COST, STAKE, prices(), exits(), M (cmodel), H (hunt_lib)
D = f"{SP}/hist_{W[:8]}"
trades = [e for l in open(f"{D}/{W[:8]}_trades.jsonl") for e in (json.loads(l)["trades"] or [])]
sigs = sorted((t, s) for s, t in json.load(open(f"{D}/{W[:8]}_sigs.json")))
by = collections.defaultdict(list)
for e in trades: by[e["m"]].append(e)
P = prices(sorted({e["quote"] for e in trades if e["quote"] and not e["quote"].startswith("1111")})); su = P.get(SOLM, {}).get("usdPrice")
rate_of = lambda q: 1.0 if not q or q.startswith("1111") else (P[q]["usdPrice"] / su * 1e9 / 10 ** P[q]["decimals"] if su and q in P and P[q].get("decimals") is not None else None)
firsts = []
for m, es in by.items():
    es.sort(key=lambda e: (e["slot"], not e["buy"]))
    if not es[0]["buy"]: continue
    r = rate_of(es[0]["quote"])
    if r is None or es[0]["q"] * r / 1e9 < 0.5 or es[0]["t"] > sigs[-1][0] - MAXAGE - 30: continue
    anchor = next((s for t, s in sigs if t >= es[0]["t"] + MAXAGE), sigs[-1][1])
    firsts.append(dict(m=m, slot=es[0]["slot"], t=es[0]["t"], rate=r, anchor=anchor))
firsts.sort(key=lambda c: c["t"]); h = len(firsts) // 2
older, newer = firsts[:h], firsts[h:]
random.seed(7); random.shuffle(older); random.shuffle(newer)
print(f"{W}: {len(firsts)} past first buys of 0.5+ SOL ({dt.datetime.fromtimestamp(firsts[0]['t'], dt.UTC):%m-%d} to "
      f"{dt.datetime.fromtimestamp(firsts[-1]['t'], dt.UTC):%m-%d}); seen = the older {len(older)}, unseen = the newer {len(newer)}; "
      f"COST {COST} SOL a round trip, {STAKE} SOL a copy, trades fetched to {MAXAGE:.0f} s after its buy")
EX = ("w4", "its", "tp2", "held", "scalp"); ntx = [0]
def run(batch):
    with cf.ThreadPoolExecutor(5) as ex: paths = list(ex.map(lambda c: M.path(c["m"], c["slot"], c["anchor"], threads=10), batch))
    out = []
    for c, tr in zip(batch, paths):
        ntx[0] += len(tr)
        k = next((i for i, e in enumerate(tr) if e["user"] == W and e["buy"] and e["slot"] == c["slot"]), None)
        if k is None: continue
        r = exits(tr, k, c["rate"])
        out.append(r if r else "refused")
    return out
def show(tag, xs):
    ok = [x for x in xs if x != "refused"]
    if not ok: return {e: float("nan") for e in EX}
    mv = {e: float(np.mean([x[e] for x in ok])) for e in EX}
    print(f"  {tag}: {len(ok)} copies ({len(xs) - len(ok)} refused over 1.5x), % a copy: " + "  ".join(f"{e} {mv[e]:+.1f}" for e in EX)
          + f"   [{ntx[0]:,} trades fetched so far]")
    return mv
seen = []
for i in range(0, min(NSEEN, len(older)), 10):
    seen += run(older[i:i + 10]); mv = show(f"seen {i + 1}-{i + 10}", seen)
    if i == 0 and all(v < STOP1 for v in mv.values()):
        print(f"STOP: every exit under {STOP1:.0f}% on the first 10 seen copies"); sys.exit()
best = max(EX, key=lambda e: mv[e])
if not mv[best] > 0:
    print(f"STOP: the best exit on the seen half ({best} {mv[best]:+.1f}%) is not above 0"); sys.exit()
print(f"picked on the seen half: {best} ({mv[best]:+.1f}%)")
unseen = []
for i in range(0, min(NUNSEEN, len(newer)), 10):
    unseen += run(newer[i:i + 10]); mu = show(f"unseen {i + 1}-{i + 10}", unseen)
    if i == 0 and mu[best] < STOP1:
        print(f"STOP: the picked exit {best} is {mu[best]:+.1f}% on the first 10 unseen copies"); sys.exit()
ok = [x[best] for x in unseen if x != "refused"]; srt = sorted(ok)
print(f"RESULT: {best} picked on the seen half {mv[best]:+.1f}%, unseen {np.mean(ok):+.1f}% on {len(ok)} copies "
      f"(without its best 2: {np.mean(srt[:-2]) if len(srt) > 2 else float('nan'):+.1f}%; live exit w4 unseen {mu['w4']:+.1f}%)")
