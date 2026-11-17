# KOLscope (an aggregator channel: "CALL ALERT: <name> @caller just called at <market cap>. <mint>", plus "DIP MODE" and
# "MULTIPLIER DETECTED" follow-ups): its call alerts split by caller into DIR/<caller>/calls.json (the format of
# tg_calls.py: [mint, unix time, text]), for every caller with MIN+ alerts, so tg_test.py and tg_pool.py score each caller.
# The export's times are local (TZ hours, as tg_calls.py). Also: the lag of KOLscope's alert after the caller's own post,
# for a caller whose own export is in OWNDIR (calls.json there).
#   python3 -I tg_kolscope.py DIR TZ [MIN=20] [OWNDIR]
import sys, os, re, json, html, collections, datetime as dt, statistics as st
D = sys.argv[1]; TZ = float(sys.argv[2]); MIN = int(sys.argv[3]) if len(sys.argv) > 3 else 20; OWN = sys.argv[4] if len(sys.argv) > 4 else None
raw = open(f"{D}/messages.html", encoding="utf-8").read()
A = collections.defaultdict(list)
for b in raw.split('<div class="message default')[1:]:
    tm = re.search(r'class="pull_right date details" title="([^"]+)"', b)
    if not tm: continue
    t = int(dt.datetime.strptime(tm.group(1).split(" UTC")[0], "%d %B %Y, %H:%M:%S").replace(tzinfo=dt.timezone(dt.timedelta(hours=TZ))).timestamp())
    txt = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", b.split('class="text"', 1)[-1])).split())
    m = re.search(r"CALL ALERT: .*?(@\w+) just called at \$?([\d.]+[KMB]?)\.\s*\S*\s*([1-9A-HJ-NP-Za-km-z]{32,44})", txt)
    if m: A[m.group(1)].append([m.group(3), t, f"{m.group(1)} at {m.group(2)}"])
n = 0
for c, v in sorted(A.items(), key=lambda x: -len(x[1])):
    if len(v) < MIN: continue
    seen, out = set(), []
    for x in sorted(v, key=lambda x: x[1]):
        if x[0] not in seen: seen.add(x[0]); out.append(x)
    os.makedirs(f"{D}/{c[1:]}", exist_ok=True); json.dump(out, open(f"{D}/{c[1:]}/calls.json", "w")); n += 1
    print(f"{c:24s} {len(v):4d} alerts, {len(out):4d} coins")
print(f"{n} callers with {MIN}+ alerts written")
if OWN:
    own = {a: t for a, t, _ in json.load(open(f"{OWN}/calls.json"))}
    name = "@" + os.path.basename(OWN.rstrip("/"))
    lag = [t - own[a] for a, t, _ in A.get(name, []) if a in own]
    if lag: print(f"lag of KOLscope's alert after {name}'s own post: {len(lag)} coins, median {st.median(lag):.0f} s, quartiles {st.quantiles(lag, n=4)}")
