# Attention study, narrative bursts and the create signals together (every launch of the 48 h, a4_create_tx.py ALL=1).
# A theme word: a word of 3+ letters of the name or the ticker, lower case, minus generic ones. A coin's burst: how many
# other launches in the 30 min before it shared a theme word (news makes many creators launch the same theme within
# minutes); and whether it is the first of its theme in the hour. Then the create signals (mayhem, tips, dev buy, the
# creator's first launch of the day) and a score of the signals picked on the first 24 h, scored on the second.
#   python3 -I a7_bursts.py SP > out/a7_bursts.txt
import sys, os, re, json, bisect, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import creates
SP = sys.argv[1]; CR = creates.load(SP); OUT = json.load(open(f"{SP}/attn/outcomes.json")); D = json.load(open(f"{SP}/attn/create_tx_all.json"))["rows"]
GEN = set("the coin token inu sol solana pump fun meme memes official real new first just token2022 of and for with you your this that are not has its".split())
words = lambda s: {w for w in re.findall(r"[a-z0-9]+", (s or "").lower()) if len(w) >= 3 and w not in GEN}
L = []
for m, (s, v) in CR.items():
    f = D.get(m)
    if not f or not OUT.get(m): continue
    L.append(dict(m=m, t=v["t"], creator=v["creator"], grad=OUT[m][0], w=words(f["name"]) | words(f["symbol"]), mayhem=f["mayhem"], tips=f["transfers"],
                  dev=f["dev_buy"], payer_is_creator=f["user"] == f["creator"], sol=v["quote"] == "11111111111111111111111111111111"))
L.sort(key=lambda v: v["t"]); T = [v["t"] for v in L]; MID = L[0]["t"] + 86400
idx = collections.defaultdict(list)
for i, v in enumerate(L):
    for w in v["w"]: idx[w].append(i)
by_c = collections.defaultdict(list)
for v in L: by_c[v["creator"]].append(v["t"])
for i, v in enumerate(L):
    n30 = set(); first = True
    for w in v["w"]:
        J = idx[w]; k = bisect.bisect_left(J, i)
        for j in J[max(0, k - 400):k]:
            dt = v["t"] - L[j]["t"]
            if dt <= 1800: n30.add(j)
            if dt <= 3600: first = False
    v["burst"] = len(n30); v["first_theme"] = first and bool(v["w"])
    v["first_launch"] = not any(v["t"] - 86400 < t < v["t"] for t in by_c[v["creator"]])
A = [v for v in L if v["t"] < MID]; B = [v for v in L if v["t"] >= MID]
g = lambda X: sum(v["grad"] for v in X) / max(1, len(X))
print(f"{len(L)} launches read; graduated {g(L):.2%}; first 24 h {len(A)} ({g(A):.2%}), second {len(B)} ({g(B):.2%})")
def show(name, key):
    G = collections.defaultdict(lambda: [[], []])
    for v in A: G[key(v)][0].append(v)
    for v in B: G[key(v)][1].append(v)
    print(f"\n{name}:")
    for k in sorted(G, key=str):
        a, b = G[k]; print(f"   {str(k):26s} first 24 h {len(a):6d} {g(a):7.2%} | second 24 h {len(b):6d} {g(b):7.2%}  (x{g(b) / max(g(B), 1e-9):4.1f})")
cut = lambda x, cs: next((f"<= {c:g}" for c in cs if x <= c), f"> {cs[-1]:g}")
show("same-theme launches in the 30 min before", lambda v: cut(v["burst"], [0, 2, 5, 15, 50]))
show("first of its theme in the hour", lambda v: v["first_theme"])
show("mayhem", lambda v: v["mayhem"])
show("tips in the create", lambda v: cut(v["tips"], [0, 0.001, 0.01]))
show("dev buy (SOL)", lambda v: cut(v["dev"], [0, 0.5, 2, 5]))
show("payer is the creator", lambda v: v["payer_is_creator"])
show("creator's first launch of the day", lambda v: v["first_launch"])
# the signals together: each is kept as "good" on the first 24 h if its group beats the base there; the score counts them
sig = {"no mayhem": lambda v: not v["mayhem"], "no tips": lambda v: v["tips"] == 0, "dev buy > 2": lambda v: v["dev"] > 2,
       "first launch": lambda v: v["first_launch"], "burst 1-15": lambda v: 1 <= v["burst"] <= 15}
keep = [k for k, f in sig.items() if g([v for v in A if f(v)]) > g(A)]
print(f"\nsignals kept on the first 24 h: {keep}")
show("score: how many kept signals", lambda v: sum(sig[k](v) for k in keep))
