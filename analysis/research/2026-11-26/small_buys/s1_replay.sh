#!/bin/bash
# Our copy of each running wallet's smaller first buys (Nov 26; the owner: "dig deeper, if it is profitable allow it, do
# the same for the rest of the wallets, who mentioned a 0.5 sol floor?"). e1_ideas.py's baseline: each unit's live exit,
# 1 SOL a copy (more impact than the 0.25-0.5 SOL units take: cautious), COST 0.0064, Helius paths, the 14-day histories
# (hist26_, histp_ for 3SiQo8MJ); every copy saved (DUMP) for s2_dig.py.
#   bash s1_replay.sh SP
SP=$1; E=/home/user/copy2/analysis/research/2026-11-24/ideas/e1_ideas.py; O=$(dirname "$0")/out
run() {   # LABEL WALLET UNIT HIST BAND [ENV...]
  l=$1 w=$2 u=$3 h=$4 b=$5; shift 5
  env "$@" HIST_PREFIX=$h FETCH=1 PATHS_AT_ONCE=2 LK=$SP/lk COST=0.0064 MAXPAGES=15 MINSOL=${b%,*} BAND=$b DUMP=$O/${l}_${b/,/-}.json \
    timeout 3000 python3 -I $E $SP $w $u > $O/${l}_${b/,/-}.txt 2>&1
  echo "$l $b: $(grep -E 'baseline' $O/${l}_${b/,/-}.txt | cut -c1-150)"
}
W4=H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg
for b in 0.1,0.25 0.25,0.5; do
  run ppp 3SiQo8MJMzXaZcJexMivmk5CRgrNxDUh4bDbgb3wFAmW token histp_ $b BASEX=2,120,0,5,60
  run uuu GqWfqfG6Mt6RL8BKUWiBkirqzycUc15bgZVtFERQzxJ8 all hist26_ $b
  run iii Bing35WCqmhUwFBJ9xVNfMoNpECj8vdWEr5hD5wYyobc all hist26_ $b
  run ooo HtHkKxYN43BdJ8QJU1srMa3bqjpncLFcZgVCX8yU3AJS all hist26_ $b
  run eee CgyPomTGt9BFqnjBdRS38BCBUZvtMJDf3aKQy8sMTVKX all hist26_ $b
  run yyy 6nNzEg86rbY4J1Z6euDn9iQoih8uaSj6ZVZHZVvFxjJf token hist26_ $b
  run rrr 3XeFcZKSn8WzqoDAm5vvgbdfkU82rMmhJfp1q4LXtnX6 token hist26_ $b
  run ttt 6LwMLkCeEAqYp9Pv33ujrgd9uF987zPXdGKr9Z9sebh5 token hist26_ $b
done
# wallet 4: its token coins under its 1.3 SOL floor, the unit's exit, the last 5 days (it buys hundreds a day)
for b in 0.1,0.25 0.25,0.5 0.5,1.3; do run qqq $W4 token hist26_ $b BASEX=4,600,180,5,60 T_MIN=1795219200; done
