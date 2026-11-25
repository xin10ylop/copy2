#!/bin/bash
# The screen itself, run by run_screen.sh (`sss`) as a background service (rugsnipe-screen), so a dropped SSH session
# can't stop it or hide its result (Nov 25). Args: OUT_DIR MIN_COPIES SCRIPT. Writes OUT_DIR/screen.txt, OUT_DIR/rc at the end.
D=$1; N=$2; S=$3
date +%s > "$D/start"; rm -f "$D/rc"
/opt/rugsnipe/venv/bin/python -I "$S" /var/lib/rugsnipe-tape 0.5 "$N" > "$D/screen.txt" 2>&1
echo $? > "$D/rc"
