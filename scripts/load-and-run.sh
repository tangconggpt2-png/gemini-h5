#!/bin/bash
# 在新机器上执行（与 gemini-h5-image.tar、docker-compose.image.yml 放同一目录）
set -e
cd "$(dirname "$0")/.."

if [ ! -f gemini-h5-image.tar ]; then
  echo "缺少 gemini-h5-image.tar，请先从旧机执行 scripts/save-image.sh"
  exit 1
fi

docker load -i gemini-h5-image.tar
docker compose -f docker-compose.image.yml up -d

echo ""
echo "已启动。本机访问: http://127.0.0.1:10000/"
docker compose -f docker-compose.image.yml ps
