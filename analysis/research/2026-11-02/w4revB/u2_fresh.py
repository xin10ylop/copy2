# Step 4a: the fresh window, P3 = Oct 27 00:00 - Nov 1 23:00 UTC (wallet 4 changed its exits on Oct 27). Every landed
# quote-control create of the window as the part-A agent read it (../w4rev/out/qc_creates_1793059200_1793574000.json,
# read-only), classed (u1_universe.cls, pools as of Nov 1), part B = class E; the create-time features of f1_table.py
# with the creator history running from Oct 19 (both windows). Wallet 4's launch picks are labelled later from each
# sampled coin's own tape (a TradeEvent by wallet 4 in the create slot or the next).
# Sample: the coins passing rule RULE (seeded NR a day) and a base sample of the other launches of the P1/P2 active
# quotes (NB a day, by quote as t0_sample.py), each with its weight.
#   python3 -I u2_fresh.py [NR=150] [NB=120] -> out/fresh_table.json, out/fresh_sample.json, out/coins_fresh.json
import sys, os, re, time, bisect, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blib, u1_universe as u1
from f1_table import host, progs
from f2_rule import RULES
NR = int(sys.argv[1]) if len(sys.argv) > 1 else 150; NB = int(sys.argv[2]) if len(sys.argv) > 2 else 120
F_LO, F_HI = 1793059200, 1793574000
FQC = blib.A_OUT + f"/qc_creates_{F_LO}_{F_HI}.json"
if __name__ == "__main__":
    A = [r for r in blib.jl(blib.A_OUT + f"/qc_creates_{blib.T_LO}_{blib.T_HI}.json").values() if r.get("mint")]
    B = [r for r in blib.jl(FQC).values() if r.get("mint") and F_LO <= (r.get("cbt") or 0) < F_HI]
    u1.ensure([r["quote"] for r in B])
    ALL = sorted(A + B, key=lambda r: (r["cslot"], r.get("cidx") or 0))
    by = collections.defaultdict(list)
    for r in ALL: by[r["user"]].append(r)
    hist = {}
    for u, L in by.items():
        for i, r in enumerate(L):
            if r["cbt"] < F_LO: continue
            prev = L[:i]
            hist[r["csig"]] = dict(prior=len(prev), prior24=sum(1 for p in prev if p["cbt"] >= r["cbt"] - 86400),
                                   gap=(r["cbt"] - prev[-1]["cbt"]) if prev else -1, prior_same_q=sum(1 for p in prev if p["quote"] == r["quote"]))
    E = [r for r in B if u1.cls(r["quote"]) == "E"]
    qt = collections.defaultdict(list)
    for r in sorted(E, key=lambda r: r["cbt"]): qt[r["quote"]].append(r["cbt"])
    T = []
    for r in E:
        v0 = r.get("vquote") or 1; buys = [d for d in r["dev"] if d[1]]; dq = sum((d[4] or 0) for d in buys)
        ts = qt[r["quote"]]; i = bisect.bisect_left(ts, r["cbt"]); j = bisect.bisect_left(ts, r["cbt"] - 3600)
        f = dict(mint=r["mint"], csig=r["csig"], cslot=r["cslot"], cbt=r["cbt"], cidx=r.get("cidx"), per="P3", quote=r["quote"], qsym=u1.sym(r["quote"]),
                 depth=r.get("depth") or 0, cfee=r.get("cfee"), mayhem=r.get("mayhem") or 0, dev_sol=round(30.0 * dq / v0, 4), dev_n=len(buys),
                 dev_users=len({d[0] for d in buys}), dev_tok=round(sum(d[3] for d in buys) / 1e13, 3), cre_is_user=int(r["creator"] == r["user"]),
                 host=host(r.get("uri") or ""), hour=time.gmtime(r["cbt"]).tm_hour, progs=progs(r), user=r["user"], creator=r["creator"],
                 vquote=r["vquote"], vtok=r["vtok"], name=r["name"], sym=r["sym"], q_heat1h=i - j, day=time.strftime("%m-%d", time.gmtime(r["cbt"])))
        f.update(hist[r["csig"]])
        T.append(f)
    blib.jdump(T, blib.OUT + "/fresh_table.json")
    TB = blib.jl(blib.OUT + "/table.json")
    pk = collections.Counter(t["quote"] for t in TB if t["pick"]); ACTIVE = {q for q, n in pk.items() if n >= 5}
    R2 = RULES["R2 R1 + manual create tx (ata[+cb]+pump[+sys])"]
    print(f"P3 quote-control creates {len(B)}; part B (class E) {len(T)}; R2 {sum(1 for t in T if R2(t))}; in the P1/P2 active quotes {sum(1 for t in T if t['quote'] in ACTIVE)}")
    print("part-B creates by day:", sorted(collections.Counter(t["day"] for t in T).items()))
    print("R2 by day:", sorted(collections.Counter(t["day"] for t in T if R2(t)).items()))
    print("top quotes:", [(u1.sym(q), n) for q, n in collections.Counter(t["quote"] for t in T).most_common(15)])
    print("top quotes in R2:", [(u1.sym(q), n) for q, n in collections.Counter(t["quote"] for t in T if R2(t)).most_common(15)])
    rnd = random.Random(20261103); S = {}
    for d in sorted({t["day"] for t in T}):
        pool = [t for t in T if t["day"] == d and R2(t)]
        for t in rnd.sample(pool, min(NR, len(pool))): S[t["mint"]] = dict(set="r2", w=len(pool) / min(NR, len(pool)), per="P3", quote=t["quote"], day=d)
        base = [t for t in T if t["day"] == d and not R2(t) and t["quote"] in ACTIVE]
        g = collections.defaultdict(list)
        for t in base: g[t["quote"]].append(t)
        for q, L in g.items():
            k = min(len(L), max(3, round(NB * len(L) / max(1, len(base)))))
            for t in rnd.sample(L, k): S[t["mint"]] = dict(set="base", w=len(L) / k, per="P3", quote=q, day=d)
    blib.jdump(S, blib.OUT + "/fresh_sample.json")
    blib.jdump(sorted(S, key=lambda m: (S[m]["set"] != "r2", S[m]["day"])), blib.OUT + "/coins_fresh.json")
    print("fresh sample:", collections.Counter((v["set"], v["day"]) for v in S.values()))
