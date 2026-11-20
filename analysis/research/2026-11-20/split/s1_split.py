# s1: the split, backtested (Nov 20, the owner: "check pnl if we run both strategies, if we run first only or second only,
# all vs each other"). Wallet 4's buys of 1.3+ SOL (the live min_sol), Oct 21 - Nov 13 (m15f's corpus, before the 4 days
# the dip was picked on: out of sample for leg 2; leg 1's exit was picked on data that includes this period).
#   leg 1 = the copy as live: lands the next slot, price limit 1.5x its price (max_premium 0.5), tp 4x its price, 600 s,
#           sell pressure 5/60 from 30 s, stall 180 s, its early sale (30-290 s under 1.5x) followed: hunt_lib.model
#   leg 2 = the dip as live: the first trade of a later slot within 60 s of its buy at or under 0.90x the price its buy
#           left; tp 1.5x our fill, 900 s from our fill, nothing else; only when we pay with a float (dip_float_only)
# Each leg 0.0345 SOL a round trip (the convention). Shown at 0.5 SOL a leg (the live split) and each leg alone at 1 SOL
# (the curve impact of the bigger buy is modelled; the 0.0345 is kept per round trip: its fees are per transaction).
# Not modelled: max_open (2 a leg live) and the daily stop.
#   python3 -I s1_split.py SP H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg > out/s1_split.txt
import sys, os, re, json, gzip, numpy as np
SP, W = sys.argv[1], sys.argv[2]
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-17/wallet_hunt"); import hunt_lib as H
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-18/churn"); import slot_order as SO
FLOATS = ("3NZ9JMVB", "pumpCmXq", "SPCXxcqX", "TTWofwAg", "DJTu7vi8", "98sMhvDw", "XsbEhLAt")
COST = 0.0345
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-17/wallet_hunt/market"); import m14_dip_after as D
rows = []
def add(tr, k, rate, sol, q8, cls):
    if sol < 0.5: return
    rows.append(dict(t=tr[k]["t"], tr=tr, k=k, rate=rate, cls=cls, sol=sol))
# source 3 (wallet 4): its research corpus, Oct 21 - Nov 16 (allq / cq / since_stop / newq: every trade for 31 minutes from
# its buy; the rate from routable.json's SOL value), true in-slot order; the 4 days above are then not added twice
if True:
    seen = set(); got = {}
    for d_ in ("allq", "cq", "since_stop", "newq"):
        try: P = json.load(gzip.open(f"{SP}/{d_}/paths.json.gz")); R_ = {f"{r['slot']}_{r['mint8']}": r for r in json.load(open(f"{SP}/{d_}/routable.json"))}
        except Exception: continue
        for kk, vv in P.items():
            if not vv or kk not in R_: continue
            m_, tr = vv
            if m_ in got and got[m_] >= len(tr): continue
            got[m_] = len(tr)
    INP = {}   # what the bot pays with: the planner's route input (scan_hops.out / scan.out); a coin quoted in a float is float-paid today (7 floats)
    for d_ in ("allq", "cq", "since_stop", "newq"):
        for f_ in ("scan_hops.out", "scan.out"):
            if not os.path.exists(f"{SP}/{d_}/{f_}"): continue
            for l in open(f"{SP}/{d_}/{f_}"):
                m = re.match(r"(\d+) (\S{8}) .*? quote (\S+) .*?ROUTABLE.*?input: (\w{8})", l)
                if m: INP.setdefault(f"{d_}/{m.group(1)}_{m.group(2)}", "float" if m.group(4) in FLOATS or m.group(3)[:8] in FLOATS else "wsol")
    for d_ in ("allq", "cq", "since_stop", "newq"):
        try: P = json.load(gzip.open(f"{SP}/{d_}/paths.json.gz")); R_ = {f"{r['slot']}_{r['mint8']}": r for r in json.load(open(f"{SP}/{d_}/routable.json"))}
        except Exception: continue
        for kk, vv in P.items():
            if not vv or kk not in R_: continue
            m_, tr = vv
            if got.get(m_) != len(tr) or not R_[kk].get("ok", True): continue   # routable only (the bot copies it)
            got[m_] = -1; tr = SO.reorder(tr)
            k = next((i for i, e in enumerate(tr) if e["user"] == W and e["buy"] and e["slot"] == R_[kk]["slot"]), None)
            if k is None or tr[k]["t"] in seen or tr[-1]["t"] - tr[k]["t"] < 600: continue
            rate = R_[kk]["sol"] * 1e9 / (tr[k]["q"] * (1 + tr[k]["bps"] / 1e4))
            q8 = str(R_[kk].get("quote", "?"))[:8]
            add(tr, k, rate, R_[kk]["sol"], q8, INP.get(f"{d_}/{kk}", "float" if q8 in FLOATS else "wsol"))

import datetime as dt, numpy as np, collections
CUT = 1794618422   # the 4 days start (Nov 14 01:07 UTC): nothing from there on
rows = [r for r in rows if r["t"] < CUT]; rows.sort(key=lambda r: r["t"])

def leg1(tr, k, rate, stake):
    v, why = H.model(H.prep(tr, k, rate, "slot+1", pmax=1.5), stake=stake)
    return v - (COST - 0.0026), why
def leg2(tr, k, rate, stake):
    pk = tr[k]["vq"] / tr[k]["vt"]
    j = next((i for i in range(k + 1, len(tr)) if tr[i]["t"] - tr[k]["t"] <= 60 and tr[i]["slot"] > tr[k]["slot"] and tr[i]["vq"] / tr[i]["vt"] <= 0.9 * pk), None)
    if j is None or j >= len(tr) - 1: return None
    p = H.prep(tr, k, rate, j - k, pmax=1e9)
    if not len(p["px"]): return None
    vt0, vq0, b0 = p["ent"]; net_in = stake * 1e9 / rate * 1e4 / (1e4 + b0); tok = vt0 - vt0 * vq0 / (vq0 + net_in)
    vq, vt, bb = p["vq"], p["vt"], p["bps"]; vq_r = vq + net_in; vt_r = vt * vq / vq_r
    val = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - bb / 1e4) * rate / 1e9 - stake - 0.0026; n = len(val)
    age = p["age"] - p["last"]; g = H.first(p["grad"])
    c = [n - 1] + ([g] if g is not None else [])
    i = H.first(age >= 900); c += [i] if i is not None else []
    i = H.first(val >= 0.5 * stake); c += [min(i + 1, n - 1)] if i is not None else []
    return val[min(c)] - (COST - 0.0026)

import datetime as dt, collections
out = []
for r in rows:
    if r["sol"] < 1.3: continue
    tr, k, rate = r["tr"], r["k"], r["rate"]
    a5, _ = leg1(tr, k, rate, 0.5); a1, _ = leg1(tr, k, rate, 1.0)
    b5 = b1 = b25 = None
    if r["cls"] == "float":
        b5 = leg2(tr, k, rate, 0.5); b1 = leg2(tr, k, rate, 1.0); b25 = leg2(tr, k, rate, 0.25)
    out.append(dict(t=r["t"], cls=r["cls"], a5=a5, a1=a1, b5=b5, b1=b1, b25=b25))
print(f"wallet 4: {len(out)} buys of 1.3+ SOL, {dt.datetime.fromtimestamp(out[0]['t'], dt.UTC):%m-%d} to {dt.datetime.fromtimestamp(out[-1]['t'], dt.UTC):%m-%d} UTC; "
      f"{sum(o['cls'] == 'float' for o in out)} float-paid; leg 2 fired on {sum(o['b5'] is not None for o in out)}; COST {COST} a round trip")
def wk(t): return dt.datetime.fromtimestamp(t - (t - 1792540800) % (7 * 86400), dt.UTC).strftime("%m-%d")
SC = {"leg 1 only, 1 SOL": lambda o: [o["a1"]],
      "leg 2 only, 1 SOL": lambda o: [o["b1"]] if o["b1"] is not None else [],
      "both, 0.5 + 0.5 (live)": lambda o: [o["a5"]] + ([o["b5"]] if o["b5"] is not None else []),
      "both, 1 + 1": lambda o: [o["a1"]] + ([o["b1"]] if o["b1"] is not None else []),
      "both, 1 + 0.5": lambda o: [o["a1"]] + ([o["b5"]] if o["b5"] is not None else []),
      "both, 1 + 0.25": lambda o: [o["a1"]] + ([o["b25"]] if o["b25"] is not None else []),
      "leg 2 only, 0.25 SOL": lambda o: [o["b25"]] if o["b25"] is not None else [],
      "leg 1 only, 0.5 SOL": lambda o: [o["a5"]],
      "leg 2 only, 0.5 SOL": lambda o: [o["b5"]] if o["b5"] is not None else []}
print(f"\n{'scenario':26} {'trades':>6} {'SOL':>8} {'w/o best 2%':>11} {'won':>5}  {'SOL a buy of its':>16}  by week (SOL)")
for name, f in SC.items():
    per = [(o["t"], sum(f(o))) for o in out if f(o)]; x = np.array([v for o in out for v in f(o)])
    k2 = max(1, round(0.02 * len(x))); W_ = collections.defaultdict(float)
    for t, v in per: W_[wk(t)] += v
    print(f"{name:26} {len(x):>6} {x.sum():>+8.2f} {np.sort(x)[:-k2].sum():>+11.2f} {int((x > 0).sum()):>5}  {x.sum() / len(out):>+16.4f}  " + "  ".join(f"{a} {b:+.2f}" for a, b in sorted(W_.items())))
# the same buys by what we pay with
for cls in ("float", "wsol"):
    oo = [o for o in out if o["cls"] == cls]
    a = sum(o["a5"] for o in oo); b = sum(o["b5"] for o in oo if o["b5"] is not None); nb = sum(o["b5"] is not None for o in oo)
    print(f"\npaid {cls}: {len(oo)} buys; leg 1 at 0.5: {a:+.2f} SOL ({100 * a / len(oo) / 0.5:+.1f}% a trade); leg 2 at 0.5: {nb} trades {b:+.2f} SOL"
          + (f" ({100 * b / nb / 0.5:+.1f}% a trade)" if nb else ""))
# where the legs overlap: on the buys where the dip fired, how leg 1 did
both = [o for o in out if o["b5"] is not None]
print(f"\non the {len(both)} buys where the dip fired: leg 1 at 0.5 {sum(o['a5'] for o in both):+.2f} SOL, leg 2 at 0.5 {sum(o['b5'] for o in both):+.2f} SOL; "
      f"correlation of the two legs {np.corrcoef([o['a5'] for o in both], [o['b5'] for o in both])[0, 1]:+.2f}")
# worst day of each scenario (risk)
for name, f in SC.items():
    D_ = collections.defaultdict(float)
    for o in out:
        for v in f(o): D_[dt.datetime.fromtimestamp(o["t"], dt.UTC).strftime("%m-%d")] += v
    d = np.array(list(D_.values()))
    print(f"{name:26} days {len(d)}, up {int((d > 0).sum())}, worst {d.min():+.2f}, best {d.max():+.2f}")
# cost check: at 1 SOL the 0.0155 fill bias of the 0.0345 doubled (0.050 a round trip)
for name, key in (("leg 1 only, 1 SOL", "a1"), ("leg 2 only, 1 SOL", "b1")):
    x = np.array([o[key] for o in out if o[key] is not None]) - 0.0155
    print(f"{name}, 0.050 a round trip: {x.sum():+.2f} SOL, w/o best 2% {np.sort(x)[:-max(1, round(0.02 * len(x)))].sum():+.2f}")
