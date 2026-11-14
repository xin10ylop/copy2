# Moving the long copy to another box (Nov 14)

Why: Vultr asked the owner for a passport and ID on Nov 14; the owner chose to move to Cherry Servers **Cloud VDS 2**
(Gen 1, `G1-4-16gb-100nv-ded`, 4 vCores on 2 physical cores, 16 GB, 100 GB NVMe), **Frankfurt**, back in stock,
$33.93 a month on the autumn sale. The rules of Oct 29 hold: **monthly billing**, the wallet file never only on one
box, and **only one box runs the wallet at a time** (two would both buy every copy).

The order:
1. **Order** (Cherry portal): Cloud VDS 2, the German flag, Ubuntu 24.04, monthly billing.
2. **New box as root:** password, full upgrade, hostname `fra-long2`, user `ops` in `sudo`, the four pings
   (`../07-rework-2026-10-28/infra.md` §9 test 1; every average under 1 ms), reboot.
3. **From the laptop:** `ssh-copy-id ops@NEW`; then on the box password login off, and a second login checked.
4. **New box as ops:** clone this branch, `sudo bash deploy/install.sh --role hot --force`, then
   `/etc/rugsnipe/keys/api-keys.toml` typed in from the Triton and Nozomi dashboards (`deploy-frankfurt.md` §1),
   0400. If a dashboard limits by IP, add the new one.
5. **The move, when the old box shows `0 open`:** on the old box `disable --now` the unit first; copy the wallet
   file, `long.toml`, `rugsnipe.toml` and a tar of `/var/lib/rugsnipe-long` (the book and the booked fees) to `~`
   for `ops`; laptop `scp` old → laptop → new; sha256 prefix of the wallet file compared on both boxes; installed on
   the new box (wallet 0400 root, configs 0600 root, the state owned by `rugsnipe`); the home copies deleted on both;
   `enable --now` on the new box. Check: the start line names `Eao8T2Pk...` and the live settings, `long feed
   connected`, and `status --chain` shows the same book.
6. **Then** the old box is destroyed in Vultr's portal (its disk with it) and the laptop keeps the wallet file.
