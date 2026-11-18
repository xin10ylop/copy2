# Wallet 4's look-alikes, found directly by what they ARE (Nov 18, the owner: "find wallets that are making the same
# amount of SOL, filter directly in the search: it also buys floats, holds the coin..."). No copy model at this step:
# every wallet's OWN trading on every coin in the 4 days of paths on disk (paths_full: each coin's first ~40 minutes),
# its first buys of 0.5+ SOL on coins priced in another token. Per wallet: coins, SOL in, its own result (sales + what
# it still holds at the coin's last price in the path, 0.9 of it), the result without its best 2 coins, coins won, days
# active and days positive, how long it holds (first buy to first sale), the share of its sales on one fixed delay (a
# timer bot like TAB16RxX), the share bought in the coin's create slot (a bundler), the share on float-quoted coins.
# Wallet 4 is printed as the yardstick. Wallet-4-like = the filters at the end.
#   python3 -I p1_profile.py SP > ../out/p1_profile.txt
import sys, os, json, gzip, collections, statistics as st, datetime as dt
from multiprocessing import Pool
SP = sys.argv[1]; O = f"{SP}/market"; PD = f"{O}/paths_full"; MINSOL = float(os.environ.get("MINSOL", 0.5)); HOLDMIN = float(os.environ.get("HOLDMIN", 90)); MINN = int(os.environ.get("MINN", 15))
W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"; WSOL = "So11111111111111111111111111111111111111112"
FLOATS = ("3NZ9JMVB", "pumpCmXq", "SPCXxcqX", "TTWofwAg", "DJTu7vi8", "98sMhvDw", "XsbEhLAt")
L = {}
for f_ in (f"{O}/launches_1794618422.json", f"{O}/launches.json", f"{O}/launches_1794877622.json"):
    L.update({m: x for m, x in json.load(open(f_)).items() if x and os.path.exists(f"{PD}/{m}.json.gz")})
PR = json.load(open(f"{O}/prices.json")); su = PR[WSOL]["usdPrice"]
rate_of = lambda q: PR[q]["usdPrice"] / su * 1e9 / 10 ** PR[q]["decimals"] if q in PR else None
def coin(m):
    x = L[m]; q = x["quote"]
    if q in (WSOL, None) or q.startswith("1111"): return []
    r = rate_of(q)
    if r is None: return []
    try: tr = json.load(gzip.open(f"{PD}/{m}.json.gz"))
    except Exception: return []
    if not tr: return []
    led = {}; s0 = tr[0]["slot"]; last = tr[-1]; px = last["vq"] / last["vt"]
    for e in tr:
        u = e["user"]; d = led.get(u)
        if d is None:
            if not e["buy"]: continue
            d = led[u] = dict(t=e["t"], slot=e["slot"], inn=0.0, out=0.0, tok=0, first_sell=None)
        sol = e["q"] * r / 1e9
        if e["buy"]: d["inn"] += sol * (1 + e["bps"] / 1e4); d["tok"] += e["tok"]
        else:
            d["out"] += sol * (1 - e["bps"] / 1e4); d["tok"] -= e["tok"]
            if d["first_sell"] is None: d["first_sell"] = e["t"]
    out = []
    for u, d in led.items():
        if d["inn"] < MINSOL or last["t"] - d["t"] < 600: continue
        held = max(0, d["tok"]) * px * r / 1e9 * 0.9
        out.append((u, dict(m=m, t=d["t"], inn=d["inn"], pnl=d["out"] + held - d["inn"], hold=(d["first_sell"] - d["t"]) if d["first_sell"] else None,
                            cslot=d["slot"] == s0, flt=q[:8] in FLOATS)))
    return out
if __name__ == "__main__":
    W = collections.defaultdict(list)
    with Pool(4) as p:
        for rows in p.imap_unordered(coin, list(L), chunksize=20):
            for u, r in rows: W[u].append(r)
    def prof(u, cs):
        cs = sorted(cs, key=lambda c: c["t"]); p = sorted((c["pnl"] for c in cs), reverse=True); h = [c["hold"] for c in cs if c["hold"] is not None]
        days = collections.defaultdict(float)
        for c in cs: days[dt.datetime.fromtimestamp(c["t"], dt.UTC).strftime("%m-%d")] += c["pnl"]
        mode = collections.Counter(round(x / 10) for x in h).most_common(1)
        return dict(u=u, n=len(cs), inn=sum(c["inn"] for c in cs), pnl=sum(p), pnl2=sum(p[2:]), won=sum(x > 0 for x in p) / len(p),
                    days=len(days), dpos=sum(v > 0 for v in days.values()), hold=st.median(h) if h else None, timer=mode[0][1] / len(h) if h else 0,
                    quick=sum(x <= 10 for x in h) / len(h) if h else 0, cslot=sum(c["cslot"] for c in cs) / len(cs), flt=sum(c["flt"] for c in cs) / len(cs),
                    held=1 - len(h) / len(cs))
    P = [prof(u, cs) for u, cs in W.items() if len(cs) >= 5 or u == W4]
    def line(r):
        return (f"{r['u'][:8]} {r['n']:4d} {r['inn']:7.1f} {r['pnl']:+7.2f} {r['pnl2']:+7.2f} {100 * r['won']:4.0f}% {r['days']}/{r['dpos']} "
                f"{r['hold'] if r['hold'] is not None else -1:6.0f} {100 * r['timer']:4.0f}% {100 * r['quick']:4.0f}% {100 * r['cslot']:4.0f}% {100 * r['flt']:4.0f}% {100 * r['held']:4.0f}%")
    hdr = "wallet   coins  SOL in   result  w/o 2 best  won days/+ hold_s timer  <=10s cslot float  never sold"
    print(f"{len(L)} coins, {len(W)} wallets with a first buy of 0.5+ SOL on an other-token coin; {len(P)} with 5+ coins")
    print("\nTHE YARDSTICK, wallet 4:\n" + hdr); print(line(next(r for r in P if r["u"] == W4)))
    # calibrated on wallet 4 itself (Nov 18): it holds a median 180 s, sells 3% within 10 s, buys 53% in the create
    # slot; a copy arrives seconds late, so a wallet that is out in 20-30 s leaves nothing to copy
    json.dump(P, open(f"{O}/p1_all_{MINSOL}_{HOLDMIN:.0f}_{MINN}.json", "w"))
    like = [r for r in P if r["n"] >= MINN and r["days"] >= 3 and r["pnl"] > 0 and r["pnl2"] > 0 and r["dpos"] >= 2 and r["hold"] is not None and HOLDMIN <= r["hold"] <= 1200
            and r["timer"] < 0.5 and r["quick"] < 0.1 and r["flt"] >= 0.5]
    print(f"\nWALLET-4-LIKE ({len(like)}; buys of {MINSOL}+ SOL): {MINN}+ coins on 3+ of the 4 days, its own result positive and without its best 2 coins, positive on 2+ days,"
          f" holds {HOLDMIN:.0f}-1200 s (median; wallet 4 180), no fixed timer (under 50% of sales on one 10 s delay), under 10% sold within 10 s (wallet 4 3%),"
          f" the create slot allowed (wallet 4 53%), half or more on float-quoted coins; by the result without its best 2:\n" + hdr)
    for r in sorted(like, key=lambda r: -r["pnl2"])[:40]: print(line(r))
    json.dump(sorted(like, key=lambda r: -r["pnl2"]), open(f"{O}/p1_like_{MINSOL}_{HOLDMIN:.0f}_{MINN}.json", "w"))
    print("\nFOR SCALE, the 15 biggest own results among all wallets with 15+ coins (no behaviour filter):\n" + hdr)
    for r in sorted([r for r in P if r["n"] >= 15], key=lambda r: -r["pnl2"])[:15]: print(line(r))
