# Is wallet 3's 45 s sale overfitted? (Nov 19; the owner: "check that wallet 3's 45 seconds rule is not overfitted".)
# rhd19 chose 45 s, time only, on ALL the data. Here, week by week: (a) the hold picked BLIND on the weeks before (time
# only, 3-900 s; and the old exits tp 3 / 300 s / sp 8-60 / stall 240 among the choices) scored on the unseen week;
# (b) 45 s, 30 s, 60 s, 90 s and the old exits, each week. Wallet 3's buys of 0.03+ ETH, limit 3x, exact model, LANDB.
#   python3 -I rhd28_w3_45s_blind.py DIR GROUPS_JSON > out/rhd28_w3_45s_blind.txt
import sys, os, json, numpy as np, datetime as dt
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here); import rhd_lib as R
T, H, S, ST, I = R.TP, R.HOLD, R.SPS, R.STALL, R.ITS
H[:] = [3, 5, 8, 10, 15, 20, 25, 30, 45, 60, 90, 120, 180, 300, 600, 900]
D = sys.argv[1]; DATA = R.Data(D); A = {"0xc54d3914f91f984d61b63d491f38934c4e706b79"}
OLD = (T.index(3), H.index(300), S.index((8, 60)), ST.index(240), 0)
rows = []
for c in DATA.L:
    if c not in DATA.TR or not any(x[3] in A and x[2] for x in DATA.TR[c]): continue
    tr = DATA.path(c); k = next((j for j, e in enumerate(tr) if e["user"] in A and e["buy"]), None)
    if k is None or tr[k]["q"] / 1e9 < 0.03 or tr[k]["t"] > DATA.t_end - 960: continue
    if tr[k]["vq"] / 1e9 - R.V0 >= 3.8: continue
    prems, vals = R.copy_one(tr, k)
    V = np.mean([vals[l] if prems[l] <= 3.0 else np.full(vals[l].shape, -0.0004) for l in range(len(vals))], axis=0) / R.RATE
    rows.append((tr[k]["t"], np.array([V[T.index(1e9), j, 0, 0, 0] for j in range(len(H))] + [V[OLD]])))
rows.sort(key=lambda r: r[0]); t = np.array([r[0] for r in rows]); X = np.array([r[1] for r in rows])
labels = [f"{h} s" for h in H] + ["old exits"]; pc = lambda x: 100 * x.mean() / R.STAKE if len(x) else float("nan")
wk0 = dt.datetime(2026, 10, 15, tzinfo=dt.UTC).timestamp(); weeks = []
s = wk0
while s < t.max(): weeks.append((s, s + 7 * 86400)); s += 7 * 86400
print(f"wallet 3: {len(rows)} copies {dt.datetime.fromtimestamp(t.min(), dt.UTC):%m-%d} to {dt.datetime.fromtimestamp(t.max(), dt.UTC):%m-%d}; landing {R.LANDB}; a copy, by week")
print(f"{'week':12s} {'copies':>6s} | {'45 s':>7s} {'30 s':>7s} {'60 s':>7s} {'90 s':>7s} {'old':>7s} | picked blind on the weeks before -> its result")
tot = {"45 s": [], "old exits": [], "blind": []}
for a, b in weeks:
    m = (t >= a) & (t < b); past = t < a
    if not m.any(): continue
    cells = " ".join(f"{pc(X[m, labels.index(l)]):+6.1f}%" for l in ("45 s", "30 s", "60 s", "90 s", "old exits"))
    if past.sum() >= 40:
        j = int(np.argmax(X[past].sum(axis=0))); bl = X[m, j]; tot["blind"] += list(bl); pick = f"{labels[j]:9s} -> {pc(bl):+6.1f}%"
    else: pick = "(too little before)"
    if past.sum() >= 40: tot["45 s"] += list(X[m, labels.index("45 s")]); tot["old exits"] += list(X[m, labels.index("old exits")])
    print(f"{dt.datetime.fromtimestamp(a, dt.UTC):%m-%d} {m.sum():6d}       | {cells} | {pick}")
print(f"\nover the weeks that had a blind pick: blind pick {pc(np.array(tot['blind'])):+.1f}% a copy ({len(tot['blind'])}); 45 s {pc(np.array(tot['45 s'])):+.1f}%; old exits {pc(np.array(tot['old exits'])):+.1f}%")
print("\nthe whole curve (all copies), time only:  " + "  ".join(f"{l} {pc(X[:, i]):+.1f}%" for i, l in enumerate(labels)))
