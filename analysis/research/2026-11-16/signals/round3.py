# Round 3 (the owner, Nov 15 night: "you sure there are no other stuff like the 2 signals? ... buyers and sellers and
# price movement and top holders"). What rounds 1-2 did not try, each ADDED to the setup live since Nov 15 19:29 UTC
# (tp 4.0, 600 s, early 30-290 s under 1.5x, sell_pressure [5, 60, 30], stall 180 s), so a gain here is a gain on top:
#   uniq     different sellers minus different buyers over W s at N or more (wallets, not trades)
#   ratio    sells at r times the buys or more, with at least m sells, over W s
#   nettok   tokens sold minus bought by the others over W s at s% of the supply or more
#   drought  no buy by anyone else for T s
#   quiet    fewer than k trades by the others in the last 60 s (the coin went dead)
#   tstop    under x times our buy price T s or more after its buy (a stop that waits)
#   dev      the coin's creator sells (any size, or 1%+ of the supply); the creator is in wallet 4's buy event
#   his      wallet 4's own sale followed more widely than 30-290 s under 1.5x (#36: it sold at 63 s at 2.07x)
#   timer    300 to 1790 s instead of 600 (the stall rule may make the timer needless)
#   press    the pressure rule over 90 / 120 s or with another N; stall 120 / 150 / 240 s (the neighbours, on the full setup)
#   python3 -I round3.py CQ ALL > out/round3.txt
import sys, os, json, collections, random, struct
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.argv = sys.argv[:3]
import signals2 as S2
from signals2 import L, ROWS, PREP, EX, CAPS, blk, day
SPD = sys.argv[2]
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
def b58(b):
    n = int.from_bytes(b, "big"); out = ""
    while n: n, r = divmod(n, 58); out = B58[r] + out
    return "1" * (len(b) - len(b.lstrip(b"\0"))) + out
def b58d(s):
    n = 0
    for ch in s: n = n * 58 + B58.index(ch)
    return n.to_bytes((n.bit_length() + 7) // 8, "big").rjust(len(s) - len(s.lstrip("1")) + (n.bit_length() + 7) // 8, b"\0") if n else b"\0" * len(s)
def creator_of(d):                                           # crates/pump-codec/src/events.rs TradeEvent, to `creator`
    try:
        o = 32 + 8 + 8 + 1 + 32 + 8 + 8 + 8 + 8 + 8 + 32 + 8 + 8
        return b58(d[:32]), b58(d[o:o + 32]) if len(d) >= o + 32 else None
    except Exception: return None, None
files = collections.defaultdict(list)
for f in os.listdir(f"{SPD}/w4tx"): files[f.split("_")[0]].append(f)
CRE, miss = {}, 0
for r in ROWS:
    got = None
    for fn in files.get(str(r["slot"]), []):
        tx = json.load(open(f"{SPD}/w4tx/{fn}")); m = tx["meta"]
        for g in m.get("innerInstructions") or []:
            for ix in g["instructions"]:
                raw = b58d(ix.get("data", ""))
                if len(raw) > 200 and raw[8:16] == bytes.fromhex("bddb7fd34ee661ee"):
                    mint, c = creator_of(raw[16:])
                    if mint and mint.startswith(r["mint8"]) and c: got = c
    CRE[r["key"]] = got; miss += got is None
for (key, n), x in EX.items():
    c = CRE.get(key); x["dev"] = np.array([x["sell"][i] and u == c for i, u in enumerate(x["user"])], dtype=bool) if c else np.zeros(len(x["user"]), dtype=bool)
base_trigger = S2.trigger
def trigger(p, x, sig):
    kind = sig[0]
    if kind in ("sellers", "stall"): return base_trigger(p, x, sig)
    age, px = p["age"], p["px"] / x["pin"]; n = len(age)
    if n == 0: return None
    a, w = sig[1], sig[2]
    if kind == "tstop": return L.first((px < a) & (age >= w))
    if kind == "dev": return L.first(x["dev"] & (x["tok"] >= a))
    if kind == "drought":
        last = np.maximum.accumulate(np.where(x["buy"], age, p["last"])); return L.first((age - last >= a) & (age >= 30))
    lo = np.searchsorted(age, age - w, side="left")
    if kind == "nettok":
        c = np.concatenate([[0], np.cumsum(np.where(x["sell"], x["tok"], 0) - np.where(x["buy"], x["tok"], 0))]); return L.first(((c[1:] - c[lo]) >= a) & (age >= 30))
    s = np.concatenate([[0], np.cumsum(x["sell"])]); b = np.concatenate([[0], np.cumsum(x["buy"])]); ns, nb = s[1:] - s[lo], b[1:] - b[lo]
    if kind == "ratio": return L.first((ns >= sig[3]) & (ns >= a * nb) & (age >= 30))
    if kind == "quiet": return L.first((ns + nb < a) & (age >= 60))
    if kind == "uniq":
        for i in np.nonzero((ns - nb >= max(1, a - 3)) & (age >= 30) & (age < 1800))[0]:   # a cheap gate, then the wallets
            us = x["user"][lo[i]:i + 1]; sl = x["sell"][lo[i]:i + 1]; bl = x["buy"][lo[i]:i + 1]
            if len({u for u, f in zip(us, sl) if f}) - len({u for u, f in zip(us, bl) if f}) >= a: return int(i)
        return None
def model(p, x, stake, sigs, tp, hold, early):
    if p["refused"]: return (-0.0004, "refused", 0)
    base = L.model(p, stake, tp, hold, early, None)
    t = [(i, s[0]) for i, s in ((trigger(p, x, s), s) for s in sigs) if i is not None]
    if not t: return base
    i, why = min(t)
    if p["age"][i] >= hold: return base
    ex = min(i + 1, len(p["px"]) - 1)
    if p["age"][ex] > base[2] or (p["age"][ex] == base[2] and base[1] != "time"): return base
    vt0, vq0, bps0 = p["ent"]
    Q = stake * 1e9 * p["hopf"] / p["rate"]; net_in = Q * 1e4 / (1e4 + bps0); tok = vt0 - vt0 * vq0 / (vq0 + net_in)
    vq_r = p["vq"][ex] + net_in; vt_r = p["vt"][ex] * p["vq"][ex] / vq_r
    out = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - p["bps"][ex] / 1e4)
    return (out * p["rate"] * p["hopf"] / 1e9 - stake - 0.0026, why, int(p["age"][ex]))
def score(rule):
    sigs, tp, hold, early = rule
    tot, blocks, wo5, days, whys = 0, [0, 0, 0], 0, collections.defaultdict(float), collections.Counter()
    for n in L.LAND:
        out, open_ = [], []
        for r in ROWS:
            open_ = [y for y in open_ if y[0] > r["t"]]
            if len(open_) >= 2 or sum(1 for y in open_ if y[1] == r["anchor"]) >= CAPS[r["anchor"]]: continue
            net, why, held = model(PREP[r["key"], n], EX[r["key"], n], 0.5, sigs, tp, hold, early)
            if why != "refused": open_.append((r["t"] + held, r["anchor"]))
            out.append((r, net, why))
        v = sorted((y[1] for y in out), reverse=True); tot += sum(v) / 3; wo5 += sum(v[5:]) / 3
        for r, net, why in out: blocks[blk(r)] += net / 3; days[day(r["t"])] += net / 3; whys[why] += 1 / 3
    ks = sorted(days)[1:-1]; dv = sorted(days[k] for k in ks)
    return dict(tot=tot, b=blocks, wo5=wo5, neg=sum(1 for y in dv if y < 0), nd=len(dv), worst=dv[0], days=[days[k] for k in ks], whys=whys)
SEL, STALL, E = ("sellers", 5, 60, None), ("stall", 1.0, 180, None), (30, 290, 1.5)
BASE = ((SEL, STALL), 4.0, 600, E)
add = lambda s: ((SEL, STALL, s), 4.0, 600, E)
R = {}
for N in (2, 3, 5, 8):
    for W in (60, 90, 120): R[f"uniq: {N}+ more selling wallets than buying in {W} s"] = add(("uniq", N, W))
for r_, m in ((2, 5), (3, 5), (2, 10), (3, 10)):
    for W in (60, 120): R[f"ratio: sells {r_}x the buys, {m}+ sells, in {W} s"] = add(("ratio", r_, W, m))
for s in (0.02, 0.03, 0.05, 0.08):
    for W in (60, 120): R[f"nettok: {s * 100:.0f}%+ of supply sold net in {W} s"] = add(("nettok", s, W))
for T in (30, 60, 90, 120, 180): R[f"drought: no buy for {T} s"] = add(("drought", T, 0))
for k in (2, 3, 5): R[f"quiet: under {k} trades in 60 s"] = add(("quiet", k, 60))
for xx in (0.5, 0.6, 0.7, 0.8):
    for T in (60, 120, 180, 300): R[f"tstop: under {xx}x after {T} s"] = add(("tstop", xx, T))
for s in (0.0, 0.01): R[f"dev: the creator sells{' 1%+' if s else ''}"] = add(("dev", s, 0))
for nm, e in (("30-290 s at any price", (30, 290, 1e9)), ("0-600 s under 1.5x", (0, 600, 1.5)), ("any time, any price", (0, 600, 1e9)), ("30-180 s under 1.5x", (30, 180, 1.5)),
              ("30-290 s under 2.0x", (30, 290, 2.0)), ("30-290 s under 3.0x", (30, 290, 3.0)), ("never", None)):
    R[f"his: its sale followed {nm}"] = ((SEL, STALL), 4.0, 600, e)
for h in (300, 450, 900, 1200, 1790): R[f"timer: {h} s"] = ((SEL, STALL), 4.0, h, E)
for N, W in ((3, 60), (3, 90), (5, 90), (4, 90), (5, 120), (3, 120)): R[f"press: {N}+ more sells than buys in {W} s (in place of 5 in 60)"] = ((("sellers", N, W, None), STALL), 4.0, 600, E)
for T in (120, 150, 240): R[f"press: stall {T} s (in place of 180)"] = ((SEL, ("stall", 1.0, T, None)), 4.0, 600, E)
if __name__ == "__main__":
    B0 = score(BASE); random.seed(7)
    print(f"{len(ROWS)} buys; the creator known for {len(ROWS) - miss}; 0.5 SOL, 2 open; {len(R)} additions to the live setup")
    hdr = f"   {'rule':66s} | total  | gain   | A      B      C      | w/o best 5 | days<0 | worst | ahead in draws | exits by it"
    def row(nm, s):
        g = [a - b for a, b in zip(s["days"], B0["days"])]; dr = [sum(random.choice(g) for _ in g) for _ in range(1000)]
        mine = sum(c for w, c in s["whys"].items() if w not in ("tp", "time", "its_sell", "graduated", "refused", "sellers", "stall"))
        return f"   {nm:66s} | {s['tot']:+6.2f} | {s['tot'] - B0['tot']:+6.2f} | {s['b'][0]:+6.2f} {s['b'][1]:+6.2f} {s['b'][2]:+6.2f} | {s['wo5']:+6.2f}     | {s['neg']:2d}/{s['nd']} | {s['worst']:+5.2f} | {100 * sum(1 for y in dr if y > 0) / 1000:5.1f}%         | {mine:.0f}"
    print("== the live setup (both signals, tp 4.0, 600 s)\n" + hdr + "\n" + row("live", B0))
    S = {nm: score(r) for nm, r in R.items()}
    fam = lambda nm: nm.split(":")[0]
    for f in ("uniq", "ratio", "nettok", "drought", "quiet", "tstop", "dev", "his", "timer", "press"):
        xs = [(nm, s) for nm, s in S.items() if fam(nm) == f]
        print(f"== {f}: {sum(1 for nm, s in xs if s['tot'] > B0['tot'])} of {len(xs)} ahead of the live setup, {sum(1 for nm, s in xs if all(s['b'][i] > B0['b'][i] for i in range(3)))} in all three blocks\n" + hdr)
        for nm, s in xs: print(row(nm, s))
    print("== picked on two blocks, scored on the third (gain over the live setup in the held-out block)")
    tot = 0
    for held in range(3):
        other = [i for i in range(3) if i != held]
        rk = sorted(S.items(), key=lambda q: -sum(q[1]["b"][i] for i in other))
        g = rk[0][1]["b"][held] - B0["b"][held]; tot += g
        print(f"   held out {'ABC'[held]}: picked '{rk[0][0]}' ({sum(rk[0][1]['b'][i] - B0['b'][i] for i in other):+.2f} on the other two) -> {g:+.2f}; the 10 best picks on average {sum(s['b'][held] - B0['b'][held] for nm, s in rk[:10]) / 10:+.2f}")
    print(f"   total out of sample: {tot:+.2f} SOL")
