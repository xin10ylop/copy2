# Fetch a list of signatures (JSON list in argv[1]) into the tri cache with N threads. Prints progress.
import sys; sys.path.insert(0, "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/wallet")
from w4lib import *
from concurrent.futures import ThreadPoolExecutor
S = json.load(open(sys.argv[1])); n = 0; bad = 0
def one(s):
    for k in range(3):
        try: return tri.tx(s)
        except Exception: time.sleep(1)
    return None
with ThreadPoolExecutor(int(sys.argv[2]) if len(sys.argv) > 2 else 8) as ex:
    for r in ex.map(one, S):
        n += 1; bad += r is None
        if n % 250 == 0: print(time.strftime("%H:%M:%S"), n, "/", len(S), "bad", bad, flush=True)
print("done", n, "bad", bad, flush=True)
