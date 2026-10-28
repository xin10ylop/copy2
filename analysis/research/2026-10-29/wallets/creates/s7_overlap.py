# Step 7: is a top wallet independent of wallet 4, or does it follow it? For each wallet: the coins it shares with
# wallet 4 (both bought at +0/+1), and on those, whether it bought before or after wallet 4 (slot, then index).
#   python3 -I s7_overlap.py WALLET ...  ->  stdout
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crc
R = crc.json.load(open(crc.OUT + "/s5_rank.json")); W = R["coins"][crc.W4]
print("wallet                                        coins  shared  share  before w4  same slot after  later slot after")
for u in sys.argv[1:]:
    cs = R["coins"].get(u)
    if not cs: print(u, "not saved"); continue
    sh = [m for m in cs if m in W]
    bef = sum(1 for m in sh if (cs[m]["slot"], cs[m]["idx"] or 0) < (W[m]["slot"], W[m]["idx"] or 0))
    same = sum(1 for m in sh if cs[m]["slot"] == W[m]["slot"] and (cs[m]["idx"] or 0) > (W[m]["idx"] or 0))
    later = sum(1 for m in sh if cs[m]["slot"] > W[m]["slot"])
    print(f"{u:44s} {len(cs):6d} {len(sh):7d} {len(sh)/len(cs):6.0%} {bef:10d} {same:16d} {later:17d}")
