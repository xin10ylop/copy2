# Step 3b: buying at launch ourselves, on the tapes of s4_paths.py, with the gaps refined where an exit fires.
# Fill: after the last trade of the create slot (F=0) or of the next slot (F=1); a coin's own fill is F = hash(mint) % 2
# (half and half), both are kept. Our buy at STAKE SOL: SOL -> quote at pump's own price of the quote (30 SOL / the
# curve's initial virtual quote) x the checked factor (creates/README.md §4: WBTC 1.130, pump-coin quotes 0.892), less
# 0.30% per extra pool hop (route A or B: 1 hop, C: none), then the curve (1.25% fee). Path model "cautious": every
# later recorded state shifted by our quote (later buyers spend fixed amounts). Exits on the price our buy left:
# TP when a trade takes it to TP (sold on that trade's state, 1% under), SL when a trade takes it to SL or under (sold on
# that state), else sold on the last state at or before our fill + 1800 s. Sale: the curve (1.25%) and the hop back
# (0.30% a hop); 0.003 SOL fixed a round trip.
# Refinement: wherever an exit fires on a sampled state with unread transactions between it and the state before, those
# are read (all if <= 30, else 30 evenly spaced, again until none are left between), and gaps whose two ends come within
# 80% of a TP or 115% of an SL are read the same way; at most BUDGET reads a coin.
#   python3 -I s5_sim.py COINS_JSON [BUDGET=120] [THREADS=6] -> out/sim_<name>.json {mint: {cfg: result}}
import sys, os, time, zlib, collections
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib, tape
FEE, HOP, FIX, TPH = 0.0125, 0.003, 0.003, 0.99
EXITS = {"its": (2.5, 0.7), "ours": (2.0, 0.8)}
STAKES = (1.0, 0.1)
FACT = {"C": 1.130, "A": 0.892, "B": 0.892}
HOPS = {"C": 0, "A": 1, "B": 1}
TD = lib.OUT + "/tapes"
VT0 = 1073000000000000                        # every create's initial virtual token reserve (114,104 of 114,104)
def seq(d, csig, c=None):
    """known states in tape order: [(pos, slot, bt, vt, vq)] after each fetched tx (its last trade of the coin); the
    create's own state when the create carries no dev buy"""
    order = [csig] + [r[0] for r in d["sigs"]]
    meta = {r[0]: r for r in d["sigs"]}
    out = []
    if c is not None and not d["tr"].get(csig): out.append((0, c["cslot"], c["cbt"], VT0, c["vquote"]))
    for pos, s in enumerate(order):
        x = d["tr"].get(s)
        if x:
            t = x[-1]; out.append((pos, t[0], t[10] or (meta[s][2] if s in meta else None), t[7], t[8]))
    return order, out
def run_cfg(c, d, order, S, F, stake, tp, sl):
    cls = c["cls"]; spq = 30e9 * FACT[cls] / c["vquote"]                 # lamports per quote unit
    slot_f = c["cslot"] + F
    pre = [x for x in S if x[1] <= slot_f]
    if not pre: return None
    f = pre[-1]; fpos, fbt = f[0], (f[2] or c["cbt"])
    vq_f, vt_f = f[4], f[3]; k = vq_f * vt_f
    qin = stake * 1e9 / spq * (1 - HOP * HOPS[cls]); net = qin * (1 - FEE)
    vq_o = vq_f + net; T = vt_f - k / vq_o
    def sale(vq):
        vqo = vq + net; vto = k / vqo
        g = vqo - k / (vto + T)
        return g * (1 - FEE) * (1 - HOP * HOPS[cls]) * spq / 1e9
    after = [x for x in S if x[0] > fpos and (x[2] or 0) <= fbt + 1800]
    prev = f
    for x in after:
        m = ((x[4] + net) / vq_o) ** 2
        if m >= tp: return dict(kind="tp", pnl=sale(x[4]) * TPH - stake - FIX, m=m, t=(x[2] or fbt) - fbt, pos=x[0], prev=prev[0], fpos=fpos, fbt=fbt)
        if m <= sl: return dict(kind="sl", pnl=sale(x[4]) - stake - FIX, m=m, t=(x[2] or fbt) - fbt, pos=x[0], prev=prev[0], fpos=fpos, fbt=fbt)
        prev = x
    last = after[-1] if after else f
    m = ((last[4] + net) / vq_o) ** 2
    return dict(kind="time" if after else "none", pnl=sale(last[4]) - stake - FIX, m=m, t=(last[2] or fbt) - fbt, pos=last[0], prev=last[0], fpos=fpos, fbt=fbt)
def cfgs():
    for F in (0, 1):
        for stake in STAKES:
            for name, (tp, sl) in EXITS.items():
                yield f"{name}|{stake}|F{F}", F, stake, tp, sl
def unread(order, d, a, b):
    return [order[p] for p in range(a + 1, b) if order[p] not in d["tr"]]
def take(L, n=30):
    return L if len(L) <= n else [L[int(i * (len(L) - 1) / (n - 1))] for i in range(n)]
def sim(c, budget):
    fn = f"{TD}/{c['mint']}.json"
    d = lib.jl(fn); used = 0; changed = False
    while True:
        order, S = seq(d, c["csig"], c)
        want = []
        for key, F, stake, tp, sl in cfgs():
            r = run_cfg(c, d, order, S, F, stake, tp, sl)
            if not r: continue
            if r["kind"] in ("tp", "sl"): want += unread(order, d, r["prev"], r["pos"])
            # gaps near a level, before the exit
            spq = 30e9 * FACT[c["cls"]] / c["vquote"]
            pre = [x for x in S if x[0] >= r["fpos"] and x[0] <= r["pos"]]
            for x, y in zip(pre, pre[1:]):
                if y[0] - x[0] <= 1: continue
                net = stake * 1e9 / spq * (1 - HOP * HOPS[c["cls"]]) * (1 - FEE)
                vq_o = pre[0][4] + net
                mx = max(((x[4] + net) / vq_o) ** 2, ((y[4] + net) / vq_o) ** 2); mn = min(((x[4] + net) / vq_o) ** 2, ((y[4] + net) / vq_o) ** 2)
                if mx >= 0.8 * tp or mn <= 1.15 * sl: want += unread(order, d, x[0], y[0])
            if want: break
        want = list(dict.fromkeys(want))
        if not want or used >= budget: break
        for s in take(want, min(30, budget - used)):
            x = tape.trades(s, c["mint"]); used += 1; changed = True
            d["tr"][s] = x or []
    if changed: lib.jdump(d, fn)
    order, S = seq(d, c["csig"], c)
    res = {}
    for key, F, stake, tp, sl in cfgs():
        r = run_cfg(c, d, order, S, F, stake, tp, sl)
        if r: res[key] = {k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items() if k not in ("pos", "prev", "fpos")}
    res["_reads"] = used; res["_n"] = d["n"]; res["_gaps"] = d["gaps"]
    res["_F"] = zlib.crc32(c["mint"].encode()) % 2
    return res
if __name__ == "__main__":
    src = sys.argv[1]; BUDGET = int(sys.argv[2]) if len(sys.argv) > 2 else 120; TH = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    lib.crc.MIN_GAP = 0.03
    C = lib.jl(src); name = os.path.basename(src).replace("coins_", "").replace(".json", "")
    op = lib.OUT + f"/sim_{name}.json"; have = lib.jl(op) if os.path.exists(op) else {}
    todo = [m for m in C if m not in have and os.path.exists(f"{TD}/{m}.json")]
    def one(m):
        c = dict(C[m], mint=m)
        try: return m, sim(c, BUDGET)
        except Exception as e: return m, dict(err=lib.red(e)[:120])
    t0 = time.time(); n = 0
    with ThreadPoolExecutor(TH) as ex:
        for m, r in ex.map(one, todo):
            have[m] = r; n += 1
            if n % 200 == 0: print(time.strftime("%H:%M:%S"), n, "/", len(todo), f"calls {lib.crc.NCALLS[0]}", flush=True); lib.jdump(have, op)
    lib.jdump(have, op)
    print(f"{len(have)} simulated ({sum(1 for v in have.values() if 'err' in v)} errors), reads {sum(v.get('_reads', 0) for v in have.values())}, calls {lib.crc.NCALLS[0]} in {time.time()-t0:.0f} s")
