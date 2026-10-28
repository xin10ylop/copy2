# The profile of one wallet, the marks of README.md's table, from the pipeline's files (run after early.py, create.py,
# full_paths.py; grid.py prints mark 7 itself). P1 = Oct 19-22, P2 = Oct 23 -> Oct 27 00:20, P3 = Oct 27 00:20 -> its
# last row (UTC), by the time of its first buy of the coin; (+x) = without the period's best 2.
#   1 its first buys of pump coins priced in another token, 1.45+ SOL and 0.5+ SOL (SOL value, trips.py), per day; how
#     many came at the coin's create slot or the next (create.py); the quote tokens (pull.py "qm")
#   2 its rule: one-buy one-sell curve trips of those coins (exitrule.py's _exits.json): hold, the multiple at its sale,
#     the share sold at 1,790 s or later (wallet 4's timer), its own most common hold and the share there
#   3 early sales (early.py's _early.json: sold before 1,790 s between 0.75x and 2.4x), 1.45+ SOL
#   4 lands: failed signatures against failed + landed transactions it signed (sigs.py, pull.py)
#   5 routable share of its 1.45+ (and 0.5+) first buys by the curve's quote (route_q.py: A, B, C)
#   6 its own result by period (ledger.py via groups.py's _tokens.json), all tokens and pump coins priced in another token
#   8 the frenzy after its buys: curve transactions after its buy in its slot and the next (full_paths.py n01), and the
#     curve trades on the recorded path in the same two slots (the measure wallet 4's old paths allow)
#   python3 -I marks.py WALLET [FLOOR=1.45]
import sys, os, json, datetime, collections, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
SP = os.environ.get("SP", "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/score")
W = sys.argv[1]; FLOOR = float(sys.argv[2]) if len(sys.argv) > 2 else 1.45
os.environ["W"] = W
from route_q import cls
H = f"{SP}/h9long/{W[:8]}"
T = json.load(open(f"{H}_trips.json"))
rows = [json.loads(l) for l in open(f"{H}.jsonl")]
sigs = json.load(open(f"{H}_sigs.json"))
P3 = 1793060400
def per(t): return "P1" if datetime.datetime.fromtimestamp(t, datetime.timezone.utc).day <= 22 else "P2" if t < P3 else "P3"
end = max(r["bt"] for r in rows)
DAYS = {"P1": 4.0, "P2": (P3 - 1792713600) / 86400, "P3": (end - P3) / 86400}
def q(xs, ps=(10, 25, 50, 75, 90), nd=2):
    xs = sorted(xs); return [round(xs[min(len(xs) - 1, int(p / 100 * len(xs)))], nd) for p in ps] if xs else []
NAMES = {"CARDSccU": "CARDS", "pumpCmXq": "PUMP", "3NZ9JMVB": "WBTC", "TTWofwAg": "TTWO", "WXMRyRZh": "WXMR", "A7bdiYdS": "A7bd",
         "SPCXxcqX": "SPCX", "98sMhvDw": "98sM", "Pren1FvF": "Pren", "DJTu7vi8": "DJTu", "XsoCS1Tf": "XsoC", "7vfCXTUX": "WETH",
         "EPjFWdd5": "USDC", "Es9vMFrz": "USDT", "USD1ttGY": "USD1", "So111111": "wSOL"}
QM = {}
for r in rows:
    for t in r["tr"]:
        if t[1] == W and t[0] in r.get("qm", {}): QM.setdefault(t[0], r["qm"][t[0]])
def qname(m): z = QM.get(m); return "?" if not z else NAMES.get(z[:8], "xStock" if z.startswith("Xs") else z[:8])
if not QM and os.path.exists(f"{H}_quote.json"):       # wallet 4's old rows have no "qm": the token it paid or got (byquote.py)
    _Q = json.load(open(f"{H}_quote.json"))
    def qname(m): return _Q.get(m, "via SOL only")
CR = json.load(open(f"{H}_create.json")) if os.path.exists(f"{H}_create.json") else {}
M = dict(w=W, floor=FLOOR, days=DAYS)          # the key figures, for row.py
print(f"== {W}  rows {len(rows)}, last row {datetime.datetime.fromtimestamp(end, datetime.timezone.utc):%m-%d %H:%M} UTC, "
      f"days P1 {DAYS['P1']:.2f} P2 {DAYS['P2']:.2f} P3 {DAYS['P3']:.2f}")
# 1
first = [x for x in T if x["tr"] and x["tr"][0]["buy"]]
oq = [x for x in first if x["kind"] == "pump, other quote"]
print("\n1. first buys of coins priced in another token (and SOL-priced, for scale), by its SOL value")
print(f"   its first-buy SOL, other quote: p10..p90 {q([x['tr'][0]['v'] or 0 for x in oq])}   SOL-priced: {q([x['tr'][0]['v'] or 0 for x in first if x['kind'] == 'pump, SOL quote'])}")
for lo in (FLOOR, 0.5):
    for p in ("P1", "P2", "P3"):
        xs = [x for x in oq if (x["tr"][0]["v"] or 0) >= lo and per(x["tr"][0]["bt"]) == p]
        sol = [x for x in first if x["kind"] == "pump, SOL quote" and (x["tr"][0]["v"] or 0) >= lo and per(x["tr"][0]["bt"]) == p]
        meas = [x for x in xs if CR.get(x["m"]) and CR[x["m"]][0] is not None]
        c01 = sum(1 for x in meas if x["tr"][0]["s"] - CR[x["m"]][0] <= 1)
        c2s = sum(1 for x in meas if CR[x["m"]][1] and x["tr"][0]["bt"] - CR[x["m"]][1] <= 2)
        M[f"m1_{lo}_{p}"] = dict(n=len(xs), day=len(xs) / DAYS[p], meas=len(meas), c01=c01, c2s=c2s, sol=len(sol))
        print(f"   {lo}+ SOL {p}: {len(xs):5d} coins, {len(xs) / DAYS[p]:6.1f} a day;  create+0/+1 {c01} of {len(meas)} measured"
              f" ({100 * c01 / max(len(meas), 1):.0f}%), {c01 / DAYS[p]:.1f} a day; within 2 s {c2s};  SOL-priced {lo}+: {len(sol)}")
    xs = [x for x in oq if (x["tr"][0]["v"] or 0) >= lo]
    M[f"m1_{lo}_quotes"] = collections.Counter(qname(x["m"]) for x in xs).most_common(6)
    M[f"m5_{lo}"] = dict(n=len(xs), abc=sum(cls(x) in "ABC" for x in xs), cls=dict(collections.Counter(cls(x) for x in xs)))
    print(f"   {lo}+ quote mix: " + "  ".join(f"{k} {v}" for k, v in collections.Counter(qname(x["m"]) for x in xs).most_common(10)))
    print(f"   {lo}+ route class (route_q): " + "  ".join(f"{k} {v}" for k, v in sorted(collections.Counter(cls(x) for x in xs).items()))
          + f"   routable (A B C) {sum(cls(x) in 'ABC' for x in xs)} of {len(xs)} ({100 * sum(cls(x) in 'ABC' for x in xs) / max(len(xs), 1):.0f}%)")
# 2
R = json.load(open(f"{H}_exits.json"))
print("\n2. its one-buy one-sell curve trips (exitrule.py), coins priced in another token")
for lo, name in ((0, "all sizes"), (FLOOR, f"{FLOOR}+ SOL")):
    rs = [r for r in R if r["kind"] == "pump, other quote" and (r["buy_sol"] or 0) >= lo]
    if not rs: print(f"   {name}: none"); continue
    secs = [r["sec"] for r in rs]
    M[f"m2_{lo}"] = dict(n=len(rs), sec=q(secs, nd=0), t1790=sum(s >= 1790 for s in secs), marg=q([r["marg"] for r in rs]),
                         tp24=sum(r["marg"] >= 2.4 for r in rs), sl75=sum(r["marg"] <= 0.75 for r in rs))
    mode = collections.Counter(min(s // 10 * 10, 99990) for s in secs if s >= 3).most_common(3)
    md = mode[0][0] if mode else 0
    at = sum(1 for s in secs if md - 10 <= s <= md + 20)
    print(f"   {name}: {len(rs)} trips; seconds held p10..p90 {q(secs, nd=0)}; held 1,790 s or more {sum(s >= 1790 for s in secs)} "
          f"({100 * sum(s >= 1790 for s in secs) / len(rs):.0f}%); its most common holds (10-s bins) {mode}: {at} ({100 * at / len(rs):.0f}%) within -10/+20 s of {md} s")
    print(f"      marginal multiple at its sale p10..p90 {q([r['marg'] for r in rs])}; >= 2.4x {sum(r['marg'] >= 2.4 for r in rs)}, "
          f"<= 0.75x {sum(r['marg'] <= 0.75 for r in rs)}, 0.75-2.4x before 1,790 s {sum(0.75 < r['marg'] < 2.4 and r['sec'] < 1790 for r in rs)}; "
          f"its net {sum(r['net'] or 0 for r in rs):+.2f}, won {sum((r['net'] or 0) > 0 for r in rs)}")
    hb = collections.Counter(("<5 s", "5-30 s", "30 s-2 min", "2-10 min", "10-29.8 min", "29.8-31 min", ">31 min")[(s >= 5) + (s >= 30) + (s >= 120) + (s >= 600) + (s >= 1790) + (s >= 1860)] for s in secs)
    print("      held: " + "  ".join(f"{k} {hb[k]}" for k in ("<5 s", "5-30 s", "30 s-2 min", "2-10 min", "10-29.8 min", "29.8-31 min", ">31 min")))
    tm = [r["marg"] for r in rs if r["sec"] < 1790]
    mb = collections.Counter(("<0.5", "0.5-0.75", "0.75-1.0", "1.0-1.5", "1.5-2.0", "2.0-2.4", "2.4-3", "3+")[(m >= .5) + (m >= .75) + (m >= 1) + (m >= 1.5) + (m >= 2) + (m >= 2.4) + (m >= 3)] for m in tm)
    print("      multiple at sales before 1,790 s: " + "  ".join(f"{k} {mb[k]}" for k in ("<0.5", "0.5-0.75", "0.75-1.0", "1.0-1.5", "1.5-2.0", "2.0-2.4", "2.4-3", "3+")))
for p in ("P1", "P2", "P3"):                   # its result by the shape of the coin's trades (one sale or several)
    g = collections.defaultdict(list)
    for x in oq:
        if per(x["tr"][0]["bt"]) != p: continue
        nb = sum(t["buy"] for t in x["tr"]); ns = len(x["tr"]) - nb
        g["1 buy 1 sale" if (nb, ns) == (1, 1) else "1 buy, 2+ sales" if nb == 1 and ns >= 2 else "no sale" if not ns else "2+ buys"].append(x["net"] or 0)
    M[f"m2_shape_{p}"] = {k: (len(v), sum(v)) for k, v in g.items()}
    print(f"   {p} by shape: " + "  ".join(f"{k} {len(v)} {sum(v):+.2f}" for k, v in sorted(g.items())))
nt = collections.Counter(len(x["tr"]) for x in oq)
print(f"   coins priced in another token by its curve trades: 2 (one buy one sell) {nt[2]}, 1 {nt[1]}, 3+ {sum(v for k, v in nt.items() if k >= 3)}")
# 3
if os.path.exists(f"{H}_early.json"):
    E = json.load(open(f"{H}_early.json"))
    print(f"\n3. early sales, {FLOOR}+ SOL one-buy one-sell trips (early.py)")
    for p in ("P1", "P2", "P3"):
        xs = [r for r in E if r["per"] == p]; c = collections.Counter(r["how"] for r in xs)
        M[f"m3_{p}"] = dict(n=len(xs), early=c["early"], tp=c["tp"], stop=c["stop"], time=c["time"])
        print(f"   {p} {len(xs)}: tp {c['tp']} stop {c['stop']} time {c['time']} early {c['early']} ({100 * c['early'] / max(len(xs), 1):.1f}%)")
# 4
fail = sum(1 for s in sigs if s[3]); own = sum(1 for r in rows if r["signer"])
M["m4"] = dict(sigs=len(sigs), fail=fail, own=own)
print(f"\n4. signatures {len(sigs)}: failed {fail}; landed {len(sigs) - fail}, of which it signed {own}; failed / (failed + its landed) "
      f"{100 * fail / max(fail + own, 1):.1f}%  (failed / all {100 * fail / max(len(sigs), 1):.1f}%)")
for p in ("P1", "P2", "P3"):
    f_ = sum(1 for s in sigs if s[3] and per(s[2]) == p); o_ = sum(1 for r in rows if r["signer"] and per(r["bt"]) == p)
    print(f"   {p}: failed {f_}, its landed {o_}: {100 * f_ / max(f_ + o_, 1):.1f}%")
# 6
K = json.load(open(f"{H}_tokens.json"))
print("\n6. its own result (ledger.py, by the coin's first buy)")
for p in ("P1", "P2", "P3"):
    for name, sel in (("all tokens", lambda x: True), ("pump, other quote", lambda x: x["kind"] == "pump, other quote"),
                      ("pump, SOL quote", lambda x: x["kind"] == "pump, SOL quote")):
        v = sorted((x["net"] for x in K if per(x["first"]) == p and sel(x)), reverse=True)
        M[f"m6_{p}_{name}"] = (len(v), sum(v), sum(v[2:]))
        print(f"   {p} {name:18s} {len(v):5d} tokens  {sum(v):+8.2f} ({sum(v[2:]):+8.2f})")
# 8
FP = json.load(open(f"{H}_fpaths.json")) if os.path.exists(f"{H}_fpaths.json") else {}
Tm = {x["m"]: x for x in T}
n01, pth = [], []
for m, v in FP.items():
    x = Tm.get(m)
    if not v or not x or x["kind"] != "pump, other quote" or (x["tr"][0]["v"] or 0) < FLOOR: continue
    b = x["tr"][0]
    if v.get("n01") is not None: n01.append(v["n01"])
    if "path" in v: pth.append(sum(1 for r in v["path"] if (r[0], r[1]) > (b["s"], b["i"] or 0) and r[0] <= b["s"] + 1))
M["m8"] = dict(n01=st.median(n01) if n01 else None, n=len(n01), q=q(n01, (25, 50, 75), 0), path=st.median(pth) if pth else None)
json.dump(M, open(f"{H}_marks{'' if FLOOR == 1.45 else '_' + str(FLOOR)}.json" if not os.environ.get("ROUTECLS") else os.devnull, "w"))
print(f"\n8. after its {FLOOR}+ SOL buys (coins priced in another token, full_paths): curve transactions in its slot after it and the next:"
      f" median {st.median(n01) if n01 else None} (p25..p75 {q(n01, (25, 50, 75), 0)}, n {len(n01)});"
      f" curve trades on the recorded path, same slots: median {st.median(pth) if pth else None} (p25..p75 {q(pth, (25, 50, 75), 0)}, n {len(pth)})")
