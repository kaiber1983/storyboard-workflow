# GPT-Image-2 出图环境

通过中转站 `http://hxzdq.aiflow321.cn/v1` 调用 `gpt-image-2` 模型生成图片。

## 安装

```powershell
pip install -r requirements.txt
```

## 配置

配置已写入 `.env`（该文件已被 `.gitignore` 排除，请勿提交）：

```
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=http://hxzdq.aiflow321.cn/v1
IMAGE_MODEL=gpt-image-2
```

## 使用

**连通性测试**（先跑这个确认通路 OK）：

```powershell
python test_api.py
```

**生成图片**：

```powershell
python generate.py "一只赛博朋克风格的橘猫，霓虹灯背景"
python generate.py "未来城市夜景" --size 1024x1024 --n 2 --out ./output
```

图片保存到 `./output/`，文件名格式：`时间戳_提示词slug_序号.png`。

## 注意

- 中转站可能返回 `url` 或 `b64_json`，脚本已双路兼容。
- 若 `test_api.py` 报 404/401，先确认 base_url 是否需要带 `/v1` 后缀（当前已带）。
- `gpt-image-2` 支持的 size 参考官方/中转站文档，常用 `1024x1024` / `1024x1536` / `1536x1024`。
- API Key 明文存储于 `.env`，如需更强安全性可改为系统环境变量。
