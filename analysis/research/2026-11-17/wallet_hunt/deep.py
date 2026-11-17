# The deep test of one wallet that passed on a small sample (FZU56d9i's lesson: +17% on 39 coins, +1.6% on 188). All its
# landed transactions back to T0 (default Oct 21 18:30 UTC, where wallet 4's study starts) into SP/hunt/tx/<w8>/, the
# bot's detection over them (examples/scan.rs, the seven floats), then our copy of EVERY routable first buy of 0.9+ SOL
# (step2_model.py's model, the frozen live setup), split by whether wallet 4 also traded the coin since Nov 3.
#   RPC_URL=... LK=<dir> python3 -I deep.py SP WALLET SCANBIN > out/deep_<w8>.txt
import sys, os, re, json, glob, time, bisect, datetime, subprocess, urllib.request
from concurrent.futures import ThreadPoolExecutor
import numpy as np
SP, W, BIN = sys.argv[1:4]; H = f"{SP}/hunt"; URL = os.environ["RPC_URL"]; D = f"{H}/tx/{W[:8]}"; os.makedirs(D, exist_ok=True)
T0 = datetime.datetime(2026, 10, 21, 18, 30, tzinfo=datetime.timezone.utc).timestamp(); WIN = 720
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-13/tab_exits"); import cmodel as M
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import hunt_lib as HL
def call(m, p):
    for i in range(8):
        try:
            rq = urllib.request.Request(URL, json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), {"Content-Type": "application/json"})
            r = json.load(urllib.request.urlopen(rq, timeout=60))
            if "error" in r: raise RuntimeError("rpc error")
            return r["result"]
        except Exception: time.sleep(1.5 * (i + 1))
    return None
SF = f"{H}/tx/{W[:8]}_deep_sigs.json"
if os.path.exists(SF): sigs = json.load(open(SF))
else:
    sigs, before = [], None
    while True:
        p = {"limit": 1000}
        if before: p["before"] = before
        r = call("getSignaturesForAddress", [W, p])
        if not r: break
        sigs += [[s["signature"], s["slot"], s["blockTime"]] for s in r if not s["err"] and (s["blockTime"] or 0) >= T0]
        before = r[-1]["signature"]
        if (r[-1]["blockTime"] or 0) < T0 or len(r) < 1000: break
    json.dump(sigs, open(SF, "w"))
todo = [s for s in sigs if not os.path.exists(f"{D}/{s[1]}_{s[0][:20]}.json")]
def get(s):
    t = call("getTransaction", [s[0], M.TXO])
    if t: json.dump(t, open(f"{D}/{s[1]}_{s[0][:20]}.json", "w"))
with ThreadPoolExecutor(48) as ex: list(ex.map(get, todo))
f = lambda t: datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%m-%d %H:%M")
print(f"{W}: {len(sigs)} landed transactions {f(sigs[-1][2])} to {f(sigs[0][2])} UTC ({len(todo)} newly fetched)", flush=True)
FL = ",".join(json.load(open(f"{SP}/newq/floatmints.json")).values())
out = subprocess.run([BIN, URL, D, f"{SP}/newq/prices.json", "0.9"], env=dict(os.environ, W=W, FLOATS=FL), capture_output=True, text=True).stdout
open(f"{H}/scan/{W[:8]}_deep.out", "w").write(out)
# every coin wallet 4 traded since Oct 21 18:30 UTC (w4_mints.py with T0)
W4M = json.load(open(f"{H}/w4_mints_all.json")); t_of = {s[1]: s[2] for s in sigs}; first = {}
for l in out.splitlines():
    m = re.match(r"(\d+) (\S{8}) ([\d.]+) SOL from (\S+) quote (\S+) jupiter (\S+): ROUTABLE hops (\d+)", l)
    if not m or int(m.group(1)) not in t_of: continue
    r = dict(slot=int(m.group(1)), t=t_of[int(m.group(1))], m8=m.group(2), sol=float(m.group(3)), frm=m.group(4), hops=int(m.group(7)))
    if r["m8"] not in first or r["t"] < first[r["m8"]]["t"]: first[r["m8"]] = r
S2 = sorted(sigs, key=lambda s: s[2]); T = [s[2] for s in S2]
def one(r):
    for fn in glob.glob(f"{D}/{r['slot']}_*.json"):
        tx = json.load(open(fn))
        for k in tx["meta"].get("postTokenBalances") or []:
            if not k["mint"].startswith(r["m8"]): continue
            if not [e for e in M.trades(tx, k["mint"]) if e["user"] == W and e["buy"]]: continue
            i = bisect.bisect_left(T, r["t"] + WIN)
            if i >= len(S2): return None
            try: tr = M.path(k["mint"], r["slot"], S2[i][0], threads=16)
            except Exception: return None
            j = next((x for x, e in enumerate(tr) if e["user"] == W and e["buy"] and e["slot"] == r["slot"]), None)
            if j is None: return None
            e = tr[j]; rate = r["sol"] * 1e9 / (e["q"] * (1 + e["bps"] / 1e4)); res, res2 = [], []
            for n in (4, 8, "slot+1"):
                p = HL.prep(tr, j, rate, n); p["hopf"] = 0.997 ** (r["hops"] - 1); res.append(HL.model(p)); res2.append(HL.model(p, early=None))
            w4 = k["mint"] in W4M and r["t"] <= 1794858000            # its data ends Nov 16 19:39 UTC
            return dict(r, mint=k["mint"], net=sum(q[0] for q in res) / 3, net2=sum(q[0] for q in res2) / 3, why=res[0][1], w4=w4)
    return None
B = [r for r in first.values() if r["sol"] >= 0.9]
with ThreadPoolExecutor(8) as ex: got = sorted([g for g in ex.map(one, B) if g], key=lambda g: g["t"])
json.dump(got, open(f"{H}/deep_{W[:8]}.json", "w"))
def show(nm, v):
    if not v: print(f"  {nm}: none"); return
    nets = sorted((g["net"] for g in v), reverse=True); c = [g for g in v if g["why"] != "refused"]; h = len(v) // 2
    days = sorted({f(g["t"])[:5] for g in v}); byday = {d: sum(g["net"] for g in v if f(g["t"])[:5] == d) for d in days}
    print(f"  {nm:34s}: {len(v):4d} copies ({f(v[0]['t'])[:5]} to {f(v[-1]['t'])[:5]}) | net {sum(nets):+6.2f} SOL {100 * sum(nets) / max(1, len(c)) / 0.5:+6.1f}% a copy,"
          f" won {100 * sum(1 for g in c if g['net'] > 0) / max(1, len(c)):3.0f}%, tp {sum(1 for g in c if g['why'] == 'tp')} | w/o best 5 {sum(nets[5:]):+6.2f}, w/o best 10 {sum(nets[10:]):+6.2f} |"
          f" halves {sum(g['net'] for g in v[:h]):+5.2f} / {sum(g['net'] for g in v[h:]):+5.2f} | losing days {sum(1 for x in byday.values() if x < 0)} of {len(days)} |"
          f" its sale never followed {sum(g['net2'] for g in v):+6.2f}")
print(f"routable first buys of 0.9+ SOL: {len(B)}; modelled {len(got)}")
show("every copy", got); show("coins wallet 4 did not trade", [g for g in got if not g["w4"]]); show("coins wallet 4 traded too", [g for g in got if g["w4"]])
for lo, hi in ((0.9, 1.5), (1.5, 3), (3, 99)): show(f"its buy {lo}-{hi} SOL", [g for g in got if lo <= g["sol"] < hi])
