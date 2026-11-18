# Copy bots point to the wallets worth copying (Nov 18). The same-slot wallets (they buy wallet 4's coins in its slot)
# make money only on wallet 4's coins and lose on the rest (../../2026-11-17/wallet_hunt/out/m5_notw4_*.txt): they look
# like copy bots, and a copy bot follows a LIST of wallets. For each of their first buys (any coin, cached path), the
# "leader" = the wallets that bought the same coin in the same slot before it or in the 2 slots before (not the bot
# itself, not the coin's create-slot bundle). Leaders seen on 3+ of a bot's buys are its likely targets.
#   python3 -I l1_leaders.py SP BOT ... > out/l1_leaders.txt
import sys, os, json, glob, gzip, collections
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-18/churn"); import slot_order as SO
SP = sys.argv[1]; BOTS = sys.argv[2:]; W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
def path(slot, m):
    for d in ("cpaths_s", "cpaths"):
        f = f"{SP}/winners/{d}/{slot}_{m}.json.gz"
        if os.path.exists(f): return SO.reorder(json.load(gzip.open(f)))
    return None
allc = collections.Counter(); per = {}
for b in BOTS:
    h = json.load(open(glob.glob(f"{SP}/winners/hist/{b}*.json")[0])); first = {}
    for e in sorted(h["trades"], key=lambda e: e["t"]):
        if e["buy"]: first.setdefault(e["m"], e)
    c = collections.Counter(); n = 0
    for m, e in first.items():
        tr = path(e["slot"], m)
        if not tr: continue
        k = next((j for j, y in enumerate(tr) if y["user"] == b and y["buy"] and y["slot"] == e["slot"]), None)
        if k is None: continue
        s0 = tr[0]["slot"]; n += 1
        lead = {y["user"] for y in tr[:k] if y["buy"] and y["slot"] >= e["slot"] - 2 and y["slot"] > s0 and y["user"] != b}
        c.update(lead)
    per[b] = (n, c); allc.update({u: 1 for u in c if c[u] >= 3})
    print(f"\n== bot {b[:8]}: {n} of its first buys with a cached path; leaders seen on 3+ of them:")
    for u, k in c.most_common(12):
        if k < 3: break
        print(f"   {u}  {k:3d} ({100 * k / n:4.0f}%){'  <- wallet 4' if u == W4 else ''}")
print("\n== leaders shared by 2+ bots:", [(u[:8], k) for u, k in allc.most_common() if k >= 2])
json.dump(sorted({u for b, (n, c) in per.items() for u, k in c.items() if k >= 3 and u != W4}), open(f"{SP}/leaders.json", "w"))
