# The quote mix of step 2's creates, with each quote's symbol from a create of a coin quoted in it when that quote is
# itself a pump coin (depth >= 1), the share of frenzy coins (step 3) and the initial virtual quote reserves.
#   python3 -I s2_mix.py  ->  stdout
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crc
C = crc.json.load(open(crc.OUT + "/s2_creates.json")); K = crc.json.load(open(crc.OUT + "/s3_coins.json"))
rows = [r for r in C.values() if r.get("ncreate")]
sym = {r["mint"]: r.get("sym") for r in rows}
q = collections.Counter(r["quote"] for r in rows); tot = len(rows)
oth = {k: v for k, v in q.items() if k not in crc.SOL_LIKE}; no = sum(oth.values())
print(f"{tot} creates with a CreateEvent; SOL quote {tot-no} ({(tot-no)/tot:.1%}), other quote {no} ({no/tot:.1%}) in {len(oth)} quote mints")
fr = collections.Counter(K[m]["quote"] for m in K if "err" not in K[m] and K[m]["s0"] + K[m]["s1"] + K[m]["s2"] >= 4)
dep = collections.Counter(r.get("depth") for r in rows if r["quote"] not in crc.SOL_LIKE)
print("depth (0 = quote is a plain token, 1+ = quote is itself a pump coin):", dict(dep))
print("quote mint                                     creates  share  frenzy  frenzy%  initial vquote  symbol(if pump coin in window)")
for k, v in sorted(oth.items(), key=lambda kv: -kv[1])[:30]:
    vq = collections.Counter(r.get("vquote") for r in rows if r["quote"] == k).most_common(1)[0][0]
    print(f"{k:46s} {v:7d} {v/no:6.1%} {fr.get(k,0):7d} {fr.get(k,0)/v:7.0%} {vq:15d}  {sym.get(k, '')}")
rest = sorted(oth.items(), key=lambda kv: -kv[1])[30:]
print(f"... {len(rest)} more quote mints with {sum(v for _, v in rest)} creates ({sum(v for _, v in rest)/no:.1%}), "
      f"{sum(fr.get(k,0) for k,_ in rest)} frenzy")
