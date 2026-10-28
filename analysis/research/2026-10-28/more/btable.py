# The part-B table per pay token: its class-E buys of 1.45+ SOL (quotes.json: count, its net P1 / P2), the PumpSwap pools
# from wSOL and WBTC (pools.py: canonical or not, the deepest one's SOL side and a 1 SOL hop's impact), and what our
# route would need. multi_hop_swap takes canonical pools only (sim_pool.py: "OnlyPumpPools"), so only a canonical pool
# makes a buy routable.   python3 -I btable.py [N]
import sys, json, collections
SPX = "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/more"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 14
Qs = [q for q in json.load(open(f"{SPX}/quotes.json")) if q["cls"] == "E"]
RT = json.load(open(f"{SPX}/routes.json")); PL = json.load(open(f"{SPX}/pools.json"))["tokens"]
SYM = {"pumpCmXq": "PUMP", "CARDSccU": "CARDS", "A7bdiYdS": "ZEC (A7bd)", "TTWofwAg": "TTWO", "WXMRyRZh": "XMR (WXMR)",
       "SPCXxcqX": "SPCX", "Pren1FvF": "Pren1F", "EPjFWdd5": "USDC", "7vfCXTUX": "WETH", "DJTu7vi8": "DJTu"}
g = collections.defaultdict(list)
for q in Qs: g[q["pay"]].append(q)
print("| paid in | buys | P1 its net | P2 its net | its route | wSOL pools (canonical) | deepest SOL side | 1 SOL impact | WBTC pools | routable (2 hops) |")
print("|---|---|---|---|---|---|---|---|---|---|")
for t, v in sorted(g.items(), key=lambda kv: -len(kv[1]))[:N]:
    p = PL.get(t) or {}; ws = (p.get("pools") or {}).get("wsol") or []; wb = (p.get("pools") or {}).get("wbtc") or []
    hops = collections.Counter(len((RT.get(q["sig"]) or {}).get("hops") or []) for q in v)
    route = ", ".join(f"{'direct' if n == 0 else f'{n}-hop'} {c}" for n, c in sorted(hops.items()))
    a = [q for q in v if q["per"] == "P1"]; b = [q for q in v if q["per"] == "P2"]
    canon = p.get("canonical_wsol") or p.get("canonical_wbtc")
    best = ws[0]["sol_side"] if ws else None
    print(f"| {SYM.get(t[:8], t[:8])} | {len(v)} | {sum(q['net'] or 0 for q in a):+.2f} ({len(a)}) | {sum(q['net'] or 0 for q in b):+.2f} ({len(b)}) | "
          f"{route} | {len(ws)} ({'yes' if p.get('canonical_wsol') else 'no'}) | "
          f"{best:.1f} | {1 / (best + 1):.1%} | {len(wb)} ({'yes' if p.get('canonical_wbtc') else 'no'}) | {'yes' if canon else 'no'} |" if best else
          f"| {SYM.get(t[:8], t[:8])} | {len(v)} | {sum(q['net'] or 0 for q in a):+.2f} ({len(a)}) | {sum(q['net'] or 0 for q in b):+.2f} ({len(b)}) | "
          f"{route} | {len(ws)} ({'yes' if p.get('canonical_wsol') else 'no'}) | - | - | {len(wb)} ({'yes' if p.get('canonical_wbtc') else 'no'}) | {'yes' if canon else 'no'} |")
rest = sorted(g.items(), key=lambda kv: -len(kv[1]))[N:]
print(f"| {len(rest)} other tokens | {sum(len(v) for _, v in rest)} | | | | canonical: {sum(1 for t, _ in rest if (PL.get(t) or {}).get('canonical_wsol'))} | | | | |")
