# Telegram call test, step 1: the calls in a channel's exported history (Telegram Desktop, HTML or JSON). Each message's
# time (the export's local time; the zone is set by TZ hours and checked on the chain in step 2), its text, and every
# Solana address in it; a coin's call = its first mention. Out: <dir>/calls.json [[mint, unix time, text start], ...].
#   python3 -I tg_calls.py DIR TZ_HOURS
import sys, os, re, json, html, datetime as dt
D = sys.argv[1]; TZ = float(sys.argv[2])
ADDR = re.compile(r"(?<![1-9A-HJ-NP-Za-km-z])[1-9A-HJ-NP-Za-km-z]{32,44}(?![1-9A-HJ-NP-Za-km-z])")
msgs = []
if os.path.exists(f"{D}/result.json"):
    for m in json.load(open(f"{D}/result.json"))["messages"]:
        t = m.get("date_unixtime"); txt = m.get("text")
        if isinstance(txt, list): txt = "".join(x if isinstance(x, str) else x.get("text", "") + " " + x.get("href", "") for x in txt)
        if t: msgs.append((int(t), txt or ""))
else:
    raw = open(f"{D}/messages.html", encoding="utf-8").read()
    for blk in raw.split('<div class="message default')[1:]:
        tm = re.search(r'class="pull_right date details" title="([^"]+)"', blk)
        if not tm: continue
        s = tm.group(1).split(" UTC")[0]
        t = dt.datetime.strptime(s, "%d %B %Y, %H:%M:%S").replace(tzinfo=dt.timezone(dt.timedelta(hours=TZ)))
        body = html.unescape(re.sub(r"<[^>]+>", " ", blk.split('class="from_name"', 1)[-1]))
        hrefs = " ".join(re.findall(r'href="([^"]+)"', blk))
        msgs.append((int(t.timestamp()), body + " " + hrefs))
calls, seen = [], set()
for t, txt in sorted(msgs):
    for a in ADDR.findall(txt):
        if a in seen: continue
        seen.add(a); calls.append([a, t, " ".join(txt.split())[:80]])
json.dump(calls, open(f"{D}/calls.json", "w"))
print(f"{len(msgs)} messages, {len(calls)} first mentions of an address; "
      f"{dt.datetime.fromtimestamp(msgs[0][0], dt.timezone.utc):%m-%d %H:%M} to {dt.datetime.fromtimestamp(msgs[-1][0], dt.timezone.utc):%m-%d %H:%M} UTC")
