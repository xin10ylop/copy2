# Fresh study: the paper copies that left behind its early sale (and the 2 the price limit refused), on the recorded path (_fpaths.json): our entry at its
# slot + 1 against its price, the price just before and just after its sale, and our exit over our entry (before fees).
#   python3 -I paper_early.py
import json
SP = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad/fresh3"
W = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
T = {x["m"][:8]: x for x in json.load(open(f"{SP}/h9long/{W[:8]}_trips.json"))}
P = {m[:8]: v for m, v in json.load(open(f"{SP}/h9long/{W[:8]}_fpaths.json")).items()}
for c in "CkFH2smc BPhav4G4 ChonQdJ8 FUCKKmZZ rAPE9kiT HytpiyuR 6DS5ErwH DJXThGNt 9hhXcHT9 3j9ex53k 5a7nDZcR EwsKTHxB 9ENc9LwF".split():
    x = T[c]; b, s = x["tr"]; vab = b["vt"]
    path = [r for r in P[c]["path"] if (r[0], r[1]) > (b["s"], b["i"] or 0)]
    ahead = [r for r in path if r[0] <= b["s"] + 1]; va = ahead[-1][5] if ahead else vab
    e, pre, post = (vab / va) ** 2, (vab / (s["vt"] - s["tok"])) ** 2, (vab / s["vt"]) ** 2
    print(f"   {c}  held {s['bt'] - b['bt']:5d} s  our entry {e:.3f}x its price  its sale: {pre:.3f}x before, {post:.3f}x after  our exit / entry {post / e:.3f}")
