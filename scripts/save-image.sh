#!/bin/bash
# 在 72（或任意已构建的机器）上执行，导出可迁移镜像包
set -e
cd "$(dirname "$0")/.."

docker compose build
docker save gemini-h5:latest -o gemini-h5-image.tar

echo ""
echo "已导出: $(pwd)/gemini-h5-image.tar"
echo "换机方式一（离线）拷贝:"
echo "  gemini-h5-image.tar + docker-compose.image.yml + scripts/load-and-run.sh"
echo ""
echo "换机方式二（在线）推荐:"
echo "  1. 配置 registry.env 后执行 bash scripts/push-image.sh"
echo "  2. 新机 bash scripts/pull-and-run.sh"
