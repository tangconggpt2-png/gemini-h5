param(
    [string]$Owner,
    [string]$Repo = "gemini-h5",
    [string]$Token,
    [string]$Branch = "main"
)

$ErrorActionPreference = "Stop"
if (-not $Owner) { $Owner = $env:GITHUB_OWNER }
if (-not $Token) { $Token = $env:GITHUB_TOKEN }
if (-not $Token) { throw "Set GITHUB_TOKEN" }
if (-not $Owner) { throw "Set GITHUB_OWNER" }

$root = Split-Path $PSScriptRoot -Parent
$headers = @{
    Authorization = "Bearer $Token"
    "User-Agent"  = "gemini-h5-deploy"
}

try {
    Invoke-RestMethod -Uri "https://api.github.com/repos/$Owner/$Repo" -Headers $headers -TimeoutSec 30 | Out-Null
} catch {
    throw "Repo $Owner/$Repo not found. Create empty repo gemini-h5 on GitHub first."
}

Push-Location $root
$files = @(git ls-files)
if ($files.Count -eq 0) { throw "No files to upload" }

Write-Host "Uploading $($files.Count) files to $Owner/$Repo ..."

$tree = @()
foreach ($path in $files) {
    $full = Join-Path $root $path
    $bytes = [System.IO.File]::ReadAllBytes($full)
    $b64 = [Convert]::ToBase64String($bytes)
    $blobBody = @{ content = $b64; encoding = "base64" } | ConvertTo-Json
    $blob = Invoke-RestMethod -Method Post `
        -Uri "https://api.github.com/repos/$Owner/$Repo/git/blobs" `
        -Headers $headers -ContentType "application/json" -Body $blobBody
    $tree += @{
        path = ($path -replace "\\", "/")
        mode = "100644"
        type = "blob"
        sha  = $blob.sha
    }
    Write-Host "  $path"
}

$treeBody = @{ tree = $tree } | ConvertTo-Json -Depth 6
$treeObj = Invoke-RestMethod -Method Post `
    -Uri "https://api.github.com/repos/$Owner/$Repo/git/trees" `
    -Headers $headers -ContentType "application/json" -Body $treeBody

$commitBody = @{
    message = "Sync from Codeup"
    tree    = $treeObj.sha
} | ConvertTo-Json
$commit = Invoke-RestMethod -Method Post `
    -Uri "https://api.github.com/repos/$Owner/$Repo/git/commits" `
    -Headers $headers -ContentType "application/json" -Body $commitBody

$updated = $false
try {
    $refBody = @{ sha = $commit.sha; force = $true } | ConvertTo-Json
    Invoke-RestMethod -Method Patch `
        -Uri "https://api.github.com/repos/$Owner/$Repo/git/refs/heads/$Branch" `
        -Headers $headers -ContentType "application/json" -Body $refBody | Out-Null
    $updated = $true
} catch {
    $null = $_
}

if (-not $updated) {
    $refBody = @{ ref = "refs/heads/$Branch"; sha = $commit.sha } | ConvertTo-Json
    Invoke-RestMethod -Method Post `
        -Uri "https://api.github.com/repos/$Owner/$Repo/git/refs" `
        -Headers $headers -ContentType "application/json" -Body $refBody | Out-Null
}

Pop-Location
Write-Host "Done: https://github.com/$Owner/$Repo"
