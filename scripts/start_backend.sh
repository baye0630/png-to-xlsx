#!/bin/bash
# 后端服务启动脚本

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "错误：虚拟环境不存在，请先运行：python3.11 -m venv venv"
    exit 1
fi

# 检查依赖
if [ ! -f "venv/bin/uvicorn" ]; then
    echo "错误：依赖未安装，请先运行：./venv/bin/pip install -r backend/requirements.txt"
    exit 1
fi

# 设置 PYTHONPATH
export PYTHONPATH="$PROJECT_ROOT/backend:$PYTHONPATH"

# 启动服务
echo "正在启动后端服务..."
cd backend
../venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo "服务已启动在 http://0.0.0.0:8000"
echo "API 文档: http://0.0.0.0:8000/docs"
echo "Health 检查: http://0.0.0.0:8000/health"
