# Wallet 4's own exits on its routable 1.45+ SOL buys (the coins the copy follows), from the 31-minute curve paths
# (paths.json.gz from model.py): its first sale after its buy, the price then against the price its buy left, how long
# after, whether it sold everything at once. Classes as in fresh/early.py: tp (sold at 2.4x or more), stop (0.75x or
# less), timer (sold 1780-1870 s after its buy), early (before that, between the two), none (no sale in the window).
#   python3 -I rules.py SPD
import sys, json, gzip, datetime, collections, statistics
SPD = sys.argv[1]; W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
P = json.load(gzip.open(f"{SPD}/paths.json.gz")); rows = {f"{r['slot']}_{r['mint8']}": r for r in json.load(open(f"{SPD}/routable.json"))}
day = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d")
out = []
for k, (m, tr) in P.items():
    r = rows[k]; i = next((i for i, e in enumerate(tr) if e["user"] == W4 and e["buy"] and e["slot"] == r["slot"]), None)
    if i is None: continue
    b = tr[i]; vta = b["vt"]
    sells = [(j, e) for j, e in enumerate(tr[i + 1:], i + 1) if e["user"] == W4 and not e["buy"]]
    if not sells: out.append(dict(day=day(r["t"]), cls="none", px=None, dt=None, full=None, its=None)); continue
    j, s = sells[0]; px = (vta / tr[j - 1]["vt"]) ** 2; dt = s["t"] - b["t"]
    cls = "tp" if px >= 2.4 else "stop" if px <= 0.75 else "timer" if 1780 <= dt <= 1870 else "early" if dt < 1780 else "late"
    sold = sum(e["tok"] for _, e in sells); its = (sum(e["q"] for _, e in sells) - b["q"]) / b["q"]
    out.append(dict(day=day(r["t"]), cls=cls, px=px, dt=dt, full=sold >= 0.99 * b["tok"], its=its))
print(f"{len(out)} routable trips of wallet 4, Oct 28 20:34 to Nov 4 16:11 Beirut")
by = collections.defaultdict(list)
for o in out: by[o["day"]].append(o)
print(f"{'day':6s} {'trips':>5s} {'tp':>4s} {'stop':>4s} {'timer':>5s} {'early':>5s} {'none':>4s}  early: median price, median s   its own result per trip (quote)")
for d in sorted(by) + ["all"]:
    v = out if d == "all" else by[d]; c = collections.Counter(o["cls"] for o in v); e = [o for o in v if o["cls"] == "early"]
    res = [o["its"] for o in v if o["its"] is not None]
    print(f"{d:6s} {len(v):5d} {c['tp']:4d} {c['stop']:4d} {c['timer']:5d} {c['early']:5d} {c['none'] + c['late']:4d}  "
          + (f"{statistics.median(o['px'] for o in e):.2f}x {statistics.median(o['dt'] for o in e):4.0f} s" if e else "      -      ")
          + f"   mean {statistics.mean(res):+.1%}, sum {sum(res):+.2f}" if res else "")
c = collections.Counter(o["cls"] for o in out)
print(f"early-sale rate {c['early'] / len(out):.1%}  (Oct 19-22: 3.5%, Oct 23-27: 13.6%, Oct 27-28: 49.0%; fresh/README §2); "
      f"held to its timer {c['timer'] / len(out):.1%} (67%, 67%, 39%); sold all at once on {sum(1 for o in out if o['full']) / max(1, sum(1 for o in out if o['full'] is not None)):.0%}")
