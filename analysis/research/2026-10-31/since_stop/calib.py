# How far the model misses the bot's real trades, by exit type (the 12 closed trades of report.py with their real number
# of trades between, plus the three 1 SOL timer trades rebuilt from the chain, landing 4 assumed), and the copy since a
# date corrected by that median miss per exit type. 1 SOL, max_open 2, tp 2.0, 1790 s, hold through its sale.
#   python3 -I calib.py SPD "YYYY-MM-DD HH:MM" (FROM, Beirut time)
import sys, os, io, contextlib, datetime, statistics
SPD = sys.argv[1]; FROM = datetime.datetime.strptime(sys.argv[2], "%Y-%m-%d %H:%M").replace(tzinfo=datetime.timezone.utc).timestamp() - 7200
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.argv = [sys.argv[0], SPD, "4"]
with contextlib.redirect_stdout(io.StringIO()): import copy_grid as G
# real results: coin -> (stake, net % of the stake, coin trades between its buy and ours); deploy-frankfurt.md §6
REAL = {"FUN1RZrj": (0.1, 92.7, 3), "EMJs7igZ": (0.1, 102.8, 6), "GUcG2eK2": (0.1, 81.8, 5), "6TrDECwR": (0.1, -33.4, 3),
        "JAckzYTT": (0.1, 107.4, 5), "E61exR62": (0.1, -36.6, 13), "96jEWfbD": (0.5, -27.8, 4), "DyNxDFcT": (0.5, 93.7, 2),
        "QkhZhyUK": (0.5, -2.7, 4), "6xQijdyc": (0.5, -7.7, 4), "7YLdWetK": (0.5, 95.6, 4), "FqDzSqvf": (0.5, 79.9, 2),
        "iNE6pSzD": (1.0, 1.42, 4), "HotHTmeY": (1.0, -4.24, 4), "3NWyukFy": (1.0, -1.90, 4)}
miss = {}
print("== the model against the real trades (points of the stake)")
for r in G.M.rows:
    if r["mint8"] not in REAL or f"{r['slot']}_{r['mint8']}" not in G.P: continue
    st, real, ahead = REAL[r["mint8"]]; m, tr = G.P[f"{r['slot']}_{r['mint8']}"]
    o = G.M.model(r, m, tr, st, ahead, sl=0.8)
    if o["exit"] == "refused": print(f"   {r['mint8']} real {real:+.1f}%, model refused at {o['px_in']:.2f}x (skipped)"); continue
    d = real - 100 * o["net"] / st; miss.setdefault(o["exit"], []).append(d)
    print(f"   {r['mint8']} {o['exit']:5s} real {real:+6.1f}%  model {100 * o['net'] / st:+6.1f}%  miss {d:+5.1f}")
bias = {k: statistics.median(v) / 100 for k, v in miss.items()}
print("   median miss by exit:", {k: f"{100 * v:+.1f} points on {len(miss[k])}" for k, v in bias.items()})
rs = [r for r in G.trips if r["t"] >= FROM]
for n in (2, 4, 7):
    for name, sl in (("0.8 stop", 0.8), ("no stop ", None)):
        res = G.sim(rs, n=n, cap=2, tp=2.0, sl=sl, hold=1790)
        raw = sorted((o["net"] for _, o in res), reverse=True)
        cor = sorted((o["net"] + (bias.get(o["exit"], 0) if o["exit"] != "refused" else 0) for _, o in res), reverse=True)
        print(f"landing {n} {name}: raw {sum(raw):+6.2f} ({sum(raw[2:]):+6.2f})   corrected {sum(cor):+6.2f} ({sum(cor[2:]):+6.2f})  on {len(raw)}")
