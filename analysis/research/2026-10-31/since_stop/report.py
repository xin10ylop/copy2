# Validation of model.py against the bot's real trades (Oct 28 18:34 to Oct 29 11:52 UTC), then the copy since the stop.
#   python3 -I report.py SPD
import sys, json, gzip, datetime, statistics
sys.argv = [sys.argv[0], sys.argv[1]]
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__))); import model as M
SPD = M.SPD
P = {tuple([int(k.split("_")[0]), k.split("_")[1]]): v for k, v in json.load(gzip.open(f"{SPD}/paths.json.gz")).items()}
f = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d %H:%M")
LIVE1 = 1793274720 + 600
# the bot's real results: (stake, net % of stake, coin trades between its buy and ours), from the owner's history paste
# and the on-chain checks of Oct 28-29 (03-strategy-A-long-copy/deploy-frankfurt.md §6)
REAL = {"FUN1RZrj": (0.1, 92.7, 3), "E3hauBDZ": (0.1, None, 7), "EMJs7igZ": (0.1, 102.8, 6), "GUcG2eK2": (0.1, 81.8, 5),
        "6TrDECwR": (0.1, -33.4, 3), "JAckzYTT": (0.1, 107.4, 5), "E61exR62": (0.1, -36.6, 13), "Fawdfdv9": (0.5, None, 2),
        "2HuAFrTr": (0.5, None, 5), "96jEWfbD": (0.5, -27.8, 4), "DyNxDFcT": (0.5, 93.7, 2), "QkhZhyUK": (0.5, -2.7, 4),
        "6xQijdyc": (0.5, -7.7, 4), "7YLdWetK": (0.5, 95.6, 4), "FqDzSqvf": (0.5, 79.9, 2)}
print("== the model against the bot's real trades (Beirut time; net % of the stake)")
print(f"{'coin':9s} {'bought':11s} {'stake':>5s} {'real':>7s} {'model':>7s}  model exit")
diffs = []
for r in sorted((r for r in M.rows if r["t"] < LIVE1), key=lambda r: r["t"]):
    v = P.get((r["slot"], r["mint8"]))
    if not v: continue
    st, real, ahead = REAL.get(r["mint8"], (1.0, None, 4))
    o = M.model(r, v[0], v[1], st, ahead)
    mp = 100 * o["net"] / st if "net" in o else None
    if real is not None and mp is not None: diffs.append(mp - real)
    print(f"{r['mint8']:9s} {f(r['t']):11s} {st:5.1f} {('%+6.1f%%' % real) if real is not None else ' refus.' if r['mint8'] in REAL else '   1SOL':>7s} {('%+6.1f%%' % mp) if mp is not None else '   n/a':>7s}  {o.get('exit', o.get('note'))} in {o.get('px_in', 0):.2f}x out {o.get('px_out', 0):.2f}x")
print(f"   model minus real on {len(diffs)} closed trades: median {statistics.median(diffs):+.1f} points, mean {statistics.mean(diffs):+.1f}")
for n in (4, "slot+1", 2, 7):
    res = []
    for r in sorted((r for r in M.rows if r["t"] >= LIVE1), key=lambda r: r["t"]):
        v = P.get((r["slot"], r["mint8"]))
        if v: res.append((r, M.model(r, v[0], v[1], 1.0, n)))
    nets = sorted((o["net"] for _, o in res if "net" in o), reverse=True)
    days = {}
    for r, o in res:
        if "net" in o: days.setdefault(f(r["t"])[:5], []).append(o["net"])
    ex = {}
    for _, o in res: ex[o.get("exit", "?")] = ex.get(o.get("exit", "?"), 0) + 1
    print(f"\n== since the stop, 1 SOL a copy, landing {n}{' trades after its buy' if isinstance(n, int) else ''}: {len(nets)} copies, NET {sum(nets):+.2f} SOL (without the best 2: {sum(nets[2:]):+.2f}); exits {ex}")
    print("   by day (Beirut):", "  ".join(f"{d} {len(v)} {sum(v):+.2f}" for d, v in sorted(days.items())))
    if n == 4:
        for r, o in res:
            print(f"   {r['mint8']:9s} {f(r['t'])} {r['sol']:.2f} SOL {o.get('exit', o.get('note')):9s} in {o.get('px_in', 0):.2f}x out {o.get('px_out', 0):.2f}x peak {o.get('peak', 0):.2f}x held {o.get('held', 0):5.0f}s net {o.get('net', 0):+.3f}")
