# The forward check of the ladder flip (PREREG_ladder_flip.md), the way a live bot would see it: EVERY pump launch since
# T0 (default Nov 18 00:00 UTC, after all the data the rule was tested on), wallet-independent. (1) the creates: pump's
# mint authority's signatures back to T0, each create transaction -> the coin, its slot, SOL-priced or not; (2) each SOL
# coin's first curve transactions (its bonding curve's signatures, oldest page) in the create slot -> the buys; a LADDER =
# buys of 2+ ladder sizes (1.10 / 1.54 / 2.18 SOL within 0.005) from different wallets in the create slot; (3) each ladder
# coin's trades for HOLD s (w5_copy's cpath) and the frozen flip: buy 0.5 SOL at the first trade after the create slot + 1,
# sell at +20% over our entry or 30 s later; 0.0345 SOL a round trip. RPC from RPC_URL, never printed.
#   RPC_URL=... LK=SP/fwd/lk HOLD=120 python3 -I f1_scan.py SP [T0] > out/f1_scan.txt
import sys, os, json, time, datetime as d, numpy as np
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-13/tab_exits"); import lib, cmodel as M
from solders.pubkey import Pubkey as P
SP = sys.argv[1]; T0 = int(sys.argv[2]) if len(sys.argv) > 2 else 1794960000; NOW = time.time(); os.environ.setdefault("HOLD", "120")
SIZES = (1.10, 1.54, 2.18); MINT_AUTH = "TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM"
curve = lambda m: str(P.find_program_address([b"bonding-curve", bytes(P.from_string(m))], P.from_string(lib.PUMP))[0])
# (1) the creates since T0
S, before = [], None
while True:
    pg = lib.sigs(MINT_AUTH, before=before, limit=1000, cache=False)
    if not pg: break
    S += [x for x in pg if x.get("err") is None and (x.get("blockTime") or 0) >= T0]; before = pg[-1]["signature"]
    if (pg[-1].get("blockTime") or 0) < T0 or len(pg) < 1000: break
S = [x for x in S if NOW - x["blockTime"] > 180]   # 3+ minutes old: its first trades are in
print(f"{len(S)} creates since {d.datetime.fromtimestamp(T0, d.UTC):%b %d %H:%M} UTC", flush=True)
def create(x):
    try: t = lib.tx(x["signature"])
    except Exception: return None
    if not t: return None
    cr = next((e for k, e in lib.events(t) if k == "create"), None)
    if not cr: return None
    q = cr.get("quote_mint"); return dict(m=cr["mint"], slot=x["slot"], t=x["blockTime"], sol=q in (None, lib.WSOL, lib.ZERO))
with ThreadPoolExecutor(24) as ex: C = [c for c in ex.map(create, S) if c and c["sol"]]
print(f"{len(C)} SOL-priced coins", flush=True)
# (2) the ladder in the create slot
def ladder(c):
    try: pg = lib.sigs(curve(c["m"]), limit=1000, cache=False)
    except Exception: return None
    s0 = [x for x in pg if x.get("err") is None and x["slot"] == c["slot"]]
    buys = []
    for x in s0:
        t = lib.tx(x["signature"])
        if t: buys += [e for k, e in lib.events(t) if k == "trade" and e.get("mint") == c["m"] and e.get("is_buy")]
    lad = {e["user"] for e in buys if any(abs(e["sol"] / 1e9 - s) <= 0.005 for s in SIZES)}
    return dict(c, lad=sorted(lad), n_slot0=len(s0)) if len(lad) >= 2 else None
with ThreadPoolExecutor(24) as ex: L = [x for x in ex.map(ladder, C) if x]
print(f"{len(L)} ladder coins ({len(L) / max(1, len(C)):.1%} of the SOL-priced launches)", flush=True)
json.dump(L, open(f"{SP}/fwd_ladder.json", "w"))
# (3) the frozen flip on each
here = "/home/user/copy2/analysis/research/2026-11-17/winners"; src = open(f"{here}/w5_copy.py").read().split("EX = [")[0]
sys.argv = ["x", SP, "6ua7w2Gv"]; ns = {"__file__": f"{here}/w5_copy.py"}; exec(compile(src, "w5_copy.py", "exec"), ns); cpath = ns["cpath"]
def flip(c):
    try: tr = cpath(c["m"], c["slot"], c["t"])
    except Exception: return None
    i = next((j for j, e in enumerate(tr) if e["slot"] > c["slot"] + 1), None)
    if i is None: return None
    a = tr[i]; fee = a["bps"] / 1e4; tok = 0.5e9 * (1 - fee) * a["vt"] / (a["vq"] + 0.5e9); p0 = a["vq"] / a["vt"]; j_out = len(tr) - 1
    for j in range(i + 1, len(tr)):
        e = tr[j]
        if e.get("real") == 0 or e["vq"] / e["vt"] >= 1.2 * p0 or e["t"] - a["t"] >= 30: j_out = j; break
    b = tr[j_out]; vq = b["vq"] + 0.5e9 * (1 - fee); vt = b["vt"] * b["vq"] / vq
    out = (vq - vq * vt / (vt + tok)) * (1 - b["bps"] / 1e4) / 1e9 - 0.5 - 0.0345
    return dict(m=c["m"], t=c["t"], net=out, held=b["t"] - a["t"], why="tp" if b["vq"] / b["vt"] >= 1.2 * p0 else ("grad" if b.get("real") == 0 else "30 s"))
with ThreadPoolExecutor(8) as ex: R = sorted([x for x in ex.map(flip, L) if x], key=lambda x: x["t"])
json.dump(R, open(f"{SP}/fwd_flip.json", "w"))
v = np.array([r["net"] for r in R]); h = len(v) // 2
if len(v):
    k = max(1, round(0.02 * len(v))); bs = np.random.default_rng(7).choice(v, size=(10000, len(v))).mean(axis=1)
    print(f"THE FROZEN FLIP, forward: {len(v)} ladder coins, {v.sum():+.2f} SOL ({100 * v.mean() / 0.5:+.1f}% a copy); halves {100 * v[:h].mean() / 0.5:+.1f}% / {100 * v[h:].mean() / 0.5:+.1f}%;"
          f" without the best 2% {np.sort(v)[:-k].sum():+.2f}; P(mean > 0) {np.mean(bs > 0):.1%}; won {np.mean(v > 0):.0%}; exits: tp {sum(r['why'] == 'tp' for r in R)}, 30 s {sum(r['why'] == '30 s' for r in R)}, grad {sum(r['why'] == 'grad' for r in R)}")
