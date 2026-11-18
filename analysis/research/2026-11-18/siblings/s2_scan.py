# Wallet 4's siblings, step 2: every wallet's launch-window buys (the create slot to +2, not the creator) on the coins with
# trades on disk (SP/winners/paths: the week's graduations and the 48 h sample; SP/market/paths: the 48 h other-token
# coins), up to PER buy transactions a wallet (its newest first), each read and fingerprinted as in s1; a wallet's score =
# the share of its buys that match wallet 4's usual pattern on each trait (s1's most common value: the durable nonce, the
# unit limit, the tip amounts, the programs, the instruction count). Wallet 4 itself must score near 100%.
#   RPC_URL=... LK=SP/sib/lk python3 -I s2_scan.py SP [PER=6] > out/s2_scan.txt
import sys, os, json, gzip, glob, collections
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from s1_fingerprint import fp, lib
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-17/attention"); import creates
SP = sys.argv[1]; PER = int(sys.argv[2]) if len(sys.argv) > 2 else 6; W4 = lib.W4
CR = {m: v for m, (s, v) in creates.load(SP).items()}; meta = json.load(open(f"{SP}/winners/week_meta.json"))
cslot = {m: (v["slot"], v["creator"]) for m, v in CR.items()}; cslot.update({m: (v["slot"], v["creator"]) for m, v in meta.items()})
B = collections.defaultdict(list); nc = 0
for f in glob.glob(f"{SP}/winners/paths/*.json.gz") + glob.glob(f"{SP}/market/paths/*.json.gz"):
    m = os.path.basename(f)[:-8]
    if m not in cslot: continue
    s0, creator = cslot[m]; nc += 1
    try: tr = json.load(gzip.open(f))
    except Exception: continue
    seen = set()
    for e in tr:
        if e["slot"] - s0 > 2: break
        if e["buy"] and e["user"] not in seen and e["user"] != creator and e.get("sig"): B[e["user"]].append((e["t"], e["sig"]))
        seen.add(e["user"])
W = {u: sorted(v, reverse=True)[:PER] for u, v in B.items() if len(v) >= 3}
W[W4] = sorted(B.get(W4, []), reverse=True)[:PER * 3]
ref = json.load(open(f"{SP}/sib_w4_fp.json"))
mode = lambda k: collections.Counter(json.dumps(f[k]) for f in ref).most_common(1)[0][0]
REF = {k: mode(k) for k in ("nonce", "cu_limit", "progs", "n_ix")}; REF["tipamts"] = collections.Counter(json.dumps(sorted(a for a, _ in f["tips"])) for f in ref).most_common(1)[0][0]
print(f"{nc} coins read; {len(W)} wallets with 3+ launch-window buys; wallet 4's usual pattern: {REF}")
def one(u):
    out = []
    for t, sg in W[u]:
        try: x = lib.tx(sg)
        except Exception: continue
        if not x: continue
        f = fp(x); out.append({"nonce": json.dumps(f["nonce"]) == REF["nonce"], "cu_limit": json.dumps(f["cu_limit"]) == REF["cu_limit"],
                              "progs": json.dumps(list(f["progs"])) == REF["progs"] or json.dumps(f["progs"]) == REF["progs"], "n_ix": json.dumps(f["n_ix"]) == REF["n_ix"],
                              "tips": json.dumps(sorted(a for a, _ in f["tips"])) == REF["tipamts"]})
    return u, out
with ThreadPoolExecutor(24) as ex: R = dict(ex.map(one, list(W)))
rows = []
for u, out in R.items():
    if not out: continue
    sc = {k: sum(o[k] for o in out) / len(out) for k in out[0]}; rows.append((sum(sc.values()) / len(sc), u, len(B[u]), len(out), sc))
rows.sort(reverse=True)
print("score  wallet   | launch buys seen, read | nonce  cu_limit  programs  n_ix  tips")
for s, u, n, r, sc in rows[:40]:
    print(f"{s:5.0%}  {u[:8]} | {n:4d} {r:3d} | {sc['nonce']:4.0%} {sc['cu_limit']:6.0%} {sc['progs']:7.0%} {sc['n_ix']:6.0%} {sc['tips']:5.0%}{'  <- WALLET 4' if u == W4 else ''}")
json.dump([dict(u=u, score=s, n=n, read=r, sc=sc) for s, u, n, r, sc in rows], open(f"{SP}/sib_scan.json", "w"))
