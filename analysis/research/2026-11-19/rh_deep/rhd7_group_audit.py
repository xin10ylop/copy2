# The 5-wallet group (0xe3fdae6c...) before it goes live (Nov 19; the owner: "please audit final time before we add the
# group"). (1) The research copied each coin at the group's FIRST buy and filtered that buy; the bot (five leaders, a coin
# seen only once copied) copies the first member buy that PASSES the filters, so a coin whose first buy is filtered out can
# still be copied at a later member's buy. How often, and what those extra copies make. (2) Its activity lately.
#   python3 -I rhd7_group_audit.py DIR GROUPS_JSON > out/rhd7_group_audit.txt
import sys, os, json, collections, numpy as np, datetime as dt
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here); import rhd_lib as R
D, GJ = sys.argv[1], sys.argv[2]; DATA = R.Data(D)
M = {m.split(":")[1] for m in json.load(open(GJ))["0xe3fdae6c"]}
IX = (R.TP.index(3.5), R.HOLD.index(600), 0, R.STALL.index(240), R.ITS.index("early")); MINQ, MAXC = 0.02, 0.5
def value(tr, k):
    prems, vals = R.copy_one(tr, k); return np.mean([vals[l][IX] for l in range(len(vals))]) / R.RATE   # no price limit (3x bound: never hit here)
first_rule, bot_rule, extra = [], [], []
T_last = []
for c in DATA.L:
    if c not in DATA.TR or not any(x[3] in M and x[2] for x in DATA.TR[c]): continue
    tr = DATA.path(c); idx = [j for j, e in enumerate(tr) if e["buy"] and e["user"] in M and e["t"] <= DATA.t_end - 600]
    if not idx: continue
    T_last += [tr[j]["t"] for j in idx]
    ok = lambda j: tr[j]["q"] / 1e9 >= MINQ and ((tr[j - 1]["vq"] / 1e9 - R.V0) if j else 0.0) < MAXC and tr[j]["vq"] / 1e9 - R.V0 < 3.8
    j0 = idx[0]
    if ok(j0): v = value(tr, j0); first_rule.append((tr[j0]["t"], v)); bot_rule.append((tr[j0]["t"], v))
    else:
        jb = next((j for j in idx if ok(j)), None)
        if jb is not None: v = value(tr, jb); bot_rule.append((tr[jb]["t"], v)); extra.append((tr[jb]["t"], v, jb - j0, (tr[j0]["vt"] / tr[jb]["vt"]) ** 2))
def line(lab, rows):
    x = np.array([r[1] for r in rows]); k = max(1, round(0.02 * len(x)))
    return f"   {lab:44s} {len(x):4d} copies {x.sum():+.4f} ETH ({100 * x.mean() / R.STAKE if len(x) else 0:+6.1f}% a copy), w/o 2% {np.sort(x)[:-k].sum() if len(x) > k else 0:+.4f}, won {100 * np.mean(x > 0) if len(x) else 0:.0f}%"
print(f"data to {dt.datetime.fromtimestamp(DATA.t_end, dt.UTC):%m-%d %H:%M} UTC; landing +{R.LANDB} blocks; the group's setting (0.02+, under 0.5 ETH, tp 3.5, 600 s, stall 240, early sale)")
print(line("the research's rule (the group's first buy)", first_rule))
print(line("the bot's rule (the first member buy passing)", bot_rule))
print(line("   the extra copies alone", extra))
if extra: print(f"      their buy came {np.median([e[2] for e in extra]):.0f} trades after the group's first (median), at {np.median([e[3] for e in extra]):.2f}x the first buy's price")
T_last = np.array(sorted(T_last))
for h in (24, 48, 72, 168):
    print(f"   member buys of 0.01+ ETH in the last {h:3d} h: {int(np.sum(T_last >= DATA.t_end - h * 3600))}")
print(f"   the last member buy: {dt.datetime.fromtimestamp(T_last.max(), dt.UTC):%m-%d %H:%M} UTC")
for lab, a in (("last 7 days", 7), ("last 3 days", 3)):
    for nm, rows in (("research", first_rule), ("bot", bot_rule)):
        x = [r[1] for r in rows if r[0] >= DATA.t_end - a * 86400]
        print(f"   {lab}, {nm} rule: {len(x)} copies {sum(x):+.4f} ETH ({100 * np.mean(x) / R.STAKE if x else 0:+.1f}% a copy)")
