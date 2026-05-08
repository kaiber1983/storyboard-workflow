# Image Studio - Railway 部署说明

## 快速部署

### 方法 1：直接部署静态文件

1. **重命名文件**
   ```bash
   # 将 image-studio.html 重命名为 index.html
   mv image-studio.html index.html
   ```

2. **创建 GitHub 仓库**
   ```bash
   git init
   git add index.html
   git commit -m "Initial commit: Image Studio"
   git remote add origin https://github.com/你的用户名/image-studio.git
   git push -u origin main
   ```

3. **在 Railway 部署**
   - 访问 railway.app
   - 创建新项目
   - 选择 GitHub 仓库
   - Railway 会自动识别为静态网站
   - 生成域名

### 方法 2：使用 Nginx 服务器

如果 Railway 无法直接识别静态文件，创建以下配置：

**创建 `Dockerfile`：**
```dockerfile
FROM nginx:alpine
COPY index.html /usr/share/nginx/html/
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**创建 `railway.json`：**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "startCommand": "nginx -g 'daemon off;'",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

然后推送到 GitHub 并在 Railway 部署。

---

## 部署后的域名

部署完成后，你会得到类似这样的域名：
```
https://image-studio-production.up.railway.app
```

保存这个域名，我们将在分镜工具中使用它。
