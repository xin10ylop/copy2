# The owner, Nov 18: "are you sure you are treating the best 5 correctly? shouldnt it be a percentage of how much it
# trades?" A fixed "without the best 5" removes 0.3% of wallet 4's 1,559 copies but 12% of a 42-copy wallet's. Two fairer
# measures for every wallet, wallet 4 as the yardstick: (1) without the best 2% of copies (at least 1), the same share for
# all; (2) a bootstrap: 10,000 resamples of the copies (seed 7), the share with a positive mean, and the 5th percentile of
# the mean a copy. At 0.0345 SOL a round trip; each wallet under its exit named below (fixed: sell pressure 5/60, our
# standard, and its own sale; wallet 4 under the live model).
#   python3 -I r1_trim.py SP > out/r1_trim.txt
import sys, json, gzip, os, numpy as np
SP = sys.argv[1]; rng = np.random.default_rng(7)
def row(name, v):
    v = np.array(v); n = len(v); k = max(1, int(round(0.02 * n))); s = np.sort(v)
    bs = rng.choice(v, size=(10000, n)).mean(axis=1)
    print(f"{name:32s} {n:5d} | {v.sum():+7.2f} ({100 * v.mean() / 0.5:+6.1f}%) | w/o best 5 {s[:-5].sum() if n > 5 else 0:+7.2f} | "
          f"w/o best 2% ({k}) {s[:-k].sum():+7.2f} ({100 * s[:-k].mean() / 0.5:+6.1f}%) | P(mean > 0) {np.mean(bs > 0):5.1%} | 5th pct {100 * np.percentile(bs, 5) / 0.5:+6.1f}%")
print("wallet / exit                     copies | net (a copy) | the fixed test | the same share for all | bootstrap")
W = json.load(gzip.open(f"{SP}/hunt_screen.json.gz"))["H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"]
row("WALLET 4 (live model, 1.3+ SOL)", [r["net"] - 0.0319 for r in W if r["w4big"]])
row("WALLET 4 (live model, all)", [r["net"] - 0.0319 for r in W])
for w, suf in (("6ua7w2Gv", "_partial"), ("4sgdNABj", "_interim_p2"), ("B4BMZH3T", "_p2"), ("AnHnjfGJ", ""), ("Dj216RQs", ""), ("8Fux3NDf", ""), ("q2q38wAb", "_partial"), ("q2jJy82z", "_partial")):
    f = f"{SP}/winners/study_{w}{suf}.json"
    if not os.path.exists(f): continue
    R = [r for r in json.load(open(f)) if not r["refused"]]
    for e in ("sp5/60s", "its-sale"): row(f"{w}{suf} {e}", [r["ex"][e] - 0.0319 for r in R])
