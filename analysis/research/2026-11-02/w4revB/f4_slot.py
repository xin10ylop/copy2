# Step 2d: the create slot as a feature (sampled coins with a tape, each counted with its sample weight): buys in the
# create slot by wallets other than the creator and wallet 4, counted only before wallet 4's own buy when it bought in
# that slot (what follows it may be its copiers), split into the launch bundle (within 5 transactions of the create, as
# ../agents/scan/src/.../creates/README.md §5 defines it) and later buys; their size in SOL at pump's config price
# (30 SOL x quote / the curve's initial virtual quote). Pick rates by bucket, P1 / P2; and R2 with a bundle condition.
#   python3 -I f4_slot.py -> out/slot.json {mint: features}
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blib
from f2_rule import RULES
R2 = RULES["R2 R1 + manual create tx (ata[+cb]+pump[+sys])"]
S = blib.jl(blib.OUT + "/sample.json"); TB = {t["mint"]: t for t in blib.jl(blib.OUT + "/table.json")}
U = {r["mint"]: r for r in blib.jl(blib.OUT + "/universe.json")}
TD = os.path.join(blib.HERE, "tapes")
F = {}
for m, s in S.items():
    fn = f"{TD}/{m}.json"
    if not os.path.exists(fn): continue
    d = blib.jl(fn); c = U[m]; t = TB[m]
    cidx = c.get("cidx") or 0
    w4slot, w4idx = c.get("w4bslot"), c.get("w4bidx")
    b_n = b_q = l_n = l_q = 0; users = set()
    for sig, tr in d["tr"].items():
        for x in tr:
            slot, idx, k, user, buy, q, tok, vt, vq, ix, bt = x
            if slot != c["cslot"] or not buy or user in (c["creator"], c["user"], blib.W4) or sig == c["csig"]: continue
            if w4slot == c["cslot"] and w4idx is not None and idx is not None and idx > w4idx: continue
            v = 30.0 * (q or 0) / c["vquote"]
            if idx is not None and idx <= cidx + 5: b_n += 1; b_q += v
            else: l_n += 1; l_q += v
            users.add(user)
    F[m] = dict(b_n=b_n, b_sol=round(b_q, 3), l_n=l_n, l_sol=round(l_q, 3), n_users=len(users), n02=d["n02"])
blib.jdump(F, blib.OUT + "/slot.json")
def rate(name, f, buckets):
    print(f"\n== {name}: weighted creates / launch picks (rate), P1 | P2   (sampled coins with a tape)")
    for lab, lo, hi in buckets:
        line = f"  {lab:10s}"
        for pp in ("P1", "P2"):
            M = [m for m in F if S[m]["per"] == pp and lo <= f(F[m]) < hi]
            N = sum(S[m]["w"] for m in M); p = sum(S[m]["w"] for m in M if TB[m]["pick"])
            line += f" | {N:8.0f} {p:6.0f} ({p / N if N else 0:5.1%}) [n {len(M)}]"
        print(line)
B = [("0", 0, 1), ("1", 1, 2), ("2-3", 2, 4), ("4+", 4, 999)]
rate("bundle buys (within 5 txs of the create)", lambda x: x["b_n"], B)
rate("later buys in the create slot (before its own)", lambda x: x["l_n"], B)
rate("bundle SOL", lambda x: x["b_sol"], [("0", 0, 1e-9), ("<0.5", 1e-9, 0.5), ("0.5-2", 0.5, 2), ("2-5", 2, 5), ("5+", 5, 1e9)])
print("\n== inside R2: pick rate by bundle buys")
for lab, lo, hi in B:
    line = f"  {lab:10s}"
    for pp in ("P1", "P2"):
        M = [m for m in F if S[m]["per"] == pp and R2(TB[m]) and lo <= F[m]["b_n"] < hi]
        N = sum(S[m]["w"] for m in M); p = sum(S[m]["w"] for m in M if TB[m]["pick"])
        line += f" | {N:8.0f} {p:6.0f} ({p / N if N else 0:5.1%}) [n {len(M)}]"
    print(line)
