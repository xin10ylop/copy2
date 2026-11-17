# SolHouse Signal (an automated channel, 18k subscribers): its public "Exclusive Solana Gem Alert" posts carry the VIP
# call's market cap and the market cap at the public post ("Market Cap : 62.72K ( VIP Call ) -> 138.22K (2x ACHIEVED!)").
# The public post comes after the paid VIP call. This writes the public calls (gem alerts only, not the paid-listing or
# whale posts) to DIR/calls.json for tg_test.py / tg_pool.py, and DIR/vip.json {mint: VIP mc / public mc}: the price
# ratio at which the VIP call was made, to place it on the chain before the public post.
#   python3 -I tg_solhouse.py DIR TZ
import sys, re, json, html, datetime as dt
D = sys.argv[1]; TZ = float(sys.argv[2])
def num(s): return float(s[:-1]) * {"K": 1e3, "M": 1e6, "B": 1e9}[s[-1]] if s[-1] in "KMB" else float(s)
raw = open(f"{D}/messages.html", encoding="utf-8").read(); calls, vip, seen = [], {}, set()
for b in raw.split('<div class="message default')[1:]:
    tm = re.search(r'class="pull_right date details" title="([^"]+)"', b)
    txt = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", b.split('class="text"', 1)[-1])).split())
    if not tm or "Gem Alert" not in txt: continue
    m = re.search(r"Market Cap\s*:\s*([\d.]+[KMB]?)\s*\(\s*VIP Call\s*\)\s*\S*\s*([\d.]+[KMB]?)", txt)
    ca = re.search(r"Contract Address\s*:\s*([1-9A-HJ-NP-Za-km-z]{32,44})", txt)
    if not ca or ca.group(1) in seen: continue
    t = int(dt.datetime.strptime(tm.group(1).split(" UTC")[0], "%d %B %Y, %H:%M:%S").replace(tzinfo=dt.timezone(dt.timedelta(hours=TZ))).timestamp())
    seen.add(ca.group(1)); calls.append([ca.group(1), t, txt[:80]])
    if m: vip[ca.group(1)] = num(m.group(1)) / num(m.group(2))
json.dump(calls, open(f"{D}/calls.json", "w")); json.dump(vip, open(f"{D}/vip.json", "w"))
r = sorted(vip.values())
print(f"{len(calls)} gem alerts (coins); VIP mc / public mc known for {len(vip)}: median {r[len(r) // 2]:.2f} "
      f"(the public post came at {1 / r[len(r) // 2]:.1f}x the VIP price, median); under 0.5 (2x+ already): {sum(x < 0.5 for x in r)}")
