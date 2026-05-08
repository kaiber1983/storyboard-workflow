# Railway 快速部署教程

## 🚀 5 分钟部署到公网

### 前置准备

1. 一个 GitHub 账号
2. 一个 Railway 账号（用 GitHub 登录即可）

---

## 📝 详细步骤

### 步骤 1：将项目上传到 GitHub

如果你的项目还没有上传到 GitHub：

```bash
# 在项目文件夹中打开终端/命令行

# 初始化 Git 仓库
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: Storyboard Workflow"

# 在 GitHub 上创建新仓库后，连接远程仓库
git remote add origin https://github.com/你的用户名/仓库名.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

**重要文件清单（确保这些文件都在仓库中）：**
- ✅ `storyboard-workflow.html`
- ✅ `storyboard_agent_server.py`
- ✅ `requirements.txt`
- ✅ `railway.json`
- ✅ `AGENTS.md`（如果有）

---

### 步骤 2：在 Railway 创建项目

1. **访问 Railway**
   - 打开 [railway.app](https://railway.app)
   - 点击右上角 "Login" 使用 GitHub 登录

2. **创建新项目**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 授权 Railway 访问你的 GitHub
   - 选择你刚才创建的仓库

3. **等待自动部署**
   - Railway 会自动检测到 `railway.json` 和 `requirements.txt`
   - 自动安装依赖并启动服务
   - 大约 2-3 分钟完成

---

### 步骤 3：配置环境变量（可选）

如果你想启用服务器端大模型功能：

1. 在 Railway 项目页面，点击你的服务
2. 切换到 "Variables" 标签
3. 添加以下环境变量：

```
HOST=0.0.0.0
PORT=8787

# 启用大模型（可选）
STORYBOARD_LLM_ENABLED=true
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=sk-你的OpenAI密钥
```

4. 点击 "Add" 保存

**注意：** 如果不配置这些，用户仍然可以在网页中手动输入 API 配置。

---

### 步骤 4：生成公网域名

1. 在 Railway 项目页面，点击 "Settings" 标签
2. 找到 "Domains" 部分
3. 点击 "Generate Domain"
4. Railway 会自动生成一个域名，例如：
   ```
   https://storyboard-workflow-production.up.railway.app
   ```

5. **复制这个域名，分享给你的朋友！**

---

### 步骤 5：测试你的应用

1. 访问生成的域名
2. 你应该能看到"剧本到分镜生产流程"页面
3. 测试功能：
   - 点击"填入示例"
   - 点击"生成分镜与提示词"
   - 查看是否正常生成分镜表

---

## 🎉 完成！

你的应用现在已经部署到公网，任何人都可以通过域名访问。

### 后续操作

**更新代码：**
```bash
# 修改代码后
git add .
git commit -m "更新说明"
git push

# Railway 会自动检测到更新并重新部署
```

**查看日志：**
- 在 Railway 项目页面，点击 "Deployments"
- 点击最新的部署，查看 "Logs" 标签

**监控使用情况：**
- 在 Railway 项目页面，点击 "Metrics"
- 查看 CPU、内存、网络使用情况
- 免费额度：$5/月（约 500 小时运行时间）

---

## ⚠️ 常见问题

### 1. 部署失败？

**检查 requirements.txt：**
确保文件内容正确：
```
openai>=1.50.0
python-dotenv>=1.0.0
requests>=2.31.0
```

**检查 railway.json：**
确保文件存在且格式正确。

### 2. 访问域名显示 404？

- 等待 2-3 分钟，部署可能还在进行中
- 检查 Railway 的 Logs，看是否有错误信息
- 确保 `storyboard-workflow.html` 文件在仓库中

### 3. 后端功能不工作？

- 检查浏览器控制台（F12）是否有错误
- 确保 `storyboard_agent_server.py` 正确启动
- 查看 Railway Logs 中的错误信息

### 4. 超出免费额度？

Railway 免费额度用完后：
- 方案 1：升级到付费计划（$5/月起）
- 方案 2：迁移到 Render（完全免费但会休眠）
- 方案 3：使用自己的服务器

---

## 📞 需要帮助？

如果遇到问题，提供以下信息：
1. Railway 部署日志（Logs 标签）
2. 浏览器控制台错误信息（F12）
3. 具体的错误描述

我可以帮你诊断和解决问题！
