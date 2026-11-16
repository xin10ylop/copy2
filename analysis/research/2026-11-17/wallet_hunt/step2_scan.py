# Step 2b: what each candidate buys on its own. The bot's detection and route planner (examples/scan.rs, W=<wallet>,
# the seven floats) over its fetched transactions: every buy of a coin priced in another token, its SOL value, the
# route or why none. Then by wallet: buys of 0.9+ SOL a day, routable, and how many are coins wallet 4 also traded
# (since Nov 3, w4_mints.json): only the others can add trades. -> SP/hunt/scan/<w8>.out, SP/hunt/rows.json
#   RPC_URL=... python3 -I step2_scan.py SP SCANBIN
import sys, os, re, json, subprocess, datetime, collections
SP, BIN = sys.argv[1], sys.argv[2]; H = f"{SP}/hunt"; os.makedirs(f"{H}/scan", exist_ok=True)
FL = ",".join(json.load(open(f"{SP}/newq/floatmints.json")).values())
W4M = json.load(open(f"{H}/w4_mints.json")); W4LAST = 1794858000            # Nov 16 19:39 UTC, its last transaction on disk
full = {w[:8]: w for w in json.load(open(f"{SP}/hunt_cands.json"))}
done = {l.split(':')[0] for l in open(f"{H}/fetch.log") if 'landed signatures' in l}   # fetched in full
rows = {}
for w8 in sorted(os.listdir(f"{H}/tx")):
    D = f"{H}/tx/{w8}"
    if not os.path.isdir(D) or w8 not in full or w8 not in done: continue
    out = f"{H}/scan/{w8}.out"
    if not os.path.exists(out):
        r = subprocess.run([BIN, os.environ["RPC_URL"], D, f"{SP}/newq/prices.json", "0.9"], env=dict(os.environ, W=full[w8], FLOATS=FL), capture_output=True, text=True)
        open(out, "w").write(r.stdout)
    sigs = json.load(open(f"{H}/tx/{w8}_sigs.json"))[:6000]; t_of = {s[1]: s[2] for s in sigs}
    R = []
    for l in open(out):
        m = re.match(r"(\d+) (\S{8}) ([\d.]+) SOL from (\S+) quote (\S+) jupiter (\S+): (.*)", l)
        if not m: continue
        slot = int(m.group(1)); t = t_of.get(slot)
        if t is None: continue
        rt = re.match(r"ROUTABLE hops (\d+) how (\S+)", m.group(7))
        mint = next((k for k in W4M if k.startswith(m.group(2))), None)
        R.append(dict(slot=slot, t=t, m8=m.group(2), sol=float(m.group(3)), frm=m.group(4), quote=m.group(5), routable=bool(rt), hops=int(rt.group(1)) if rt else None,
                      how=rt.group(2) if rt else m.group(7)[:60], w4=("yes" if mint else ("?" if t > W4LAST else "no"))))
    rows[full[w8]] = R
json.dump(rows, open(f"{H}/rows.json", "w"))
f = lambda t: datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%m-%d %H:%M")
print("wallet   | its transactions fetched: span | other-token buys of 0.9+ SOL: all, a day | routable | of those: wallet 4 also traded the coin / not / after our data")
for w, R in sorted(rows.items(), key=lambda x: -sum(1 for r in x[1] if r["routable"] and r["w4"] == "no")):
    sigs = json.load(open(f"{H}/tx/{w[:8]}_sigs.json"))[:6000]; span = (sigs[0][2] - sigs[-1][2]) / 86400 if sigs else 0
    first = {}
    for r in sorted(R, key=lambda r: r["t"]): first.setdefault(r["m8"], r)
    F = list(first.values()); ro = [r for r in F if r["routable"]]; c = collections.Counter(r["w4"] for r in ro)
    print(f"{w[:8]} | {len(sigs):5d} txs {f(sigs[-1][2]) if sigs else '-'} to {f(sigs[0][2]) if sigs else '-'} ({span:4.1f} d) | {len(F):4d}, {len(F) / max(span, 0.1):5.1f} a day | {len(ro):4d} |"
          f" {c['yes']:4d} / {c['no']:4d} / {c['?']:3d}")
