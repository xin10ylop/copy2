# Did the engineered copy behave as it should lately? (Nov 18; the owner: "no paper, last 3 days, behaved as it
# should? if yes, build"). rh6's copies (our buy 2/3/5 blocks after its buy) under ONE fixed setting
# "size,coin,limit,tp,hold,sp,stall,its" (coin = any or <0.5 ETH in the curve), by UTC day, the last 3 days apart,
# and the wallet's own behaviour then (buys a day, size, hold) against before.
#   STAKE=0.05 LANDB=2,3,5 python3 -I rh11_days.py DIR WALLET SPEC
import sys, os, numpy as np, datetime as dt
here = os.path.dirname(os.path.abspath(__file__)); D, WAL, SPEC = sys.argv[1], sys.argv[2].lower(), sys.argv[3]
src = open(os.path.join(here, "rh6_engineer.py")).read().split("rows.sort(key=lambda r: r[\"t\"])")[0]
sys.argv = ["x", D, WAL]; exec(src)
z = SPEC.split(","); sz, coin, pm = float(z[0]), z[1], (1e9 if z[2] == "none" else float(z[2]))
ix = (TP.index(1e9 if z[3] == "none" else float(z[3])), HOLD.index(int(z[4])), SPS.index(None if z[5] == "off" else tuple(int(v) for v in z[5].split("/"))), STALL.index(0 if z[6] == "off" else int(z[6])), ITS.index(z[7]))
sel = [r for r in rows if r["sz"] >= sz and (coin == "any" or r["prog"] < 0.5)]
v = np.array([np.mean([r["vl"][l][ix] if r["prem"][l] <= pm else -0.0004 for l in range(3)]) / RATE for r in sel]); t = np.array([r["t"] for r in sel])
end = max(r["t"] for r in rows); cut = end - 3 * 86400
print(f"{WAL}  setting {SPEC}, our {STAKE} ETH a copy, landing blocks +{os.environ.get('LANDB', '?')}")
days = sorted({dt.datetime.fromtimestamp(x, dt.UTC).strftime("%m-%d") for x in t})
for d_ in days[-10:]:
    f = np.array([dt.datetime.fromtimestamp(x, dt.UTC).strftime("%m-%d") == d_ for x in t]); x = v[f]
    print(f"   {d_}: {f.sum():3d} copies {x.sum():+.4f} ETH ({100 * x.mean() / STAKE:+6.1f}% a copy), won {100 * np.mean(x > 0):3.0f}%")
for lab, f in (("before the last 3 days", t < cut), ("THE LAST 3 DAYS", t >= cut)):
    x = v[f]; k = max(1, round(0.02 * len(x))) if len(x) else 1
    if len(x): print(f"   {lab}: {len(x)} copies ({len(x) / ((cut - t.min()) / 86400 if lab.startswith('before') else 3):.1f} a day), {x.sum():+.4f} ETH ({100 * x.mean() / STAKE:+.1f}% a copy), w/o 2% {np.sort(x)[:-k].sum():+.4f}, won {100 * np.mean(x > 0):.0f}%")
    else: print(f"   {lab}: no copies")
