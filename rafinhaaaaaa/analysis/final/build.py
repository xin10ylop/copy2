# Final pass, step 1: every GMGN activity row of a wallet over its 7-day window (rows/<wallet>.json), all its round trips
# rebuilt (stage3.trips_of; routing legs dropped), then at most MAXT of them kept, spread evenly over day x quote class
# (SOL / token) x its own buy-size tercile, so a small slice (wallet 4's copyable part was ~4% of its trips) keeps
# enough trips. Writes trips/<wallet>.json in the s3 layout. Window: the s3 file's if there is one, else the last 7 days.
#   MAXT=200 GMGN_API_KEY=... python3 -I build.py WALLET
import json, os, sys, time, subprocess, collections
F = os.path.dirname(os.path.abspath(__file__)); GO = os.path.dirname(F)
MAXT = int(os.environ.get("MAXT", "200"))

def gm(args):
    for i in range(4):
        r = subprocess.run(["gmgn-cli"] + args + ["--raw"], capture_output=True, text=True, timeout=120)
        try: return json.loads(r.stdout)
        except Exception: time.sleep(5 * (i + 1))
    return None

def fetch(w, T0):
    fn = f"{F}/rows/{w}.json"
    if os.path.exists(fn): return json.load(open(fn))["rows"]
    rows, cur = [], None
    for _ in range(600):
        a = ["portfolio", "activity", "--chain", "sol", "--wallet", w, "--limit", "100", "--type", "buy", "--type", "sell"]
        if cur: a += ["--cursor", cur]
        d = gm(a); time.sleep(0.35)
        for wait in (60, 120, 300):
            if d: break
            time.sleep(wait); d = gm(a)
        if not d: print(w[:8], "GMGN gave up at", len(rows), flush=True); break
        rows += d.get("activities") or []
        cur = d.get("next")
        if not cur or (rows and min(r["timestamp"] for r in rows) < T0): break
    json.dump(dict(wallet=w, t0=T0, rows=rows), open(fn, "w"))
    return rows

def trips_of(rows):                                     # stage3.trips_of, but oldest first within a second: GMGN lists
    # rows newest first, so a plain stable sort keyed a trip on the LAST of several same-second buys (G3, G6)
    rows = sorted(rows[::-1], key=lambda r: r["timestamp"]); pos, open_, done = {}, {}, []
    for r in rows:
        m = r["token"]["address"]; amt, px = float(r["token_amount"] or 0), float(r["price_usd"] or 0)
        if amt <= 0 or px <= 0: continue
        if r["event_type"] == "buy":
            if m not in open_:
                open_[m] = dict(mint=m, sym=r["token"].get("symbol"), quote=(r.get("quote_token") or {}).get("symbol"),
                                t0=r["timestamp"], px0=px, sig0=r["tx_hash"], usd_in=0.0, usd_out=0.0, peak=0.0, sells=[])
            t = open_[m]; t["usd_in"] += float(r.get("cost_usd") or 0); pos[m] = pos.get(m, 0.0) + amt; t["peak"] = max(t["peak"], pos[m])
        elif m in open_:
            t = open_[m]; sold = min(amt, pos.get(m, 0.0)); pos[m] = pos.get(m, 0.0) - sold; t["usd_out"] += float(r.get("cost_usd") or 0)
            t["sells"].append(dict(t=r["timestamp"], px=px, sig=r["tx_hash"], frac=sold / t["peak"] if t["peak"] else 0.0))
            if pos[m] <= 0.01 * t["peak"]: done.append(open_.pop(m)); pos[m] = 0.0
    return done

w = sys.argv[1]; s3f = f"{GO}/s3/{w}.json"
PREV = int(os.environ.get("PREV", "0"))                 # PREV=1: the week before (the out-of-sample check)
if os.path.exists(s3f): s3 = json.load(open(s3f)); T0, NOW = s3["t0"], s3["now"]
else: NOW = int(time.time()); T0 = NOW - 7 * 86400
if PREV: T0, NOW = T0 - 7 * 86400 * PREV, NOW - 7 * 86400 * PREV
if os.environ.get("WIN_T0"): T0, NOW = int(os.environ["WIN_T0"]), int(os.environ["WIN_NOW"])   # an explicit window
if os.environ.get("WIN_T0") and not PREV: PREV = 9                                                   # fetch its own rows file
SFX = os.environ.get("OUTSFX") or (f".prev{PREV}" if PREV else "")
_fetch = fetch
def fetch(w, T0):                                       # the previous week needs rows reaching further back
    if not PREV: return _fetch(w, T0)
    fn = f"{F}/rows/{w}{SFX}.json"
    if os.path.exists(fn): return json.load(open(fn))["rows"]
    keep = f"{F}/rows/{w}.json"; tmp = keep + ".hold"
    if os.path.exists(keep): os.rename(keep, tmp)
    try: rows = _fetch(w, T0); os.rename(keep, fn)
    finally:
        if os.path.exists(tmp): os.rename(tmp, keep)
    return rows
rows = fetch(w, T0)
allt = trips_of(rows)
legs = {(u["sig0"], u["quote"]) for u in allt}
allt = [t for t in allt if (t["sig0"], t["sym"]) not in legs and T0 <= t["t0"] < NOW]
keep = allt
if len(allt) > MAXT:
    sizes = sorted(t["usd_in"] for t in allt); q1, q2 = sizes[len(sizes) // 3], sizes[2 * len(sizes) // 3]
    cell = collections.defaultdict(list)
    for t in sorted(allt, key=lambda t: t["t0"]):
        cell[((t["t0"] - T0) // 86400, t["quote"] in ("WSOL", "SOL"), 0 if t["usd_in"] < q1 else 1 if t["usd_in"] < q2 else 2)].append(t)
    quota, left = {k: 0 for k in cell}, MAXT           # round-robin over the cells until MAXT
    while left > 0:
        moved = False
        for k, v in cell.items():
            if quota[k] < len(v) and left > 0: quota[k] += 1; left -= 1; moved = True
        if not moved: break
    keep = []
    for k, v in cell.items():                           # each cell's share spread evenly over its trips
        m = quota[k]; keep += [v[int((j + 0.5) * len(v) / m)] for j in range(m)] if m else []
    keep.sort(key=lambda t: t["t0"])
os.makedirs(f"{F}/trips", exist_ok=True)
json.dump(dict(wallet=w, rows=len(rows), t0=T0, now=NOW, trips_in_window=len(allt), trips=keep), open(f"{F}/trips/{w}{SFX}.json", "w"))
print(time.strftime("%H:%M:%S"), w[:8], len(rows), "rows,", len(allt), "trips in the window, kept", len(keep), flush=True)
