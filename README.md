# gemini-h5

无障碍 H5 文案助手：Flask + nginx + frp，支持 prompt / 示例 / API 配置热更新。

## 快速部署（推荐：ACR 拉镜像）

```bash
docker pull crpi-v6rtj1tjk3pa7z2d.cn-hangzhou.personal.cr.aliyuncs.com/tangcong0526/gemini-h5:latest
docker run -d --name gemini-h5 --restart unless-stopped \
  -p 10000:10000 \
  -v gemini-h5-data:/opt/gemini-h5/backend/data \
  crpi-v6rtj1tjk3pa7z2d.cn-hangzhou.personal.cr.aliyuncs.com/tangcong0526/gemini-h5:latest
```

## 从源码构建

```bash
cp .env.example .env
cp config/ai.config.example config/ai.config    # 填写 API
cp frp/frpc.ini.example frp/frpc.ini            # 填写 FRP token
# 将 frpc 二进制放入 frp/

docker compose up -d --build
```

## 配置说明

见 `config/说明.txt`。运行时优先读挂载目录，否则用镜像内 `defaults/`。

## 推送镜像到 ACR

```bash
cp registry.env.example registry.env
docker login crpi-v6rtj1tjk3pa7z2d.cn-hangzhou.personal.cr.aliyuncs.com
bash scripts/push-image.sh
```
