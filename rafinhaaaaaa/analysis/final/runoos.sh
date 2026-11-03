#!/bin/bash
# a rule picked on one week, scored on the weeks before it: runoos.sh WALLET WIN_T0 WIN_NOW "FIXRULE" SUFFIX
F=/tmp/claude-0/-home-user/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad/gmgn-out/final; W=$1
: "${GMGN_API_KEY:?set GMGN_API_KEY (GMGN API key)}"
cd $F
MAXT=${MAXT:-600} WIN_T0=$2 WIN_NOW=$3 OUTSFX=.$5 python3 -I build.py $W >> logs_build.log 2>&1
python3 -I chain.py trips/$W.$5.json >> logs_chain.log 2>&1
python3 -I reprice.py trips/$W.$5.json s3q2/$W.$5.json >> logs_reprice.log 2>&1
python3 -I addk.py s3q2/$W.$5.json 2 >> logs_addk.log 2>&1
python3 -I paths_g1.py s3q2/$W.$5.json >> logs_paths.log 2>&1
FIXRULE="$4" python3 -I sim_g1.py s3q2/$W.$5.json > out/sim_$W.$5.txt 2>&1
echo "$(date -u +%H:%M:%S) ${W:0:8} OUT-OF-SAMPLE $5 done: $(grep -m1 'K=2:' out/sim_$W.$5.txt)" >> final.log
