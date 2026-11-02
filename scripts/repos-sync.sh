#!/usr/bin/env bash
# Clone every repo listed in repos/manifest.txt that is missing, then fetch and
# show a one-line status for each. Usage: scripts/repos-sync.sh [--no-fetch]
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
manifest="$root/repos/manifest.txt"
fetch=1
[[ "${1:-}" == "--no-fetch" ]] && fetch=0

[[ -f "$manifest" ]] || { echo "no manifest at $manifest" >&2; exit 1; }

while read -r name url branch _; do
  [[ -z "$name" || "$name" == \#* ]] && continue
  dir="$root/repos/$name"
  if [[ ! -d "$dir/.git" ]]; then
    echo "== $name: cloning $url"
    if [[ -n "${branch:-}" ]]; then
      git clone --branch "$branch" "$url" "$dir"
    else
      git clone "$url" "$dir"
    fi
    continue
  fi
  if (( fetch )); then
    git -C "$dir" fetch --quiet --all --prune || echo "   fetch failed (no access or offline)"
  fi
  br="$(git -C "$dir" rev-parse --abbrev-ref HEAD 2>/dev/null || echo detached)"
  dirty="$(git -C "$dir" status --porcelain | wc -l)"
  read -r behind ahead < <(git -C "$dir" rev-list --left-right --count "@{upstream}...HEAD" 2>/dev/null || echo "- -")
  echo "== $name: $br  dirty=$dirty  ahead=$ahead  behind=$behind"
done < "$manifest"
