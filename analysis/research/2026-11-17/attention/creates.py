# The launches of SP/market/creates.json, one row per coin: m1_launches.py took "the new mint" of each create
# transaction, and 35 coins (451 rows) also show up as new in other transactions; the earliest row is the real create.
import json
def load(SP):
    best = {}
    for s, v in json.load(open(f"{SP}/market/creates.json")).items():
        if v and (v["mint"] not in best or v["slot"] < best[v["mint"]][1]["slot"]): best[v["mint"]] = (s, v)
    return best
