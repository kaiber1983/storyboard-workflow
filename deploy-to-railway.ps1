# Railway 部署自动化脚本
# 使用方法：在 PowerShell 中运行此脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Storyboard Workflow - Railway 部署" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Git 是否安装
Write-Host "[1/5] 检查 Git 是否安装..." -ForegroundColor Yellow
$gitInstalled = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitInstalled) {
    Write-Host "❌ 未检测到 Git，请先安装 Git：https://git-scm.com/download/win" -ForegroundColor Red
    Write-Host "安装后重新运行此脚本。" -ForegroundColor Red
    pause
    exit
}
Write-Host "✅ Git 已安装" -ForegroundColor Green
Write-Host ""

# 检查是否已经初始化 Git
Write-Host "[2/5] 检查 Git 仓库状态..." -ForegroundColor Yellow
if (Test-Path ".git") {
    Write-Host "⚠️  检测到已存在的 Git 仓库" -ForegroundColor Yellow
    $continue = Read-Host "是否继续？这将添加新的提交 (y/n)"
    if ($continue -ne "y") {
        Write-Host "已取消" -ForegroundColor Red
        pause
        exit
    }
} else {
    Write-Host "初始化 Git 仓库..." -ForegroundColor Cyan
    git init
    Write-Host "✅ Git 仓库初始化完成" -ForegroundColor Green
}
Write-Host ""

# 获取 GitHub 仓库地址
Write-Host "[3/5] 配置 GitHub 仓库" -ForegroundColor Yellow
Write-Host "请先在 GitHub 上创建一个新仓库（不要添加 README、.gitignore 或 license）" -ForegroundColor Cyan
Write-Host "然后复制仓库地址，例如：https://github.com/username/repo.git" -ForegroundColor Cyan
Write-Host ""
$repoUrl = Read-Host "请输入你的 GitHub 仓库地址"

if ([string]::IsNullOrWhiteSpace($repoUrl)) {
    Write-Host "❌ 仓库地址不能为空" -ForegroundColor Red
    pause
    exit
}

# 检查是否已经添加了 remote
$remoteExists = git remote | Select-String "origin"
if ($remoteExists) {
    Write-Host "⚠️  检测到已存在的 origin，将更新地址" -ForegroundColor Yellow
    git remote set-url origin $repoUrl
} else {
    git remote add origin $repoUrl
}
Write-Host "✅ GitHub 仓库配置完成" -ForegroundColor Green
Write-Host ""

# 添加文件并提交
Write-Host "[4/5] 添加文件并提交..." -ForegroundColor Yellow
git add .
git commit -m "Initial commit: Storyboard Workflow with Railway deployment"
Write-Host "✅ 文件已提交" -ForegroundColor Green
Write-Host ""

# 推送到 GitHub
Write-Host "[5/5] 推送到 GitHub..." -ForegroundColor Yellow
Write-Host "如果提示需要登录，请按照提示操作" -ForegroundColor Cyan
git branch -M main
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 代码已成功推送到 GitHub！" -ForegroundColor Green
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  下一步：部署到 Railway" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. 访问 https://railway.app" -ForegroundColor White
    Write-Host "2. 使用 GitHub 账号登录" -ForegroundColor White
    Write-Host "3. 点击 'New Project' → 'Deploy from GitHub repo'" -ForegroundColor White
    Write-Host "4. 选择你的仓库并部署" -ForegroundColor White
    Write-Host "5. 在 Settings → Networking 中生成域名" -ForegroundColor White
    Write-Host ""
    Write-Host "详细步骤请查看：部署步骤.txt" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "❌ 推送失败，请检查：" -ForegroundColor Red
    Write-Host "1. GitHub 仓库地址是否正确" -ForegroundColor White
    Write-Host "2. 是否有权限推送到该仓库" -ForegroundColor White
    Write-Host "3. 网络连接是否正常" -ForegroundColor White
    Write-Host ""
    Write-Host "如需帮助，请查看错误信息或联系支持" -ForegroundColor Yellow
}

Write-Host ""
pause
