#!/bin/bash
# stage 1 for one wallet; FULL TEST ones are queued for run.sh (stage 2)
F=/tmp/claude-0/-home-user/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad/gmgn-out/final; W=$1
: "${GMGN_API_KEY:?set GMGN_API_KEY (GMGN API key)}"
cd $F
MAXT=40 OUTSFX=.quick python3 -I build.py $W >> logs_build.log 2>&1 || { echo "$W quick build failed" >> quick.log; exit; }
python3 -I quick.py $W >> quick.log 2>&1
grep "^${W:0:8} quick" quick.log | tail -1 | grep -q "FULL TEST" && { echo $W >> full_queue.txt; nohup $F/run.sh $W > /dev/null 2>&1 & }
