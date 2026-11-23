#!/bin/bash
# The weekly wallet screen on the Frankfurt box (Nov 23; the alias `sss`). Pulls the repo, runs s1_screen.py on the tape
# (free: no credits), keeps the whole output in /tmp/screen.txt and prints the part to paste back. MIN_COPIES (default 20)
# as the first argument.
cd ~/rugsnipe || exit 1
git pull --ff-only -q && git log --oneline -1
S=~/rugsnipe/analysis/research/2026-11-20/tape_screen/s1_screen.py; PY=/opt/rugsnipe/venv/bin/python
sudo env COST=0.0064 MIN_HOLD=20 TOPN=60 TOP_JSON=/tmp/screen_top.json systemd-run --scope -q -p MemoryMax=2G nice -n 19 $PY -I $S /var/lib/rugsnipe-tape 0.5 "${1:-20}" > /tmp/screen.txt 2>&1
grep -E "^tape|bundles|jumpy|late|median price" /tmp/screen.txt; sed -n '/by the mean over/,+15p' /tmp/screen.txt; grep -E "^TOPMEAN|^TOPOWN" /tmp/screen.txt
