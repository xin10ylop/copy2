# The coin at its buy, for each copy of one wallet (Nov 24; the owner: "have you tried to analyze holders, bonding curve
# progress, market cap, top 10 holders ...?"). w3_robust.py's copies (its first buys of 0.5+ SOL, the cached coin paths,
# our copy landing at the end of the slot after its buy, 1 SOL, COST a round trip) with what the bot could know when its
# buy lands, read from its own trade event and the trades of its slot before it:
#   prog    curve progress: 1 - real tokens left / 793.1M (0 = launch, 1 = graduation)
#   mcap    market cap in SOL: the price its buy left x 1B tokens, at the quote's rate
#   bps     the curve's fee tier (protocol + creator) of its trade
#   size    its buy in SOL;  impact: its buy's quote over the curve's quote after it
#   ahead   other buyers in its slot before it
# and our result on each of the menu's exits (w3_robust.py's 8). Holders need the coin's trades from its launch: not here.
#   LK=SP/lk COST=0.0064 python3 -I f1_rows.py SP WALLET OUT.json
import sys, os, json
SP, W, OUTF = sys.argv[1], sys.argv[2], sys.argv[3]
TS = "/home/user/copy2/analysis/research/2026-11-20/tape_screen"
sys.argv = [sys.argv[0], SP, W, "0", "0", "14"]
src = open(f"{TS}/w2_grid.py").read().split("firsts.sort(key=lambda c: c[\"t\"]); h = len(firsts) // 2")[0]
g = {"__file__": f"{TS}/w2_grid.py", "__name__": "__main__", "OUTF": OUTF}
exec(compile(src, "w2_grid", "exec"), g)
exec(compile('''
MENU_EXITS = {"live (tp 4, 600 s, sp 5/60, stall 180, its early sale)": (4.0, 600, (5, 60), 180, 2),
              "live without its sale": (4.0, 600, (5, 60), 180, 0), "tp 2x / 120 s": (2.0, 120, None, 0, 0),
              "tp 1.5x / 60 s": (1.5, 60, None, 0, 0), "held 300 s": (None, 300, None, 0, 0), "its sale (to 600 s)": (None, 600, None, 0, 1),
              "tp 3x / 420 s / stall 240": (3.0, 420, None, 240, 0), "tp 2.5x / 300 s / sp 5/60": (2.5, 300, (5, 60), 0, 0)}
IDX = [np.ravel_multi_index((TP.index(tp), HOLD.index(h_), SPS.index(sp), STALL.index(st), it), SH) for tp, h_, sp, st, it in MENU_EXITS.values()]
_grid = grid
def grid(c, tr):
    r_ = _grid(c, tr)
    if not r_: return r_
    k = next(i for i, e in enumerate(tr) if e["user"] == W and e["buy"] and e["slot"] == c["slot"])
    e = tr[k]
    r_["g"] = [float(x) for x in r_["g"][IDX]]
    r_.update(m=c["m"], prog=(1 - e["real"] / 7.931e14) if e.get("real") is not None else None,
              mcap=e["vq"] / e["vt"] * 1e15 * c["rate"] / 1e9, bps=e.get("bps"), size=c["sol"],
              impact=e["q"] / e["vq"] if e["vq"] else None,
              ahead=sum(1 for x in tr[:k] if x["slot"] == c["slot"] and x["buy"] and x["user"] != W), prem=float(r_["prem"]))
    return r_
firsts.sort(key=lambda c: c["t"])
rows = []
for i in range(0, len(firsts), 30):
    rows += fetch(firsts[i:i + 30])
rows.sort(key=lambda r_: r_["t"])
json.dump(dict(wallet=W, exits=list(MENU_EXITS), rows=rows), open(OUTF, "w"))
print(f"{W[:8]}: {len(rows)} copies of {len(firsts)} first buys of 0.5+ SOL -> {OUTF}")
''', "f1", "exec"), g)
