# How big is the sell-pressure gain against chance? (Nov 23; the owner: "on ttt, rrr and www it looks better, what do you
# mean within the noise"). The same copies under no sell pressure and under each kind (w3_sp_check.py's menu), the
# blind blocks, the coins the unit copies: the mean gain a copy, its standard error (paired: the same coins both ways),
# and how often the gain survives a reshuffle of which copies the sample drew (bootstrap, 2,000 draws).
#   RPC_URL=... LK=SP/lk COST=0.0064 KIND=token|all python3 -I w3_sp_noise.py SP WALLET
import sys, os
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "w3_robust.py")).read()
a, b = src.split("MENU_EXITS = {", 1); b = b.split("}\n", 1)[1]
SPL = [None, (3, 30), (3, 60), (5, 30), (5, 60), (5, 120), (8, 60), (10, 60), (15, 60), (15, 120)]
menu = "MENU_EXITS = {" + ", ".join(f'"{sp}": (3.0, 420, {sp}, 240, 0)' for sp in SPL) + "}\n"
src = (a + menu + b).split("real = rolling(G)")[0] + '''
KIND = os.environ.get("KIND", "token")
V, keep = value((KIND, 0.5)); bl = np.concatenate(blocks[1:]); ix = bl[keep[bl]]
rng = np.random.default_rng(7)
print(f"{W[:8]}, {KIND} coins, the 3 blind blocks: {len(ix)} copies; gain a copy over no sell pressure (tp 3x / 420 / stall 240)")
base = V[ix, 0]
for j in range(1, len(ENAMES)):
    d = V[ix, j] - base; se = d.std(ddof=1) / np.sqrt(len(d))
    bs = np.array([d[rng.integers(0, len(d), len(d))].mean() for _ in range(2000)])
    print(f"  sell pressure {ENAMES[j]:10s} gain {100 * d.mean():+5.1f} points, give or take {100 * se:4.1f} (1 se); "
          f"above 0 in {np.mean(bs > 0):4.0%} of reshuffles; copies where it changed the result: {np.mean(np.abs(d) > 1e-9):.0%}")
'''
exec(compile(src, "sp_noise", "exec"), {"__file__": os.path.join(os.path.dirname(os.path.abspath(__file__)), "w3_robust.py"), "__name__": "__main__"})
