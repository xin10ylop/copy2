# Shared by the skip-filter scripts: the cached copies (base.py), the coin history before its buy (fetch_before.py),
# the bot's run with a skip rule (the slot limit applied, so a skipped copy frees a slot), and the measures the brief
# asks for. Blocks: A = Oct 21 18:30 - Oct 29 12:02 UTC, B = to Nov 6 05:32 UTC, C = after. Days are Beirut days
# (UTC+2); "full days" = Oct 22 - Nov 13 (23), as in ../../steady/.
import os, json, pickle, datetime, collections, random
SKQ = "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/skipq_opus"
LAND = (4, 8, "slot+1")
CAPS = {"SOL": 1, "WBTC": 2, "PUMP": 1, "SPCX": 1}
TB = 1793274720 + 600                                         # Oct 29 12:02 UTC
TC = datetime.datetime(2026, 11, 6, 5, 32, tzinfo=datetime.timezone.utc).timestamp()
blk = lambda t: 0 if t < TB else 1 if t < TC else 2
day = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d")
R = pickle.load(open(f"{SKQ}/base.pkl", "rb"))
for r in R:                                                   # the coin's history before its buy (one RPC call a coin)
    b = json.load(open(f"{SKQ}/before/{r['key']}.json"))["res"]
    ok = [x for x in b if x[2] and x[1]]
    f = r["f"]; f["n_before"] = len(ok); f["capped"] = len(b) >= 1000
    f["age_s"] = r["t"] - min(x[1] for x in b if x[1]) if b else 0          # a lower bound when capped
    f["tx_60s"] = sum(1 for x in ok if r["t"] - x[1] <= 60); f["tx_300s"] = sum(1 for x in ok if r["t"] - x[1] <= 300)
    f["fail_share"] = 1 - len(ok) / len(b) if b else 0.0
    r["blk"] = blk(r["t"]); r["day"] = day(r["t"])
    c = json.load(open(f"{SKQ}/create/{r['key']}.json"))            # the coin's first transaction: its creation
    ak = c["transaction"]["message"]["accountKeys"]; r["creator"] = ak[0]
    dev = sum(int(x["uiTokenAmount"]["amount"]) for x in c["meta"]["postTokenBalances"] if x["mint"] == r["mint"] and x.get("owner") == ak[0])
    f["dev_share"] = dev / 1e15; f["slots_since_create"] = r["slot"] - c["slot"]
    f["is_create"] = any("Instruction: Create" in l for l in c["meta"]["logMessages"] or [])
for r in R:                                                   # the creator's earlier coins that wallet 4 bought big
    prev = [q for q in R if q["t"] < r["t"] and q["creator"] == r["creator"]]
    r["f"]["creator_prev"] = len(prev)
    r["f"]["creator_prev_net"] = sum(q["res"][4][0] for q in prev if q["t"] + q["res"][4][2] < r["t"])
DAYS_ALL = sorted({r["day"] for r in R}); FULL = [d for d in DAYS_ALL if d not in ("10-21", "11-14")]
def sim(skip=None, n=4):
    """The bot's run at landing n: 2 open, CAPS; skip(rec, n) -> True drops the buy before it takes a slot.
    -> [(rec, net, why)] for the copies taken (refused buys included at their 0.0004 cost)."""
    out, open_ = [], []
    for r in R:
        open_ = [x for x in open_ if x[0] > r["t"]]
        if len(open_) >= 2 or sum(1 for x in open_ if x[1] == r["anchor"]) >= CAPS[r["anchor"]]: continue
        if skip is not None and skip(r, n): continue
        net, why, held = r["res"][n]
        if why != "refused": open_.append((r["t"] + held, r["anchor"]))
        out.append((r, net, why))
    return out
def measures(skip=None, base=None):
    """Everything the brief asks for, mean of the three landings unless said. base = measures(None) for kept/lost."""
    runs = {n: sim(skip, n) for n in LAND}
    m = dict(runs=runs)
    m["copies"] = sum(sum(1 for x in runs[n] if x[2] != "refused") for n in LAND) / 3
    m["net"] = sum(sum(x[1] for x in runs[n]) for n in LAND) / 3
    m["net_land"] = [sum(x[1] for x in runs[n]) for n in LAND]
    m["blocks"] = [sum(sum(x[1] for x in runs[n] if x[0]["blk"] == b) for n in LAND) / 3 for b in range(3)]
    srt = {n: sorted((x[1] for x in runs[n]), reverse=True) for n in LAND}
    m["wo5"] = sum(sum(srt[n][5:]) for n in LAND) / 3; m["wo10"] = sum(sum(srt[n][10:]) for n in LAND) / 3
    d = collections.defaultdict(float)
    for n in LAND:
        for r, net, why in runs[n]: d[r["day"]] += net / 3
    m["daynet"] = {k: d[k] for k in DAYS_ALL}
    v = [d[k] for k in FULL]; m["neg_days"] = sum(1 for x in v if x < 0); m["worst_day"] = min(v)
    falls = []
    for n in LAND:
        cum = hi = lo = 0.0
        for r, net, why in runs[n]: cum += net; hi = max(hi, cum); lo = min(lo, cum - hi)
        falls.append(lo)
    m["fall"] = sum(falls) / 3
    m["tp"] = sum(sum(1 for x in runs[n] if x[2] == "tp") for n in LAND) / 3
    m["tpkeys"] = {n: {x[0]["key"] for x in runs[n] if x[2] == "tp"} for n in LAND}
    if base is not None:
        m["tp_lost"] = sum(len(base["tpkeys"][n] - m["tpkeys"][n]) for n in LAND) / 3
        m["tp_new"] = sum(len(m["tpkeys"][n] - base["tpkeys"][n]) for n in LAND) / 3
        taken = {n: {x[0]["key"] for x in runs[n]} for n in LAND}
        m["loss_skipped"] = sum(sum(1 for x in base["runs"][n] if x[1] < 0 and x[2] != "refused" and x[0]["key"] not in taken[n]) for n in LAND) / 3
        m["loss_skipped_sol"] = sum(sum(x[1] for x in base["runs"][n] if x[1] < 0 and x[2] != "refused" and x[0]["key"] not in taken[n]) for n in LAND) / 3
        m["win_skipped_sol"] = sum(sum(x[1] for x in base["runs"][n] if x[1] > 0 and x[0]["key"] not in taken[n]) for n in LAND) / 3
        m["big20_lost"] = sum(sum(1 for x in base["big20"][n] if x[0]["key"] not in taken[n]) for n in LAND) / 3
        m["rows_skipped"] = sum(sum(1 for r in R if skip(r, n)) for n in LAND) / 3
    m["big20"] = {n: sorted(runs[n], key=lambda x: -x[1])[:20] for n in LAND}
    return m
def boot(m, base, draws=10000, seed=1):
    """Beirut days redrawn with replacement: share of draws where the filter's total beats the baseline's."""
    diff = [m["daynet"][k] - base["daynet"][k] for k in DAYS_ALL]; rnd = random.Random(seed); n = len(diff); win = 0
    for _ in range(draws):
        if sum(diff[rnd.randrange(n)] for _ in range(n)) > 0: win += 1
    return win / draws
HDR = "copies | TP (lost/new) | big20 lost | losers skipped (SOL) | wins skipped SOL | net    | w/o5   | w/o10  | A      B      C      | days<0 | worst | fall  | L4 / L8 / slot+1"
def row(m, base=None):
    s = f"{m['copies']:6.1f} | {m['tp']:4.1f}"
    s += f" ({m.get('tp_lost', 0):4.1f}/{m.get('tp_new', 0):3.1f})" if base else "            "
    s += f" | {m.get('big20_lost', 0):10.1f} | {m.get('loss_skipped', 0):5.1f} ({m.get('loss_skipped_sol', 0):+6.2f}) | {m.get('win_skipped_sol', 0):+16.2f}" if base else " |            |                      |                 "
    return s + (f" | {m['net']:+6.2f} | {m['wo5']:+6.2f} | {m['wo10']:+6.2f} | " + " ".join(f"{b:+6.2f}" for b in m["blocks"])
                + f" | {m['neg_days']:6d} | {m['worst_day']:+5.2f} | {m['fall']:+5.2f} | " + " / ".join(f"{x:+.2f}" for x in m["net_land"]))
