# One wallet's own pump trades from a start date (w4_history.history, batched; Alchemy), for m5_confirm (Nov 18: the
# third wallet, 5KcKcGcz, found on 4 days, needs its other days). SP/winners/hist/<wallet>.json.
#   RPC_URL=... python3 -I f1_history.py SP WALLET T0 [MAXSIG]
import sys, os
SP, WAL, T0_, MX = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]) if len(sys.argv) > 4 else 60000
src = open("/home/user/copy2/analysis/research/2026-11-17/winners/w4_history.py").read().split("def curve")[0]
sys.argv = ["x", SP, str(MX)]; ns = {"__file__": "w4_history.py"}; exec(compile(src, "w4_history.py", "exec"), ns)
ns["T0"] = T0_; h = ns["history"](WAL)
import datetime as dt; b = [e for e in h["trades"] if e["buy"]]
print(f"{WAL[:8]}: {h['n_sigs']} transactions since {dt.datetime.fromtimestamp(h['t_first'] or 0, dt.UTC):%m-%d %H:%M} UTC, {len(h['trades'])} own trades, {len(b)} buys")
