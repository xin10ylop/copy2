# Attention study, H7 step 3: each field of the create transaction (a4_create_tx.py), wallet 4's coins against the
# random others of the same hours: the share of each, and how many graduated. A field that separates them is a
# candidate for "what wallet 4 reads"; it is then picked on the first 24 h and scored on the second (a6).
#   python3 -I a5_create_features.py SP > out/a5_create_features.txt
import sys, json, collections, urllib.parse
SP = sys.argv[1]; D = json.load(open(f"{SP}/attn/create_tx.json")); OUT = json.load(open(f"{SP}/attn/outcomes.json"))
mine = set(D["mine"]); R = {m: v for m, v in D["rows"].items() if v}
for m, v in R.items(): v["grad"] = OUT[m][0]; v["w4"] = m in mine
Y = [v for v in R.values() if v["w4"]]; N = [v for v in R.values() if not v["w4"]]
g = lambda X: sum(v["grad"] for v in X) / max(1, len(X))
print(f"read: wallet 4's coins {len(Y)} (graduated {g(Y):.2%}), others {len(N)} (graduated {g(N):.2%})")
def bins(x, cuts):
    if x is None: return "none"
    for c in cuts:
        if x <= c: return f"<= {c:g}"
    return f"> {cuts[-1]:g}"
def show(name, key):
    k = collections.defaultdict(lambda: [[], []])
    for v in Y: k[key(v)][0].append(v)
    for v in N: k[key(v)][1].append(v)
    print(f"\n{name}: share of w4's | share of others | graduated: w4's | others")
    for a, (y, n) in sorted(k.items(), key=lambda x: -len(x[1][0]) - len(x[1][1])):
        if len(y) + len(n) < 20: continue
        print(f"   {str(a)[:34]:34s} {len(y) / len(Y):6.1%} | {len(n) / len(N):6.1%} | {g(y):6.2%} ({len(y):4d}) | {g(n):6.2%} ({len(n):4d})")
show("dev buy in the create (SOL)", lambda v: bins(v["dev_buy"], [0, 0.1, 0.5, 1, 2, 5]))
show("other buyers inside the create transaction", lambda v: bins(v["n_buyers"] - (v["dev_buy"] > 0), [0, 1, 3]))
show("fee payer's SOL before", lambda v: bins(v["payer_sol"], [0.05, 0.2, 0.5, 1, 3, 10, 100]))
show("transaction fee (SOL)", lambda v: bins(v["fee"], [0.000005, 0.00005, 0.0005, 0.005]))
show("compute unit price (micro-lamports)", lambda v: bins(v["cu_price"], [0, 1000, 100000, 1000000, 10000000]))
show("SOL transfers inside (tips etc.)", lambda v: bins(v["transfers"], [0, 0.0001, 0.001, 0.01, 0.1]))
show("instructions", lambda v: bins(v["n_ix"], [2, 3, 4, 5, 7, 10]))
show("signers", lambda v: v["n_sig"])
show("programs called", lambda v: ",".join(p[:6] for p in v["progs"] if p not in ("ComputeBudget111111111111111111111111111111", "11111111111111111111111111111111")))
show("mayhem", lambda v: v["mayhem"]); show("cashback", lambda v: v["cashback"]); show("creator fee bps", lambda v: v["cfee"])
show("token program", lambda v: (v["tprog"] or "none")[:8])
show("metadata host", lambda v: urllib.parse.urlparse(v["uri"] or "").netloc[:30] or "none")
show("payer is the creator", lambda v: v["user"] == v["creator"])
show("name length", lambda v: bins(len(v["name"] or ""), [3, 6, 10, 16, 24]))
show("ticker", lambda v: "upper" if (v["symbol"] or "").isupper() else ("lower" if (v["symbol"] or "").islower() else "mixed/other"))
