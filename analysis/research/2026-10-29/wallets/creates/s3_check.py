# Check of step 3's shortcut: for N random frenzy coins, the full signature list paged back from the newest (no cache)
# against s3's list, compared on slots +0..+3 (s3's lists cover at least +0..+3).
#   python3 -I s3_check.py [N=30]  ->  stdout
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crc
N = int(sys.argv[1]) if len(sys.argv) > 1 else 30
K = crc.json.load(open(crc.OUT + "/s3_coins.json"))
fr = sorted(m for m, r in K.items() if "err" not in r and r["s0"] + r["s1"] + r["s2"] >= 4)
random.seed(29); pick = random.sample(fr, N); same = 0
for m in pick:
    r = K[m]; rows, before = [], None
    for _ in range(30):
        page = crc.sigs(m, before=before, until=r["csig"], limit=1000, cache=False); rows += page
        if len(page) < 1000: break
        before = page[-1]["signature"]
    full = sorted(p["signature"] for p in rows if p.get("err") is None and p["slot"] - r["slot"] <= 3)
    mine = sorted(s for s, sl, bt in crc.json.load(open(f"{crc.OUT}/s3_sigs/{m}.json")) if sl - r["slot"] <= 3)
    same += full == mine
    if full != mine: print("differs", m, len(full), len(mine))
print(f"{same} of {N} identical on slots +0..+3")
