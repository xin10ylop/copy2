# The pump.fun tape (Nov 19-20)

Every pump trade and create from the live logs stream, for the wallet search (wallet 4 was found on tapes like this).

- `t1_record.py OUT`: Triton websocket `logsSubscribe` on the pump program, events decoded from "Program data:" lines,
  one JSON line an event, hourly files `OUT/tape_<YYYYmmddHH>_<pid>.jsonl`, gzipped once the hour is closed, older than
  `TAPE_KEEP_DAYS` (14) deleted; reconnects by itself, also after 60 s with no message; a stats line every minute.
- Nov 19 17:22 - 20:17 UTC: run in the cloud session (`t2_watchdog.sh`), stopped by the session's 2-hour cap: about 490,000
  events, the scratchpad only.
- **Nov 20: the unit `rugsnipe-tape` on the Frankfurt box** (`deploy/systemd/rugsnipe-tape.service`, installed by
  `deploy/install.sh`, enabled by hand): tapes in `/var/lib/rugsnipe-tape`, the URL from the box's api-keys file (its
  `RPC_URL` line, as a systemd credential, never printed). About 30-40 MB of gzip an hour (the Nov 19 hours), ~1 GB a
  day; ~65 GB a day of stream at Triton (~$5).
