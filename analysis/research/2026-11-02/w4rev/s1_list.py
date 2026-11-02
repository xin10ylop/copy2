# Step 1a: every signature on the pump mint authority (account #1 of create and create_v2) from Oct 29 00:00 UTC back to
# Oct 19 00:00 UTC, paged with getSignaturesForAddress from the oldest signature of the scan agent's listing
# (../agents/scan/out/s1_sigs.json, Oct 29 00:00 .. Oct 31 22:51).   python3 -I s1_list.py -> out/s1_sigs.json [[sig, slot, bt, failed]]
import sys, os, time, calendar, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
t_lo = calendar.timegm((2026, 10, 19, 0, 0, 0))
S = lib.jl(os.path.join(lib.HERE, "..", "agents", "scan", "out", "s1_sigs.json"))
start = min(S, key=lambda r: (r[1], r[2]))
rows = [dict(signature=start[0], slot=start[1], blockTime=start[2], err=None)]
t0 = time.time()
while rows[-1]["blockTime"] >= t_lo:
    page = lib.sigs(lib.MINT_AUTH, before=rows[-1]["signature"], limit=1000)
    if not page: break
    rows += page
    if len(rows) % 20000 < 1000: print(time.strftime("%H:%M:%S"), len(rows), time.strftime("%m-%d %H:%M", time.gmtime(rows[-1]["blockTime"])), flush=True)
rows = [r for r in rows[1:] if r["blockTime"] >= t_lo]
out = [[r["signature"], r["slot"], r["blockTime"], r.get("err") is not None] for r in rows]
lib.jdump(out, lib.OUT + "/s1_sigs.json")
ok = [r for r in out if not r[3]]; span = (out[0][2] - out[-1][2]) / 3600
print(f"window {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(out[-1][2]))} .. {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(out[0][2]))} UTC"
      f" ({span:.2f} h): {len(out)} signatures, {len(ok)} landed; calls {lib.crc.NCALLS[0]} in {time.time()-t0:.0f} s")
byd = collections.Counter(time.strftime("%m-%d", time.gmtime(r[2])) for r in ok)
print("landed by day (UTC):", sorted(byd.items()))
