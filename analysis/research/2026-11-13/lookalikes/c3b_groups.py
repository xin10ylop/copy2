# Search 2, step 3b: wallets of c3 that buy the same coins (launch bundles that span 5+ creators): two wallets are one
# group when 70%+ of the smaller one's coins are the other's. Keeps one wallet a group (the one with most coins) with
# NMIN+ coins, drops the wallets already rejected (FLIP: the Oct 29 table and this study's hold marks), prints the rest.
#   python3 -I c3b_groups.py [NMIN=60]  -> LK/c3b_keep.json
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lib
NMIN = int(sys.argv[1]) if len(sys.argv) > 1 else 60
R = [r for r in json.load(open(lib.OUT + "/c3_rank_1.0.json"))["rows"] if r["creators"] >= 5 and r["n"] >= 20]
S = {r["w"]: set(r["coins"]) for r in R}; grp = {}
for i, a in enumerate(R):
    if a["w"] in grp: continue
    grp[a["w"]] = a["w"]
    for b in R[i + 1:]:
        if b["w"] not in grp and len(S[a["w"]] & S[b["w"]]) >= 0.7 * min(len(S[a["w"]]), len(S[b["w"]])): grp[b["w"]] = a["w"]
FLIP = {"Fhbh1DTUDKt6qu9zVg8Q5VgnZa1WWWbxBxG6pCoJoggA": "flips in 0-1 s (Oct 29; s1)", "6Z91Dgiz9E44bMW11rQuMBjt1NwwPoQGXFNZieGfVtAb": "flips in 1-4 s (s1)",
        "dKMjeGJ4Mk9S3hxdfTThvZ7exks2xMwWqSM5NvN2CTK": "slot-0 sniper, sells in seconds (Oct 29)", "FiFawHqxeTVBhv6YbqbLwDVuvokRpPUM1bNwAyxhGc6W": "flips in 0-5 s (s1)",
        "AMDEmVocLtN5ji2gBY7BrmSHEyM5vt6TGszBbg4crMXg": "flips, median 15 s (c4)", "53DnQU1dJZNHfKBpv2Lhsd4EBGNpwsF4tS13Egc1m6Tv": "flips, median 6-22 s (s1, s5)",
        "6anjqMeWigQFo5wpciARAunVQUXTqoat8w8fFWarCkpc": "flips, median 2 s (c4)", "DsGJkPzFEQZuwy7JjZzPcJEyEfdC6StV7rarXG4ftRSA": "20 s timer (Oct 29)",
        "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg": "wallet 4", "TAB16RxXmazWzCTpJbnKiREWUybdEoskuyidaV291u3": "scored", "EcrMBga8HvSiCX2jQNiTfDuvrqkSE7ABQQ7YN5JTKcTb": "scored"}
keep = []
print(f"{len(R)} wallets with 20+ launch buys of 1.0+ SOL on 5+ creators; {len(set(grp.values()))} groups")
for r in R:
    g = [w for w, h in grp.items() if h == r["w"]]
    if grp[r["w"]] != r["w"] or r["n"] < NMIN: continue
    tag = FLIP.get(r["w"], "")
    print(f"{r['w']:45s} {r['n']:5d} coins ({r['n']/4:.0f} a day)  SOL {r['sol']:.2f}  slot {r['ds']:.0f}  group of {len(g)}  {tag}")
    if not tag: keep.append(r["w"])
json.dump(keep, open(lib.OUT + "/c3b_keep.json", "w")); print(len(keep), "to the hold check")
