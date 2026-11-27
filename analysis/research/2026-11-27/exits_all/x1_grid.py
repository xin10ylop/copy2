# The exit grid for one running unit (Nov 27; the owner: "review the exits ... after QQQ you're not engineering well every
# other wallet. Like neither sell pressure, buy pressure, following it sell, timer, you take profit, you're not optimizing
# really well without overfitting"). Until now every unit but wallet 4's got one deep check of 8 fixed exits and then the
# standard exit (tp 3x / 420 s / stall 240). Here each unit gets the full grid wallet 4's exit came from, on its own copies:
#   its first buys over the last 14 days at the unit's floor and coin kind (config/*.live.example.toml), the most recent CAP
#   (default 300); our copy replayed on each coin as w2_grid.py does it (../../2026-11-20/tape_screen/: we land in the slot
#   after its buy, the unit's stake, COST 0.0064 a round trip, refused over 1.5x its price = max_premium 0.5, a trigger
#   sells on the next trade, curve sales only, out at graduation), every exit setting of a coarser grid than w2's (fewer,
#   wider steps, so a lucky narrow setting has less room):
#     take profit (x its price) none 1.3 1.5 1.75 2 2.5 3 4 5 (9) | timer 60 90 120 180 240 300 420 600 s (8)
#     sell pressure off, N more sells than buys by others over W s: 3/30 5/30 5/60 8/60 10/120 (6)
#     stall (no new high for S s after the price passed our fill) off 60 120 180 240 (5)
#     its sale: never | always | early 30-290 s under 1.5x (wallet 4's) | 30-290 s any price | 0-60 s | 0-120 s (6)
#   = 12,960 settings. Saves SP/exits_all/<unit>.npz: per copy, its value for every setting as a share of the stake.
#   OUTSIDE=1 (the owner: "even for the by size, if it's sol or floats ... everything"): the copies the unit does NOT take
#   (its first buys of 0.1+ SOL outside its floor or coin kind), CAP of them at random, each standing for n/CAP of them
#   (`w`); saves <unit>_out.npz.
#   HELIUS_URL=... LK=SP/lk python3 -I x1_grid.py SP UNIT
import sys, os, json, numpy as np
SP, LAB = sys.argv[1], sys.argv[2]
# unit: wallet, coin kind, floor (min_sol), stake (stake_sol), live exit (tp, hold, sell pressure, stall, its sale)
STD = (3.0, 420, None, 240, ("never",))
UNITS = {"qqq": ("H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg", "token", 1.3, 1.0, (4.0, 600, (5, 60), 180, ("early", 30, 290, 1.5))),
         "eee": ("CgyPomTGt9BFqnjBdRS38BCBUZvtMJDf3aKQy8sMTVKX", "all", 0.5, 0.5, STD),
         "rrr": ("3XeFcZKSn8WzqoDAm5vvgbdfkU82rMmhJfp1q4LXtnX6", "token", 0.5, 0.5, STD),
         "ttt": ("6LwMLkCeEAqYp9Pv33ujrgd9uF987zPXdGKr9Z9sebh5", "token", 0.5, 0.5, STD),
         "yyy": ("6nNzEg86rbY4J1Z6euDn9iQoih8uaSj6ZVZHZVvFxjJf", "token", 0.25, 0.5, STD),
         "uuu": ("GqWfqfG6Mt6RL8BKUWiBkirqzycUc15bgZVtFERQzxJ8", "all", 0.5, 1.0, STD),
         "iii": ("Bing35WCqmhUwFBJ9xVNfMoNpECj8vdWEr5hD5wYyobc", "all", 0.5, 1.0, STD),
         "ooo": ("HtHkKxYN43BdJ8QJU1srMa3bqjpncLFcZgVCX8yU3AJS", "all", 0.5, 0.5, STD),
         "ppp": ("3SiQo8MJMzXaZcJexMivmk5CRgrNxDUh4bDbgb3wFAmW", "token", 0.1, 0.25, (2.0, 120, (5, 60), 0, ("never",))),
         "ddd": ("E2XwSeqewRHqBZQZAnSn6NyC9pF17E9KWcFQzquUwZMi", "all", 0.5, 0.5, STD),
         "hhh": ("2GJUPUrkxs6RZfJCgRncf1Xq9Xe6MbuDynVaoiiPKoJ4", "all", 0.5, 0.5, STD),
         # Nov 27 (the owner: "check deeply if we should add it back"): the stopped CqCAzte8 unit, its token-coin exit
         "www": ("CqCAzte8TwCDbCBrhjUpsfG6Au9pZPdrTXrVDidKHGAn", "all", 0.5, 0.5, STD)}
# a candidate (Nov 27, deep_box/): LAB cand_<wallet8> with CAND_W, all its coins of 0.5+ SOL at 0.5 SOL, the standard exit
if LAB.startswith("cand_"): UNITS[LAB] = (os.environ["CAND_W"], "all", 0.5, 0.5, STD)
W, KIND, MIN, STAKE_, LIVE_X = UNITS[LAB]
TS = "/home/user/copy2/analysis/research/2026-11-20/tape_screen"
os.environ["NOSTOP"] = "1"; os.environ["STAKE"] = str(STAKE_); os.environ.setdefault("COST", "0.0064")
sys.argv = [sys.argv[0], SP, W, "0", "0", "14"]
src = open(f"{TS}/w2_grid.py").read().split('firsts.sort(key=lambda c: c["t"]); h = len(firsts) // 2')[0]
OUT = bool(os.environ.get("OUTSIDE"))
for a, b in [('if es[0]["q"] * r / 1e9 >= 0.5 and', f'if es[0]["q"] * r / 1e9 >= {0.1 if OUT else MIN} - 1e-6 and'),
             ("STAKE = 1.0", "STAKE = float(os.environ['STAKE'])"),
             ("TP = [None] + [round(1.2 + 0.1 * i, 1) for i in range(39)]; HOLD = list(range(60, 601, 30))",
              "TP = [None, 1.3, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 5.0]; HOLD = [60, 90, 120, 180, 240, 300, 420, 600]"),
             ("SPS = [None] + [(n, w) for n in (3, 5, 8, 10, 15) for w in (30, 60, 120)]; STALL = [0, 60, 90, 120, 180, 240, 300]",
              "SPS = [None, (3, 30), (5, 30), (5, 60), (8, 60), (10, 120)]; STALL = [0, 60, 120, 180, 240]")]:
    assert a in src, a
    src = src.replace(a, b)
g = {"__file__": f"{TS}/w2_grid.py", "__name__": "__main__"}
exec(compile(src, "w2_grid", "exec"), g)
inside = lambda c: (KIND == "all" or c["tok"]) and c["sol"] >= MIN - 1e-6
CAP = int(os.environ.get("CAP", 300))
if OUT:
    pool = [c for c in g["firsts"] if not inside(c)]; import random; random.seed(11)
    firsts = random.sample(pool, CAP) if len(pool) > CAP else pool; WT = len(pool) / max(1, len(firsts))
else:
    firsts = [c for c in g["firsts"] if inside(c)]; firsts.sort(key=lambda c: c["t"]); firsts = firsts[-CAP:]; WT = 1.0
print(f"{LAB} {W[:8]}: {len(firsts)} first buys ({KIND} coins, {MIN}+ SOL), fetching paths", flush=True)
rows = g["fetch"](firsts)
TP, HOLD, SPS, STALL, ITS, SH = (g[k] for k in ("TP", "HOLD", "SPS", "STALL", "ITS", "SH"))
G = np.stack([r["g"] for r in rows]) / STAKE_
prem = np.array([r["prem"] for r in rows]); G[prem > 1.5] = -0.0004 / STAKE_   # max_premium 0.5: refused, the send's fee
live = np.ravel_multi_index((TP.index(LIVE_X[0]), HOLD.index(LIVE_X[1]), SPS.index(LIVE_X[2]), STALL.index(LIVE_X[3]), ITS.index(LIVE_X[4])), SH)
os.makedirs(f"{SP}/exits_all", exist_ok=True)
np.savez_compressed(f"{SP}/exits_all/{LAB}{'_out' if OUT else ''}.npz", w=WT, G=G.astype(np.float32), t=np.array([r["t"] for r in rows]), sol=np.array([r["sol"] for r in rows]),
                    tok=np.array([r["tok"] for r in rows]), prem=prem, live=live, SH=np.array(SH),
                    axes=json.dumps(dict(TP=TP, HOLD=HOLD, SPS=SPS, STALL=STALL, ITS=ITS)))
print(f"{LAB}{' outside' if OUT else ''}: {len(rows)} copies saved (each for {WT:.2f}); live exit {100 * G[:, live].mean():+.1f}% a copy; refused {int((prem > 1.5).sum())}", flush=True)
