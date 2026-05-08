# 剧本到分镜生产流程 - 部署版

一个专业的影视分镜故事板生成工具，支持剧本输入、自动分镜、AI 提示词生成。

## ✨ 功能特点

- 📝 **剧本解析** - 自动将剧本拆分为连续的分镜 Cut
- 🎬 **专业分镜表** - 生成包含景别、机位、运镜、调度等专业信息
- 🤖 **AI 提示词** - 自动生成用于 Midjourney/Stable Diffusion 的图像提示词
- 🎥 **视频提示词** - 生成用于 Runway/Pika 的视频生成提示词
- 🖼️ **参考图支持** - 上传角色、场景、版式参考图
- 🧠 **大模型集成** - 可选接入 OpenAI 等大模型优化生成质量

## 🚀 快速开始

### 本地运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动服务
python storyboard_agent_server.py

# 3. 打开浏览器访问
http://127.0.0.1:8787
```

### 部署到公网

我们提供了多种部署方案，选择最适合你的：

#### 方案 1：Railway（推荐）
- ⚡ 5 分钟完成部署
- 💰 免费额度 $5/月
- 🔒 自动 HTTPS
- 📖 [查看详细教程](./Railway部署教程.md)

#### 方案 2：Render
- 🆓 完全免费
- 🔒 自动 HTTPS
- ⏰ 15 分钟无访问会休眠
- 📖 [查看部署指南](./部署指南.md)

#### 方案 3：Docker
- 🐳 适合自有服务器
- 💪 完全控制
- 📖 [查看部署指南](./部署指南.md)

## 📚 文档

- [完整部署指南](./部署指南.md) - 所有部署方案对比
- [Railway 快速教程](./Railway部署教程.md) - 5 分钟上线
- [原始部署文档](./DEPLOY.md) - 技术细节

## 🔧 环境变量配置

### 基础配置

```bash
HOST=0.0.0.0          # 监听地址
PORT=8787             # 端口号
```

### 大模型配置（可选）

```bash
STORYBOARD_LLM_ENABLED=true                    # 启用大模型
LLM_BASE_URL=https://api.openai.com/v1        # API 地址
LLM_MODEL=gpt-4o-mini                          # 模型名称
LLM_API_KEY=sk-your-api-key                    # API 密钥
```

**注意：** 如果不配置服务器端大模型，用户仍可在网页中手动输入 API 配置。

## 📦 项目结构

```
├── storyboard-workflow.html      # 前端页面
├── storyboard_agent_server.py    # Python 后端服务
├── AGENTS.md                      # Agent 规则文件
├── requirements.txt               # Python 依赖
├── Dockerfile                     # Docker 配置
├── railway.json                   # Railway 配置
├── render.yaml                    # Render 配置
├── 部署指南.md                    # 完整部署文档
└── Railway部署教程.md             # 快速部署教程
```

## 🎯 使用流程

1. **输入剧本** - 描述剧情、动作、情绪、地点
2. **配置参数** - 设置时长、分镜数量、画幅比例
3. **上传参考图**（可选）- 角色、场景、版式参考
4. **生成分镜** - 点击"生成分镜与提示词"
5. **获取提示词** - 复制提示词到 AI 工具生成图片/视频

## 🔐 安全建议

- ✅ 使用环境变量存储 API 密钥
- ✅ 不要在前端代码中硬编码密钥
- ✅ 部署到公网时启用 HTTPS
- ✅ 考虑添加访问频率限制

## 📊 技术栈

- **前端：** HTML + CSS + JavaScript（原生）
- **后端：** Python 3.11 + http.server
- **AI 集成：** OpenAI API（可选）
- **部署：** Railway / Render / Docker

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

## 🆘 需要帮助？

- 📖 查看 [部署指南](./部署指南.md)
- 🚀 查看 [Railway 教程](./Railway部署教程.md)
- 💬 提交 Issue 获取支持

---

**立即开始：** 选择一个部署方案，5 分钟让你的应用上线！
