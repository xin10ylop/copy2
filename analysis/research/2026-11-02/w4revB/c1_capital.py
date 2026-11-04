# Capital a rule ties up: every coin the rule passes (all creates of out/table.json, not only the sample), each held
# from its create for HOLD seconds (default the 1800 s cap, an upper bound; the sims' median hold is printed beside),
# no cap on open positions. Positions open at once (median, 90%, max, at each buy), and per quote the most open at once
# (= the float a 1 SOL stake needs in that token, in SOL).   python3 -I c1_capital.py [HOLD=1800]
import sys, os, bisect, collections, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blib
from f2_rule import RULES
from score import SEL, SIM, S as SAMPLE
from u1_universe import sym
HOLD = int(sys.argv[1]) if len(sys.argv) > 1 else 1800
T = blib.jl(blib.OUT + "/table.json")
def openat(ts):
    ts = sorted(ts); out = []
    for i, t in enumerate(ts): out.append(i - bisect.bisect_left(ts, t - HOLD) + 1)
    return out
for name in ("its 1.45+ SOL picks", "its picks (all sizes)", "R2 (picks and not)", "R4 (R2, dev buy 0.5-2)", "tree3 (prior 0, ata+cb+pump, dev > 0.47)"):
    f = SEL[name]
    for pp in ("P1", "P2"):
        L = [t for t in T if t["per"] == pp and f(t, None)]
        o = openat([t["cbt"] for t in L])
        q = collections.defaultdict(list)
        for t in L: q[t["quote"]].append(t["cbt"])
        mq = sorted(((max(openat(v)), k) for k, v in q.items()), reverse=True)[:5]
        print(f"{name:42s} {pp}: {len(L):6d} buys ({len(L) / 4:.0f} a day); open at once median {statistics.median(o):.0f}, 90% {sorted(o)[int(0.9 * len(o))]}, max {max(o)}"
              f"  -> at 1 SOL, up to {max(o)} SOL in flight; most open per quote: " + ", ".join(f"{sym(k)} {n}" for n, k in mq))
# the sims' hold times (float, ours, 1 SOL, its own fill), sampled coins
TB = {t["mint"]: t for t in T}
for name in ("its 1.45+ SOL picks", "R2 (picks and not)"):
    hs = [SIM[m][f"float|ours|1.0|F{SIM[m]['_h']}"]["t"] for m in SAMPLE if m in SIM and "err" not in SIM[m] and SEL[name](TB[m], None)
          and f"float|ours|1.0|F{SIM[m]['_h']}" in SIM[m]]
    if hs: print(f"hold in the sims ({name}, float, ours, 1 SOL): median {statistics.median(hs):.0f} s, share held the full 1800 s {sum(1 for h in hs if h >= 1800) / len(hs):.0%} (n {len(hs)})")
