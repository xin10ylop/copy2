# USDC-quoted creates mostly bypass the quote-control PDA (11 of the 15 USDC creates in the part-A agent's seeded sample
# of 1,500 landed mint-authority signatures, ../w4rev/out/s2_check.json, are not in its quote-control list), so u1's
# universe under-counts USDC. Estimate: the sample's USDC share x all landed mint-authority signatures of Oct 19-26
# (../w4rev/out/s1_sigs.json), with a Wilson 95% interval; wallet 4's USDC launch picks from ../w4rev/out/picks.json.
#   python3 -I u1b_usdc.py
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blib
R = blib.jl(blib.A_OUT + "/s2_check.json"); USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
n = len(R); k = sum(1 for v in R.values() if v and v["quote"] == USDC)
N = sum(1 for r in blib.jl(blib.A_OUT + "/s1_sigs.json") if not r[3] and blib.T_LO <= r[2] < blib.T_HI)
z = 1.96; p = k / n; c = (p + z * z / (2 * n)) / (1 + z * z / n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
P = blib.jl(blib.A_OUT + "/picks.json")
pk = [p_ for p_ in P.values() if p_.get("quote") == USDC and p_.get("ds") is not None and p_["ds"] <= 1 and blib.T_LO <= p_["cbt"] < blib.T_HI]
U = [t for t in blib.jl(blib.OUT + "/universe.json") if t["quote"] == USDC]
print(f"sample: {k} USDC creates in {n} landed mint-authority signatures; all landed in Oct 19-26: {N}")
print(f"USDC creates estimated {p * N:.0f} (95% {max(0, c - h) * N:.0f} - {(c + h) * N:.0f}); in the quote-control universe {len(U)}")
print(f"wallet 4's USDC launch picks {len(pk)} (1.45+: {sum(1 for x in pk if x['v'] >= 1.45)}), its net {sum(x['net'] for x in pk):+.2f}; "
      f"pick share about {len(pk) / (p * N):.2%} (95% {len(pk) / ((c + h) * N):.2%} - {len(pk) / max(1, (c - h) * N):.2%})")
