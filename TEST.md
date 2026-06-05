# 测试说明（nginx 在容器里安装，不靠从 Pod 拷 mime.types）

## 三层测试

### 1. 只测后端（不要 nginx）
容器内或本机：
```bash
cd /opt/gemini-h5/backend && python3 main.py
curl -s -X POST http://127.0.0.1:8000/api/chat -H 'Content-Type: application/json' -d '{"message":"测试"}'
```
浏览器无法直接打开 H5 调 API（页面请求 `/api/chat` 需要反代）。

### 2. 测 H5 静态页（不要 Flask）
```bash
cd html && python3 -m http.server 9000
```
只能看页面，点提交会 404（没有 /api）。

### 3. 完整测试（与线上一致，需要 nginx）
```bash
docker compose up -d --build
curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:10000/
curl -s -X POST http://127.0.0.1:10000/api/chat -H 'Content-Type: application/json' -d '{"message":"测试"}'
```
nginx:10000 -> 静态页 + /api/ -> Flask:8000

## 临时关闭 FRP（避免与 73 抢 55730）
编辑 supervisord.conf，注释 [program:frpc] 整段后再 build。
