# SolHouse VIP, estimated from the public channel: each public gem alert gives the VIP call's market cap, so the VIP price =
# the public post's price x (VIP mc / public mc). On the chain (tg_test.py's curve paths: 10 min before the public post to
# an hour after), the VIP call is placed at the last trade at or below that price before the public post (the coin was at
# the VIP's market cap then). The lead = public post - VIP call. Our copy at the VIP call (+1 s), the same exits as
# tg_channel.py. Only calls whose VIP point lies inside the 10 min the paths cover (a longer lead is counted).
# The catch, printed with the result: the public channel posts a VIP call only once it has doubled, so every call here is a
# VIP winner; the VIP's losers are not in this data. The break-even share of winners is computed from the losers of the
# other channels' calls (tg_channel.py's post + exit on every call that did not reach the exit's target).
#   python3 -I tg_vip.py TGDIR > out/tg_vip.txt
import sys, os, json, gzip, glob, statistics as st
TG = sys.argv[1]; D = f"{TG}/solhousesignal"; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util
spec = importlib.util.spec_from_file_location("tc", os.path.join(os.path.dirname(os.path.abspath(__file__)), "tg_channel.py"))
src = open(spec.origin).read().split("for cj in sorted(glob.glob")[0]   # tg_channel's load() and sim() only
sys.argv = [sys.argv[0], TG]; ns = {}; exec(compile(src, spec.origin, "exec"), ns); load, sim = ns["load"], ns["sim"]
vip = json.load(open(f"{D}/vip.json")); C = load(D); pr = lambda r: r[1] / r[2]
lead, far, rows = [], 0, []
for t, m, P in C:
    if m not in vip: continue
    pre = [r for r in P if r[0] <= t]; p0 = pr(pre[-1]); pv = p0 * vip[m]
    at = [r for r in pre if pr(r) <= pv * 1.02]
    if not at: far += 1; continue
    tv = at[-1][0]; lead.append(t - tv); rows.append((tv, m, P))
print(f"{len(C)} public calls with a curve path; VIP point found in the 10 min before the post for {len(rows)}, earlier than that for {far}")
if lead: print(f"lead of the VIP over the public post: median {st.median(lead):.0f} s, quartiles {[round(x) for x in st.quantiles(lead, n=4)]}")
print("\nexit   | at the public post (all calls)      | at the VIP call (these winners only)")
for ex in ["tp1.5", "tp2", "tp3", "t10", "t30", "t60"]:
    a = [x for x in (sim(t, P, "post", ex) for t, _, P in C) if x is not None]
    b = [x for x in (sim(tv, P, "post", ex) for tv, _, P in rows) if x is not None]
    fmt = lambda v: f"{len(v):3d} {sum(v):+6.2f} ({sum(v) / len(v) / 0.5:+6.1%}), won {sum(x > 0 for x in v) / len(v):3.0%}" if v else "0"
    print(f"{ex:6s} | {fmt(a):34s} | {fmt(b)}")
# break-even: a VIP winner at tp2 earns w; a VIP loser is taken as the average losing copy of every other channel's calls
others = [d for d in glob.glob(f"{TG}/**/calls.json", recursive=True) if "solhouse" not in d and "klevercalls" not in d]
losers = []
for cj in others:
    for t, _, P in load(os.path.dirname(cj)):
        x = sim(t, P, "post", "tp2")
        if x is not None and x <= 0: losers.append(x)
w = [x for x in (sim(tv, P, "post", "tp2") for tv, _, P in rows) if x is not None]
if w and losers:
    W, L = st.mean(w), -st.mean(losers)
    print(f"\nbreak-even at tp2: a VIP winner here makes {W:+.3f} SOL a copy; the average losing copy of the other channels' calls {-L:+.3f}; "
          f"so the VIP pays only if more than {L / (W + L):.0%} of ALL its calls are such winners ({len(losers)} losing copies averaged)")
