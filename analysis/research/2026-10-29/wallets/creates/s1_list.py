# Step 1: every signature on the pump mint authority (TSLvdd..., account #1 of create and create_v2, IDL
# crates/pump-codec/fixtures/idl/pump.json) for HOURS back from the newest, paging with before=.
#   python3 -I s1_list.py [HOURS=24]   ->  OUT/s1_sigs.json  [[sig, slot, blockTime, failed], ...] newest first
# The head is fixed on the first run (OUT/s1_head.json), so a rerun reads the same window from the cache.
import sys, os, time, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crc
H = float(sys.argv[1]) if len(sys.argv) > 1 else 24
hp = crc.OUT + "/s1_head.json"
if os.path.exists(hp): head = crc.json.load(open(hp))
else:
    head = crc.sigs(crc.MINT_AUTH, limit=1000, cache=False); crc.jdump(head, hp)
rows = list(head); t_end = head[0]["blockTime"]; t_lo = t_end - H * 3600
while rows[-1]["blockTime"] >= t_lo:
    page = crc.sigs(crc.MINT_AUTH, before=rows[-1]["signature"], limit=1000)
    if not page: break
    rows += page
    print(time.strftime("%H:%M:%S"), len(rows), time.strftime("%m-%d %H:%M", time.gmtime(rows[-1]["blockTime"])), flush=True)
rows = [r for r in rows if r["blockTime"] >= t_lo]
out = [[r["signature"], r["slot"], r["blockTime"], r.get("err") is not None] for r in rows]
crc.jdump(out, crc.OUT + "/s1_sigs.json")
ok = [r for r in out if not r[3]]
span = (out[0][2] - out[-1][2]) / 3600
print(f"window {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(out[-1][2]))} .. {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(out[0][2]))} UTC"
      f" ({span:.2f} h), slots {out[-1][1]}..{out[0][1]}: {len(out)} signatures, {len(ok)} landed, {len(ok)/span:.0f} landed an hour,"
      f" {(out[0][1]-out[-1][1])/(out[0][2]-out[-1][2]):.3f} slots/s")
byh = collections.Counter(time.strftime("%m-%d %H", time.gmtime(r[2])) for r in ok)
for k in sorted(byh): print(" ", k, byh[k])
