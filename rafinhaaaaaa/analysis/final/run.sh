#!/bin/bash
# The final pass for one wallet, with group G1's method checked against the live run (agents/G1/REPORT.md §0):
# all trips (build.py, at most MAXT spread over day x quote x size), chain facts, our price K = 2 trades behind (K = 1, 4, 7
# as checks; reprice.py fallbacks for nobody-behind legs), exits on the chain path, its own rules read on P1 with ours
# just inside them, scored on P2 (sim_g1.py).          run.sh WALLET
F=/tmp/claude-0/-home-user/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad/gmgn-out/final; W=$1
: "${GMGN_API_KEY:?set GMGN_API_KEY (GMGN API key)}"
cd $F
[ -z "$FORCE" ] && { mkdir claim/$W 2>/dev/null || exit 0; }          # one worker per wallet (two driver queues)
python3 -I build.py $W >> logs_build.log 2>&1 || { echo "$W build failed" >> final.log; exit; }
python3 -I chain.py trips/$W.json >> logs_chain.log 2>&1
python3 -I reprice.py trips/$W.json s3q2/$W.json >> logs_reprice.log 2>&1
python3 -I addk.py s3q2/$W.json 2 >> logs_addk.log 2>&1
python3 -I paths_g1.py s3q2/$W.json >> logs_paths.log 2>&1
python3 -I sim_g1.py s3q2/$W.json > out/sim_$W.txt 2>&1
echo "$(date -u +%H:%M:%S) ${W:0:8} done: $(grep -m1 'K=2: P1' out/sim_$W.txt)" >> final.log
