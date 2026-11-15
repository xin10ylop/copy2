# Step 6. A second entry filter on top of the first: the bot already skips bps < 125; every filter of filters.py's
# grid (the same 150, cut values unchanged) added to it, scored the same way (better than "bps < 125 alone" in each of
# the blocks A, B and C).
#   python3 -I filters2.py > out/filters2.txt
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import common as C, filters as FI
LOW = lambda r, n: r["f"]["bps"] < 125
if __name__ == "__main__":
    base0 = C.measures(); base = C.measures(LOW, base0)
    print("bps < 125 alone (the new baseline here)"); print("   " + C.HDR); print("   " + C.row(base, base0))
    res = []
    for name, fn in FI.grid():
        if name.startswith("bps"): continue
        sk = lambda r, n, fn=fn: LOW(r, n) or fn(r, n); m = C.measures(sk, base)
        d = [m["blocks"][b] - base["blocks"][b] for b in range(3)]; res.append((name, m, d, all(x > 0 for x in d)))
    print(f"\n{len(res)} second filters tried; better than bps < 125 alone in all three blocks: {sum(1 for x in res if x[3])}")
    print("   " + "added filter".ljust(34) + " | change A / B / C      | all    | " + C.HDR + " | days ahead of bps<125 alone")
    for name, m, d, ok in sorted(res, key=lambda x: -sum(x[2]))[:25]:
        print(f"   {name:34s} | {d[0]:+6.2f} {d[1]:+6.2f} {d[2]:+6.2f} | {sum(d):+6.2f} | {C.row(m, base)} | {100 * C.boot(m, base):.1f}%{'  <- all three' if ok else ''}")
