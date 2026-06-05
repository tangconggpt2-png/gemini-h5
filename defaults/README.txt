镜像内置默认配置（构建时打入镜像）
================================

此目录下的 config/ 与 examples/ 会在容器启动时复制到运行目录，
仅当外部挂载目录中对应文件不存在时生效。

换机部署时：即使宿主机 config/、examples/ 为空或未准备，服务也能用这里的默认值启动。

更新镜像默认值：修改本目录后执行 docker compose up -d --build

换机方式一（离线 tar）：
  旧机 save-image.sh → 新机 load-and-run.sh

换机方式二（在线 pull，推荐）：
  1. 复制 registry.env.example → registry.env，填写 DOCKER_IMAGE
  2. docker login 后，旧机: bash scripts/push-image.sh
  3. 新机: bash scripts/pull-and-run.sh
  或一条命令:
  docker pull <镜像名> && docker run -d --name gemini-h5 --restart unless-stopped -p 10000:10000 -v gemini-h5-data:/opt/gemini-h5/backend/data <镜像名>
