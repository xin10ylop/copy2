# Does the bot buy what the backtest counts? (Nov 19 audit.) Every buy of our wallet on chain since it went live: which
# copied wallet bought just before (within 20 blocks), whether that was the leader's FIRST buy on the coin (the backtest
# copies only first buys), whether that first buy passes the backtest's filters for that wallet, and our result.
#   python3 -I rhd25_bot_vs_backtest_set.py DIR GROUPS_JSON > out/rhd25_bot_vs_backtest_set.txt
import sys, os, json, datetime as dt
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here); import rhd_lib as R
D, GJ = sys.argv[1], sys.argv[2]; DATA = R.Data(D); ME = "0x35bb5c55a531d14213380fd978a501f0e239a77e"
G = {m.split(":")[1] for m in json.load(open(GJ))["0xe3fdae6c"]}
W = {"w1": ({"0x9a3955a122ab8a649a8511df2dce169471fd0ec1"}, 0.1, 0.5), "w2": ({"0x5bc235acecff3dde394f4bfc696f7c35efd502f0"}, 0.05, 0),
     "w3": ({"0xc54d3914f91f984d61b63d491f38934c4e706b79"}, 0.03, 0), "grp": (G, 0.02, 0.5)}
n = 0; tot = {"first & passes": [0, 0.0], "other": [0, 0.0]}
for c in DATA.L:
    if c not in DATA.TR or not any(x[3] == ME for x in DATA.TR[c]): continue
    tr = DATA.path(c); b = next(i for i, e in enumerate(tr) if e["user"] == ME and e["buy"]); s = next((e for e in tr[b:] if e["user"] == ME and not e["buy"]), None)
    pnl = (s["q"] / 1e9 - tr[b]["q"] / 1e9) if s else None
    lead = [(i, nm) for i, e in enumerate(tr[:b]) if e["buy"] and tr[b]["slot"] - e["slot"] <= 20 for nm, (a, _, _) in W.items() if e["user"] in a]
    if not lead: print(f"{dt.datetime.fromtimestamp(tr[b]['t'], dt.UTC):%m-%d %H:%M:%S} {c[:10]} NO copied wallet's buy in the 20 blocks before ours"); continue
    i, nm = lead[-1]; a, mn, mx = W[nm]; k = next(j for j, e in enumerate(tr) if e["user"] in a and e["buy"])
    before = (tr[k - 1]["vq"] / 1e9 - R.V0) if k else 0.0
    passes = tr[k]["q"] / 1e9 >= mn and not (mx and before >= mx) and tr[k]["vq"] / 1e9 - R.V0 < 3.8
    key = "first & passes" if (i == k and passes) else "other"
    if pnl is not None: tot[key][0] += 1; tot[key][1] += pnl
    print(f"{dt.datetime.fromtimestamp(tr[b]['t'], dt.UTC):%m-%d %H:%M:%S} {c[:10]} {nm:4s} its buy {tr[i]['q']/1e9:.3f} ETH  {'its FIRST buy' if i == k else 'NOT its first buy (#%d)' % sum(1 for e in tr[:i+1] if e['user'] in a and e['buy'])}  "
          f"{'passes' if passes else 'FAILS the filters'}  lag {tr[b]['slot'] - tr[i]['slot']} blocks  ours {('%+.4f' % pnl) if pnl is not None else 'open'}")
print({k: (v[0], round(v[1], 5)) for k, v in tot.items()})
