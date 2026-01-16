#!/bin/bash
# OCR PNG to Excel - 启动脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PROJECT_DIR="/home/lenovo/development_project/ocrpngtoexcel_test"

echo -e "${GREEN}=== OCR PNG to Excel 启动脚本 ===${NC}"
echo ""

# 检查是否在项目目录
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}错误: 项目目录不存在${NC}"
    exit 1
fi

cd "$PROJECT_DIR"

# 1. 启动后端服务
echo -e "${YELLOW}[1/2] 启动后端服务...${NC}"
if lsof -i :8000 > /dev/null 2>&1; then
    echo -e "${YELLOW}警告: 端口 8000 已被占用，跳过启动${NC}"
else
    source venv/bin/activate
    cd backend
    nohup python -m app.main > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    echo -e "${GREEN}✓ 后端服务已启动 (PID: $BACKEND_PID)${NC}"
    
    # 等待后端启动
    echo -n "等待后端服务启动"
    for i in {1..10}; do
        sleep 1
        echo -n "."
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo -e " ${GREEN}完成${NC}"
            break
        fi
    done
fi

# 2. 启动前端服务
echo -e "${YELLOW}[2/2] 启动前端服务...${NC}"
if lsof -i :3000 > /dev/null 2>&1; then
    echo -e "${YELLOW}警告: 端口 3000 已被占用，跳过启动${NC}"
else
    cd frontend
    nohup npm start > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    echo -e "${GREEN}✓ 前端服务已启动 (PID: $FRONTEND_PID)${NC}"
fi

echo ""
echo -e "${GREEN}=== 启动完成 ===${NC}"
echo ""
echo "访问地址:"
echo "  前端: http://localhost:3000"
echo "  后端: http://localhost:8000"
echo ""
echo "查看日志:"
echo "  后端: tail -f logs/backend.log"
echo "  前端: tail -f logs/frontend.log"
echo ""
echo "停止服务: ./scripts/stop.sh"
echo ""
