# Fetch every landed transaction of wallet 4 before Oct 19 00:00 UTC (from w4_oldsigs.jsonl) into the tri cache.
import sys, json, time
from concurrent.futures import ThreadPoolExecutor
SP = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad"
sys.path.insert(0, SP + "/month"); import tri
allp = [x for l in open("w4_oldsigs.jsonl") for x in json.loads(l)]
todo = [x[0] for x in allp]  # failed ones too (cheap, 36)
n = 0; bad = 0
def one(s):
    for k in range(3):
        try: return tri.tx(s)
        except Exception as e: err = e
    return None
with ThreadPoolExecutor(8) as ex:
    for r in ex.map(one, todo):
        n += 1; bad += r is None
        if n % 300 == 0: print(time.strftime("%H:%M:%S"), n, "bad", bad, flush=True)
print("done", n, "bad", bad)
