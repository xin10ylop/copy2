#!/bin/bash
# The week before, for a wallet that came close: the same steps on trips/<w>.prev1.json (chain and path caches are keyed
# by signature, so they are shared with this week's).        runprev.sh WALLET
F=/tmp/claude-0/-home-user/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad/gmgn-out/final; W=$1
: "${GMGN_API_KEY:?set GMGN_API_KEY (GMGN API key)}"
cd $F
PREV=${PREV:-1} python3 -I build.py $W >> logs_build.log 2>&1
python3 -I chain.py trips/$W.prev1.json >> logs_chain.log 2>&1
python3 -I reprice.py trips/$W.prev1.json s3q2/$W.prev1.json >> logs_reprice.log 2>&1
python3 -I addk.py s3q2/$W.prev1.json 2 >> logs_addk.log 2>&1
python3 -I paths_g1.py s3q2/$W.prev1.json >> logs_paths.log 2>&1
python3 -I sim_g1.py s3q2/$W.prev1.json > out/sim_$W.prev1.txt 2>&1
echo "$(date -u +%H:%M:%S) ${W:0:8} PREVIOUS WEEK done: $(grep -m1 'K=2: P1' out/sim_$W.prev1.txt)" >> final.log
