#!/bin/bash
# Scores one wallet with the per-wallet pipeline (README.md "Run order"). Outputs in out/<w8>_<step>.txt.
#   bash run.sh WALLET fetch      sigs + sharded pull (Oct 19 00:00 UTC to now; T0 overrides the start)
#   bash run.sh WALLET score      every step after the fetch (create.py and full_paths.py fetch from Triton too)
#   bash run.sh WALLET band LO    the copy from its own size LO (routable, coins priced in another token)
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
  KINDS="pump, other quote" python3 -I full_paths.py $W 1.45 > out/${w}_fpaths.log
  python3 -I marks.py $W > out/${w}_marks.txt
  for g in cap land tp mix; do CAP=4 python3 -I grid.py $g q 1 1.45 9 > out/${w}_grid_$g.txt; done ;;
band)
  # its own size when it rarely buys 1.45+: full paths of its routable one-buy one-sell trips from LO SOL (coins priced in
  # another token), then the same grid from that floor
  LO=$3
  # MULTI=1: a coin it bought once and sold in parts is one trip to its last sale (else grid.py sees one-sale coins only)
  MULTI=1 KINDS="pump, other quote" ROUTES=ABC python3 -I full_paths.py $W $LO > out/${w}_fpaths_$LO.log
  for g in cap land tp mix days itsown; do MULTI=1 CAP=4 python3 -I grid.py $g q 1 $LO 9 > out/${w}_grid_${g}_$LO.txt; done
  CAP=4 python3 -I grid.py cap q 1 $LO 9 > out/${w}_grid_cap_${LO}_onesale.txt
  MULTI=1 CAP=4 STAKE=0.5 python3 -I grid.py cap q 1 $LO 9 > out/${w}_grid_cap_${LO}_stake05.txt
  MULTI=1 CAP=4 ITS_TP=99 python3 -I grid.py cap q 1 $LO 9 > out/${w}_grid_cap_${LO}_nolift.txt
  python3 -I early.py $LO > out/${w}_early_$LO.txt          # rewrites <w8>_early.json at this floor (marks.py reads it)
  python3 -I marks.py $W $LO > out/${w}_marks_$LO.txt
  python3 -I early.py 1.45 > /dev/null ;;                   # back to the 1.45 file
esac
