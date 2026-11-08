#!/bin/bash
# Nov 8: Rafinhaaaaaa from Nov 4 18:05 UTC (the end of the Nov 4 check) to WIN_NOW (unix), the fixed rule, then the
# slot landings (addslot.py), in the analysis/final scratchpad folder. Needs GMGN_API_KEY in the environment.
#   bash nov08.sh WIN_NOW
: "${GMGN_API_KEY:?set GMGN_API_KEY (GMGN API key)}"
cd /tmp/claude-0/-home-user/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad/gmgn-out/final
MIN_USD=150 bash runoos.sh Hn6vBWWySnxA8XjxRQDEmZEuH5QL7KqosnJGcLcUzFJ6 1793815529 $1 "buy>=5.00|None|None|300|1.0" nov08
python3 -I addslot.py s3q2/Hn6vBWWySnxA8XjxRQDEmZEuH5QL7KqosnJGcLcUzFJ6.nov08.json 3 2.9
