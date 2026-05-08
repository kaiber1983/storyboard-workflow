# Image Studio 集成到分镜工具方案

## 📋 工具分析

### Image Studio 核心功能

这是一个基于 GPT Image-2 / DALL-E 3 / Gemini Imagen 3 的专业生图工具，具有以下特点：

**主要功能：**
1. ✅ **文生图（Text to Image）** - 直接从提示词生成图像
2. ✅ **图生图（Image to Image）** - 基于参考图生成新图像
3. ✅ **结构化提示词编辑器** - 分层管理提示词（主体、风格、质量、负面）
4. ✅ **词库系统** - 预设词库和组合词
5. ✅ **批量生成** - 支持一次生成多张图片
6. ✅ **本地保存** - 自动保存到本地目录
7. ✅ **图库管理** - 查看和管理生成的图片
8. ✅ **多模型支持** - GPT Image-2、DALL-E 3、Gemini Imagen 3、Grok Aurora
9. ✅ **高分辨率支持** - 最高支持 4K（3840x2160）

**技术特点：**
- 纯前端实现（单 HTML 文件）
- 使用 OpenAI 兼容 API
- 支持本地文件系统访问
- 响应式设计

---

## 🎯 集成方案

### 方案一：独立工具链接（推荐 - 最简单）

**实现方式：**
在分镜工具中添加一个"生成图像"按钮，点击后：
1. 自动复制当前组的图像提示词
2. 在新标签页打开 Image Studio
3. 用户粘贴提示词并生成

**优点：**
- ✅ 实现简单，无需修改现有代码
- ✅ 两个工具独立运行，互不干扰
- ✅ 用户可以自由调整参数

**缺点：**
- ❌ 需要手动复制粘贴
- ❌ 工作流不够流畅

**实现步骤：**
1. 将 Image Studio HTML 文件部署到 Railway
2. 在分镜工具中添加"打开生图工具"按钮
3. 点击时自动复制提示词并打开新窗口

---

### 方案二：嵌入式集成（推荐 - 最流畅）

**实现方式：**
将 Image Studio 作为 iframe 嵌入到分镜工具中，实现无缝集成。

**优点：**
- ✅ 工作流流畅，无需切换窗口
- ✅ 可以自动传递提示词
- ✅ 用户体验最佳

**缺点：**
- ❌ 需要修改两边的代码
- ❌ 可能有跨域问题

**实现步骤：**
1. 在分镜工具中添加"生成图像"标签页
2. 使用 iframe 嵌入 Image Studio
3. 通过 postMessage 传递提示词

---

### 方案三：API 集成（最强大）

**实现方式：**
在分镜工具后端添加图像生成功能，直接调用 OpenAI API。

**优点：**
- ✅ 完全集成，用户无需离开页面
- ✅ 可以自动化整个流程
- ✅ 可以批量生成所有分镜

**缺点：**
- ❌ 需要大量开发工作
- ❌ 需要处理 API 密钥安全问题
- ❌ 需要处理图像存储

**实现步骤：**
1. 在后端添加图像生成接口
2. 前端添加"一键生成所有分镜"功能
3. 自动调用 API 生成图像

---

## 💡 推荐方案：方案一 + 方案二 混合

**第一阶段：快速实现（方案一）**
- 立即部署 Image Studio
- 在分镜工具中添加链接按钮
- 用户可以快速开始使用

**第二阶段：优化体验（方案二）**
- 将 Image Studio 嵌入到分镜工具
- 实现自动传递提示词
- 优化工作流程

---

## 🚀 快速实现：方案一

### 步骤 1：部署 Image Studio

**方法 A：部署到 Railway（推荐）**

1. **创建新的 GitHub 仓库**
   ```bash
   # 创建新文件夹
   mkdir image-studio
   cd image-studio
   
   # 复制 HTML 文件
   cp "H:/xwechat_files/.../image-studio-standalone-v11(2).html" index.html
   
   # 初始化 Git
   git init
   git add .
   git commit -m "Initial commit: Image Studio"
   
   # 推送到 GitHub
   git remote add origin https://github.com/你的用户名/image-studio.git
   git push -u origin main
   ```

2. **在 Railway 部署**
   - 创建新项目
   - 选择 GitHub 仓库
   - Railway 会自动识别为静态网站
   - 生成域名

**方法 B：直接使用本地文件**
- 将 HTML 文件放到分镜工具的同一目录
- 通过相对路径访问

### 步骤 2：修改分镜工具，添加"生成图像"按钮

在 `storyboard-workflow.html` 中添加：

```html
<!-- 在每个提示词组后面添加按钮 -->
<button onclick="openImageStudio(this)" data-prompt="图像提示词内容">
  🎨 打开生图工具
</button>

<script>
function openImageStudio(btn) {
  const prompt = btn.dataset.prompt;
  
  // 复制提示词到剪贴板
  navigator.clipboard.writeText(prompt).then(() => {
    // 打开 Image Studio
    window.open('https://你的image-studio域名.railway.app', '_blank');
    
    // 提示用户
    alert('提示词已复制！请在新窗口中粘贴（Ctrl+V）');
  });
}
</script>
```

### 步骤 3：优化提示词格式

确保分镜工具生成的提示词格式与 Image Studio 兼容：

```javascript
// 在生成提示词时，添加格式化
function formatPromptForImageStudio(prompt) {
  // Image Studio 支持的格式：
  // 主体描述 + 风格 + 质量参数
  
  return prompt
    .replace(/\n\n/g, '\n')  // 减少空行
    .trim();
}
```

---

## 🔧 进阶实现：方案二（嵌入式）

### 步骤 1：修改 Image Studio，添加消息监听

在 `image-studio-standalone-v11(2).html` 的 `<script>` 部分添加：

```javascript
// 监听来自父窗口的消息
window.addEventListener('message', (event) => {
  // 验证来源（安全考虑）
  if (event.origin !== 'https://你的分镜工具域名.railway.app') {
    return;
  }
  
  const { type, data } = event.data;
  
  if (type === 'SET_PROMPT') {
    // 设置提示词
    document.getElementById('promptInput').value = data.prompt;
    
    // 如果有尺寸信息，也设置
    if (data.size) {
      document.getElementById('size').value = data.size;
    }
  }
});

// 生成完成后，发送消息给父窗口
function notifyParentImageGenerated(imageUrl) {
  window.parent.postMessage({
    type: 'IMAGE_GENERATED',
    data: { imageUrl }
  }, 'https://你的分镜工具域名.railway.app');
}
```

### 步骤 2：修改分镜工具，嵌入 iframe

在 `storyboard-workflow.html` 中添加：

```html
<!-- 添加一个模态窗口 -->
<div id="imageStudioModal" style="display:none; position:fixed; inset:0; z-index:9999; background:rgba(0,0,0,0.8);">
  <div style="width:95vw; height:95vh; margin:2.5vh auto; background:white; border-radius:12px; overflow:hidden;">
    <div style="display:flex; justify-content:space-between; padding:12px; background:#111827; color:white;">
      <h3>🎨 图像生成工具</h3>
      <button onclick="closeImageStudio()" style="background:none; border:none; color:white; font-size:24px; cursor:pointer;">×</button>
    </div>
    <iframe id="imageStudioFrame" 
            src="https://你的image-studio域名.railway.app" 
            style="width:100%; height:calc(100% - 50px); border:none;">
    </iframe>
  </div>
</div>

<script>
function openImageStudioEmbedded(prompt, size) {
  // 显示模态窗口
  document.getElementById('imageStudioModal').style.display = 'block';
  
  // 等待 iframe 加载完成
  const iframe = document.getElementById('imageStudioFrame');
  iframe.onload = () => {
    // 发送提示词到 iframe
    iframe.contentWindow.postMessage({
      type: 'SET_PROMPT',
      data: { prompt, size }
    }, 'https://你的image-studio域名.railway.app');
  };
}

function closeImageStudio() {
  document.getElementById('imageStudioModal').style.display = 'none';
}

// 监听来自 iframe 的消息
window.addEventListener('message', (event) => {
  if (event.origin !== 'https://你的image-studio域名.railway.app') {
    return;
  }
  
  const { type, data } = event.data;
  
  if (type === 'IMAGE_GENERATED') {
    console.log('图像生成完成:', data.imageUrl);
    // 可以在这里处理生成的图像
  }
});
</script>
```

### 步骤 3：在提示词组旁添加按钮

```html
<button onclick="openImageStudioEmbedded(imagePrompt, '1024x1792')" 
        class="btn-primary">
  🎨 生成图像
</button>
```

---

## 📊 完整工作流程

### 用户视角

1. **编写剧本** → 在分镜工具中输入剧本
2. **生成分镜** → 点击"生成分镜与提示词"
3. **查看提示词** → 查看生成的图像提示词
4. **生成图像** → 点击"生成图像"按钮
5. **调整参数** → 在 Image Studio 中调整尺寸、质量等
6. **批量生成** → 生成多张图片
7. **下载图片** → 保存到本地
8. **继续视频生成** → 使用生成的图片进行视频生成

### 技术流程

```
分镜工具（Railway）
    ↓ 生成提示词
Image Studio（Railway）
    ↓ 调用 OpenAI API
GPT Image-2 / DALL-E 3
    ↓ 返回图像
本地保存 / 继续处理
```

---

## 🎯 推荐配置

### Image Studio 推荐设置

**模型选择：**
- **GPT Image-2** - 最新，质量最好，支持 4K
- **DALL-E 3** - 稳定，兼容性好
- **Gemini Imagen 3** - 多比例支持

**尺寸选择：**
- **分镜故事板：** 1536x2048（3:4）或 2048x1536（4:3）
- **单个分镜：** 1024x1792（9:16 竖屏）或 1792x1024（16:9 横屏）
- **高质量输出：** 3840x2160（4K）

**质量参数：**
- `quality: high` - 最高质量（推荐）
- `quality: medium` - 平衡质量和速度
- `quality: low` - 快速生成

---

## 💰 成本估算

### OpenAI API 定价（2026年）

**GPT Image-2：**
- 1024x1024: $0.04/张
- 1024x1792: $0.08/张
- 2048x2048: $0.12/张
- 3840x2160 (4K): $0.20/张

**DALL-E 3：**
- 1024x1024: $0.04/张
- 1024x1792: $0.08/张

**示例：15 秒短片（5 个分镜）**
- 使用 1024x1792: 5 × $0.08 = $0.40
- 使用 2048x2048: 5 × $0.12 = $0.60
- 使用 4K: 5 × $0.20 = $1.00

---

## 🔐 安全建议

1. **API 密钥管理**
   - 不要在前端硬编码 API 密钥
   - 使用环境变量或后端代理
   - 定期轮换密钥

2. **访问控制**
   - 添加用户认证
   - 限制生成次数
   - 监控 API 使用量

3. **数据隐私**
   - 不要上传敏感内容
   - 定期清理生成的图片
   - 遵守 OpenAI 使用政策

---

## 📝 实施计划

### 第一周：快速部署（方案一）

**Day 1-2：部署 Image Studio**
- [ ] 创建 GitHub 仓库
- [ ] 部署到 Railway
- [ ] 测试基本功能

**Day 3-4：集成到分镜工具**
- [ ] 添加"生成图像"按钮
- [ ] 实现提示词复制功能
- [ ] 测试完整流程

**Day 5-7：优化和测试**
- [ ] 优化提示词格式
- [ ] 添加使用说明
- [ ] 用户测试和反馈

### 第二周：优化体验（方案二）

**Day 8-10：嵌入式集成**
- [ ] 修改 Image Studio 添加消息监听
- [ ] 在分镜工具中添加 iframe
- [ ] 实现自动传递提示词

**Day 11-12：功能增强**
- [ ] 添加批量生成功能
- [ ] 优化界面布局
- [ ] 添加进度显示

**Day 13-14：测试和发布**
- [ ] 完整流程测试
- [ ] 性能优化
- [ ] 文档更新

---

## 🎉 总结

**推荐实施路径：**

1. **立即行动（今天）**
   - 部署 Image Studio 到 Railway
   - 在分镜工具中添加链接按钮

2. **短期优化（1-2 周）**
   - 实现嵌入式集成
   - 优化工作流程

3. **长期规划（1-2 月）**
   - 考虑 API 集成
   - 添加批量生成
   - 完善自动化流程

**预期效果：**
- ✅ 从剧本到图像的完整流程
- ✅ 专业级分镜故事板生成
- ✅ 高质量 AI 图像生成
- ✅ 流畅的用户体验

---

**准备好开始了吗？我可以帮你实施任何一个方案！** 🚀
