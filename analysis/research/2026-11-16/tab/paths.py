# Step 2b: the 31-minute path of every coin the bot could copy from TAB16RxX (the scan with the six floats, 0.5+ SOL),
# built by ../../2026-11-13/tab_exits/cmodel.py (model.py for any wallet), one file a coin in LK/paths; the ones
# already there are kept. A coin bought again within the hour is skipped, as the bot skips it.
#   RPC_URL=... LK=<tab/lk> python3 -I paths.py TXDIR SIGS.json SCAN_OUT
import sys, os, re, json, glob, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-13/tab_exits"); import cmodel as M
W = "TAB16RxXmazWzCTpJbnKiREWUybdEoskuyidaV291u3"; TXDIR, SIGS, SCAN = sys.argv[1:4]
sigs = sorted(json.load(open(SIGS)), key=lambda s: s[2])
byslot = {}
for f in glob.glob(f"{TXDIR}/*.json"): byslot.setdefault(int(os.path.basename(f).split("_")[0]), []).append(f)
rows = []
for l in open(SCAN):
    m = re.match(r"(\d+) (\S{8}) ([\d.]+) SOL from (\S+) quote (\S+) jupiter (\S+): ROUTABLE", l)
    if not m: continue
    slot, m8 = int(m.group(1)), m.group(2)
    for f in byslot.get(slot, []):
        t = json.load(open(f))
        mint = next((b["mint"] for b in t["meta"].get("postTokenBalances") or [] if b.get("owner") == W and b["mint"].startswith(m8)), None)
        if mint: rows.append(dict(m=mint, slot=slot, t=t["blockTime"])); break
rows.sort(key=lambda r: r["t"]); last, todo = {}, []
for r in rows:
    again = r["m"] in last and r["t"] - last[r["m"]] < 3600; last[r["m"]] = r["t"]
    if not again and r["t"] + 1880 < sigs[-1][2]: todo.append(r)
need = [r for r in todo if not os.path.exists(f"{M.PC}/{r['slot']}_{r['m']}.json.gz")]
print(f"{len(rows)} routable buys, {len(todo)} to model, {len(need)} paths to fetch", flush=True)
anchor = lambda t: next((s[0] for s in sigs if s[2] >= t + 1880), sigs[-1][0])
n = [0]; t0 = time.time()
def getp(r):
    try: tr = M.path(r["m"], r["slot"], anchor(r["t"]), threads=6)
    except Exception as e: print("path failed", r["m"][:8], str(e)[:60].replace(os.environ["RPC_URL"], "<rpc>"), flush=True); return
    n[0] += 1
    if n[0] % 20 == 0: print(f"{n[0]} paths, {time.time() - t0:.0f} s", flush=True)
with ThreadPoolExecutor(4) as ex: list(ex.map(getp, need))
print("done", len(os.listdir(M.PC)), flush=True)
