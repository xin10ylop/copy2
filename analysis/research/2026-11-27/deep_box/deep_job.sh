#!/bin/bash
# The deep test of candidate wallets on the Frankfurt box (Nov 27), run by run_deep.sh (`deep`) as a background service
# (rugsnipe-deep). Per wallet, on its last 14 days (Helius, HELIUS_URL / RPC_URL from the service's EnvironmentFile, which
# never prints): the blind rolling pick (w3_robust.py), the coin kind x size x exit table (w3_setup.py), the exit grid on the
# copies it would take and on those it would not (x1_grid.py), the exit and rule search (x2_analyze.py, x4_rules.py), and the
# verdict by the rules fixed in x5_verdict.py. Args: OUT_DIR WALLET,WALLET,... Writes OUT_DIR/out/<wallet8>_*.txt,
# OUT_DIR/summary.txt, OUT_DIR/progress, OUT_DIR/rc.
D=$1; WS=$2; R=/home/user/copy2/analysis/research
PY=/opt/rugsnipe/venv/bin/python; [ -x $PY ] || PY=python3
SP=$D/sp; O=$D/out; mkdir -p $SP $O; date +%s > $D/start; rm -f $D/rc
: > $D/progress; p() { echo "$(date '+%H:%M') $*" >> $D/progress; }
if ! $PY -c "import numpy, solders" 2>/dev/null; then p "FAILED: numpy or solders missing for $PY"; echo 2 > $D/rc; exit 2; fi
# Nov 28: HELIUS_URL may be empty (the key out of credits): the scripts then read the public node or Triton at RPC_URL, slower
if [ -z "$RPC_URL" ]; then p "FAILED: no RPC_URL (the key file)"; echo 3 > $D/rc; exit 3; fi
H=h$(date -u +%m%d)_   # a fresh history folder each day
{ echo "deep test of $(date -u '+%b %d %H:%M') UTC (14 days each; the rules: x5_verdict.py)"; } > $D/summary.txt
cd $SP
for W in ${WS//,/ }; do
  W8=${W:0:8}; p "$W8: history and the blind rolling pick"
  HIST_PREFIX=$H NOSTOP=1 PATHS_AT_ONCE=2 LK=$SP/lk COST=0.0064 TABLE=1 MAXPAGES=15 timeout 3600 $PY -I $R/2026-11-20/tape_screen/w3_robust.py $SP $W 700 > $O/${W8}_all.txt 2> $O/${W8}_all.err
  p "$W8: the coin kind x size x exit table"
  HIST_PREFIX=$H NOSTOP=1 PATHS_AT_ONCE=2 LK=$SP/lk COST=0.0064 MAXPAGES=15 timeout 1800 $PY -I $R/2026-11-20/tape_screen/w3_setup.py $SP $W > $O/${W8}_setup.txt 2>&1
  p "$W8: the exit grid"
  CAND_W=$W HIST_PREFIX=$H MAXPAGES=15 PATHS_AT_ONCE=3 LK=$SP/lk timeout 3600 $PY -I $R/2026-11-27/exits_all/x1_grid.py $SP cand_$W8 > $O/${W8}_x1.log 2>&1
  CAND_W=$W OUTSIDE=1 HIST_PREFIX=$H MAXPAGES=15 PATHS_AT_ONCE=3 LK=$SP/lk timeout 3600 $PY -I $R/2026-11-27/exits_all/x1_grid.py $SP cand_$W8 > $O/${W8}_x1out.log 2>&1
  p "$W8: the exit and rule search"
  $PY -I $R/2026-11-27/exits_all/x2_analyze.py $SP cand_$W8 > $O/${W8}_x2.txt 2>&1
  $PY -I $R/2026-11-27/exits_all/x4_rules.py $SP cand_$W8 > $O/${W8}_x4.txt 2>&1
  $PY -I $R/2026-11-27/deep_box/x5_verdict.py $O $W8 >> $D/summary.txt 2>&1
  p "$W8: done"
done
p "all done"; echo 0 > $D/rc
