# Windows 新机测试用（需已安装 Docker Desktop）
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

if (-not (Test-Path "gemini-h5-image.tar")) {
    throw "缺少 gemini-h5-image.tar"
}

docker load -i gemini-h5-image.tar
docker compose -f docker-compose.image.yml up -d
docker compose -f docker-compose.image.yml ps
Write-Host "访问: http://127.0.0.1:10000/"
