# Step 1d: every signature on pump's quote-control PDA (["quote-control"], pump program; account #19 of a create_v2 with a
# quote tail, crates/pump-codec tests/adversarial.rs), from now back to Oct 19 00:00 UTC: the other-quote creates
# (checked against the mint-authority sample in s2_check.py).   python3 -I s1c_qc_list.py -> out/qc_sigs.json [[sig, slot, bt, failed]]
import sys, os, time, calendar, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
t_lo = calendar.timegm((2026, 10, 19, 0, 0, 0))
QC = lib.find_pda([b"quote-control"], lib.PUMP)
hp = lib.OUT + "/qc_head.json"
if os.path.exists(hp): head = lib.jl(hp)
else: head = lib.sigs(QC, limit=1000, cache=False); lib.jdump(head, hp)
rows = list(head); t0 = time.time()
while rows[-1]["blockTime"] >= t_lo:
    page = lib.sigs(QC, before=rows[-1]["signature"], limit=1000)
    if not page: break
    rows += page
    if len(rows) % 20000 < 1000: print(time.strftime("%H:%M:%S"), len(rows), time.strftime("%m-%d %H:%M", time.gmtime(rows[-1]["blockTime"])), flush=True)
rows = [r for r in rows if r["blockTime"] >= t_lo]
out = [[r["signature"], r["slot"], r["blockTime"], r.get("err") is not None] for r in rows]
lib.jdump(out, lib.OUT + "/qc_sigs.json")
ok = [r for r in out if not r[3]]
print(f"quote-control {QC}: {len(out)} signatures, {len(ok)} landed, {time.strftime('%F %T', time.gmtime(out[-1][2]))} .. {time.strftime('%F %T', time.gmtime(out[0][2]))} UTC; calls {lib.crc.NCALLS[0]} in {time.time()-t0:.0f} s")
print("landed by day (UTC):", sorted(collections.Counter(time.strftime("%m-%d", time.gmtime(r[2])) for r in ok).items()))
