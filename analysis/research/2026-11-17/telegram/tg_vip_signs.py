# SolHouse VIP: winners against losers, and a setup built from the signs that hold (the owner, Nov 17: "differentiate
# winning from losing coins ... a good setup is what differentiates us"). Every sampled VIP call with a price path at the
# post (tg_channel.py's load(): the curve, or its pool, the pool going on after a graduation).
#   winner = the price reached 1.5x the post's within the hour.
# Signs: from the post (tier, market cap, age in minutes, on the curve or in a pool, channels spotted in, 24 h volume and
# transactions); from the chain in the 10 min before (the run over 10 min and over the last minute, trades, net SOL in,
# the biggest buy, the share of sales; sizes from the reserve changes, curve or pool alike); from the first 2 min after
# (the price at +60 s and +120 s, a stall: no new high in the last 90 s of the 2 min, net SOL in).
# Each numeric sign is cut at its median on the first half of the days (A); it holds when its winner rate is higher on the
# same side in A and in the second half (B), by 5 points or more in both. The setup = every holding sign at the post
# (entry at the post) or every holding sign up to 2 min (entry at +2 min), the exit picked on A from tg_channel's menu,
# scored on B, without the best 5.
#   python3 -I tg_vip_signs.py TGDIR > out/tg_vip_signs.txt
import sys, os, json, statistics as st
TG = sys.argv[1]; D = f"{TG}/vip"; here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, "tg_channel.py")).read().split("for cj in sorted(glob.glob")[0]
sys.argv = [sys.argv[0], TG]; ns = {}; exec(compile(src, "tg_channel.py", "exec"), ns); load, sim, EX = ns["load"], ns["sim"], ns["EX"]
meta = json.load(open(f"{D}/meta.json")); C = load(D); pr = lambda r: r[1] / r[2]
def age_min(a):
    if not a: return None
    n = float("".join(ch for ch in a if ch.isdigit() or ch == ".") or 0); u = a[-1]
    return n * {"s": 1 / 60, "m": 1, "h": 60, "d": 1440}.get(u, 1)
rows = []
for t, m, P in C:
    mt = meta.get(m, {}); pre = [r for r in P if r[0] <= t]; p0 = pr(pre[-1])
    w10 = [r for r in P if t - 600 < r[0] <= t]; old = [r for r in P if r[0] <= t - 600]; m1 = [r for r in P if r[0] <= t - 60]
    dq = [b[1] - a[1] for a, b in zip(w10, w10[1:])]   # quote reserve change per trade: + a buy, - a sale (lamports)
    a2 = [r for r in P if t < r[0] <= t + 120]; dq2 = [b[1] - a[1] for a, b in zip([pre[-1]] + a2, a2)]
    hi, hi_t = p0, t
    for r in a2:
        if pr(r) > hi: hi, hi_t = pr(r), r[0]
    at = lambda o: pr([r for r in P if r[0] <= t + o][-1]) / p0
    pk = max(pr(r) for r in P if t < r[0] <= t + 3600) / p0
    rows.append(dict(t=t, m=m, P=P, win=pk >= 1.5, tier=mt.get("tier"), curve=float((mt.get("pool") or "").strip() == "Pump.fun"),
        mc=mt.get("mc", 0), age=age_min(mt.get("age")) or 0, spotted=mt.get("spotted", 0), vol=mt.get("vol", 0), txns=mt.get("txns", 0),
        run10=p0 / pr(old[-1]) if old else p0 / pr(P[0]), run1=p0 / pr(m1[-1]) if m1 else 1.0, n10=len(w10),
        flow10=sum(dq) / 1e9, big10=max([x for x in dq if x > 0] or [0]) / 1e9, sell10=sum(x < 0 for x in dq) / max(1, len(dq)),
        p60=at(60), p120=at(120), stall=float(not a2 or (t + 120) - hi_t >= 90), flow2=sum(dq2) / 1e9))
rows.sort(key=lambda r: r["t"]); mid = (rows[0]["t"] + rows[-1]["t"]) / 2
A = [r for r in rows if r["t"] < mid]; B = [r for r in rows if r["t"] >= mid]
wr = lambda v: sum(r["win"] for r in v) / len(v) if v else float("nan")
print(f"{len(rows)} VIP calls with a price path; winners (1.5x in the hour) {wr(rows):.0%}; first half {len(A)} ({wr(A):.0%}), second half {len(B)} ({wr(B):.0%})")
print("\nby tier: winner rate first half / second half")
for tr in ("Diamond", "Safe", "Gamble", "Gamble Risk"):
    print(f"  {tr:12s} {wr([r for r in A if r['tier'] == tr]):4.0%} ({sum(r['tier'] == tr for r in A):3d}) / {wr([r for r in B if r['tier'] == tr]):4.0%} ({sum(r['tier'] == tr for r in B):3d})")
SIGNS = [("mc", "post"), ("age", "post"), ("curve", "post"), ("spotted", "post"), ("vol", "post"), ("txns", "post"),
         ("run10", "post"), ("run1", "post"), ("n10", "post"), ("flow10", "post"), ("big10", "post"), ("sell10", "post"),
         ("p60", "2 min"), ("p120", "2 min"), ("stall", "2 min"), ("flow2", "2 min")]
print("\nsign      when   | cut (A median) | winner rate low / high: first half A | second half B | holds")
hold = []
for k, when in SIGNS:
    cut = st.median([r[k] for r in A])
    lo = lambda v: [r for r in v if r[k] <= cut]; hi = lambda v: [r for r in v if r[k] > cut]
    da, db = wr(hi(A)) - wr(lo(A)), wr(hi(B)) - wr(lo(B))
    ok = da == da and db == db and abs(da) >= 0.05 and abs(db) >= 0.05 and (da > 0) == (db > 0)
    if ok: hold.append((k, when, cut, da > 0))
    print(f"{k:9s} {when:6s} | {cut:12.3f}   | {wr(lo(A)):4.0%} / {wr(hi(A)):4.0%}             | {wr(lo(B)):4.0%} / {wr(hi(B)):4.0%}   | {'YES, keep ' + ('high' if da > 0 else 'low') if ok else ''}")
def passes(r, upto):
    return all((r[k] > c) if high else (r[k] <= c) for k, w, c, high in hold if upto == "2 min" or w == "post")
for upto, entry_delay in (("post", 0), ("2 min", 120)):
    a = [r for r in A if passes(r, upto)]; b = [r for r in B if passes(r, upto)]
    print(f"\nsetup with the signs up to {upto} ({', '.join(k + ('>' if h else '<=') + format(c, '.3g') for k, w, c, h in hold if upto == '2 min' or w == 'post') or 'none'}):"
          f" first half {len(a)} calls ({wr(a):.0%} winners), second half {len(b)} ({wr(b):.0%})")
    best = None
    for ex in EX:
        va = [x for x in (sim(r["t"] + entry_delay, r["P"], "post", ex) for r in a) if x is not None]
        vb = [x for x in (sim(r["t"] + entry_delay, r["P"], "post", ex) for r in b) if x is not None]
        if va and (best is None or sum(va) > best[0]): best = (sum(va), ex, va, vb)
    if best:
        _, ex, va, vb = best; s = sorted(vb, reverse=True)
        print(f"  exit picked on the first half: {ex} ({len(va)} copies {sum(va):+.2f}) -> second half {len(vb)} copies {sum(vb):+.2f} "
              f"({sum(vb) / max(1, len(vb)) / 0.5:+.1%} a copy), without the best 5 {sum(s[5:]):+.2f}")
    allb = [x for x in (sim(r["t"] + entry_delay, r["P"], "post", "tp2") for r in B) if x is not None]
    print(f"  for comparison, every call (no filter), tp2, second half: {len(allb)} copies {sum(allb):+.2f}")
