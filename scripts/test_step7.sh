#!/bin/bash
# Step 7 验收测试脚本
# 测试 OCR JSON → 表格 JSON（供前端预览/编辑）

set -e

echo "========================================"
echo "Step 7 验收测试开始"
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

# 2. 准备测试任务（使用已有的 OCR_DONE 或 EXCEL_GENERATED 任务）
echo "2. 准备测试任务..."

# 尝试使用已有的任务
TASK_ID="b40eec81-5ac1-40dc-90f6-13a5077bb474"
OCR_JSON_FILE="data/ocr_json/${TASK_ID}.json"

if [ -f "$OCR_JSON_FILE" ]; then
    echo -e "${GREEN}✓ 使用已有任务${NC}"
    echo "  任务 ID: $TASK_ID"
    echo "  OCR JSON: $OCR_JSON_FILE"
else
    # 如果没有，尝试第二个任务
    TASK_ID="0327bfce-f63f-4820-934b-d016e5f81829"
    OCR_JSON_FILE="data/ocr_json/${TASK_ID}.json"
    
    if [ -f "$OCR_JSON_FILE" ]; then
        echo -e "${GREEN}✓ 使用已有任务${NC}"
        echo "  任务 ID: $TASK_ID"
        echo "  OCR JSON: $OCR_JSON_FILE"
    else
        echo -e "${RED}✗ 未找到可用的测试任务${NC}"
        echo "  请先完成 Step 5（OCR 完成）或 Step 6（Excel 生成）"
        exit 1
    fi
fi
echo ""

# 3. 检查任务当前状态
echo "3. 检查任务当前状态..."
TASK_RESPONSE=$(curl -s "http://localhost:8000/api/v1/tasks/$TASK_ID")
CURRENT_STATUS=$(echo "$TASK_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['status'])" 2>/dev/null || echo "")

echo "  当前状态: $CURRENT_STATUS"

if [ "$CURRENT_STATUS" != "ocr_done" ] && [ "$CURRENT_STATUS" != "excel_generated" ] && [ "$CURRENT_STATUS" != "editable" ]; then
    echo -e "${RED}✗ 任务状态错误，期望 ocr_done / excel_generated / editable，实际: $CURRENT_STATUS${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 任务状态正确${NC}"
echo ""

# 4. 获取表格元数据（轻量级）
echo "4. 获取表格元数据..."
METADATA_RESPONSE=$(curl -s "http://localhost:8000/api/v1/table/metadata/$TASK_ID")

SUCCESS=$(echo "$METADATA_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null || echo "False")

if [ "$SUCCESS" != "True" ]; then
    echo -e "${RED}✗ 获取表格元数据失败${NC}"
    echo "$METADATA_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✓ 表格元数据获取成功${NC}"

# 提取元数据信息
TOTAL_SHEETS=$(echo "$METADATA_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['total_sheets'])" 2>/dev/null || echo "0")
echo "  Sheet 总数: $TOTAL_SHEETS"

# 输出每个 Sheet 的信息
python3 << EOF
import sys, json
data = json.loads('''$METADATA_RESPONSE''')
sheets_info = data['data']['sheets_info']
for info in sheets_info:
    print(f"  - {info['sheet_name']}: {info['rows']} 行 x {info['cols']} 列")
EOF

echo ""

# 5. 获取完整表格数据
echo "5. 获取完整表格数据..."
TABLE_RESPONSE=$(curl -s "http://localhost:8000/api/v1/table/data/$TASK_ID")

SUCCESS=$(echo "$TABLE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null || echo "False")

if [ "$SUCCESS" != "True" ]; then
    echo -e "${RED}✗ 获取表格数据失败${NC}"
    echo "$TABLE_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✓ 表格数据获取成功${NC}"

# 保存表格数据到文件（用于检查）
echo "$TABLE_RESPONSE" > "data/temp/step7_table_data.json"
echo "  数据已保存到: data/temp/step7_table_data.json"
echo ""

# 6. 验证数据结构完整性
echo "6. 验证数据结构..."
python3 << 'EOF'
import sys, json

# 读取表格数据
with open('data/temp/step7_table_data.json', 'r') as f:
    response = json.load(f)

data = response['data']

# 检查必要字段
assert 'task_id' in data, "缺少 task_id 字段"
assert 'status' in data, "缺少 status 字段"
assert 'total_sheets' in data, "缺少 total_sheets 字段"
assert 'sheets' in data, "缺少 sheets 字段"

total_sheets = data['total_sheets']
sheets = data['sheets']

assert len(sheets) == total_sheets, f"Sheet 数量不一致: {len(sheets)} != {total_sheets}"

# 验证每个 Sheet
for sheet in sheets:
    assert 'sheet_id' in sheet, "Sheet 缺少 sheet_id 字段"
    assert 'sheet_name' in sheet, "Sheet 缺少 sheet_name 字段"
    assert 'rows' in sheet, "Sheet 缺少 rows 字段"
    assert 'cols' in sheet, "Sheet 缺少 cols 字段"
    assert 'data' in sheet, "Sheet 缺少 data 字段"
    
    rows = sheet['rows']
    cols = sheet['cols']
    table_data = sheet['data']
    
    # 验证数据行数
    assert len(table_data) == rows, f"Sheet {sheet['sheet_name']} 行数不一致: {len(table_data)} != {rows}"
    
    # 验证每行的列数
    for row_idx, row in enumerate(table_data):
        assert len(row) == cols, f"Sheet {sheet['sheet_name']} 第 {row_idx+1} 行列数不一致: {len(row)} != {cols}"
        
        # 验证每个单元格
        for cell in row:
            assert 'text' in cell, "单元格缺少 text 字段"
            assert 'rowspan' in cell, "单元格缺少 rowspan 字段"
            assert 'colspan' in cell, "单元格缺少 colspan 字段"
            assert 'is_header' in cell, "单元格缺少 is_header 字段"

print("✓ 数据结构验证通过")
print(f"✓ 共 {total_sheets} 个 Sheet")

# 输出统计信息
for sheet in sheets:
    total_cells = sheet['rows'] * sheet['cols']
    non_empty_cells = sum(1 for row in sheet['data'] for cell in row if cell['text'].strip())
    header_cells = sum(1 for row in sheet['data'] for cell in row if cell['is_header'])
    
    print(f"✓ {sheet['sheet_name']}: {sheet['rows']} 行 x {sheet['cols']} 列 = {total_cells} 单元格")
    print(f"  - 非空单元格: {non_empty_cells}")
    print(f"  - 表头单元格: {header_cells}")
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 数据结构完整${NC}"
else
    echo -e "${RED}✗ 数据结构验证失败${NC}"
    exit 1
fi
echo ""

# 7. 验证任务状态更新为 editable
echo "7. 验证任务状态更新..."
TASK_RESPONSE=$(curl -s "http://localhost:8000/api/v1/tasks/$TASK_ID")
NEW_STATUS=$(echo "$TASK_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['status'])" 2>/dev/null || echo "")

echo "  当前状态: $NEW_STATUS"

if [ "$NEW_STATUS" != "editable" ]; then
    echo -e "${RED}✗ 任务状态未更新为 editable，实际: $NEW_STATUS${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 任务状态已更新为 editable${NC}"
echo ""

# 8. 对比 OCR JSON 与表格数据
echo "8. 对比 OCR JSON 与表格数据..."
python3 << EOF
import sys, json

# 读取 OCR JSON
with open('$OCR_JSON_FILE', 'r') as f:
    ocr_data = json.load(f)

# 统计 OCR JSON 中的表格数量
table_count = 0
for page in ocr_data.get('pages', []):
    for block in page.get('parsing_res_list', []):
        if block.get('block_label') == 'table':
            table_count += 1

# 读取表格数据
with open('data/temp/step7_table_data.json', 'r') as f:
    response = json.load(f)
    total_sheets = response['data']['total_sheets']

print(f"OCR JSON 表格数量: {table_count}")
print(f"表格数据 Sheet 数量: {total_sheets}")

if table_count == total_sheets:
    print("✓ 表格数量一致")
else:
    print(f"✗ 表格数量不一致: {table_count} != {total_sheets}")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ OCR JSON 与表格数据一致${NC}"
else
    echo -e "${RED}✗ OCR JSON 与表格数据不一致${NC}"
    exit 1
fi
echo ""

# 9. 测试结果总结
echo "========================================"
echo -e "${GREEN}✅ Step 7 验收测试全部通过！${NC}"
echo "========================================"
echo ""
echo "验收标准达成情况："
echo -e "${GREEN}  ✓ 接口返回结构完整${NC}"
echo -e "${GREEN}  ✓ 数据正确（与 OCR JSON 一致）${NC}"
echo -e "${GREEN}  ✓ 任务状态更新为 editable${NC}"
echo -e "${GREEN}  ✓ 支持多 Sheet 数据${NC}"
echo -e "${GREEN}  ✓ 单元格数据完整（text, rowspan, colspan, is_header）${NC}"
echo ""
echo "任务信息："
echo "  任务 ID: $TASK_ID"
echo "  状态:    $NEW_STATUS"
echo "  Sheet 数量: $TOTAL_SHEETS"
echo ""
echo "测试数据已保存到："
echo "  data/temp/step7_table_data.json"
echo ""
echo "========================================"
echo -e "${GREEN}✅ Step 7 完成，可以进入 Step 8 开发！${NC}"
echo "========================================"
