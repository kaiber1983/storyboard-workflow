FROM python:3.11-slim

WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY storyboard_agent_server.py .
COPY storyboard-workflow.html .
COPY AGENTS.md .

# 暴露端口
EXPOSE 8787

# 设置环境变量
ENV HOST=0.0.0.0
ENV PORT=8787

# 启动服务
CMD ["python", "storyboard_agent_server.py"]
