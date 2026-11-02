# Step 4c: score P3 (creates of Oct 27 00:00 - Nov 1 23:00 UTC; out/sim_fresh.json, weights out/fresh_sample2.json):
#  (1) the rotation rule that passed P2: R2 inside the quotes where R2 was positive on P1 (set A), and inside the quotes
#      where it was positive on P2 (set B, the weekly re-pick), each model with its own sets (out/rot_sets.json);
#  (2) wallet 4's own part-B launch buys (sampled from its transactions; perfect selection, not knowable at launch),
#      all and 1.45+ SOL.
# Wallet 4's picks inside the rotation coins are read from each tape (a buy by it in the create slot or the next).
# Coins created later than 30 min before the last cursor (blib.cursor_max_bt) are left out (their 30 min not listed).
# Quote prices: the last own-swap price (Oct 26-27), held (no move); Jupiter costs of Nov 1.
#   python3 -I s9_fresh.py
import sys, os, collections, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blib
from u1_universe import sym
from score import stats, fmt, HDR
SIM = blib.jl(blib.OUT + "/sim_fresh.json"); S = blib.jl(blib.OUT + "/fresh_sample2.json")
FT = {t["mint"]: t for t in blib.jl(blib.OUT + "/fresh_table.json")}
RS = blib.jl(blib.OUT + "/rot_sets.json")
TMAX = blib.cursor_max_bt() - 1830
TD = os.path.join(blib.HERE, "tapes")
def picked(m):
    fn = f"{TD}/{m}.json"
    if not os.path.exists(fn): return None
    d = blib.jl(fn); c = FT[m]
    return int(any(x[3] == blib.W4 and x[4] == 1 and x[0] <= c["cslot"] + 1 for tr in d["tr"].values() for x in tr))
def rows(cfg, keep, wkey, days=None):
    model = cfg.split("|")[0]; out = []
    for m, s in S.items():
        if s.get(wkey) is None or not keep(m, s): continue
        if FT[m]["cbt"] > TMAX: continue
        if days and s["day"] not in days: continue
        r = SIM.get(m)
        if not r or "err" in r: continue
        F = r["_h"] + (1 if model == "jup" else 0)
        x = r.get(f"{cfg}|F{F}")
        if not x: continue
        out.append((x["pnl"], x["pnl0"], s[wkey], x["kind"], m))
    return out
D28 = {"10-28", "10-29", "10-30", "10-31", "11-01"}
print(f"P3 coins simulated: {sum(1 for m in S if m in SIM and 'err' not in SIM[m])} of {len(S)}; left out as too late (created after "
      f"{__import__('time').strftime('%m-%d %H:%M', __import__('time').gmtime(TMAX))} UTC): {sum(1 for m in S if FT[m]['cbt'] > TMAX)}")
print(f"\n(1) the rotation rule, R2 inside the quote set, 1 SOL                      {HDR}")
for cfg in ("float|ours|1.0", "jup|ours|1.0", "float|its|1.0"):
    base = cfg if cfg in RS else "float|ours|1.0"
    for name in ("A", "B"):
        Q = set(RS[cfg][name]) if cfg in RS else set(RS["float|ours|1.0"][name])
        lab = "set A (positive on P1)" if name == "A" else "set B (positive on P2)"
        for dl, days in (("Oct 27 - Nov 1", None), ("Oct 28 - Nov 1", D28)):
            L = rows(cfg, lambda m, s: s["quote"] in Q, "rot_w", days)
            st = stats(L)
            print(f"  {cfg:15s} {lab:23s} {dl:15s} {fmt(st)} {'PASS' if st['tot'] > 0 and st['wo2'] > 0 else ''}")
print("\n   by quote (float|ours|1.0, Oct 27 - Nov 1; total (sampled) [w/o best 2], its launch picks among the sampled coins)")
QA = set(RS["float|ours|1.0"]["A"]) | set(RS["float|ours|1.0"]["B"]) | set(RS["jup|ours|1.0"]["A"]) | set(RS["jup|ours|1.0"]["B"])
for q in sorted(QA, key=lambda q: sym(q)):
    for cfg in ("float|ours|1.0", "jup|ours|1.0"):
        L = rows(cfg, lambda m, s: s["quote"] == q, "rot_w")
        if not L: continue
        st = stats(L)
        pk = [picked(m) for _, _, _, _, m in L]
        inA = "A" if q in RS[cfg]["A"] else "-"; inB = "B" if q in RS[cfg]["B"] else "-"
        print(f"   {sym(q):10s} {cfg:15s} [{inA}{inB}] {st['tot']:+8.2f} ({st['n']:3d}, N {st['N']:5.0f}) [{st['wo2']:+7.2f}]  median {st['med']:+.3f}"
              f"  its picks {sum(1 for p in pk if p)} of {len(pk)}")
print(f"\n(2) wallet 4's own part-B launch buys (sampled from its transactions; weight = 1 / sampling rate), bought by us at launch")
for sel, f in (("all sizes", lambda m, s: True), ("1.45+ SOL", lambda m, s: (s.get("w4sol") or 0) >= 1.45), ("under 1.45", lambda m, s: (s.get("w4sol") or 0) < 1.45)):
    for cfg in ("float|ours|1.0", "float|its|1.0", "jup|ours|1.0", "jup|its|1.0"):
        for dl, days in (("Oct 27 - Nov 1", None), ("Oct 28 - Nov 1", D28)):
            st = stats(rows(cfg, f, "pick_w", days))
            print(f"  {sel:10s} {cfg:15s} {dl:15s} {fmt(st)} {'PASS' if st['tot'] > 0 and st['wo2'] > 0 else ''}")
print("\n   its buys by quote (float|ours|1.0, all sizes): total (sampled) [w/o best 2]")
g = collections.Counter(s["quote"] for s in S.values() if s.get("pick_w"))
for q, n in g.most_common(12):
    st = stats(rows("float|ours|1.0", lambda m, s: s["quote"] == q, "pick_w"))
    print(f"   {sym(q):10s} {st['tot']:+8.2f} ({st['n']:3d}, N {st['N']:5.0f}) [{st['wo2']:+7.2f}]")
