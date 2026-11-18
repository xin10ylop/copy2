# Tracking two candidates that went quiet (the owner, Nov 18: "check if they are using other wallets, track"):
# B4BMZH3T (last pump trade Nov 16 08:13 UTC) and 8QzUkGJi (last transaction Nov 16 21:41 UTC). Their newest transactions
# (up to PAGES pages of 1,000): per day, what they did (pump trades, other programs), and every SOL move of 0.1+ SOL in or
# out with the other side, so a new wallet funded from the old one shows. RPC from RPC_URL, never printed.
#   RPC_URL=... LK=SP/track/lk python3 -I t1_flows.py SP WALLET... > out/t1_flows.txt
import sys, os, json, collections, datetime as d
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-13/tab_exits"); import lib
SP = sys.argv[1]; WS = sys.argv[2:]; PAGES = int(os.environ.get("PAGES", 3))
day = lambda t: d.datetime.fromtimestamp(t, d.UTC).strftime("%m-%d")
for w in WS:
    sigs, before = [], None
    for _ in range(PAGES):
        s = lib.sigs(w, before=before, limit=1000, cache=False)
        if not s: break
        sigs += [x for x in s if x.get("err") is None]; before = s[-1]["signature"]
        if len(s) < 1000: break
    with ThreadPoolExecutor(24) as ex: TX = list(ex.map(lambda x: (x, lib.tx(x["signature"])), sigs))
    act = collections.defaultdict(collections.Counter); moves = []
    for x, t in TX:
        if not t: continue
        dd = day(x["blockTime"]); ks = lib.keys_of(t); ev = lib.events(t)
        if any(k == "trade" and e.get("user") == w for k, e in ev): act[dd]["pump trade"] += 1
        else:
            progs = {ix.get("programId", "?")[:6] for ix in t["transaction"]["message"]["instructions"]}
            act[dd]["other: " + ",".join(sorted(progs - {"Comput", "111111"})) or "other: SOL only"] += 1
        if w in ks:
            i = ks.index(w); delta = (t["meta"]["postBalances"][i] - t["meta"]["preBalances"][i]) / 1e9
            if abs(delta) >= 0.1:
                # the other side: the account whose balance moved the opposite way the most
                others = [(abs((t["meta"]["postBalances"][j] - t["meta"]["preBalances"][j]) / 1e9), ks[j]) for j in range(len(ks)) if j != i]
                o = max(others)[1] if others else "?"
                moves.append((x["blockTime"], delta, o, ks[0] == w))
    print(f"\n== {w}: {len(sigs)} transactions read, {day(sigs[-1]['blockTime']) if sigs else '-'} to {day(sigs[0]['blockTime']) if sigs else '-'}")
    for dd in sorted(act): print(f"   {dd}: " + ", ".join(f"{k} {n}" for k, n in act[dd].most_common(4)))
    print("   SOL moves of 0.1+ (UTC, change, the other side, it signed):")
    for t, dl, o, signed in sorted(moves)[-25:]:
        print(f"      {d.datetime.fromtimestamp(t, d.UTC):%m-%d %H:%M}  {dl:+9.3f}  {o}  {'yes' if signed else 'no'}")
