# Attention study, step 2: H1-H3, what is known at the create (README). Every launch of the 48 h; the outcome is
# graduation (a1_outcomes.py). Pick on the first 24 h, score on the second. A creator's record counts only its coins
# created 2+ h before this one (an earlier coin's graduation time is not read; most graduate within the first hour,
# so 2 h keeps the look-ahead small: checked below with a 6 h variant).
#   python3 -I a2_create_time.py SP > out/a2_create_time.txt
import sys, json, collections, datetime, bisect
SP = sys.argv[1]
C = {v["mint"]: v for v in json.load(open(f"{SP}/market/creates.json")).values() if v}
OUT = json.load(open(f"{SP}/attn/outcomes.json"))
L = sorted((v for m, v in C.items() if OUT.get(m)), key=lambda v: v["t"])
for v in L: v["grad"] = OUT[v["mint"]][0]
T0 = L[0]["t"]; MID = T0 + 86400
SOL = "11111111111111111111111111111111"
print(f"{len(C)} creates, {len(L)} with a curve read; graduated {sum(v['grad'] for v in L)} ({sum(v['grad'] for v in L) / len(L):.2%})")
A = [v for v in L if v["t"] < MID]; B = [v for v in L if v["t"] >= MID]
rate = lambda X: (sum(v["grad"] for v in X) / len(X)) if X else 0.0
print(f"first 24 h: {len(A)} launches, {rate(A):.2%} graduated | second 24 h: {len(B)}, {rate(B):.2%}\n")
def table(name, key):
    ka = collections.defaultdict(list); kb = collections.defaultdict(list)
    for v in A: ka[key(v)].append(v)
    for v in B: kb[key(v)].append(v)
    print(f"{name}:")
    for k in sorted(set(ka) | set(kb), key=lambda k: (str(type(k)), k)):
        a, b = ka.get(k, []), kb.get(k, [])
        print(f"   {str(k):28s} first 24 h {len(a):6d} {rate(a):7.2%} | second 24 h {len(b):6d} {rate(b):7.2%}  (x{rate(b) / max(rate(B), 1e-9):4.1f} the base)")
    print()
# H2: the quote token
QN = collections.Counter(v["quote"] for v in L)
table("H2 the quote token", lambda v: "SOL" if v["quote"] == SOL else (v["quote"][:8] if QN[v["quote"]] >= 500 else "other token (small)"))
# H3: the hour (UTC)
table("H3 the hour (UTC, 4 h blocks)", lambda v: f"{datetime.datetime.fromtimestamp(v['t'], datetime.timezone.utc).hour // 4 * 4:02d}-{datetime.datetime.fromtimestamp(v['t'], datetime.timezone.utc).hour // 4 * 4 + 4:02d}")
# H1: the creator's record, its earlier coins only
by_c = collections.defaultdict(list)
for v in L: by_c[v["creator"]].append(v)
for GAP in (21600, 7200):   # 2 h last: the tables after use it
    for v in L:
        prev = [w for w in by_c[v["creator"]] if w["t"] < v["t"]]
        known = [w for w in prev if w["t"] <= v["t"] - GAP]
        v["n24"] = sum(1 for w in prev if w["t"] > v["t"] - 86400); v["kg"] = sum(w["grad"] for w in known); v["kn"] = len(known)
    table(f"H1 the creator's earlier coins graduated (known {GAP // 3600} h+ before)", lambda v: "none earlier" if v["kn"] == 0 else ("0 of its earlier" if v["kg"] == 0 else ("1 graduated" if v["kg"] == 1 else "2+ graduated")))
table("H1 the creator's launches in the 24 h before", lambda v: "0 (first)" if v["n24"] == 0 else ("1" if v["n24"] == 1 else ("2-4" if v["n24"] <= 4 else ("5-19" if v["n24"] <= 19 else "20+"))))
# the quote and the record together
table("H1 x H2", lambda v: ("SOL " if v["quote"] == SOL else "other ") + ("none earlier" if v["kn"] == 0 else ("0 graduated" if v["kg"] == 0 else "1+ graduated")))
