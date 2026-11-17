# Attention study, the money test (README): a random 250 of each day's score 4+ launches (seed 7), as tg_test.py "calls"
# (the coin, its create time): DIR/calls.json for day 1 and day 2.
#   python3 -I a8_money.py SP   -> SP/attn/money_d1/calls.json, SP/attn/money_d2/calls.json
import sys, os, json, random, runpy
SP = sys.argv[1]; here = os.path.dirname(os.path.abspath(__file__))
sys.argv = ["a7", SP]; import io, contextlib
with contextlib.redirect_stdout(io.StringIO()): g = runpy.run_path(os.path.join(here, "a7_bursts.py"))
L, MID = g["L"], g["MID"]
for name, X in (("money_d1", [v for v in L if v["t"] < MID and v["score"] >= 4]), ("money_d2", [v for v in L if v["t"] >= MID and v["score"] >= 4])):
    pick = random.Random(7).sample(X, min(250, len(X))); os.makedirs(f"{SP}/attn/{name}", exist_ok=True)
    json.dump([[v["m"], v["t"], "create"] for v in pick], open(f"{SP}/attn/{name}/calls.json", "w"))
    print(name, len(X), "score 4+ coins;", len(pick), "picked; graduated among them", sum(v["grad"] for v in pick))
