#!/bin/bash
# OCR PNG to Excel - 状态检查脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== OCR PNG to Excel 系统状态 ===${NC}"
echo ""

# 1. 检查后端服务
echo -e "${YELLOW}[1/3] 后端服务 (端口 8000)${NC}"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "  状态: ${GREEN}✓ 运行中${NC}"
    HEALTH=$(curl -s http://localhost:8000/health)
    echo "  健康检查: $HEALTH" | python3 -m json.tool 2>/dev/null || echo "  $HEALTH"
    
    # 显示进程信息
    BACKEND_PID=$(ps aux | grep "python -m app.main" | grep -v grep | awk '{print $2}')
    if [ ! -z "$BACKEND_PID" ]; then
        echo -e "  进程 PID: ${BLUE}$BACKEND_PID${NC}"
        echo -n "  CPU/内存: "
        ps aux | grep $BACKEND_PID | grep -v grep | awk '{print $3"% / "$4"%"}'
    fi
else
    echo -e "  状态: ${RED}✗ 未运行${NC}"
fi
echo ""

# 2. 检查前端服务
echo -e "${YELLOW}[2/3] 前端服务 (端口 3000)${NC}"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null)
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "  状态: ${GREEN}✓ 运行中${NC}"
    echo -e "  访问地址: ${BLUE}http://localhost:3000${NC}"
    
    # 显示进程信息
    FRONTEND_PID=$(ps aux | grep "node.*react-scripts" | grep -v grep | awk '{print $2}' | head -1)
    if [ ! -z "$FRONTEND_PID" ]; then
        echo -e "  进程 PID: ${BLUE}$FRONTEND_PID${NC}"
        echo -n "  CPU/内存: "
        ps aux | grep $FRONTEND_PID | grep -v grep | head -1 | awk '{print $3"% / "$4"%"}'
    fi
else
    echo -e "  状态: ${RED}✗ 未运行${NC}"
fi
echo ""

# 3. 检查 OCR 服务
echo -e "${YELLOW}[3/3] OCR 服务 (端口 8088)${NC}"
if curl -s http://localhost:8088/health > /dev/null 2>&1; then
    echo -e "  状态: ${GREEN}✓ 运行中${NC}"
else
    echo -e "  状态: ${RED}✗ 未运行或无法访问${NC}"
fi
echo ""

# 4. 磁盘空间
echo -e "${YELLOW}磁盘空间使用情况:${NC}"
df -h / | tail -1 | awk '{print "  总空间: "$2"  已用: "$3"  可用: "$4"  使用率: "$5}'
echo ""

# 5. 数据目录大小
echo -e "${YELLOW}数据目录大小:${NC}"
if [ -d "data" ]; then
    du -sh data/* 2>/dev/null | while read size dir; do
        echo "  $(basename $dir): $size"
    done
else
    echo -e "  ${RED}数据目录不存在${NC}"
fi
echo ""

# 6. 最近错误
echo -e "${YELLOW}最近错误 (logs/error.log):${NC}"
if [ -f "logs/error.log" ]; then
    ERROR_COUNT=$(grep -c "ERROR" logs/error.log 2>/dev/null || echo "0")
    echo "  错误总数: $ERROR_COUNT"
    echo "  最近 3 条:"
    tail -3 logs/error.log 2>/dev/null | sed 's/^/    /' || echo "    无"
else
    echo "  日志文件不存在"
fi
echo ""

echo -e "${BLUE}=== 状态检查完成 ===${NC}"
echo ""
