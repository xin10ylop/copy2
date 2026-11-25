#!/bin/bash
# The weekly wallet screen on the Frankfurt box (Nov 23; the alias `sss`). Pulls the repo, runs s1_screen.py on the tape
# (free: no credits), keeps the whole output in /var/lib/rugsnipe-screen/screen.txt and prints the part to paste back.
#   sss          run the screen (MIN_COPIES 20); `sss 30` with MIN_COPIES 30
#   sss show     print the last result again, without rerunning
# Nov 25: the screen runs as a background service (`rugsnipe-screen`), not tied to the SSH session: before, it printed
# nothing for ~25 minutes, the SSH session froze or dropped, and the result only showed in another window. Now it prints
# a line every minute, and a dropped session loses nothing: run `sss` again and it follows the running screen, or
# `sss show` once it is done. Memory capped at 8 GB (at 4 GB a run on ~92 h of tape crawled; at 2 GB one was killed).
D=/var/lib/rugsnipe-screen; U=rugsnipe-screen; OUT=$D/screen.txt

show() {
  if [ ! -s $OUT ]; then echo "no result yet ($OUT is missing)"; return 1; fi
  echo "result of $(date -d @"$(cat $D/start 2>/dev/null || echo 0)" '+%b %d %H:%M') (box time), exit $(cat $D/rc 2>/dev/null || echo '?')"
  if ! grep -q "^tape" $OUT || ! grep -q "^TOPMEAN" $OUT; then
    echo "FAILED: the screen did not finish. Its last lines:"; tail -n 8 $OUT
    echo "and the system's word on it:"; sudo journalctl -u $U -n 40 --no-pager | grep -iE "oom|memory|killed" | tail -n 4
    return 1
  fi
  grep -E "^tape|bundles|jumpy|late|median price" $OUT; sed -n '/by the mean over/,+15p' $OUT
  sed -n '/^by consistency/,+15p' $OUT; sed -n '/^launch-slot buyers/,+10p' $OUT; sed -n '/^fast traders/,+15p' $OUT
  sed -n '/^agreement:/,+3p' $OUT; sed -n '/^benchmark/,+8p' $OUT
  grep -E "^TOPMEAN|^TOPCONS|^TOPLAUNCH|^TOPFAST" $OUT
}

if [ "$1" = show ]; then show; exit $?; fi

cd ~/rugsnipe || exit 1
git pull --ff-only -q && git log --oneline -1
echo "sudo password (if asked):"; sudo -v || exit 1
if systemctl is-active --quiet $U; then
  echo "a screen is already running: following it (it was not restarted)"
else
  sudo install -d -m 755 $D
  sudo systemd-run --unit=$U --collect -q -p MemoryMax=8G -p Nice=19 \
    --setenv=COST=0.0064 --setenv=MIN_HOLD=20 --setenv=TOPN=60 --setenv=TOP_JSON=$D/screen_top.json \
    /bin/bash ~/rugsnipe/analysis/research/2026-11-20/tape_screen/screen_job.sh $D "${1:-20}" ~/rugsnipe/analysis/research/2026-11-20/tape_screen/s1_screen.py || exit 1
  echo "screen started in the background (about 10-30 minutes)."
fi
echo "a line every minute below. If this window closes, nothing is lost: run sss again to follow it, or sss show when done."
trap 'echo; echo "stopped watching; the screen goes on. sss to follow it again, sss show when done."; exit 0' INT
sleep 2
while systemctl is-active --quiet $U; do
  s=$(cat $D/start 2>/dev/null || date +%s)
  m=$(systemctl show -p MemoryCurrent --value $U 2>/dev/null)
  case $m in ''|*[!0-9]*) mem="?";; *) mem=$(awk -v b="$m" 'BEGIN{printf "%.1f", b/1e9}');; esac
  echo "$(date '+%H:%M') running, $(( ($(date +%s) - s) / 60 )) min, memory $mem GB of 8"
  sleep 60
done
echo "done in $(( ($(date +%s) - $(cat $D/start 2>/dev/null || date +%s)) / 60 )) min"
show
