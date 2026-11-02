# Step 2a: create-time features of every part-B create (out/universe.json), from the create transaction only (what a bot
# sees when it lands in the create slot; ../w4rev/feat.py's set) plus history known at create time:
#  - dev buy: the buys inside the create transaction (dev_n, dev_users), in SOL at pump's own price of the quote
#    (30 SOL / the curve's initial virtual quote, ../w4rev/feat.py), and as a share of supply (dev_tok, 1e15 = 100%);
#  - the creator's earlier creates in the whole quote-control universe since Oct 19 (any quote; prior, prior24, gap,
#    prior_same_q), and the share of those earlier coins wallet 4 bought (w4_prior; wallet 4's own signal, reported, not
#    used by the rules);
#  - the quote's heat: part-B creates of the same quote in the hour before (q_heat1h) and its launch share of all
#    part-B creates that hour;
#  - name / symbol traits, uri host, hour (UTC), creator fee (cfee bps), mayhem, the programs of the create tx.
#   python3 -I f1_table.py -> out/table.json [row]
import sys, os, re, time, bisect, collections
from urllib.parse import urlparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blib
from u1_universe import sym
def host(u):
    try: h = urlparse(u).netloc.lower()
    except Exception: h = ""
    return h or ("(none)" if not u else "(other)")
PSHORT = {"ComputeB": "cb", "JUP6LkbZ": "jup", "6EF8rrec": "pump", "ATokenGP": "ata", "11111111": "sys", "TokenkegQ": "tok",
          "Tokenkeg": "tok", "TokenzQd": "t22", "MemoSq4g": "memo", "pAMMBay6": "pamm"}
def progs(r):
    return "+".join(sorted({PSHORT.get(p[:8], p[:6]) for p in (r.get("progs") or [])}))
if __name__ == "__main__":
    U = blib.jl(blib.OUT + "/universe.json")
    ALL = [r for r in blib.jl(blib.A_OUT + f"/qc_creates_{blib.T_LO}_{blib.T_HI}.json").values() if r.get("mint")]
    ALL.sort(key=lambda r: (r["cslot"], r.get("cidx") or 0))
    P = blib.jl(blib.A_OUT + "/picks.json")
    picked = {p["csig"] for p in P.values() if p.get("csig") and p.get("ds") is not None and p["ds"] <= 1}
    by = collections.defaultdict(list)
    for r in ALL: by[r["user"]].append(r)
    hist = {}
    for u, L in by.items():
        for i, r in enumerate(L):
            prev = L[:i]
            hist[r["csig"]] = dict(prior=len(prev), prior24=sum(1 for p in prev if p["cbt"] >= r["cbt"] - 86400),
                                   gap=(r["cbt"] - prev[-1]["cbt"]) if prev else -1,
                                   prior_same_q=sum(1 for p in prev if p["quote"] == r["quote"]),
                                   w4_prior=sum(1 for p in prev if p["csig"] in picked))
    # quote heat: same-quote part-B creates in the hour before
    Ub = sorted(U, key=lambda r: r["cbt"]); qt = collections.defaultdict(list); allt = [r["cbt"] for r in Ub]
    for r in Ub: qt[r["quote"]].append(r["cbt"])
    T = []
    for r in U:
        v0 = r.get("vquote") or 1
        buys = [d for d in r["dev"] if d[1]]
        dq = sum((d[4] or 0) for d in buys)
        ts = qt[r["quote"]]; i = bisect.bisect_left(ts, r["cbt"]); j = bisect.bisect_left(ts, r["cbt"] - 3600)
        a = bisect.bisect_left(allt, r["cbt"]); b = bisect.bisect_left(allt, r["cbt"] - 3600)
        f = dict(mint=r["mint"], csig=r["csig"], cslot=r["cslot"], cbt=r["cbt"], per=r["per"], quote=r["quote"], qsym=sym(r["quote"]),
                 depth=r.get("depth") or 0, cfee=r.get("cfee"), mayhem=r.get("mayhem") or 0,
                 dev_sol=round(30.0 * dq / v0, 4), dev_n=len(buys), dev_users=len({d[0] for d in buys}),
                 dev_tok=round(sum(d[3] for d in buys) / 1e13, 3),
                 cre_is_user=int(r["creator"] == r["user"]), payer_is_user=int(r["payer"] == r["user"]),
                 host=host(r.get("uri") or ""), hour=time.gmtime(r["cbt"]).tm_hour,
                 nlen=len(r["name"]), slen=len(r["sym"]), s_upper=int(r["sym"].isupper()), s_eq_n=int(r["sym"].lower() == r["name"].lower()),
                 nonascii=int(any(ord(ch) > 127 for ch in r["name"] + r["sym"])), digits=int(bool(re.search(r"\d", r["name"] + r["sym"]))),
                 nwords=len(r["name"].split()), progs=progs(r), nsig=r.get("nsig") or 0, cu=r.get("cu") or 0, fee=r.get("fee") or 0,
                 cidx=r.get("cidx") or 0, q_heat1h=i - j, q_share1h=round((i - j) / max(1, a - b), 4),
                 pick=r["pick"], big=r["big"], late=r["late"], w4v=r["w4v"], w4net=r["w4net"], w4ds=r["w4ds"], user=r["user"],
                 name=r["name"], sym=r["sym"], vquote=r["vquote"])
        f.update(hist[r["csig"]])
        T.append(f)
    blib.jdump(T, blib.OUT + "/table.json")
    print(f"{len(T)} rows; picks {sum(t['pick'] for t in T)}, big {sum(t['big'] for t in T)}")
    # univariate: pick rate by feature bucket, P1 and P2
    def rate(rows, key, buckets=None, top=12):
        print(f"\n== {key}: creates / launch picks (rate) / 1.45+ picks (rate), P1 | P2")
        def b(t):
            v = t[key]
            if buckets is None: return v
            for lo, hi, lab in buckets:
                if lo <= v < hi: return lab
            return "?"
        cnt = collections.Counter(b(t) for t in rows)
        keys = [k for k, _ in cnt.most_common(top)] if buckets is None else [lab for _, _, lab in buckets]
        for k in keys:
            line = f"  {str(k)[:34]:34s}"
            for pp in ("P1", "P2"):
                S = [t for t in rows if t["per"] == pp and b(t) == k]
                n = len(S); p = sum(t["pick"] for t in S); g = sum(t["big"] for t in S)
                line += f" | {n:6d} {p:5d} ({p / n if n else 0:5.1%}) {g:4d} ({g / n if n else 0:5.1%})"
            print(line)
    rate(T, "dev_n", [(0, 1, "0"), (1, 2, "1"), (2, 99, "2+")])
    rate(T, "dev_sol", [(-1, 1e-9, "0"), (1e-9, 0.1, "<0.1"), (0.1, 0.5, "0.1-0.5"), (0.5, 1, "0.5-1"), (1, 2, "1-2"), (2, 4, "2-4"), (4, 8, "4-8"), (8, 1e9, "8+")])
    rate(T, "cfee"); rate(T, "depth"); rate(T, "host", top=15); rate(T, "progs", top=10)
    rate(T, "hour", [(h, h + 3, f"{h:02d}-{h + 3:02d}") for h in range(0, 24, 3)])
    rate(T, "prior", [(0, 1, "0"), (1, 2, "1"), (2, 5, "2-4"), (5, 20, "5-19"), (20, 100, "20-99"), (100, 1e9, "100+")])
    rate(T, "w4_prior", [(0, 1, "0"), (1, 2, "1"), (2, 5, "2-4"), (5, 1e9, "5+")])
    rate(T, "nsig", [(1, 2, "1"), (2, 3, "2"), (3, 99, "3+")])
    rate(T, "q_heat1h", [(0, 1, "0"), (1, 5, "1-4"), (5, 20, "5-19"), (20, 100, "20-99"), (100, 1e9, "100+")])
    rate(T, "cre_is_user", [(0, 1, "0"), (1, 2, "1")]); rate(T, "payer_is_user", [(0, 1, "0"), (1, 2, "1")])
    rate(T, "nonascii", [(0, 1, "0"), (1, 2, "1")]); rate(T, "s_upper", [(0, 1, "0"), (1, 2, "1")])
