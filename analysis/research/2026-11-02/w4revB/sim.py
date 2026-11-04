# Step 3b: buying a part-B launch ourselves, on the tapes of t1_tapes.py (the logic of ../w4rev/s5_sim.py, with the two
# execution models of this study and the quote token's own price).
# Price of the quote: lamports per raw unit from wallet 4's own swaps (prices.py = h9long/ledger.py's source), nearest
# observation to the fill and to the exit; without a series, pump's own config price (30 SOL / the curve's initial
# virtual quote) x the checked factor (../agents/scan/src/.../creates/README.md §4: plain tokens 1.126, pump-coin
# quotes 0.892), and then no move.
# Models:
#   float: we hold the quote token. Fill after the last trade of the create slot (F0) or of the next slot (F1); a coin's
#          own fill is F = crc32(mint) % 2 (half and half), both kept. No route cost.
#   jup:   one transaction SOL -> quote (Jupiter) -> coin, one slot later: F1 or F2 (F = 1 + crc32(mint) % 2). The quote
#          leg costs half the measured Jupiter round trip each way (j1_jup.py, Nov 1, at 0.1 or 1 SOL; fees + impact).
# Our buy at STAKE SOL worth of quote, the curve fee 1.25% each side. Path model "cautious": every later recorded state
# shifted by our quote (later buyers spend fixed amounts). Exits on the price our buy left: TP when a trade takes it to
# TP (sold on that state, 1% under), SL when a trade takes it to SL or under (sold on that state), else sold on the last
# state at or before our fill + 1800 s. 0.003 SOL fixed a round trip. P&L in SOL = quote out x its price at the exit
# - stake - 0.003 ("pnl"), and with the quote's price held at the fill's ("pnl0").
# Refinement (as s5_sim.py): where an exit fires on a sampled state with unread transactions before it, or a gap's ends
# come within 80% of a TP / 115% of an SL, those transactions are read (all if <= 30, else 30 evenly spaced, again
# until none are left), at most BUDGET reads a coin.
import os, sys, zlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blib, prices
FEE, FIX, TPH = 0.0125, 0.003, 0.99
EXITS = {"its": (2.5, 0.7), "ours": (2.0, 0.8)}
STAKES = (1.0, 0.1)
MODELS = {"float": (0, 1), "jup": (1, 2)}
TD = os.path.join(blib.HERE, "tapes")
_J = None
def jup_rt(q, stake):
    global _J
    if _J is None: _J = blib.jl(blib.OUT + "/jup.json") if os.path.exists(blib.OUT + "/jup.json") else {}
    x = ((_J.get(q) or {}).get("rt") or {}).get(str(stake)) or {}
    v = x.get("rt")
    return None if v is None else max(0.0, v)
def spq_at(c, t):
    """lamports per raw quote unit at time t, and the source"""
    v = prices.lamports_per_raw(c["quote"], t)
    if v: return v, "own"
    f = 1.126 if not c.get("depth") else 0.892
    return 30e9 * f / c["vquote"], "config"
def seq(d, c):
    """known states in tape order: [(pos, slot, bt, vt, vq)] after each fetched tx (its last trade of the coin); a create
    without a trade gives the curve's initial reserves"""
    csig = c["csig"]
    order = [csig] + [r[0] for r in d["sigs"]]
    meta = {r[0]: r for r in d["sigs"]}
    out = []
    for pos, s in enumerate(order):
        x = d["tr"].get(s)
        if x:
            t = x[-1]; out.append((pos, t[0], t[10] or (meta[s][2] if s in meta else None), t[7], t[8]))
        elif pos == 0:
            out.append((0, c["cslot"], c["cbt"], c["vtok"], c["vquote"]))
    return order, out
def run(c, S, F, qin, tp, sl):
    """our buy of qin raw quote units after slot cslot + F; exit by tp / sl / 1800 s. -> dict or None"""
    slot_f = c["cslot"] + F
    pre = [x for x in S if x[1] <= slot_f]
    if not pre: return None
    f = pre[-1]; fpos, fbt = f[0], (f[2] or c["cbt"])
    vq_f, vt_f = f[4], f[3]; k = vq_f * vt_f
    net = qin * (1 - FEE); vq_o = vq_f + net; T = vt_f - k / vq_o
    def sale(vq):
        vqo = vq + net; vto = k / vqo
        return (vqo - k / (vto + T)) * (1 - FEE)
    after = [x for x in S if x[0] > fpos and (x[2] or 0) <= fbt + 1800]
    prev = f
    for x in after:
        m = ((x[4] + net) / vq_o) ** 2
        if m >= tp: return dict(kind="tp", g=sale(x[4]) * TPH, m=m, t=(x[2] or fbt) - fbt, pos=x[0], prev=prev[0], fpos=fpos, fbt=fbt, net=net)
        if m <= sl: return dict(kind="sl", g=sale(x[4]), m=m, t=(x[2] or fbt) - fbt, pos=x[0], prev=prev[0], fpos=fpos, fbt=fbt, net=net)
        prev = x
    last = after[-1] if after else f
    m = ((last[4] + net) / vq_o) ** 2
    return dict(kind="time" if after else "none", g=sale(last[4]), m=m, t=1800, pos=last[0], prev=last[0], fpos=fpos, fbt=fbt, net=net)
def cfgs(c):
    for model, Fs in MODELS.items():
        for F in Fs:
            for stake in STAKES:
                rt = 0.0 if model == "float" else jup_rt(c["quote"], stake)
                if rt is None: continue
                for name, (tp, sl) in EXITS.items():
                    yield f"{model}|{name}|{stake}|F{F}", model, F, stake, rt, tp, sl
def qin_of(c, stake, rt):
    sp, src = spq_at(c, c["cbt"])
    return stake * 1e9 * (1 - rt / 2) / sp, sp, src
def unread(order, d, a, b):
    return [order[p] for p in range(a + 1, b) if order[p] not in d["tr"]]
def take(L, n=30):
    if len(L) <= n: return L
    if n <= 1: return L[:n]
    return [L[int(i * (len(L) - 1) / (n - 1))] for i in range(n)]
def sim(c, budget=40):
    fn = f"{TD}/{c['mint']}.json"
    d = blib.jl(fn); used = 0; changed = False
    while True:
        order, S = seq(d, c)
        want = []
        for key, model, F, stake, rt, tp, sl in cfgs(c):
            qin, sp, src = qin_of(c, stake, rt)
            r = run(c, S, F, qin, tp, sl)
            if not r: continue
            if r["kind"] in ("tp", "sl"): want += unread(order, d, r["prev"], r["pos"])
            pre = [x for x in S if r["fpos"] <= x[0] <= r["pos"]]
            vq_o = pre[0][4] + r["net"] if pre else None
            for x, y in zip(pre, pre[1:]):
                if y[0] - x[0] <= 1: continue
                a = ((x[4] + r["net"]) / vq_o) ** 2; b = ((y[4] + r["net"]) / vq_o) ** 2
                if max(a, b) >= 0.8 * tp or min(a, b) <= 1.15 * sl: want += unread(order, d, x[0], y[0])
            if want: break
        want = list(dict.fromkeys(want))
        if not want or used >= budget: break
        for s in take(want, min(30, budget - used)):
            x = blib.trades(s, c["mint"]); used += 1; changed = True
            d["tr"][s] = x or []
    if changed: blib.jdump(d, fn)
    order, S = seq(d, c)
    res = {}
    for key, model, F, stake, rt, tp, sl in cfgs(c):
        qin, sp, src = qin_of(c, stake, rt)
        r = run(c, S, F, qin, tp, sl)
        if not r: continue
        sx, _ = spq_at(c, r["fbt"] + r["t"])          # the quote's price at our exit (time exits: fill + 1800 s)
        out_q = r["g"] * (1 - rt / 2)                  # quote out of the curve, less the Jupiter leg back (jup)
        # qin was sized at the create's price sp (the fill is within a second of it): the stake is the cost
        res[key] = dict(kind=r["kind"], m=round(r["m"], 4), t=r["t"], pnl=round(out_q * sx / 1e9 - stake - FIX, 6),
                        pnl0=round(out_q * sp / 1e9 - stake - FIX, 6), src=src, mv=round(sx / sp - 1, 5))
    res["_reads"] = used; res["_n"] = d["n"]; res["_gaps"] = d["gaps"]; res["_h"] = zlib.crc32(c["mint"].encode()) % 2
    return res
