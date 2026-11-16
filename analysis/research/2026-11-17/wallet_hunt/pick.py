# Step 2's candidates, by a rule fixed before any of them was looked at closer (the lessons of Oct 29 and TAB16RxX):
# 20+ buys of 0.9+ SOL on wallet 4's coins over 8+ days; not a racer of wallet 4's own signal (under half of its buys
# in wallet 4's slot or the next: those are other copiers of it, they add no coins); it holds (median first sale 45+ s
# after its buy, under 40% sold within 30 s: a flipper's coins are sold before we land); and our copy of its buys on
# these coins does not lose. Nothing here says it picks well on its own: that is step 2, on its own coins.
#   python3 -I pick.py SP > out/pick.txt
import sys, json, gzip, datetime
import numpy as np
SP = sys.argv[1]; W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
W = json.load(gzip.open(f"{SP}/hunt_screen.json.gz")); out = []
for u, v in W.items():
    if u == W4 or len(v) < 20: continue
    days = len({datetime.datetime.fromtimestamp(x["t"], datetime.timezone.utc).date() for x in v})
    held = [x["held"] if x["held"] is not None else 1e9 for x in v]
    fol = sum(1 for x in v if x["lag"] <= 1) / len(v); fast = sum(1 for h in held if h < 30) / len(v); net = sum(x["net"] for x in v)
    ok = days >= 8 and fol < 0.5 and np.median(held) >= 45 and fast < 0.4 and net >= 0
    if ok: out.append((net, u, len(v), days, np.median(held), fast))
for net, u, n, d, h, f in sorted(out, reverse=True): print(f"{u} {n:4d} buys {d:2d} days held med {h:6.0f} s, under 30 s {100 * f:3.0f}%, our copy on wallet 4's coins {net:+6.2f}")
json.dump([u for _, u, *_ in sorted(out, reverse=True)], open(f"{SP}/hunt_cands.json", "w"))
print(len(out), "candidates")
