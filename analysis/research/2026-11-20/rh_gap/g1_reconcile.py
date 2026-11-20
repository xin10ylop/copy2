# Robinhood: why live is so far from the backtest (Nov 20; the owner: "we are so far from these results, you are not
# finding what is wrong"). Since the Chicago box went live (Nov 19 14:17 UTC) to the data's end, trade by trade:
#   (1) every copy the backtest counts (each leader's first buy passing the bot's filters, the live exit, landing 2
#       blocks) and whether the bot took it;
#   (2) every buy of our wallet on chain (the live result: our sale's ETH against our buy's, gas left out);
#   (3) on the coins both have: live, the model at 2 blocks, and the model at the bot's ACTUAL landing.
# The gap then splits into: execution (live vs the model at our landing), the landing (model at our landing vs at 2
# blocks), and selection (copies the backtest counts that the bot never took, and the reverse). Results in % of the stake.
#   python3 -I g1_reconcile.py DIR GROUPS_JSON > out/g1_reconcile.txt
import sys, os, json, collections, numpy as np, datetime as dt
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-19/rh_deep"); os.environ.setdefault("STAKE", "0.01"); os.environ["LANDB"] = "2"
import rhd_lib as R
T, H, S, ST, I = R.TP, R.HOLD, R.SPS, R.STALL, R.ITS
H[:] = [45, 600, 900]
D, GJ = sys.argv[1], sys.argv[2]; DATA = R.Data(D); ME = "0x35bb5c55a531d14213380fd978a501f0e239a77e"
G = {m.split(":")[1] for m in json.load(open(GJ))["0xe3fdae6c"]}
T0 = dt.datetime(2026, 11, 19, 14, 17, tzinfo=dt.UTC).timestamp(); W2_OFF = dt.datetime(2026, 11, 19, 17, 0, tzinfo=dt.UTC).timestamp()
W = {"w1": ({"0x9a3955a122ab8a649a8511df2dce169471fd0ec1"}, 0.1, 0.5, 1.5, (T.index(4), H.index(600), 0, 0, 0), 600),
     "w2": ({"0x5bc235acecff3dde394f4bfc696f7c35efd502f0"}, 0.05, 0, 1.5, (T.index(3.5), H.index(900), S.index((10, 30)), 0, 0), 900),
     "w3": ({"0xc54d3914f91f984d61b63d491f38934c4e706b79"}, 0.03, 0, 3.0, (T.index(1e9), H.index(45), 0, 0, 0), 45),
     "grp": (G, 0.02, 0.5, 3.0, (T.index(3.5), H.index(900), 0, ST.index(240), I.index("early")), 900)}
def model(tr, k, lag, lim, ix):
    R.LANDB[:] = [lag]; prems, vals = R.copy_one(tr, k)
    if prems[0] > lim: return None   # refused by the price limit
    return 100 * vals[0][tuple(ix)] / R.RATE / R.STAKE
hhmm = lambda t: dt.datetime.fromtimestamp(t, dt.UTC).strftime("%m-%d %H:%M:%S")
rows = []   # one per coin: wallet, time, model@2, bot (lag, live, model@lag)
for c in DATA.L:
    if c not in DATA.TR: continue
    tr = None
    users = {x[3] for x in DATA.TR[c]}
    if ME not in users and not any(u in a for a, *_ in W.values() for u in users): continue
    tr = DATA.path(c)
    if not tr or tr[-1]["t"] < T0: continue
    # the backtest's copy: the first leader (in time) whose first buy passes its filters
    cand = []
    for nm, (a, mn, mx, lim, ix, hold) in W.items():
        k = next((j for j, e in enumerate(tr) if e["user"] in a and e["buy"]), None)
        if k is None or tr[k]["t"] < T0 or tr[k]["t"] > DATA.t_end - hold - 60: continue
        if nm == "w2" and tr[k]["t"] > W2_OFF: continue
        before = (tr[k - 1]["vq"] / 1e9 - R.V0) if k else 0.0
        if tr[k]["q"] / 1e9 < mn or (mx and before >= mx) or tr[k]["vq"] / 1e9 - R.V0 >= 3.8: continue
        cand.append((k, nm))
    b = next((j for j, e in enumerate(tr) if e["user"] == ME and e["buy"]), None)
    if b is not None and tr[b]["t"] < T0: continue
    m = None
    if cand:
        k, nm = min(cand); a, mn, mx, lim, ix, hold = W[nm]; m = (nm, k, model(tr, k, 2, lim, ix))
    bot = None
    if b is not None:
        s = [e for e in tr[b:] if e["user"] == ME and not e["buy"]]
        live = 100 * (sum(e["q"] for e in s) / 1e9 - tr[b]["q"] / 1e9) / (tr[b]["q"] / 1e9) if s else None
        lead = [(j, nm) for j, e in enumerate(tr[:b]) if e["buy"] and tr[b]["slot"] - e["slot"] <= 40 for nm, w in W.items() if e["user"] in w[0]]
        if lead:
            j, nm = lead[-1]; k = next(i for i, e in enumerate(tr) if e["user"] in W[nm][0] and e["buy"]); lag = tr[b]["slot"] - tr[k]["slot"]
            ml = model(tr, k, max(lag, 1), 1e9, W[nm][4])   # the model at OUR landing (no limit: the bot did buy)
            bot = (nm, lag, live, ml, tr[b]["t"])
        else: bot = ("?", None, live, None, tr[b]["t"])
    if m or bot: rows.append((c, m, bot, tr))
print(f"data to {hhmm(DATA.t_end)} UTC; window from {hhmm(T0)}; STAKE {R.STAKE}; results in % of the stake")
print(f"\n{'time':14s} {'coin':10s} {'wallet':6s} {'model@2':>8s} | {'bot':4s} {'lag':>4s} {'live':>8s} {'model@ours':>10s}")
agg = collections.defaultdict(lambda: collections.defaultdict(list))
for c, m, bot, tr in sorted(rows, key=lambda r: (r[2][4] if r[2] else r[3][r[1][1]]["t"])):
    t = bot[4] if bot else tr[m[1]]["t"]
    f = lambda x: "refused" if x is None else f"{x:+.1f}%"
    print(f"{hhmm(t)[3:]:14s} {c[:10]:10s} {(m[0] if m else '-'):6s} {(f(m[2]) if m else '-'):>8s} | {(bot[0] if bot else '-'):4s} "
          f"{(str(bot[1]) if bot and bot[1] is not None else '-'):>4s} {(f(bot[2]) if bot and bot[2] is not None else '-'):>8s} {(f(bot[3]) if bot and bot[3] is not None else '-'):>10s}")
    nm = (bot[0] if bot else m[0])
    if m and bot and bot[2] is not None:
        agg[nm]["both_live"].append(bot[2]); agg[nm]["both_m2"].append(m[2] if m[2] is not None else 0.0)
        if bot[3] is not None: agg[nm]["both_mours"].append(bot[3])
        agg[nm]["lag"].append(bot[1])
    elif m and not bot: agg[m[0]]["model_only"].append(m[2] if m[2] is not None else 0.0)
    elif bot and bot[2] is not None: agg[nm]["bot_only"].append(bot[2])
print(f"\n{'wallet':6s} {'both: n':>8s} {'live':>8s} {'model@ours':>10s} {'model@2':>8s} {'lag med':>8s} | {'model only: n':>13s} {'mean':>7s} | {'bot only: n':>11s} {'mean':>7s}")
for nm in W:
    a = agg[nm]; mean = lambda x: f"{np.mean(x):+.1f}%" if x else "-"
    print(f"{nm:6s} {len(a['both_live']):>8d} {mean(a['both_live']):>8s} {mean(a['both_mours']):>10s} {mean(a['both_m2']):>8s} {(str(int(np.median(a['lag']))) if a['lag'] else '-'):>8s} | "
          f"{len(a['model_only']):>13d} {mean(a['model_only']):>7s} | {len(a['bot_only']):>11d} {mean(a['bot_only']):>7s}")
