# The deep redo's shared code (Nov 19): the Pons logs (rh1_fetch.py's chunks), each ETH curve's trades as a path on the
# EXACT curve, and our copy of one buy. Measured on Nov 18 from the reserves before and after single trades (docs/23):
# an ETH curve keeps q·t = 1.68e9 (1.68 ETH and 1B tokens virtual to start); a buy adds quoteIn - fee - tax to q, a sale
# takes quoteOut + fee + tax. The first pass (rh4_copy.py) fitted V0 = 1.75 and added the gross quote; it also dropped
# every coin whose trading stopped within 600 s of the copied buy, which leaves out the coins that die (a rug and then
# silence): here such a coin is sold at its last state, as the live bot would (only buys in the data's last 600 s are left
# out). Our landings: 2, 3 and 5 blocks after its buy (rh6's LANDB; a copier sees the block, then sends).
import sys, os, json, gzip, glob, bisect, collections, numpy as np
E8 = "/home/user/copy2/analysis/research/2026-11-17/wallet_hunt/market/e8_engineer.py"
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-17/wallet_hunt"); _argv = sys.argv; sys.argv = ["x", "/tmp", "x"]
exec(open(E8).read().split("rows = []")[0].replace("here = os.path.dirname(os.path.abspath(__file__))", "here = os.path.dirname(E8)"))
sys.argv = _argv
STAKE = float(os.environ.get("STAKE", 0.02)); GAS = float(os.environ.get("GAS", 0.00004))
RATE = 0.5 / STAKE                     # copy_vals' 0.5 "stake units" = STAKE ETH; the quote unit is 1e-9 ETH
COST = GAS * RATE - 0.0026             # copy_vals already charges 0.0026 units
V0, T0 = 1.68, 1e9                     # exact (K = 1.68e9)
FACTORY = "0x7ed598bcef8bd9edd8c97a195c6d13f40801ec7e"
LANDB = [int(x) for x in os.environ.get("LANDB", "2,3,5").split(",")]
EXITS = [  # fixed before looking: the first pass's four, and the three settings engineered for the live wallets
    ("w4 live exit (lim 1.5)", 1.5, (TP.index(4), HOLD.index(600), SPS.index((5, 60)), STALL.index(180), ITS.index("early"))),
    ("its sale, tp 4 (lim 1.5)", 1.5, (TP.index(4), HOLD.index(600), SPS.index((5, 60)), STALL.index(180), ITS.index("always"))),
    ("tp 2, 120 s (lim 1.5)", 1.5, (TP.index(2), HOLD.index(120), 0, 0, 0)),
    ("held 600 s (lim 1.5)", 1.5, (TP.index(1e9), HOLD.index(600), 0, 0, 0)),
    ("wallet 1's: tp 4, 600 s (lim 1.5)", 1.5, (TP.index(4), HOLD.index(600), 0, 0, 0)),
    ("wallet 2's: tp 3.5, sp 10/30 (lim 1.5)", 1.5, (TP.index(3.5), HOLD.index(600), SPS.index((10, 30)), 0, 0)),
    ("wallet 3's: tp 2.5, 300 s, sp 8/60, stall 240", 1e9, (TP.index(2.5), HOLD.index(300), SPS.index((8, 60)), STALL.index(240), 0)),
]
words = lambda d: [int(d[2 + 64 * i: 2 + 64 * (i + 1)], 16) for i in range((len(d) - 2) // 64)]

class Data:
    def __init__(self, D):
        T = json.load(open(f"{D}/topics.json")); B = {int(k): v for k, v in json.load(open(f"{D}/blocks.json")).items()}; self.bk = sorted(B); self.B = B
        self.L, self.TR, self.GRAD, self.OTHER = {}, collections.defaultdict(list), {}, collections.Counter()
        seen = set()
        for f in glob.glob(f"{D}/logs_*.json.gz"):
            for l in json.load(gzip.open(f)):
                key = (l["blockNumber"], l["logIndex"])
                if key in seen: continue
                seen.add(key); t0 = l["topics"][0]
                if t0 == T["TokenLaunched"] and l["address"].lower() == FACTORY:
                    w = words(l["data"])
                    if len(w) >= 3:
                        if w[0] == 0: self.L["0x" + l["topics"][2][-40:]] = "0x" + l["topics"][1][-40:]   # curve -> token
                        else: self.OTHER["0x%040x" % w[0]] += 1                                             # another quote token
                elif t0 == T["LaunchSwept"]: self.GRAD["0x" + l["topics"][1][-40:]] = int(l["blockNumber"], 16)
                elif t0 in (T["CurveBuy"], T["CurveSell"]):
                    buy = t0 == T["CurveBuy"]
                    self.TR[l["address"].lower()].append((int(l["blockNumber"], 16), int(l["logIndex"], 16), buy,
                        "0x" + (l["topics"][2] if buy else l["topics"][1])[-40:], "0x" + l["topics"][1][-40:], words(l["data"])))
        self.t_end = self.tm(max(self.bk)); self.t_start = self.tm(min(self.bk))
    def tm(self, n):
        bk, B = self.bk, self.B; i = min(max(bisect.bisect_left(bk, n), 1), len(bk) - 1); a, b = bk[i - 1], bk[i]
        return B[a] + (B[b] - B[a]) * (n - a) / max(1, b - a)
    def path(self, c):
        """The curve's trades in order, each with the state after it (hunt_lib's form): exact accounting."""
        Q = S = 0.0; out = []; g = self.GRAD.get(self.L[c])
        for n, i, buy, u, caller, w in sorted(self.TR[c]):
            if len(w) < 4: continue
            if buy: q, tok, dq = w[0] / 1e18, w[1] / 1e18, (w[0] - w[2] - w[3]) / 1e18; Q += dq; S += tok
            else: q, tok, dq = w[1] / 1e18, w[0] / 1e18, (w[1] + w[2] + w[3]) / 1e18; Q -= dq; S -= tok
            bps = 1e4 * (w[2] + w[3]) / max(1, w[0] if buy else (w[1] + w[2] + w[3]))
            out.append(dict(slot=n, t=self.tm(n), user=u, caller=caller, buy=buy, q=q * 1e9, tok=tok, vt=T0 - S, vq=(V0 + Q) * 1e9, bps=bps,
                            real=0 if (g and n >= g) else 1))
        return out

def landings(tr, k):
    """our buy's index for each landing (the first trade D blocks or more after its block); None if the data ends first"""
    return [next((j for j in range(k + 1, len(tr)) if tr[j]["slot"] >= tr[k]["slot"] + d), None) for d in LANDB]

def copy_one(tr, k):
    """(premium at each landing, the full exit grid's ETH at each landing) for a copy of its buy tr[k]; a landing past
    the curve's last trade buys at its last state and sells at it (the coin went quiet)"""
    js = landings(tr, k); prems, vals = [], []
    for j in js:
        if j is None:  # no trade after: we land on the last state and can only sell back into it
            p = H.prep(tr + [dict(tr[-1], user="0x", buy=True, q=0, t=tr[-1]["t"] + 1)], k, RATE, len(tr) - k, pmax=1000)
        else: p = H.prep(tr, k, RATE, j - k, pmax=1000)
        p["rate"] = RATE; prems.append((tr[k]["vt"] / p["ent"][0]) ** 2)
        if not len(p["px"]):   # nothing after our buy: sold into the same state (round-trip fees only)
            vt0, vq0, b0 = p["ent"]; Qn = 0.5e9 / RATE * 1e4 / (1e4 + b0); tok = vt0 - vt0 * vq0 / (vq0 + Qn); vq_r = vq0 + Qn; vt_r = vt0 * vq0 / vq_r
            v = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - b0 / 1e4) * RATE / 1e9 - 0.5 - 0.0026
            vals.append(np.full((len(TP), len(HOLD), len(SPS), len(STALL), len(ITS)), v) - COST)
        else: vals.append(copy_vals(p) - COST)
    return prems, vals

def fixed_vals(prems, vals):
    """each fixed exit's ETH, the landings averaged (a landing over the exit's price limit: refused, -0.0004 units)"""
    return np.array([np.mean([vals[l][ix] if prems[l] <= lim else -0.0004 for l in range(len(vals))]) for _, lim, ix in EXITS]) / RATE
