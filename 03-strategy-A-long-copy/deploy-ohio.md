# Strategy A: running it on the Ohio box

In short: the long copy runs in paper mode on the Ohio box (AWS us-east-2, user `ubuntu`). It reuses fra1's feed
settings and API keys, restored from fra1's backup. It has **no wallet**, so it can't send anything. Install and update
with `sudo bash deploy/install.sh --role analytics`. Check it with `sudo python3 -I ~/history.py paper`. fra1 itself was
terminated on Oct 28. Its backup (`/root/backups/fra1-backup.tgz` on Ohio, root only) holds wallet keys and API keys: keep
it private, never in git, never shared.

All commands run on Ohio: `ssh -i ~/.ssh/<your Ohio key>.pem ubuntu@<the Ohio address>`. The address is in your AWS
console. The text before the `$` tells you which machine you're on: `ubuntu@ip-172-31-17-131:~$` is Ohio.

## 1. First setup (done Oct 27; kept here to redo it on a new box)

**1. Code and build** (5-15 minutes):
```
cd ~/rugsnipe && git checkout -q claude/eloquent-mayer-264bxk && git pull -q --ff-only origin claude/eloquent-mayer-264bxk && git log --oneline -1
sudo bash deploy/install.sh --role analytics
ls -l /opt/rugsnipe/bin/rugsnipe-long
```
The code lives in the `xin10ylop/rugsnipe` repo, branch `claude/eloquent-mayer-264bxk`. This repo (copy2) is a snapshot of it.

**2. fra1's settings, under their own names** (Ohio's own files aren't touched):
```
sudo mkdir -p -m 700 /root/fra1
sudo tar xzf /root/backups/fra1-backup.tgz -C /root/fra1 etc/rugsnipe var/lib/rugsnipe var/lib/rugsnipe-long
sudo install -m 0640 -o root -g rugsnipe /root/fra1/etc/rugsnipe/rugsnipe.toml /etc/rugsnipe/fra1-hot.toml
sudo install -m 0600 -o root -g root /root/fra1/etc/rugsnipe/keys/api-keys.toml /etc/rugsnipe/keys/fra1-api-keys.toml
sudo sed -e 's#^hot_config = .*#hot_config = "/etc/rugsnipe/fra1-hot.toml"#' -e 's#^mode = .*#mode = "log"#' /root/fra1/etc/rugsnipe/long.toml | sudo tee /etc/rugsnipe/long.toml >/dev/null
sudo chown root:rugsnipe /etc/rugsnipe/long.toml && sudo chmod 0640 /etc/rugsnipe/long.toml
sudo grep -E '^(mode|hot_config|stake_sol|min_sol) ' /etc/rugsnipe/long.toml
```
The last line must print `mode = "log"` (paper) and `hot_config = "/etc/rugsnipe/fra1-hot.toml"`.

**3. The service without a wallet, the earlier paper record, start.** Run it from `~/rugsnipe`:
```
cd ~/rugsnipe
sed -e 's#/etc/rugsnipe/keys/api-keys.toml#/etc/rugsnipe/keys/fra1-api-keys.toml#' -e '/long-wallet/d' deploy/systemd/rugsnipe-long.service | sudo tee /etc/systemd/system/rugsnipe-long.service >/dev/null
grep -c . /etc/systemd/system/rugsnipe-long.service          # about 50; 0 means the file is empty
sudo install -d -o rugsnipe -g rugsnipe -m 0750 /var/lib/rugsnipe-long
sudo cp /root/fra1/var/lib/rugsnipe-long/{positions.json,closed.jsonl} /var/lib/rugsnipe-long/
sudo chown -R rugsnipe:rugsnipe /var/lib/rugsnipe-long && sudo ls -l /var/lib/rugsnipe-long
sudo systemctl daemon-reload && sudo systemctl enable --now rugsnipe-long
sleep 30; sudo journalctl -u rugsnipe-long -n 30 --no-pager
```
Expect `long: no wallet (...): paper only`, `long start: mode Log ... max_open 4` and `long feed connected`.

**What went wrong the first time (Oct 27), and how to avoid it:**
- After an SSH drop the user logged back into `~`, not `~/rugsnipe`. Then `sed` couldn't find
  `deploy/systemd/rugsnipe-long.service`, so `tee` wrote an empty unit, and systemd treats an empty unit as **masked**
  (`Failed to enable unit: ... is masked`). Fix: `cd ~/rugsnipe` first, and check the `grep -c .` count.
- `sudo chown rugsnipe:rugsnipe /var/lib/rugsnipe-long/*` failed (`cannot access ... No such file or directory`): the
  `*` is expanded by your shell, which can't list that folder. Use `sudo chown -R` on the folder.

**4. The history tool** (both bots, from saved files, read-only):
```
git -C ~/rugsnipe fetch -q origin claude/eloquent-mayer-264bxk && git -C ~/rugsnipe show FETCH_HEAD:deploy/bin/rugsnipe-history > ~/history.py
```

## 2. Checking it

```
sudo python3 -I ~/history.py paper                                    # the long copy's paper book, every position
sudo /opt/rugsnipe/bin/rugsnipe-long status --config /etc/rugsnipe/long.toml --last 30
sudo journalctl -u rugsnipe-long -f                                   # live (Ctrl+C stops watching, not the bot)
sudo python3 -I ~/history.py --root /root/fra1                        # the copy bot's history from fra1's backup (check.sh's view)
sudo python3 -I ~/history.py all --root /root/fra1                    # the same with every trade
```
`bash ~/check.sh` does not work on Ohio: it read fra1's live bot (its journal, its config, its database).
`history.py` (check mode) shows the same totals from the backup. The full check.sh output from fra1's last day is
`05-live/check-sh-2026-10-27.txt`.

## 3. Changing a setting

`install.sh` never overwrites an existing `/etc/rugsnipe/long.toml`, so a new repo default (for example `max_open = 4`)
needs the box's file changed too:
```
sudo sed -i -E 's/^max_open[[:space:]]*=.*/max_open = 4/' /etc/rugsnipe/long.toml
sudo grep -n '^max_open' /etc/rugsnipe/long.toml
sudo systemctl restart rugsnipe-long && sleep 15 && sudo journalctl -u rugsnipe-long -n 3 --no-pager
```
Restarting is safe: open positions and the paper record are kept (`positions.json`, `closed.jsonl`).

## 4. Updating the code: **pending; now this repo's branch (Oct 28 evening), which includes `7184554`**

The hardened code lives in this repo (`xin10ylop/copy2`, branch `claude/magical-einstein-k78idp`), ahead of upstream.
Point the box's checkout at it (copy2 is public: no key needed), build, set the paper switch, restart. On Ohio
(`ubuntu@ip-172-31-17-131`):
```
cd ~/rugsnipe
git remote add copy2 https://github.com/xin10ylop/copy2.git 2>/dev/null; git fetch -q copy2 claude/magical-einstein-k78idp
git checkout -q -B rework copy2/claude/magical-einstein-k78idp && git log --oneline -1
sudo bash deploy/install.sh --role analytics
sudo grep -q '^follow_its_sell' /etc/rugsnipe/long.toml || echo 'follow_its_sell = false' | sudo tee -a /etc/rugsnipe/long.toml
sudo systemctl restart rugsnipe-long && sleep 15 && sudo journalctl -u rugsnipe-long -n 4 --no-pager
```
What each line should print: `git log` one line with the branch's latest commit (the Oct 28 evening hardening); the
installer's usual log ending without an error; `tee` echoes `follow_its_sell = false`; the journal shows `long start:
mode Log ...` and `long feed connected`. From then on the journal has `long paper-buy ... seen at its slot +N` (Ohio's
feed lag), `long paper-sell ... fills at the end of slot +1`, and on its early sales `long its-sell #N ... not followed
(would make X SOL)`, with `its_sell_net` on every record in `closed.jsonl`, so one paper run measures both exit policies.
To go back to upstream: `git checkout -q claude/eloquent-mayer-264bxk && sudo bash deploy/install.sh --role analytics`.

The old update line (upstream, `7184554` only):
```
cd ~/rugsnipe && git pull -q --ff-only origin claude/eloquent-mayer-264bxk && git log --oneline -1
sudo bash deploy/install.sh --role analytics
sudo systemctl restart rugsnipe-long && sleep 15 && sudo journalctl -u rugsnipe-long -n 4 --no-pager
```
The `git log` line should print `7184554` (paper fills a slot after Ohio saw the buy; journal `seen at its slot +N`).
Earlier updates on Ohio: `f52cee5` (its_sell), `0aa4f24` (paper refusal), `2314377` (cap 4), all done by Oct 28 00:35
UTC. After `7184554`, read Ohio's lag with:
```
sudo journalctl -u rugsnipe-long --since "2026-10-28 00:00" --no-pager | grep -E 'paper-refused|paper-buy'
```

## 5. Stop, pause, money

- **Pause new buys:** `sudo touch /var/lib/rugsnipe-long/KILL` (exits continue); `sudo rm` it to resume.
- **Stop:** `sudo systemctl stop rugsnipe-long`. It starts again by itself after a reboot while enabled.
- **Cost:** Ohio charges while it runs. AWS **Stop** keeps the disk (and the only copy of fra1's backup); **Terminate**
  deletes both.
- **Real money:** not on this box yet. See [going-live.md](going-live.md) (wallet, Temporal's US endpoint, WBTC float,
  `mode = "on"`).

## Sources

- Session setup of Oct 27 (the commands as run, the two errors and their fixes); `deploy/install.sh`;
  `deploy/systemd/rugsnipe-long.service`; `deploy/bin/rugsnipe-history` (its header); `docs/20-long-copy.md` §4 (the
  fra1 runbook).
