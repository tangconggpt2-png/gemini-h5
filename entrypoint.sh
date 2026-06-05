#!/bin/sh
set -e

seed_dir() {
  src="$1"
  dst="$2"
  if [ ! -d "$src" ]; then
    return 0
  fi
  mkdir -p "$dst"
  for f in "$src"/*; do
    [ -f "$f" ] || continue
    base=$(basename "$f")
    if [ ! -f "$dst/$base" ]; then
      cp "$f" "$dst/$base"
      echo "seeded default: $dst/$base"
    fi
  done
}

seed_dir /opt/gemini-h5/defaults/config /opt/gemini-h5/backend/config
seed_dir /opt/gemini-h5/defaults/examples /opt/gemini-h5/backend/examples
mkdir -p /opt/gemini-h5/backend/data

exec /usr/bin/supervisord -c /etc/supervisord.conf
