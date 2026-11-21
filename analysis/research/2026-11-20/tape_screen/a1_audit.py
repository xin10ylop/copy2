# Audit of the screen's copy model against the live bot (Nov 20; the owner: "make sure it is producing copies correctly,
# take a small example and audit it"). The cloud tape (Nov 19 17:22 - 20:17 UTC) holds three coins the bot really
# traded (wallet 4's buys; the bot's journal, Nov 19, stake 0.75 SOL): #136 xqHGK1A7 its_sell after 179 s, -38.5%;
# #137 G7yni4nJ sell_pressure after 105 s, -9.1%; #138 EtawWmoE filled +10.2% over its price, sell_pressure after 63 s,
# +10.7%. The screen's model on the same buys, step by step.
#   python3 -I a1_audit.py TAPE_DIR
import sys, numpy as np, datetime as dt
src = open("s1_screen.py").read(); exec(src.split("n_rows = 0; wid = 0")[0])
LIVE = {"xqHGK1A7": ("its_sell", 179, -38.5), "G7yni4nJ": ("sell_pressure", 105, -9.1), "EtawWmoE": ("sell_pressure", 63, 10.7)}
tr_of = {k: [] for k in LIVE}; mint_of = {}
for r in rows():
    p8 = r["mint"][:8]
    if p8 in LIVE: tr_of[p8].append((tup(r), r)); mint_of[p8] = r["mint"]
for p8, (why, held, pct) in LIVE.items():
    tr = [t for t, _ in tr_of[p8]]; raw = [r for _, r in tr_of[p8]]
    k = next(i for i, e in enumerate(tr) if e[2] == W4 and e[3]); rate = RATE.get(raw[k]["quote_mint"])
    s0 = tr[k][0]; j = k
    while j + 1 < len(tr) and tr[j + 1][0] <= s0 + 1: j += 1
    prem = (tr[k][5] / tr[j][5]) ** 2
    print(f"\n{p8}: quote {raw[k]['quote_mint'][:8]}, its buy {raw[k]['quote_amount'] * rate / 1e9:.3f} SOL at slot {s0} "
          f"({dt.datetime.fromtimestamp(tr[k][1], dt.UTC):%H:%M:%S}); {len(tr) - k - 1} trades after it on the tape")
    print(f"  our landing: the end of slot {tr[j][0]} (trade {j - k} after its buy); our price {prem:.3f}x its price (the bot's journal: +10.2% on #138)")
    m = model(tr, k, rate, W4)
    print(f"  model, % of the stake: " + "  ".join(f"{e} {100 * v / STAKE:+.1f}%" for e, v in m.items()) + f"   | LIVE: {why} after {held} s, {pct:+.1f}%")
    # when the live exit's triggers fire in the model
    rest = tr[j + 1:]; age = np.array([e[1] - tr[k][1] for e in rest]); px = (tr[k][5] / np.array([e[5] for e in rest], float)) ** 2
    its = next((age[i] for i, e in enumerate(rest) if e[2] == W4 and not e[3]), None)
    other = np.array([e[2] != W4 for e in rest]); sell = np.array([not e[3] for e in rest])
    s = np.concatenate([[0], np.cumsum(other & sell)]); b = np.concatenate([[0], np.cumsum(other & ~sell)])
    lo = np.searchsorted(age, age - 60, side="left"); spi = first(((s[1:] - s[lo]) - (b[1:] - b[lo]) >= 5) & (age >= 30))
    print(f"  model triggers: its first sale at {its} s; sell pressure at {age[spi] if spi is not None else None} s (price {px[spi] if spi is not None else 0:.2f}x); "
          f"peak {px.max():.2f}x; tape gap check: trades' ages {age[:5].tolist()} ...")
