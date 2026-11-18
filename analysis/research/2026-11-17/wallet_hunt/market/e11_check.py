# The double check of a settings change (Nov 18, the owner: "double check that all changes are better, for both
# wallets"): each change alone and all together against the running setting, on the same copies (e8's loader), by
# week, by half without the best 2%, at each landing (4 trades, 8 trades, the next slot) separately, and a paired
# bootstrap of the difference (10,000 resamples of the copies, seed 7).
#   PAY=all LANDINGS=1 python3 -I e11_check.py SP WALLET "name=size,prem,tp,hold,sp,stall,its[,float]" ...  (first = the running one)
import sys, os, numpy as np, datetime as dt
here = os.path.dirname(os.path.abspath(__file__)); src = open(os.path.join(here, "e8_engineer.py")).read()
os.environ.setdefault("LANDINGS", "1"); SETS = sys.argv[3:]; sys.argv = sys.argv[:3]
exec(src.split("rows.sort(key=lambda r: r[\"t\"]);")[0].split("import collections;")[0])
if PAY != "all": rows = [r for r in rows if r["cls"] == PAY]   # e8 applies this after the part exec'd above
rows.sort(key=lambda r: r["t"]); T = np.array([r["t"] for r in rows]); SOLB = np.array([r["sol"] for r in rows]); CL = np.array([r["cls"] for r in rows])
VL = np.array([r["vl"] for r in rows]); tmid = np.median(T); A = T < tmid
def ix(z):
    return (TP.index(1e9 if z[2] == "none" else float(z[2])), HOLD.index(int(z[3])), SPS.index(None if z[4] == "off" else tuple(int(x) for x in z[4].split("/"))),
            STALL.index(0 if z[5] == "off" else int(z[5])), ITS.index(z[6]))
def per_copy(spec):
    """Each copy's SOL under the setting (0 when the setting does not buy it), per landing: (n_copies, 3). The price
    limit is applied per landing (the bot refuses a fill above it), a refused buy costs 0.0004."""
    z = spec.split(","); e = ix(z); out = np.zeros((len(rows), 3))
    for i, r in enumerate(rows):
        if r["sol"] < float(z[0]) or (len(z) > 7 and z[7] == "float" and r["cls"] != "float"): continue
        pm = 1e9 if z[1] == "none" else float(z[1])
        for l in range(3): out[i, l] = r["vl"][l][e] if r["prems"][l] <= pm else -0.0004
    return out
week0 = dt.datetime.fromtimestamp(T.min(), dt.UTC).date(); wk = np.array([(dt.datetime.fromtimestamp(t, dt.UTC).date() - week0).days // 7 for t in T])
print(f"{W}: {len(rows)} copies loaded (PAY={PAY}), {week0} to {dt.datetime.fromtimestamp(T.max(), dt.UTC):%Y-%m-%d}; halves at {dt.datetime.fromtimestamp(tmid, dt.UTC):%m-%d %H:%M} UTC")
print("weeks from " + str(week0) + ": " + ", ".join(f"wk{w} {(wk == w).sum()}" for w in sorted(set(wk))))
base = None
for s_ in SETS:
    nm, spec = s_.split("=", 1); X = per_copy(spec); v = X.mean(axis=1); bought = v != 0
    def w2(m):
        x = v[m & bought]; k = max(1, round(0.02 * len(x))); return x.sum() - np.sort(x)[len(x) - k:].sum() if len(x) else 0.0
    print(f"\n{nm:22s} {spec}")
    print(f"   copies {bought.sum()} | SOL {v.sum():+.2f} | w/o 2% half 1 {w2(A):+.2f} half 2 {w2(~A):+.2f} | landing 4 / 8 / next slot: " + " / ".join(f"{X[:, l].sum():+.2f}" for l in range(3)))
    print("   by week: " + " | ".join(f"wk{w} {v[wk == w].sum():+.2f} ({(bought & (wk == w)).sum()})" for w in sorted(set(wk))))
    if base is None: base = (v, X); continue
    d = v - base[0]; dl = X - base[1]; rng = np.random.default_rng(7); bs = rng.choice(len(d), size=(10000, len(d)))
    pos = np.mean(d[bs].sum(axis=1) > 0); k = max(1, round(0.02 * (d != 0).sum())); dd = np.sort(d[d != 0])
    print(f"   vs running: {d.sum():+.2f} SOL | half 1 {d[A].sum():+.2f} half 2 {d[~A].sum():+.2f} | without the 2% of copies that gained most {dd[:-k].sum() if len(dd) > k else 0:+.2f}"
          f" | landing 4 / 8 / next slot " + " / ".join(f"{dl[:, l].sum():+.2f}" for l in range(3)) + f" | weeks better {sum(d[wk == w].sum() > 0 for w in set(wk))} of {len(set(wk))} | P(better) {100 * pos:.1f}%")
