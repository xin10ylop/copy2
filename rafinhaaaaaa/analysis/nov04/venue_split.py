# The fixed rule (its 5.0+ SOL buys, 1 SOL, 300 s or behind its first sale, K = 2) by the venue of its buy
import sys, os, json, collections, subprocess
F = os.path.dirname(os.path.abspath(__file__))
ch = json.load(open(f"{F}/chain/Hn6vBWWySnxA8XjxRQDEmZEuH5QL7KqosnJGcLcUzFJ6.json"))
for fn in sys.argv[1:]:
    d = json.load(open(fn)); c = collections.Counter(); 
    for t in d["trips"]:
        cc = ch.get(t["sig0"]) or {}; s = -(cc.get("sol") or 0)
        if s < 5.0: continue
        v = "/".join(x for x in (cc.get("venue") or []) if x not in ("Axiom router",)) or "?"
        c[v] += 1
    print(os.path.basename(fn), dict(c.most_common()))
