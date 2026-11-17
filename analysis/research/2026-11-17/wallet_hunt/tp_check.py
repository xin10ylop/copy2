# The owner (Nov 17): is a deep test's result the live setup, and what does take profit at 2 / 3 / 4x (and more) give
# on the same copies? Re-runs the copies of deep.py (SP/hunt/deep_<w8>.json, their paths cached in LK/paths) with the
# live setup and only take profit changed; also the two signals off. Every copy, mean of the three landings, 0.5 SOL.
#   LK=<dir> RPC_URL=x python3 -I tp_check.py SP WALLET > out/tp_<w8>.txt
import sys, os, json, gzip
SP, W = sys.argv[1:3]
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-13/tab_exits"); import cmodel as M
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import hunt_lib as HL
G = json.load(open(f"{SP}/hunt/deep_{W[:8]}.json")); P = []
for g in G:
    tr = json.load(gzip.open(f"{M.PC}/{g['slot']}_{g['mint']}.json.gz"))
    j = next(x for x, e in enumerate(tr) if e["user"] == W and e["buy"] and e["slot"] == g["slot"])
    e = tr[j]; rate = g["sol"] * 1e9 / (e["q"] * (1 + e["bps"] / 1e4)); ps = []
    for n in (4, 8, "slot+1"):
        p = HL.prep(tr, j, rate, n); p["hopf"] = 0.997 ** (g["hops"] - 1); ps.append(p)
    P.append(ps)
def run(nm, **kw):
    nets = sorted((sum(HL.model(p, **kw)[0] for p in ps) / 3 for ps in P), reverse=True)
    print(f"  {nm:44s}: {len(nets)} copies, net {sum(nets):+6.2f} SOL, {100 * sum(nets) / len(nets) / 0.5:+5.1f}% a copy, w/o best 5 {sum(nets[5:]):+6.2f}")
print(f"{W}: the copies of deep.py, the live setup (its sale followed 30-290 s under 1.5x, sell_pressure [5, 60, 30], stall 180 s, 600 s) with take profit:")
for tp in (1.5, 2.0, 2.5, 3.0, 4.0, 6.0, 1e9): run(f"tp {tp if tp < 1e9 else 'none'}", tp=tp)
