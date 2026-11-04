# Does Jupiter quote a coin seconds after its first pool? Polls Jupiter's recent-token list and quotes each new coin
# at once (0.05 SOL in): python3 -I fresh_probe.py SECONDS OUT_JSON
import json, sys, time, urllib.request, datetime
T, out = float(sys.argv[1]), sys.argv[2]; t_end = time.time() + T; last = [0.0]
def get(url):
    dt = time.time() - last[0]
    if dt < 1.1: time.sleep(1.1 - dt)
    last[0] = time.time(); t0 = time.time()
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "probe"}), timeout=15)
        return r.status, json.loads(r.read()), time.time() - t0
    except urllib.error.HTTPError as e: return e.code, None, time.time() - t0
    except Exception as e: return 0, None, time.time() - t0
seen, rows = set(), []
SOL = "So11111111111111111111111111111111111111112"
while time.time() < t_end:
    st, d, _ = get("https://lite-api.jup.ag/tokens/v2/recent")
    if st != 200 or not d: time.sleep(3); continue
    for x in d:
        m = x["id"]
        if m in seen: continue
        seen.add(m)
        fp = (x.get("firstPool") or {}).get("createdAt")
        if not fp: continue
        age = time.time() - datetime.datetime.fromisoformat(fp.replace("Z", "+00:00")).timestamp()
        if age > 20: continue
        st2, q, lat = get(f"https://lite-api.jup.ag/swap/v1/quote?inputMint={SOL}&outputMint={m}&amount=50000000&slippageBps=2000")
        route = [r["swapInfo"]["label"] for r in (q or {}).get("routePlan", [])] if q else None
        rows.append(dict(mint=m, launchpad=x.get("launchpad"), age_at_quote=round(age + lat, 1), http=st2, route=route,
                         ctx=(q or {}).get("contextSlot"), lat=round(lat, 3)))
        print(rows[-1], flush=True)
json.dump(rows, open(out, "w"))
