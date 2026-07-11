# GitHubへの変更をコミット&プッシュするスクリプト
# 使い方: .\push.ps1 "コミットメッセージ"

param(
    [Parameter(Mandatory = $false)]
    [string]$Message
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not $Message) {
    $Message = Read-Host "コミットメッセージを入力してください"
    if (-not $Message) {
        Write-Host "コミットメッセージが空のため中止しました。" -ForegroundColor Yellow
        exit 1
    }
}

git status --short

git add -A

$staged = git diff --cached --name-only
if (-not $staged) {
    Write-Host "コミットする変更がありません。" -ForegroundColor Yellow
    exit 0
}

git commit -m $Message
if (-not $?) {
    Write-Host "コミットに失敗しました。" -ForegroundColor Red
    exit 1
}

$branch = git rev-parse --abbrev-ref HEAD
git push origin $branch
if (-not $?) {
    Write-Host "プッシュに失敗しました。" -ForegroundColor Red
    exit 1
}

Write-Host "GitHubへのプッシュが完了しました。(branch: $branch)" -ForegroundColor Green
