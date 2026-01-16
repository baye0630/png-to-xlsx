#!/bin/bash
# OCR PNG to Excel - 停止脚本

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== OCR PNG to Excel 停止脚本 ===${NC}"
echo ""

# 停止后端服务
echo -e "${YELLOW}停止后端服务...${NC}"
BACKEND_PIDS=$(ps aux | grep "python -m app.main" | grep -v grep | awk '{print $2}')
if [ -z "$BACKEND_PIDS" ]; then
    echo -e "${YELLOW}后端服务未运行${NC}"
else
    for PID in $BACKEND_PIDS; do
        kill -9 $PID 2>/dev/null
        echo -e "${GREEN}✓ 已停止后端服务 (PID: $PID)${NC}"
    done
fi

# 停止前端服务
echo -e "${YELLOW}停止前端服务...${NC}"
FRONTEND_PIDS=$(ps aux | grep "node.*react-scripts" | grep -v grep | awk '{print $2}')
if [ -z "$FRONTEND_PIDS" ]; then
    echo -e "${YELLOW}前端服务未运行${NC}"
else
    for PID in $FRONTEND_PIDS; do
        kill -9 $PID 2>/dev/null
        echo -e "${GREEN}✓ 已停止前端服务 (PID: $PID)${NC}"
    done
fi

echo ""
echo -e "${GREEN}=== 停止完成 ===${NC}"
echo ""
