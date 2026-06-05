#!/bin/bash
# 新机：docker pull 后直接运行（需已 docker login，私有仓库时）
set -e
cd "$(dirname "$0")/.."

if [ -f registry.env ]; then
  # shellcheck disable=SC1091
  source registry.env
fi

IMAGE="${DOCKER_IMAGE:?请设置 registry.env 中的 DOCKER_IMAGE（与 push 时一致）}"

docker pull "$IMAGE"
docker stop gemini-h5 2>/dev/null || true
docker rm gemini-h5 2>/dev/null || true
docker run -d \
  --name gemini-h5 \
  --restart unless-stopped \
  -p 10000:10000 \
  -v gemini-h5-data:/opt/gemini-h5/backend/data \
  "$IMAGE"

echo ""
echo "已启动: http://$(hostname -I | awk '{print $1}'):10000/"
docker ps --filter name=gemini-h5
