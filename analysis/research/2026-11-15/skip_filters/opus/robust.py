# Step 4. The one family of entry filters that held in all three blocks (filters.py: skip coins whose curve fee `bps`
# is low) looked at from every side: finer thresholds, each landing in each block, without each block's best 2,
# within each kind of copy, the days redrawn, what it skips among our real trades, and the whole search of filters.py
# re-run on shuffled data (the features of the 781 buys dealt out again at random, 200 times) to see how often a
# search like ours finds a filter this good by chance.
#   python3 -I robust.py > out/robust.txt
import sys, os, random, collections
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import common as C, filters as FI
REAL = [("Ci9Bg1Bx", -0.0597, "time"), ("BttUQVPM", -0.0455, "time"), ("5tePJcGm", 0.3531, "tp"), ("7dDprVHP", -0.1106, "time"), ("57pQW4mw", -0.0124, "time"),
        ("Eymbsj8M", 0.6228, "tp"), ("GZn6HC8d", -0.3763, "time"), ("GaHAZThn", -0.1884, "time"), ("3EKoHX4f", -0.0600, "time"), ("6S3iL67j", -0.0907, "time"),
        ("BUdiaswB", 1.3340, "tp"), ("GLmWEbqA", -0.2837, "time"), ("3a8RGrQg", -0.2201, "time"), ("BTCmcoKg", 0.5786, "tp"), ("FAVdiH3q", -0.0851, "time"),
        ("KgcdZjU4", -0.2493, "time"), ("oxbezHbo", -0.4291, "its sale"), ("EH6yuh4Y", -0.4260, "time"), ("4TMzhGzY", -0.0310, "its sale"),
        ("6KpdMXAS", -0.2420, "its sale"), ("DHcZRxRX", -0.1991, "time"), ("8FE3SQjW", -0.0924, "its sale"), ("4A7n9wq8", -0.0703, "its sale"), ("BURn1o8x", 0.6038, "tp")]
def blocks_wo2(m):
    out = []
    for b in range(3):
        v = [sorted((x[1] for x in m["runs"][n] if x[0]["blk"] == b), reverse=True) for n in C.LAND]
        out.append(sum(sum(x[2:]) for x in v) / 3)
    return out
def cells(m):
    return [[sum(x[1] for x in m["runs"][n] if x[0]["blk"] == b) for b in range(3)] for n in C.LAND]
ORIG = [r["f"] for r in C.R]
def search(seed):
    """filters.py's whole grid on data whose feature rows are dealt out again at random: (filters better in all three
    blocks, the largest total gain among them)."""
    rnd = random.Random(seed); fs = ORIG[:]; rnd.shuffle(fs)
    for r, f in zip(C.R, fs): r["f"] = f
    base = C.measures(); best = None; npass = 0
    for name, fn in FI.grid():
        if name.startswith("refusal"): continue               # tied to the copy, not to the shuffled features
        m = C.measures(fn); d = [m["blocks"][b] - base["blocks"][b] for b in range(3)]
        if all(x > 0 for x in d):
            npass += 1; best = max(best or -1e9, sum(d))
    return npass, best
if __name__ == "__main__":
    base = C.measures(); b2 = blocks_wo2(base); bc = cells(base)
    print("baseline: blocks without each block's best 2:", " ".join(f"{x:+.2f}" for x in b2))
    print("\n== skip when the curve's fee is under X bps (its own trade's fee, read from its transaction)")
    print("   rule              | skipped | " + C.HDR + " | A/B/C w/o best 2 (change) | days ahead | landing 4 / 8 / slot+1 by block, change")
    for x in (10, 31, 50, 76, 101, 121, 125, 126, 131, 151, 196, 201):
        fn = lambda r, n, x=x: r["f"]["bps"] < x; m = C.measures(fn, base)
        w = blocks_wo2(m); c = cells(m)
        print(f"   bps < {x:<4d}        | {m['rows_skipped']:6.0f} | {C.row(m, base)} | " + " ".join(f"{w[b] - b2[b]:+5.2f}" for b in range(3))
              + f" | {100 * C.boot(m, base):5.1f}% | " + " ; ".join(" ".join(f"{c[i][b] - bc[i][b]:+5.2f}" for b in range(3)) for i in range(3)))
    print("\n== where the gain comes from: bps < 125 applied to one kind of copy only")
    for a in ("SOL", "WBTC", "PUMP"):
        fn = lambda r, n, a=a: r["f"]["bps"] < 125 and r["anchor"] == a; m = C.measures(fn, base)
        print(f"   {a:5s} only: skipped {m['rows_skipped']:4.0f} | change A/B/C " + " ".join(f"{m['blocks'][b] - base['blocks'][b]:+5.2f}" for b in range(3)) + f" | all {m['net'] - base['net']:+.2f} | TP lost {m['tp_lost']:.1f}")
    print("\n== every copy on its own (no slot limit), mean of landings, by fee group and kind: copies, take profits, net a copy")
    groups = (("bps < 125", lambda f: f["bps"] < 125), ("bps >= 125", lambda f: f["bps"] >= 125))
    for a in ("SOL", "WBTC", "PUMP", "SPCX", "all"):
        s = []
        for gname, g in groups:
            rs = [r for r in C.R if g(r["f"]) and (a == "all" or r["anchor"] == a)]
            if not rs: continue
            net = sum(sum(r["res"][n][0] for n in C.LAND) for r in rs) / 3; tp = sum(sum(r["res"][n][1] == "tp" for n in C.LAND) for r in rs) / 3
            bl = [sum(sum(r["res"][n][0] for n in C.LAND) for r in rs if r["blk"] == b) / 3 for b in range(3)]
            s.append(f"{gname}: {len(rs):3d} copies, {tp:4.1f} TP, {net / len(rs):+.4f} a copy (A/B/C {bl[0]:+.2f} {bl[1]:+.2f} {bl[2]:+.2f})")
        print(f"   {a:5s} | " + " | ".join(s))
    print("\n== our real trades (the bot's journal) and the rule bps < 125")
    by8 = {r["mint8"]: r for r in C.R}; sk = 0.0; kept = 0.0
    for m8, net, why in REAL:
        r = by8.get(m8)
        if r is None: print(f"   {m8} {net:+.4f} {why:9s} | not among the 781 buys"); kept += net; continue
        s = r["f"]["bps"] < 125
        print(f"   {m8} {net:+.4f} {why:9s} | bps {r['f']['bps']:3d} pays with {r['anchor']:4s} | {'SKIPPED' if s else 'kept'}")
        if s: sk += net
        else: kept += net
    print(f"   skipped trades' real net {sk:+.4f}; kept {kept:+.4f}")
    print("\n== the whole search on shuffled data, 200 times (refusal-limit rules left out: they belong to the copy)")
    with Pool(4) as p: S = p.map(search, range(200))
    real_pass = 2; real_best = None
    n_any = sum(1 for a, b in S if a > 0); n_ge = sum(1 for a, b in S if b is not None and b >= 4.95)
    print(f"   shuffles with at least one filter better in all three blocks: {n_any} of 200; with one gaining +4.95 SOL or more: {n_ge} of 200")
    print(f"   filters better in all three, per shuffle: mean {sum(a for a, b in S) / 200:.2f}, most {max(a for a, b in S)}")
    bests = sorted(b for a, b in S if b is not None); print("   the best such gain in the shuffles (those with one):", " ".join(f"{x:+.2f}" for x in bests[-15:]))
