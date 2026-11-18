# Who trades a ladder coin in the 30 s after our entry (the owner, Nov 18: "is the whole ladder doing that?"). For the
# live ladder coins (SP/fwd_ladder.json) and, for comparison, the 108 coins of the +51% period (Nov 17 13:49 on, the
# ladder wallets' studied copies, SP/winners/study_*_pm.json): per coin, the traders in the 30 s after the entry slot
# (the first trade after the create slot + 1): the ladder's own wallets, wallets seen on 3+ ladder coins of the same set
# (a cross-coin bot), and the rest (one-off traders: real followers); their buys, sells and SOL.
#   python3 -I f2_who.py SP > out/f2_who.txt
import sys, os, json, glob, gzip, collections, datetime as d
SP = sys.argv[1]; S0 = 1794923340
def path(slot, m):
    f = glob.glob(f"{SP}/winners/cpaths/{slot}_{m}.json.gz") + glob.glob(f"{SP}/winners/cpaths_s/{slot}_{m}.json.gz")
    return json.load(gzip.open(f[0])) if f else None
def coins_live():
    for c in json.load(open(f"{SP}/fwd_ladder.json")):
        yield c["m"], c["slot"], c["t"], set(c["lad"])
def coins_past():
    seen = set(); SIZES = (1.10, 1.54, 2.18)
    for w in ("AsDCYFPT", "4sgdNABj", "64Dn57gX", "H2nsBdjF", "EhS8bGVC", "Gf9gk8sZ"):
        f = f"{SP}/winners/study_{w}_pm.json"
        if not os.path.exists(f): continue
        h = json.load(open(glob.glob(f"{SP}/winners/hist/{w}*.json")[0] if glob.glob(f"{SP}/winners/hist/{w}*.json") else glob.glob(f"{SP}/track/fwd/old_{w}*.json")[0]))
        slot_of = {e["m"]: e["slot"] for e in h["trades"] if e["buy"]}
        for r in json.load(open(f)):
            if r["refused"] or r["t"] < S0 or r["m"] in seen or r["m"] not in slot_of: continue
            seen.add(r["m"]); tr = path(slot_of[r["m"]], r["m"])
            if not tr: continue
            s0 = slot_of[r["m"]]; lad = {e["user"] for e in tr if e["slot"] == s0 and e["buy"] and any(abs(e["q"] / 1e9 - s) <= 0.005 for s in SIZES)}
            yield r["m"], s0, r["t"], lad
def study(name, coins):
    rows = []; seen_on = collections.Counter()
    for m, s0, t, lad in coins:
        tr = path(s0, m)
        if not tr: continue
        i = next((j for j, e in enumerate(tr) if e["slot"] > s0 + 1), None)
        if i is None: continue
        w = [e for e in tr[i + 1:] if e["t"] - tr[i]["t"] <= 30]
        users = {e["user"] for e in w}
        for u in users: seen_on[u] += 1
        rows.append((m, t, lad, w, tr[i], users))
    bots = {u for u, n in seen_on.items() if n >= 3}
    print(f"\n== {name}: {len(rows)} coins; wallets trading 3+ of these coins in their 30 s (cross-coin bots): {len(bots)}")
    tot = collections.Counter()
    for m, t, lad, w, ent, users in sorted(rows, key=lambda r: r[1]):
        k = collections.Counter(); sol = collections.Counter()
        for e in w:
            g = "ladder" if e["user"] in lad else ("bot" if e["user"] in bots else "other")
            k[g + (" buy" if e["buy"] else " sell")] += 1; sol[g] += (e["q"] if e["buy"] else -e["q"]) / 1e9
        hi = max([e["vq"] / e["vt"] for e in w], default=0) / (ent["vq"] / ent["vt"])
        tot.update(k)
        others = len({e["user"] for e in w if e["user"] not in lad and e["user"] not in bots})
        print(f"   {d.datetime.fromtimestamp(t, d.UTC):%m-%d %H:%M} {m[:8]} | ladder {k['ladder buy']:2d}b/{k['ladder sell']:2d}s {sol['ladder']:+6.2f} | bots {k['bot buy']:3d}b/{k['bot sell']:3d}s {sol['bot']:+6.2f} | others ({others:3d} wallets) {k['other buy']:3d}b/{k['other sell']:3d}s {sol['other']:+6.2f} SOL | high {hi:4.2f}x")
    n = max(1, len(rows)); print(f"   per coin: ladder {tot['ladder buy'] / n:.1f}b/{tot['ladder sell'] / n:.1f}s, bots {tot['bot buy'] / n:.1f}b/{tot['bot sell'] / n:.1f}s, others {tot['other buy'] / n:.1f}b/{tot['other sell'] / n:.1f}s")
    print("   the busiest cross-coin bots:", [(u[:8], n) for u, n in seen_on.most_common(6)])
study("LIVE (Nov 18 01:34-01:46 UTC)", coins_live())
study("THE +51% PERIOD (Nov 17 13:49 - Nov 18 ~00:50 UTC)", coins_past())
