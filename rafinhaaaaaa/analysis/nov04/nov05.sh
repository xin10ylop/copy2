#!/bin/bash
# Nov 4 evening: Rafinhaaaaaa on Nov 1 00:09 UTC (the end of the week the rule was picked on) -> $1 (unix), the fixed
# rule, through analysis/final/runoos.sh (GMGN trips, chain legs, paths, sim_g1). Needs GMGN_API_KEY in the environment.
#   bash nov05.sh WIN_NOW
: "${GMGN_API_KEY:?set GMGN_API_KEY (GMGN API key)}"
cd /tmp/claude-0/-home-user/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad/gmgn-out/final
echo "$(date -u +%H:%M:%S) start window 1793491797 -> $1" >> nov05.log
MIN_USD=300 bash runoos.sh Hn6vBWWySnxA8XjxRQDEmZEuH5QL7KqosnJGcLcUzFJ6 1793491797 $1 "buy>=5.10|None|None|300|1.0" nov05
echo "$(date -u +%H:%M:%S) raf done" >> nov05.log
