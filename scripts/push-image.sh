#!/bin/bash
# 在 72 上：构建并推送到远程仓库，新机即可 docker pull
set -e
cd "$(dirname "$0")/.."

if [ -f registry.env ]; then
  # shellcheck disable=SC1091
  source registry.env
fi

IMAGE="${DOCKER_IMAGE:?请复制 registry.env.example 为 registry.env 并设置 DOCKER_IMAGE}"
LOCAL_TAG="${LOCAL_IMAGE_TAG:-gemini-h5:latest}"

docker compose build
docker tag "$LOCAL_TAG" "$IMAGE"
docker push "$IMAGE"

echo ""
echo "推送完成: $IMAGE"
echo ""
echo "新机一条命令启动:"
echo "  docker pull $IMAGE && docker run -d --name gemini-h5 --restart unless-stopped -p 10000:10000 -v gemini-h5-data:/opt/gemini-h5/backend/data $IMAGE"
echo ""
echo "或使用: bash scripts/pull-and-run.sh（需同目录 registry.env）"
