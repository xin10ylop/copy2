# SolHouse VIP, the parts not yet tested (the owner, Nov 17: "you found something not working and decided to stop"): its
# gem alerts on coins already in a PumpSwap pool at the call, and its other posts: "Whale Update on a VIP call" (a whale
# bought a coin the VIP called), "VOLUME ALERT", "SolHouse Whale Alert". Each becomes a calls.json (mint, post time,
# label) in its own folder beside the export, for tg_pool.py. A coin's call = its first post of that type.
#   python3 -I tg_vip_other.py VIPDIR TZ [N=300]
import sys, os, re, json, html, random, datetime as dt
D = sys.argv[1]; TZ = float(sys.argv[2]); N = int(sys.argv[3]) if len(sys.argv) > 3 else 300
raw = open(f"{D}/messages.html", encoding="utf-8").read()
KINDS = {"whaleup": "Whale Update on a VIP call", "volume": "VOLUME ALERT", "whale": "SolHouse Whale Alert"}
out = {k: {} for k in KINDS}
for b in raw.split('<div class="message default')[1:]:
    tm = re.search(r'class="pull_right date details" title="([^"]+)"', b)
    txt = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", b.split('class="text"', 1)[-1])).split())
    ca = re.search(r"Contract Address\s*:\s*([1-9A-HJ-NP-Za-km-z]{32,44})", txt)
    if not tm or not ca: continue
    t = int(dt.datetime.strptime(tm.group(1).split(" UTC")[0], "%d %B %Y, %H:%M:%S").replace(tzinfo=dt.timezone(dt.timedelta(hours=TZ))).timestamp())
    for k, key in KINDS.items():
        if key in txt and ca.group(1) not in out[k]:
            pool = (re.search(r"Pool\s*:\s*([^·]+)", txt) or [None, "?"])[1].strip()
            out[k][ca.group(1)] = [ca.group(1), t, f"{k} {pool}"]
meta = json.load(open(f"{D}/meta.json"))
pool = sorted([[m, v["t"], f"gem {v['tier']}"] for m, v in meta.items() if (v.get("pool") or "").strip() == "PumpSwap"], key=lambda x: x[1])
random.Random(7).shuffle(pool); out["poolgem"] = {x[0]: x for x in pool[:N]}
base = os.path.dirname(D.rstrip("/"))
for k, v in out.items():
    d = f"{base}/vip_{k}"; os.makedirs(d, exist_ok=True); c = sorted(v.values(), key=lambda x: x[1])
    json.dump(c, open(f"{d}/calls.json", "w")); print(f"vip_{k}: {len(c)} calls" + (f" (a random {N} of {len(pool)} gem alerts in a PumpSwap pool)" if k == "poolgem" else ""))
