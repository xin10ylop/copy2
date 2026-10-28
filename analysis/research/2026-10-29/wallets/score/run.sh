#!/bin/bash
# Scores one wallet with the per-wallet pipeline (README.md "Run order"). Outputs in out/<w8>_<step>.txt.
#   bash run.sh WALLET fetch      sigs + sharded pull (Oct 19 00:00 UTC to now; T0 overrides the start)
#   bash run.sh WALLET score      every step after the fetch (create.py and full_paths.py fetch from Triton too)
set -e
cd "$(dirname "$0")"
W=$1; w=${W:0:8}; export W
T0=${T0:-1792368000}                 # Oct 19 00:00 UTC
case $2 in
fetch)
  python3 -I sigs.py $W $T0 > out/${w}_sigs.txt
  for k in 0 1 2; do SHARD=$k/3 python3 -I pull.py $W > out/${w}_pull_$k.log 2>&1 & done; wait
  python3 -I merge.py $W | tee out/${w}_merge.txt ;;
score)
  python3 -I ledger.py $W > out/${w}_ledger.txt
  python3 -I groups.py $W > out/${w}_groups.txt
  python3 -I trips.py $W > out/${w}_trips.txt
  python3 -I byquote.py $W > out/${w}_byquote.txt
  python3 -I exitrule.py $W > out/${w}_exitrule.txt
  for p in P1 P2 P3; do PER=$p python3 -I exitrule.py $W > out/${w}_exitrule_$p.txt; PER=$p python3 -I behave.py $W > out/${w}_behave_$p.txt; done
  python3 -I tprate.py $W > out/${w}_tprate.txt
  python3 -I route_q.py $W > out/${w}_route_q.txt
  python3 -I early.py 1.45 > out/${w}_early.txt
  python3 -I create.py $W 0.5 > out/${w}_create.log
  python3 -I full_paths.py $W 1.45 > out/${w}_fpaths.log
  python3 -I marks.py $W > out/${w}_marks.txt
  for g in cap land tp mix; do CAP=4 python3 -I grid.py $g q 1 1.45 9 > out/${w}_grid_$g.txt; done ;;
esac
