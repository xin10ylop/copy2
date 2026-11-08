# Per coin: its first buy (size = whole SOL change), more buys, sales, its SOL result, time to first sale (chain)
#   python3 -I coins.py ROWS_JSON [SINCE_UNIX]
import json, sys, datetime, collections
rows = json.load(open(sys.argv[1])); since = int(sys.argv[2]) if len(sys.argv) > 2 else 0
by = collections.OrderedDict()
for r in rows:
    if r["ncoins"] > 1: continue                   # multi-coin transactions (routing) left out
    by.setdefault(r["mint"], []).append(r)
f = lambda t: datetime.datetime.fromtimestamp(t, datetime.UTC).strftime("%m-%d %H:%M")
print(f"{'first buy UTC':12} {'coin':8} {'venue':28} {'1st SOL':>7} {'buys':>4} {'in SOL':>7} {'out SOL':>7} {'net':>7} {'x':>5} {'1st sale s':>9} {'sales':>5}")
tot = collections.defaultdict(float)
for m, rs in by.items():
    b = [r for r in rs if r["side"] == "buy"]
    if not b or b[0]["t"] < since: continue
    s = [r for r in rs if r["side"] == "sell" and r["t"] >= b[0]["t"]]
    sin = sum(-r["sol"] for r in b if r["sol"] < 0); sout = sum(r["sol"] for r in s if r["sol"] > 0)
    usd = any(r["stab"] for r in b)
    first = -b[0]["sol"]
    ven = "/".join(v for v in b[0]["venue"] if v not in ("Axiom router",))
    fs = (s[0]["t"] - b[0]["t"]) if s else None
    print(f"{f(b[0]['t']):12} {m[:8]} {ven[:28]:28} {first:7.2f} {len(b):4} {sin:7.2f} {sout:7.2f} {sout - sin:+7.2f} {sout / sin if sin else 0:5.2f} {fs if fs is not None else '-':>9} {len(s):5}" + ("  USDC" if usd else ""))
    k = "5.1+" if first >= 5.1 else "3-5.1" if first >= 2.9 else "<2.9"
    tot[(k, "n")] += 1; tot[(k, "net")] += sout - sin
print({k: round(v, 2) for k, v in tot.items()})
