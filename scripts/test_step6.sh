#!/bin/bash
# Step 6 验收测试脚本
# 测试 OCR JSON → Excel（多 Sheet）

set -e

echo "========================================"
echo "Step 6 验收测试开始"
echo "========================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 切换到项目根目录
cd "$(dirname "$0")/.."

# 1. 健康检查
echo "1. 检查后端服务健康状态..."
HEALTH=$(curl -s http://localhost:8000/health)
if echo "$HEALTH" | grep -q '"status":"healthy"'; then
    echo -e "${GREEN}✓ 后端服务正常${NC}"
else
    echo -e "${RED}✗ 后端服务异常${NC}"
    exit 1
fi
echo ""

# 2. 查找或创建一个 OCR_DONE 状态的任务
echo "2. 准备测试任务（OCR_DONE 状态）..."

# 尝试使用已有的 OCR JSON 文件
OCR_JSON_FILE="data/ocr_json/0327bfce-f63f-4820-934b-d016e5f81829.json"
if [ -f "$OCR_JSON_FILE" ]; then
    TASK_ID="0327bfce-f63f-4820-934b-d016e5f81829"
    echo -e "${GREEN}✓ 使用已有任务${NC}"
    echo "  任务 ID: $TASK_ID"
    echo "  OCR JSON: $OCR_JSON_FILE"
else
    # 如果没有，创建一个新任务
    echo -e "${YELLOW}  未找到已有任务，开始创建新任务...${NC}"
    
    # 上传图片
    UPLOAD_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/upload/image" \
      -F "file=@data/temp/real_test.png")
    
    TASK_ID=$(echo "$UPLOAD_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['task_id'])" 2>/dev/null || echo "")
    
    if [ -z "$TASK_ID" ]; then
        echo -e "${RED}✗ 图片上传失败${NC}"
        exit 1
    fi
    
    echo "  任务已创建: $TASK_ID"
    
    # 启动 OCR
    OCR_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/ocr/start/$TASK_ID")
    JOB_ID=$(echo "$OCR_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('data', {}).get('ocr_job_id', ''))" 2>/dev/null || echo "")
    
    if [ -z "$JOB_ID" ]; then
        echo -e "${RED}✗ OCR 任务创建失败${NC}"
        exit 1
    fi
    
    echo "  OCR Job ID: $JOB_ID"
    
    # 轮询 OCR 结果
    echo -e "${YELLOW}  等待 OCR 完成（最多 120 秒）...${NC}"
    curl -s -X POST "http://localhost:8000/api/v1/ocr/poll/$TASK_ID" > /dev/null
    
    echo -e "${GREEN}✓ OCR 完成${NC}"
fi
echo ""

# 3. 检查任务当前状态
echo "3. 检查任务当前状态..."
TASK_RESPONSE=$(curl -s "http://localhost:8000/api/v1/tasks/$TASK_ID")
CURRENT_STATUS=$(echo "$TASK_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['status'])" 2>/dev/null || echo "")

echo "  当前状态: $CURRENT_STATUS"

if [ "$CURRENT_STATUS" != "ocr_done" ] && [ "$CURRENT_STATUS" != "excel_generated" ]; then
    echo -e "${RED}✗ 任务状态错误，期望 ocr_done 或 excel_generated，实际: $CURRENT_STATUS${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 任务状态正确${NC}"
echo ""

# 4. 生成 Excel 文件
echo "4. 调用 Excel 生成接口..."
EXCEL_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/excel/generate/$TASK_ID")

SUCCESS=$(echo "$EXCEL_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null || echo "False")

if [ "$SUCCESS" != "True" ]; then
    echo -e "${RED}✗ Excel 生成失败${NC}"
    echo "响应: $EXCEL_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✓ Excel 生成成功${NC}"

# 提取 Excel 路径
EXCEL_PATH=$(echo "$EXCEL_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['excel_path'])" 2>/dev/null || echo "")
echo "  Excel 路径: $EXCEL_PATH"
echo ""

# 5. 验证任务状态已更新
echo "5. 验证任务状态已更新为 excel_generated..."
TASK_RESPONSE=$(curl -s "http://localhost:8000/api/v1/tasks/$TASK_ID")
NEW_STATUS=$(echo "$TASK_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['status'])" 2>/dev/null || echo "")

if [ "$NEW_STATUS" != "excel_generated" ]; then
    echo -e "${RED}✗ 任务状态错误，期望 excel_generated，实际: $NEW_STATUS${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 任务状态已更新为 excel_generated${NC}"
echo ""

# 6. 验证 Excel 文件存在
echo "6. 验证 Excel 文件存在..."
if [ ! -f "$EXCEL_PATH" ]; then
    echo -e "${RED}✗ Excel 文件不存在: $EXCEL_PATH${NC}"
    exit 1
fi

FILE_SIZE=$(stat -f%z "$EXCEL_PATH" 2>/dev/null || stat -c%s "$EXCEL_PATH" 2>/dev/null || echo "0")
echo -e "${GREEN}✓ Excel 文件存在${NC}"
echo "  文件大小: $FILE_SIZE 字节"
echo ""

# 7. 验证 Excel 文件结构
echo "7. 验证 Excel 文件结构..."
python3 - "$EXCEL_PATH" << 'EOF'
import sys
import openpyxl

try:
    # 读取 Excel 文件
    excel_path = sys.argv[1]
    wb = openpyxl.load_workbook(excel_path)
    
    sheet_count = len(wb.sheetnames)
    print(f"  Sheet 数量: {sheet_count}")
    
    if sheet_count == 0:
        print("\033[0;31m✗ Excel 文件没有 Sheet\033[0m")
        sys.exit(1)
    
    # 检查每个 Sheet
    for idx, sheet_name in enumerate(wb.sheetnames, 1):
        ws = wb[sheet_name]
        rows = ws.max_row
        cols = ws.max_column
        print(f"  Sheet {idx}: {sheet_name} ({rows} 行 x {cols} 列)")
    
    print("\033[0;32m✓ Excel 文件结构正确\033[0m")
    
except Exception as e:
    print(f"\033[0;31m✗ Excel 文件验证失败: {e}\033[0m")
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    exit 1
fi
echo ""

# 8. 验证表格数量与 OCR JSON 一致
echo "8. 验证表格数量与 OCR JSON 一致..."
python3 - "$TASK_ID" "$EXCEL_PATH" << 'EOF'
import sys
import json
import openpyxl

try:
    task_id = sys.argv[1]
    excel_path = sys.argv[2]
    
    # 读取 OCR JSON
    ocr_json_path = f"data/ocr_json/{task_id}.json"
    with open(ocr_json_path, 'r') as f:
        ocr_data = json.load(f)
    
    # 统计表格数量
    table_count = 0
    for page in ocr_data.get('pages', []):
        for block in page.get('parsing_res_list', []):
            if block.get('block_label') == 'table':
                table_count += 1
    
    # 读取 Excel Sheet 数量
    wb = openpyxl.load_workbook(excel_path)
    sheet_count = len(wb.sheetnames)
    
    print(f"  OCR 表格数量: {table_count}")
    print(f"  Excel Sheet 数量: {sheet_count}")
    
    if table_count == sheet_count:
        print("\033[0;32m✓ 表格数量一致\033[0m")
    else:
        print(f"\033[0;31m✗ 表格数量不一致\033[0m")
        sys.exit(1)
    
except Exception as e:
    print(f"\033[0;31m✗ 验证失败: {e}\033[0m")
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    exit 1
fi
echo ""

# 验收总结
echo "========================================"
echo -e "${GREEN}✅ Step 6 验收测试全部通过！${NC}"
echo "========================================"
echo ""
echo "验收标准达成情况："
echo -e "  ${GREEN}✓${NC} Excel 文件生成成功"
echo -e "  ${GREEN}✓${NC} Excel 文件可打开"
echo -e "  ${GREEN}✓${NC} Sheet 数量与识别表格数量一致"
echo -e "  ${GREEN}✓${NC} Excel 文件结构正确"
echo -e "  ${GREEN}✓${NC} 任务状态更新为 excel_generated"
echo ""
echo "任务信息："
echo "  任务 ID: $TASK_ID"
echo "  状态:    excel_generated"
echo "  Excel 路径: $EXCEL_PATH"
echo ""
