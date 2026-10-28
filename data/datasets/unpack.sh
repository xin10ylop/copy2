#!/bin/bash
# unpack.sh [NAME...]: check and unpack the datasets (all, or the NAMEs) into the scratchpad path the research
# scripts hard-code, so they run unchanged. SP=/other/dir bash unpack.sh puts them elsewhere (then edit SP in the scripts).
set -euo pipefail
D=$(cd "$(dirname "$0")" && pwd)
SP=${SP:-/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad}
(cd "$D" && sha256sum --quiet -c SHA256SUMS)
mkdir -p "$SP"
if [ $# -gt 0 ]; then names=("$@"); else
  mapfile -t names < <(ls "$D" | sed -n -E 's/^([A-Za-z0-9_]+)\.tar\.xz(\.part-[0-9]+)?$/\1/p' | sort -u); fi
for n in "${names[@]}"; do
  if [ -f "$D/$n.tar.xz" ]; then xz -dc "$D/$n.tar.xz"; else cat "$D/$n".tar.xz.part-* | xz -dc; fi | tar -xf - -C "$SP"
  echo "unpacked $n into $SP"
done
