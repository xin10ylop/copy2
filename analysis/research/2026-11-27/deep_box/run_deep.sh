#!/bin/bash
# The deep test of candidate wallets on the Frankfurt box (Nov 27; the alias `deep`), like `sss`: pulls the repo, runs
# deep_job.sh as a background service (rugsnipe-deep, 6 GB, nice 19), prints a line a minute, then the verdicts.
#   deep W1,W2,...   test these wallets (full addresses, comma-separated; about 10-30 minutes a wallet)
#   deep show        print the last verdicts again
# Needs, once: the Helius key in /etc/rugsnipe/keys/helius-research.env (root, 0400; two lines HELIUS_URL=... and RPC_URL=...,
# the same URL), and solders in the box's venv. The key is read by systemd from that file and never printed.
D=/var/lib/rugsnipe-deep; U=rugsnipe-deep; K=/etc/rugsnipe/keys/helius-research.env
show() {
  [ -s $D/summary.txt ] || { echo "no result yet"; return 1; }
  cat $D/summary.txt; echo "(exit $(cat $D/rc 2>/dev/null || echo '?'); the files: $D/out/)"
}
if [ "$1" = show ]; then show; exit $?; fi
[ -n "$1" ] || { echo "usage: deep WALLET,WALLET,... | deep show"; exit 64; }
cd ~/rugsnipe || exit 1
git pull --ff-only -q && git log --oneline -1
echo "sudo password (if asked):"; sudo -v || exit 1
sudo test -r $K || { echo "missing $K (the Helius key file): see the setup lines"; exit 1; }
# the research scripts read /home/user/copy2 (and /home/user/rugsnipe): this clone
[ -e /home/user/copy2 ] || { sudo mkdir -p /home/user && sudo ln -sfn "$HOME/rugsnipe" /home/user/copy2; }
[ -e /home/user/rugsnipe ] || sudo ln -sfn "$HOME/rugsnipe" /home/user/rugsnipe
if systemctl is-active --quiet $U; then
  echo "a deep test is already running: following it (it was not restarted)"
else
  sudo install -d -m 755 $D
  sudo systemd-run --unit=$U --collect -q -p MemoryMax=6G -p Nice=19 -p EnvironmentFile=$K \
    /bin/bash ~/rugsnipe/analysis/research/2026-11-27/deep_box/deep_job.sh $D "$1" || exit 1
  echo "deep test started in the background."
fi
echo "a line every minute below. If this window closes, nothing is lost: run deep show when done."
trap 'echo; echo "stopped watching; the test goes on. deep show when done."; exit 0' INT
sleep 3
while systemctl is-active --quiet $U; do
  echo "$(date '+%H:%M') $(tail -n 1 $D/progress 2>/dev/null)"; sleep 60
done
tail -n 1 $D/progress 2>/dev/null; show
