# SolHouse VIP's export: its "New Solana Gem Alert" calls (not the whale, volume or ad posts), each with the market cap,
# age, pool, "spotted in N channels" and the tier tag at its end (Diamond / Safe / Gamble / Gamble Risk). A coin's call =
# its first alert. A random sample of at most N per tier (seed 7; the whole export is ~4,500 calls, too many to price in
# an hour) -> DIR/calls.json for tg_test.py / tg_pool.py and DIR/meta.json {mint: {tier, mc, age, pool, spotted}}.
#   python3 -I tg_vip_calls.py DIR TZ [N=250]
import sys, re, json, html, random, collections, datetime as dt
D = sys.argv[1]; TZ = float(sys.argv[2]); N = int(sys.argv[3]) if len(sys.argv) > 3 else 250
def num(s):
    s = s.replace(",", ""); return float(s[:-1]) * {"K": 1e3, "M": 1e6, "B": 1e9}[s[-1]] if s[-1] in "KMB" else float(s)
TIERS = [("Diamond", "💎 Diamond"), ("Gamble Risk", "Gamble Risk"), ("Safe", "Safe"), ("Gamble", "Gamble")]
raw = open(f"{D}/messages.html", encoding="utf-8").read(); first, meta = {}, {}
for b in raw.split('<div class="message default')[1:]:
    tm = re.search(r'class="pull_right date details" title="([^"]+)"', b)
    txt = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", b.split('class="text"', 1)[-1])).split())
    if not tm or "New Solana Gem Alert" not in txt: continue
    ca = re.search(r"Contract Address\s*:\s*([1-9A-HJ-NP-Za-km-z]{32,44})", txt)
    if not ca or ca.group(1) in first: continue
    t = int(dt.datetime.strptime(tm.group(1).split(" UTC")[0], "%d %B %Y, %H:%M:%S").replace(tzinfo=dt.timezone(dt.timedelta(hours=TZ))).timestamp())
    tail = txt.split("Website")[-1]
    tier = next((name for name, key in TIERS if key in tail), "none")
    g = lambda pat: (re.search(pat, txt) or [None, None])[1]
    first[ca.group(1)] = t
    meta[ca.group(1)] = dict(tier=tier, mc=num(g(r"Market Cap\s*:\s*([\d.,]+[KMB]?)") or "0"), age=g(r"Age\s*:\s*(\S+)"),
                             pool=g(r"Pool\s*:\s*([^·]+)"), spotted=int(g(r"Spotted in\s*:\s*(\d+)") or 0),
                             vol=num(g(r"Volume \(24h\)\s*:\s*([\d.,]+[KMB]?)") or "0"), txns=num(g(r"Txns \(24h\)\s*:\s*([\d.,]+[KMB]?)") or "0"))
by = collections.defaultdict(list)
for m in first: by[meta[m]["tier"]].append(m)
rnd = random.Random(7); pick = []
for tier, ms in by.items(): pick += rnd.sample(sorted(ms), min(N, len(ms)))
calls = sorted([[m, first[m], meta[m]["tier"]] for m in pick], key=lambda x: x[1])
json.dump(calls, open(f"{D}/calls.json", "w")); json.dump(meta, open(f"{D}/meta.json", "w"))
print(f"{len(first)} coins called; by tier: " + ", ".join(f"{k} {len(v)}" for k, v in sorted(by.items(), key=lambda x: -len(x[1]))))
print("pools: " + ", ".join(f"{k.strip()} {v}" for k, v in collections.Counter((meta[m]['pool'] or '?').strip() for m in first).most_common(5)))
print(f"sampled {len(calls)} (at most {N} a tier)")
