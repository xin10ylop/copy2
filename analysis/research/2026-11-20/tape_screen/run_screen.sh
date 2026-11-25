#!/bin/bash
# The weekly wallet screen on the Frankfurt box (Nov 23; the alias `sss`). Pulls the repo, runs s1_screen.py on the tape
# (free: no credits; memory capped at 8 GB since Nov 25: at 4 GB a run on ~92 h of tape crawled near the cap), keeps the whole output in /tmp/screen.txt and prints the part to paste back. MIN_COPIES (default 20)
# as the first argument. (Nov 23: a 2 GB cap killed a run on 55 h of tape without a word; the box has 15 GB.)
cd ~/rugsnipe || exit 1
git pull --ff-only -q && git log --oneline -1
S=~/rugsnipe/analysis/research/2026-11-20/tape_screen/s1_screen.py; PY=/opt/rugsnipe/venv/bin/python
echo "screen running (about 5-20 minutes, nothing prints meanwhile; don't stop it) ..."
start=$(date +%s)
sudo env COST=0.0064 MIN_HOLD=20 TOPN=60 TOP_JSON=/tmp/screen_top.json systemd-run --scope -q -p MemoryMax=8G nice -n 19 $PY -I $S /var/lib/rugsnipe-tape 0.5 "${1:-20}" > /tmp/screen.txt 2>&1
rc=$?
echo "done in $(( ($(date +%s) - start) / 60 )) min (exit $rc)"
if ! grep -q "^tape" /tmp/screen.txt || ! grep -q "^TOPMEAN" /tmp/screen.txt; then
  echo "FAILED: the screen did not finish. Its last lines:"; tail -n 8 /tmp/screen.txt
  echo "and the system's word on it:"; sudo journalctl --since "-$(( ($(date +%s) - start) / 60 + 2 ))min" --no-pager | grep -iE "oom|memory|killed" | tail -n 4
  exit 1
fi
grep -E "^tape|bundles|jumpy|late|median price" /tmp/screen.txt; sed -n '/by the mean over/,+15p' /tmp/screen.txt; grep -E "^TOPMEAN|^TOPOWN" /tmp/screen.txt
