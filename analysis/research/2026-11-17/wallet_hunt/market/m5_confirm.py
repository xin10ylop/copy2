# The direct screen's confirmation (Nov 18): a FOUND wallet (m4_direct.py) on its own buys OUTSIDE the screen's 48 h
# (before Nov 15 01:07 and after Nov 17 01:07 UTC: never seen by the screen), scored exactly as the screen scored it:
# its first buy of a coin, 0.5+ SOL, on a coin priced in another token; our copy under wallet 4's live model (hunt_lib),
# the mean of the three landings (4 / 8 trades, the next slot), 0.0345 SOL a round trip. Paths: w5_copy's cpath (batched,
# true in-slot order), 900 s from its buy. Its SOL-priced coins are shown apart (the screen did not see that class).
#   RPC_URL=... [NS=150] python3 -I m5_confirm.py SP WALLET ... > ../out/m5_confirm.txt   (NS: a random sample of the buys, seed 7)
import sys, os, json, glob, numpy as np, datetime as d
from concurrent.futures import ThreadPoolExecutor
SP = sys.argv[1]; WALLETS = sys.argv[2:]; os.environ["HOLD"] = "900"; A, B = 1794704822, 1794877622
# NOT_W4=1 (Nov 18, the same-slot wallets): only coins wallet 4 never bought (its history and its research paths), every
# date (these wallets were picked on wallet 4's coins, so their other coins are all out of sample): the extra trades.
NOT_W4 = os.environ.get("NOT_W4") == "1"; W4C = set()
if NOT_W4:
    A = B = 0
    import gzip
    for f in glob.glob(f"{SP}/winners/hist/H9kuqGKN*.json"): W4C |= {e["m"] for e in json.load(open(f))["trades"]}
    for dd in ("allq", "cq", "since_stop", "newq"):
        try: W4C |= {v[0] for v in json.load(gzip.open(f"{SP}/{dd}/paths.json.gz")).values() if v}
        except Exception: pass
here = "/home/user/copy2/analysis/research/2026-11-17/winners"; src = open(f"{here}/w5_copy.py").read().split("EX = [")[0]
sys.argv = ["x", SP, "6ua7w2Gv"]; ns = {"__file__": f"{here}/w5_copy.py"}; exec(compile(src, "w5_copy.py", "exec"), ns)
cpath, rate_of, H, SOLQ = ns["cpath"], ns["rate_of"], ns["H"], ns["SOLQ"]; COST = 0.0345 - 0.0026
def S(v):
    v = np.array(v); n = len(v)
    if not n: return "  0"
    s = np.sort(v); k = max(1, round(0.02 * n)); bs = np.random.default_rng(7).choice(v, size=(10000, n)).mean(axis=1)
    return f"{n:3d} {v.sum():+6.2f} SOL ({100 * v.mean() / 0.5:+6.1f}% a copy) w/o 2% {s[:-k].sum() if n > 1 else 0:+6.2f} | won {100 * np.mean(v > 0):3.0f}% | P(mean>0) {100 * np.mean(bs > 0):5.1f}%"
for w in WALLETS:   # saved before w5_copy's exec rewrites sys.argv (the Nov 18 bug: it scored 6ua7w2Gv)
    h = json.load(open(glob.glob(f"{SP}/winners/hist/{w}*.json")[0])); first = {}
    for e in sorted(h["trades"], key=lambda e: e["t"]):
        if e["buy"]: first.setdefault(e["m"], e)
    buys = []
    for m, e in first.items():
        r = rate_of(e["quote"])
        if r is None or A <= e["t"] < B: continue
        if m in W4C: continue
        sol = e["q"] * (1 + e["bps"] / 1e4) * r / 1e9
        if sol >= 0.5: buys.append((m, e, r, sol))
    if os.environ.get("NS"): import random; random.Random(7).shuffle(buys); buys = buys[:int(os.environ["NS"])]   # a fixed random sample (seed 7)
    def one(x):
        m, e, r, sol = x
        try: tr = cpath(m, e["slot"], e["t"])
        except Exception: return None
        k = next((j for j, y in enumerate(tr) if y["user"] == w and y["buy"] and y["slot"] == e["slot"]), None)
        if k is None: return None
        v = sum(H.model(H.prep(tr, k, r, n))[0] for n in (4, 8, "slot+1")) / 3 - COST
        return dict(t=e["t"], sol=sol, other=e["quote"] not in SOLQ, v=v)
    with ThreadPoolExecutor(16) as ex: R = [x for x in ex.map(one, buys) if x]
    print(f"   (coins wallet 4 bought, left out: {len(W4C)})" if NOT_W4 else "", end="")
    print(f"\n== {w}: {h['n_sigs']} signatures since {d.datetime.fromtimestamp(h['t_first'] or 0, d.UTC):%m-%d %H:%M} UTC; first buys 0.5+ SOL outside the screen: {len(buys)}, modelled {len(R)}")
    for name, f in (("before the screen", lambda r: r["t"] < A), ("after the screen", lambda r: r["t"] >= B)):
        print(f"   {name:18s} other-token coins: {S([r['v'] for r in R if f(r) and r['other']])}")
        print(f"   {name:18s} SOL coins:         {S([r['v'] for r in R if f(r) and not r['other']])}")
    print(f"   ALL OUTSIDE, other-token coins:    {S([r['v'] for r in R if r['other']])}")
