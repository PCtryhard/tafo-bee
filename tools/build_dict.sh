#!/usr/bin/env sh
# rebuild data/words.txt from the debian wbritish package (scowl en-gb size 50)
# needs docker, or ar + tar with zstd support
set -eu
cd "$(dirname "$0")/.."
src=/usr/share/dict/british-english
if docker info >/dev/null 2>&1; then
  raw=$(docker run --rm debian:stable-slim sh -c "apt-get -qq update >/dev/null && apt-get -qq install -y wbritish >/dev/null && cat $src")
else
  tmp=$(mktemp -d)
  curl -sSL http://archive.ubuntu.com/ubuntu/pool/main/s/scowl/wbritish_2020.12.07-2_all.deb -o "$tmp/wb.deb"
  (cd "$tmp" && ar x wb.deb && tar xf data.tar.* ".$src")
  raw=$(cat "$tmp$src"); rm -rf "$tmp"
fi
printf '%s\n' "$raw" | grep -E '^[a-z]{4,}$' | sort -u > data/words.txt
touch data/exclude.txt
wc -l data/words.txt
