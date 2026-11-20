# The coins the bot does not copy (f2_paths_more.py), by kind, with the live exit and with e1's leader (its sale at any
# time, no sell pressure), against the bot's own kind (token coins 1.3+, f1). 1 SOL a copy; the model of e1_exits.py.
#   LK=SP/lk python3 -I e3_more.py SP > out/e3_more.txt
import sys, json, numpy as np
exec(open("e1_exits.py").read().split("ps = [p for p")[0])
more = json.load(open(f"{SP}/w4since/coins_more.json"))
groups = {"token 1.3+ (copied now)": coins}
for c in more: groups.setdefault(c["cat"], []).append(c)
print(f"{'kind':26s} {'n':>4s} | {'live exit':>28s} | {'its sale always, no sp':>28s}")
for k, cs in groups.items():
    ps_ = [p for p in map(prep, cs) if p is not None]; ps_.sort(key=lambda p: p["t"]); h = len(ps_) // 2
    out = []
    for kw in ({}, dict(its="always", sp=None)):
        x = np.array([exit_value(p, **kw) for p in ps_]); k2 = max(1, round(0.02 * len(x)))
        out.append(f"{100 * x.mean():+6.1f}% a copy, w/o 2% {100 * np.sort(x)[:-k2].mean():+5.1f}%, halves {100 * x[:h].mean():+5.1f}/{100 * x[h:].mean():+5.1f}")
    print(f"{k:26s} {len(ps_):4d} | {out[0]} | {out[1]}")
