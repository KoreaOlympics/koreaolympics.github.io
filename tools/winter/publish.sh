#!/usr/bin/env bash
# Commit data/winter + the winter hubs with a live block and deploy, only when real data changed.
# usage: tools/winter/publish.sh [force]   (force: commit even if only status.json changed)
set -euo pipefail
git add data/winter wishorttrack.html wispeedskating.html wifigure.html wisnowboard.html wialpine.html wicrosscountry.html \
  wiskijumping.html wifreestyle.html wibiathlon.html wibobsleigh.html wiskeleton.html wiluge.html
if git diff --cached --quiet -- . ':(exclude)data/winter/status.json' && [ "${1:-}" != force ]; then
  git reset -q
  echo "no data changes"; exit 0
fi
git commit -q -m "winter: update live data"
for i in 1 2 3; do git pull -q --rebase && git push -q && break; sleep 5; done
git diff --quiet HEAD @{u}
# bot pushes do not trigger push-based deploys; start the Pages deploy explicitly
gh workflow run pages.yml --ref main
