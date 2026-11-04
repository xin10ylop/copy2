# scan.out (examples/scan.rs over SPD/w4tx) -> SPD/routable.json: each 1.45+ SOL other-quote buy with its time, route
# verdict and route kind; and wallet 4's big native SOL moves (transfers in or out of 5+ SOL with no token change).
#   python3 -I build_rows.py SPD
import json, os, re, sys, datetime
SPD = sys.argv[1]; W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
bt = {}; moves = []
for f in os.listdir(f"{SPD}/w4tx"):
    t = json.load(open(f"{SPD}/w4tx/{f}")); bt[t["slot"]] = t["blockTime"]
    ks = t["transaction"]["message"]["accountKeys"] + (t["meta"].get("loadedAddresses") or {}).get("writable", [])
    i = ks.index(W4) if W4 in ks else None
    if i is None: continue
    d = (t["meta"]["postBalances"][i] - t["meta"]["preBalances"][i]) / 1e9
    tok = any(b.get("owner") == W4 for b in (t["meta"].get("postTokenBalances") or []) + (t["meta"].get("preTokenBalances") or []))
    if abs(d) >= 5 and not tok:
        others = [(ks[j], (t["meta"]["postBalances"][j] - t["meta"]["preBalances"][j]) / 1e9) for j in range(len(t["meta"]["postBalances"])) if j != i and abs(t["meta"]["postBalances"][j] - t["meta"]["preBalances"][j]) >= 1e9]
        moves.append((t["blockTime"], d, t["transaction"]["signatures"][0][:12], others))
rows = []
for l in open(f"{SPD}/scan.out"):
    m = re.match(r"(\d+) (\S{8}) ([\d.]+) SOL from (\S+) quote (\S+) jupiter (\S+): (ROUTABLE|no route)(.*)", l)
    if not m: continue
    s = int(m.group(1)); how = re.search(r'how: "([^"]+)"', l)
    rows.append(dict(slot=s, t=bt[s], mint8=m.group(2), sol=float(m.group(3)), frm=m.group(4), quote=m.group(5),
                     ok=m.group(7) == "ROUTABLE", how=how.group(1) if how else m.group(8).strip()[:40]))
json.dump(rows, open(f"{SPD}/routable.json", "w"))
f = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d %H:%M")
print(f"{len(rows)} buys of 1.45+ SOL priced in another token, {sum(r['ok'] for r in rows)} routable")
print("wallet 4's native SOL moves of 5+ SOL without a token change (Beirut time):")
for m in sorted(moves): print(f"  {f(m[0])} {m[1]:+.2f} SOL  {m[2]}  counterparties {[(a[:8], round(b, 2)) for a, b in m[3]]}")
