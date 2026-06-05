# Windows 推送到 GitHub
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

$branch = if ($env:GITHUB_BRANCH) { $env:GITHUB_BRANCH } else { "main" }

if ($env:GITHUB_TOKEN) {
    $owner = $env:GITHUB_OWNER
    if (-not $owner) { throw "请设置环境变量 GITHUB_OWNER" }
    $repo = if ($env:GITHUB_REPO) { $env:GITHUB_REPO } else { "gemini-h5" }
    git push "https://$($env:GITHUB_TOKEN)@github.com/$owner/$repo.git" "${branch}:${branch}"
} else {
    git push github $branch
}

Write-Host "GitHub 推送完成"
