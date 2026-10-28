# The float alternative for part B: hold the pay token (PUMP, CARDS, TTWO, ...) and buy its coins straight on the curve
# (no pool hop). The copy as grid.py prices it when the token is held at no risk (sim.py, ROUTES=E restricted to buys
# paid in it), and what holding it costs: its price in SOL from its own swaps against SOL (ledger.py's tokp, rows to
# Oct 28 14:54 UTC), by day, its change per period and its worst fall (peak to trough); the float a cap of 4 open needs,
# and what that float would have lost or made over each period. DATA=fresh3 adds P3.   python3 -I floats.py
import sys, os, json, datetime, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim
SPX = "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/more"
QS = {q["m"]: q for q in json.load(open(f"{SPX}/quotes.json"))}
TOK = {"PUMP": "pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn", "CARDS": "CARDSccUMFKoPRZxt5vt3ksUbxEFEcnZ3H2pd3dKxYjp",
       "TTWO": "TTWofwAge91oFhZs7kpQdyrVRkmevgM88xijGvQFbKo", "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
       "A7bd": "A7bdiYdS5GjqGFtxf17ppRHtDKPkkRqbKtR27dxvQXaS", "WBTC": sim.WBTC}
rows = sorted(sim.ROWS, key=lambda r: (r["s"], r["i"] or 0))
tokp = collections.defaultdict(list)
for r in rows:
    sol = r["d"] + r["tok"].get(sim.WSOL, [0])[0]
    tk = {m: v[0] / 10 ** v[1] for m, v in r["tok"].items() if m != sim.WSOL}
    fee = ((r["fee"] or 0) + (r["tip"] or 0)) if r["signer"] else 0
    if len(tk) == 1:
        (m, q), = tk.items(); s = (sol + fee) / 1e9
        if q and abs(s) > 0.05 and s * q < 0: tokp[m].append((r["bt"], -s / q))
def day(t): return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%m-%d")
def perx(t):
    d = datetime.datetime.fromtimestamp(t, datetime.timezone.utc)
    return "P1" if d.day <= 22 else "P2" if (d.day < 27 or (d.day == 27 and d.hour == 0 and d.minute < 20)) else "P3"
print("its price in SOL per token, from its own swaps (median of each day; n = swaps):")
for name, m in TOK.items():
    ser = tokp.get(m) or []
    if len(ser) < 5: print(f"   {name}: {len(ser)} swaps, no series"); continue
    byd = collections.defaultdict(list)
    for t, p in ser: byd[day(t)].append(p)
    med = {d: sorted(v)[len(v) // 2] for d, v in byd.items()}
    # worst fall: running peak to trough over the swap series smoothed by a 9-swap median
    sm = [sorted(p for _, p in ser[max(0, k - 4):k + 5])[len(ser[max(0, k - 4):k + 5]) // 2] for k in range(len(ser))]
    pk, dd, ddt = sm[0], 0.0, None
    for (t, _), p in zip(ser, sm):
        pk = max(pk, p)
        if p / pk - 1 < dd: dd, ddt = p / pk - 1, t
    ch = {}
    for P in ("P1", "P2", "P3"):
        v = [p for (t, _), p in zip(ser, sm) if perx(t) == P]
        if v: ch[P] = v[-1] / v[0] - 1
    print(f"   {name:5s} n {len(ser):4d}  " + "  ".join(f"{d} {p:.3g}" for d, p in sorted(med.items())))
    print(f"   {'':5s} change P1 {ch.get('P1', 0):+.1%}  P2 {ch.get('P2', 0):+.1%}  P3 {ch.get('P3', 0):+.1%}   worst fall {dd:.1%} (to {day(ddt) if ddt else '-'})"
          f"   a 4 SOL float: P1 {4 * ch.get('P1', 0):+.2f}  P2 {4 * ch.get('P2', 0):+.2f}  P3 {4 * ch.get('P3', 0):+.2f} SOL, worst {4 * dd:+.2f}")
A = sim.trips()
print("\nthe copy of its buys paid in the token, held at no risk (no hop, no price change), 1.5+ SOL:")
for name in ("PUMP", "CARDS", "TTWO", "USDC", "A7bd"):
    m0 = TOK[name]
    TR = [(m, x, p) for m, x, p in sim.trips(routes="E") if sim.pay_token(x) == m0]
    for cap in (4, 99):
        sc, got = sim.score(TR, cap=cap)
        # the most copies open at once in it (no cap)
        sim.show(f"{name} alone, at most {cap} open ({len(TR)} buys)", sc)
    sim.show(f"part A + {name}, at most 4 open", sim.score(A + TR, cap=4)[0])
    ev = sorted([(x["tr"][0]["bt"], 1) for m, x, p in TR] + [(x["tr"][0]["bt"] + 1790, -1) for m, x, p in TR])
    o = mx = 0
    for t, d in ev: o += d; mx = max(mx, o)
    print(f"   {'':46s} at most {mx} of its {name} buys open at once (each held up to 1790 s)")
sim.show("part A as built, at most 4 open", sim.score(A, cap=4)[0])
