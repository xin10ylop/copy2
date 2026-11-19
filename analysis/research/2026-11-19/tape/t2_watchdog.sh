#!/bin/bash
# Keeps t1_record.py running (Nov 19; the owner: "check every 30 minutes that it is running"): every 60 s, restarts the
# recorder if its process is gone or its log has not moved for 3 minutes (a stats line comes every minute), and gzips
# the tape files of closed hours. RPC_URL from the earlier session's Triton file, never printed.
#   bash t2_watchdog.sh OUT LOG
OUT=$1; LOG=$2; HERE=$(cd "$(dirname "$0")" && pwd)
export RPC_URL="$(cat /tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad/month/.triton_url)"
while true; do
  alive=$(pgrep -f "t1_record.py $OUT" | head -1)
  age=$(( $(date +%s) - $(stat -c %Y "$LOG" 2>/dev/null || echo 0) ))
  if [ -z "$alive" ] || [ "$age" -gt 180 ]; then
    [ -n "$alive" ] && kill "$alive"
    echo "$(date -u +%H:%M:%S) watchdog: (re)start (process ${alive:-none}, log age ${age}s)" >> "$LOG"
    nohup python3 -I "$HERE/t1_record.py" "$OUT" >> "$LOG" 2>&1 &
  fi
  now=$(date -u +%Y%m%d%H)
  for f in "$OUT"/tape_*.jsonl; do
    [ -e "$f" ] || continue
    h=$(basename "$f" | cut -d_ -f2); [ "$h" \< "$now" ] && gzip -q "$f"
  done
  sleep 60
done
