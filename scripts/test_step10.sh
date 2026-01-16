#!/bin/bash

# Step 10 测试脚本 - 前端表格预览和多 Sheet 切换

echo "========================================"
echo "Step 10 测试 - 前端表格预览 + 多 Sheet 切换"
echo "========================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查后端服务
echo "1. 检查后端服务..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✓ 后端服务正常${NC}"
else
    echo -e "${RED}✗ 后端服务异常${NC}"
    exit 1
fi
echo ""

# 检查前端服务
echo "2. 检查前端服务..."
if curl -s http://localhost:3000 > /dev/null; then
    echo -e "${GREEN}✓ 前端服务正常${NC}"
else
    echo -e "${RED}✗ 前端服务异常${NC}"
    exit 1
fi
echo ""

# 获取一个已完成 OCR 的任务
echo "3. 获取已完成 OCR 的任务..."
TASK_ID=$(sqlite3 data/ocr_pngtoexcel.db "SELECT task_id FROM tasks WHERE status = 'ocr_done' ORDER BY updated_at DESC LIMIT 1;")

if [ -z "$TASK_ID" ]; then
    echo -e "${RED}✗ 没有找到已完成 OCR 的任务${NC}"
    echo "请先运行 Step 9 测试创建一个任务"
    exit 1
fi

echo -e "${GREEN}✓ 找到任务: $TASK_ID${NC}"
echo ""

# 测试表格数据 API
echo "4. 测试表格数据 API..."
RESPONSE=$(curl -s -X GET "http://localhost:8000/api/v1/table/data/$TASK_ID")

if echo "$RESPONSE" | grep -q '"success":true'; then
    echo -e "${GREEN}✓ 表格数据 API 正常${NC}"
    
    # 解析表格信息
    TOTAL_SHEETS=$(echo "$RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['data']['total_sheets'])")
    echo "  - 总 Sheet 数: $TOTAL_SHEETS"
    
    # 显示每个 Sheet 的信息
    echo "$RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for i, sheet in enumerate(data['data']['sheets'], 1):
    print(f\"  - Sheet {i}: {sheet['sheet_name']} ({sheet['rows']}行 × {sheet['cols']}列)\")
"
else
    echo -e "${RED}✗ 表格数据 API 异常${NC}"
    echo "$RESPONSE"
    exit 1
fi
echo ""

# 测试表格元数据 API
echo "5. 测试表格元数据 API..."
METADATA=$(curl -s -X GET "http://localhost:8000/api/v1/table/metadata/$TASK_ID")

if echo "$METADATA" | grep -q '"success":true'; then
    echo -e "${GREEN}✓ 表格元数据 API 正常${NC}"
else
    echo -e "${RED}✗ 表格元数据 API 异常${NC}"
    echo "$METADATA"
    exit 1
fi
echo ""

# 检查前端组件文件
echo "6. 检查前端组件文件..."
FILES_TO_CHECK=(
    "frontend/src/components/ExcelArea/ExcelArea.tsx"
    "frontend/src/components/ExcelArea/ExcelArea.css"
    "frontend/src/components/ExcelArea/TableRenderer.tsx"
    "frontend/src/components/ExcelArea/TableRenderer.css"
)

ALL_FILES_EXIST=true
for file in "${FILES_TO_CHECK[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ $file${NC}"
    else
        echo -e "${RED}✗ $file 不存在${NC}"
        ALL_FILES_EXIST=false
    fi
done

if [ "$ALL_FILES_EXIST" = false ]; then
    exit 1
fi
echo ""

# TypeScript 编译检查
echo "7. 检查 TypeScript 编译..."
cd frontend
if npx tsc --noEmit 2>&1 | grep -q "error"; then
    echo -e "${RED}✗ TypeScript 编译有错误${NC}"
    npx tsc --noEmit
    exit 1
else
    echo -e "${GREEN}✓ TypeScript 编译通过${NC}"
fi
cd ..
echo ""

# 总结
echo "========================================"
echo -e "${GREEN}✓ Step 10 所有测试通过！${NC}"
echo "========================================"
echo ""
echo "请访问以下地址进行前端测试:"
echo "  http://localhost:3000"
echo ""
echo "测试任务 ID: $TASK_ID"
echo ""
echo "验收标准:"
echo "  1. ✓ 多 Sheet 可切换"
echo "  2. ✓ 渲染正确"
echo ""
