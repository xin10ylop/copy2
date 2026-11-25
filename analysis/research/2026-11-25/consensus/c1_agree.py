# When two of our wallets agree (Nov 25; the owner: "I am sure there is something else out there"). Each copy of the
# six wallets with replayed copies (../../2026-11-24/coin_filters/out and ../../2026-11-24/live_check/out: their first buys
# of 0.5+ SOL, the unit's live exit, 1 SOL, 0.0064 a round trip), marked by whether ANOTHER of our ten wallets had already
# bought the same coin (its first buy, any size) in the WIN seconds before: known when our copy is decided. Mean a copy,
# with and without the agreement, by wallet and by block of time.
#   python3 -I c1_agree.py SP
import sys, os, json, glob, collections, numpy as np
SP = sys.argv[1]; H = os.path.dirname(os.path.abspath(__file__))
OURS = {"H9kuqGKN": ["hist_H9kuqGKN", "hist_H9_new"], "CqCAzte8": ["old_hist/hist_CqCAzte8_pre1730", "hist_CqCAzte8"],
        "CgyPomTG": ["old_hist/hist_CgyPomTG_1795526444", "hist_CgyPomTG"], "3XeFcZKS": ["old_hist/hist_3XeFcZKS_1795526444", "hist_3XeFcZKS"],
        "6LwMLkCe": ["old_hist/hist_6LwMLkCe_1795526444", "hist_6LwMLkCe"], "6nNzEg86": ["old_hist/hist_6nNzEg86_1795526444", "hist_6nNzEg86"],
        "GqWfqfG6": ["old_hist/hist_GqWfqfG6_1795526444", "hist_GqWfqfG6"], "FatoU1bj": ["hist_FatoU1bj", "hist_Fatou_new"],
        "HtHkKxYN": ["hist_HtHkKxYN"], "3SiQo8MJ": ["hist_3SiQo8MJ"]}
first = collections.defaultdict(dict)                     # mint -> wallet -> time of its first buy
for w, ds in OURS.items():
    seen = {}
    for d in ds:
        for f in glob.glob(f"{SP}/{d}/*_trades.jsonl"):
            for l in open(f):
                for e in json.loads(l)["trades"] or []:
                    if e["buy"] and (e["m"] not in seen or e["t"] < seen[e["m"]]): seen[e["m"]] = e["t"]
    for m, t in seen.items(): first[m][w] = t
UNIT = {"CqCAzte8": "all", "CgyPomTG": "all", "GqWfqfG6": "all", "3XeFcZKS": "token", "6LwMLkCe": "token", "6nNzEg86": "token"}
rows = {}
for d in (f"{H}/../../2026-11-24/coin_filters/out", f"{H}/../../2026-11-24/live_check/out"):
    for w, kind in UNIT.items():
        p = f"{d}/{w}.json"
        if not os.path.exists(p): continue
        j = json.load(open(p)); ex = j["exits"]; et, es = ex.index("tp 3x / 420 s / stall 240"), ex.index("tp 2x / 120 s")
        for r in j["rows"]:
            if kind == "token" and not r["tok"]: continue
            v = -0.0004 if r["prem"] > 1.5 else r["g"][et if (r["tok"] or w != "CqCAzte8") else es]
            rows[(w, r["m"])] = (r["t"], v)
for WIN in (600, 3600, 6 * 3600):
    res = collections.defaultdict(lambda: [[], []])
    for (w, m), (t, v) in rows.items():
        prior = [o for o, t2 in first[m].items() if o != w and t - WIN <= t2 < t]
        res[w][1 if prior else 0].append(v); res["ALL"][1 if prior else 0].append(v)
    print(f"\nanother of our wallets bought the coin in the {WIN // 60} min before (mean a copy at 1 SOL, n):")
    for w in list(UNIT) + ["ALL"]:
        a, b = np.array(res[w][0]), np.array(res[w][1])
        print(f"  {w:9s} alone {100 * a.mean() if len(a) else float('nan'):+6.1f}% ({len(a):4d})   agreed {100 * b.mean() if len(b) else float('nan'):+6.1f}% ({len(b):3d})")
both = [(t, v) for (w, m), (t, v) in rows.items() if any(o != w and t - 3600 <= t2 < t for o, t2 in first[m].items())]
both.sort(); bl = np.array_split(np.array([v for _, v in both]), 4) if len(both) >= 8 else []
if len(bl): print("\nagreed (60 min), in 4 time blocks: " + " / ".join(f"{100 * b.mean():+.1f}% ({len(b)})" for b in bl))
