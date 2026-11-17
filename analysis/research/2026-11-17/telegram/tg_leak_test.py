# The leak test (the owner, Nov 17: "triple check that this bug is correct, that now all is correct"): every sign known at
# the call (s_*) computed twice, on the full data and on the data cut at the call (every trade after t deleted, the path
# kept alive by one placeholder far in the future so the lab keeps the row). A sign that uses only the past gives the
# same value both ways. Run on a lab file: the buggy one (before the fix) must differ, the fixed one must not.
#   python3 -I tg_leak_test.py TGDIR LAB_FILE
import sys, os, json, gzip, numpy as np
TG, LAB = sys.argv[1], sys.argv[2]; here = os.path.dirname(os.path.abspath(__file__))
def rows(cut):
    src = open(LAB).read().split("# ---- 1. signs")[0].split("rows.sort(key=lambda r: r[\"t\"])")[0]
    if cut:   # cut every path (and the trades behind holders, dev, bundle) at the call
        src = src.replace('load = ns["load"]', 'load = CUT_LOAD(ns["load"])').replace('x = json.load(gzip.open(f))', 'x = CUT_TR(json.load(gzip.open(f)), t)')
    def CUT_LOAD(f):
        def g(D):
            out = []
            for t, m, P in f(D):
                pre = [r for r in P if r[0] <= t]
                if pre: out.append((t, m, pre + [(t + 1e9,) + tuple(pre[-1][1:])]))
            return out
        return g
    def CUT_TR(x, t):
        x = dict(x); x["tr"] = [e for e in x.get("tr") or [] if e["t"] <= t]; return x
    os.environ["VDIR"] = "vip"; ns = {"__file__": os.path.join(here, "tg_vip_lab.py"), "CUT_LOAD": CUT_LOAD, "CUT_TR": CUT_TR}
    sys.argv = ["x", TG]; exec(compile(src, LAB, "exec"), ns); return {r["m"]: r for r in ns["rows"]}
full, cut = rows(False), rows(True)
keys = sorted({k for r in full.values() for k in r if k.startswith("s_")}); both = [m for m in full if m in cut]
print(f"{LAB}: {len(both)} calls compared")
bad_any = 0
for k in keys:
    diff = [m for m in both if k in full[m] and k in cut[m] and not np.isclose(full[m][k], cut[m][k], rtol=1e-9, atol=1e-12)]
    miss = sum(1 for m in both if (k in full[m]) != (k in cut[m]))
    bad_any += len(diff) + miss
    print(f"  {k:12s}: {'SAME on all' if not diff and not miss else f'DIFFERS on {len(diff)} calls' + (f', present/absent on {miss}' if miss else '')}"
          + (f"  e.g. {diff[0][:8]}: full {full[diff[0]][k]:.4g} vs cut {cut[diff[0]][k]:.4g}" if diff else ""))
print("VERDICT:", "NO LEAK: every sign at the call uses only data up to the call" if bad_any == 0 else "LEAK: some signs at the call depend on data after it")
