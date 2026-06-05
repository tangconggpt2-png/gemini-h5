#!/bin/bash
# 推送到 GitHub（需先创建空仓库并配置认证）
set -e
cd "$(dirname "$0")/.."

REMOTE="${GITHUB_REMOTE:-github}"
BRANCH="${GITHUB_BRANCH:-main}"

if [ -n "$GITHUB_TOKEN" ]; then
  OWNER="${GITHUB_OWNER:?请设置 GITHUB_OWNER，如 tangcong0526}"
  REPO="${GITHUB_REPO:-gemini-h5}"
  git push "https://${GITHUB_TOKEN}@github.com/${OWNER}/${REPO}.git" "${BRANCH}:${BRANCH}"
else
  git push "$REMOTE" "${BRANCH}"
fi

echo "GitHub 推送完成"
