#!/bin/bash
# Step 5 验收测试脚本
# 测试任务状态获取 + 拉取 OCR JSON 落盘

set -e

echo "========================================"
echo "Step 5 验收测试开始"
echo "========================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 健康检查
echo "1. 检查 OCR 服务健康状态..."
HEALTH=$(curl -s http://localhost:8000/api/v1/ocr/health)
if echo "$HEALTH" | grep -q '"healthy":true'; then
    echo -e "${GREEN}✓ OCR 服务正常${NC}"
else
    echo -e "${RED}✗ OCR 服务异常${NC}"
    exit 1
fi
echo ""

# 2. 上传图片
echo "2. 上传测试图片..."
UPLOAD_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/upload/image" \
  -F "file=@data/temp/real_test.png")

TASK_ID=$(echo "$UPLOAD_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['task_id'])" 2>/dev/null || echo "")

if [ -z "$TASK_ID" ]; then
    echo -e "${RED}✗ 图片上传失败${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 图片上传成功${NC}"
echo "  任务 ID: $TASK_ID"
echo ""

# 3. 启动 OCR 任务
echo "3. 启动 OCR 任务..."
OCR_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/ocr/start/$TASK_ID")

JOB_ID=$(echo "$OCR_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('data', {}).get('ocr_job_id', ''))" 2>/dev/null || echo "")

if [ -z "$JOB_ID" ]; then
    echo -e "${RED}✗ OCR 任务创建失败${NC}"
    echo "响应: $OCR_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✓ OCR 任务创建成功${NC}"
echo "  Job ID: $JOB_ID"
echo ""

# 4. 轮询任务状态并获取结果
echo "4. 轮询任务状态并获取 OCR JSON 结果..."
echo -e "${YELLOW}  (此步骤可能需要 30-120 秒，请耐心等待...)${NC}"
echo ""

POLL_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/ocr/poll/$TASK_ID")

SUCCESS=$(echo "$POLL_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null || echo "False")

if [ "$SUCCESS" != "True" ]; then
    echo -e "${RED}✗ OCR 轮询失败${NC}"
    echo "响应: $POLL_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✓ OCR 任务完成并获取结果${NC}"
echo ""

# 5. 验证任务状态
echo "5. 验证任务状态..."
TASK_STATUS=$(curl -s "http://localhost:8000/api/v1/tasks/$TASK_ID")

STATUS=$(echo "$TASK_STATUS" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['status'])" 2>/dev/null || echo "")
OCR_JSON_PATH=$(echo "$TASK_STATUS" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['ocr_json_path'])" 2>/dev/null || echo "")

if [ "$STATUS" != "ocr_done" ]; then
    echo -e "${RED}✗ 任务状态错误: $STATUS (期望: ocr_done)${NC}"
    exit 1
fi

if [ -z "$OCR_JSON_PATH" ] || [ "$OCR_JSON_PATH" = "None" ] || [ "$OCR_JSON_PATH" = "null" ]; then
    echo -e "${RED}✗ OCR JSON 路径未设置${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 任务状态正确${NC}"
echo "  状态: $STATUS"
echo "  OCR JSON 路径: $OCR_JSON_PATH"
echo ""

# 6. 验证 JSON 文件存在
echo "6. 验证 OCR JSON 文件..."
if [ ! -f "$OCR_JSON_PATH" ]; then
    echo -e "${RED}✗ OCR JSON 文件不存在: $OCR_JSON_PATH${NC}"
    exit 1
fi

FILE_SIZE=$(wc -c < "$OCR_JSON_PATH")
if [ "$FILE_SIZE" -lt 10 ]; then
    echo -e "${RED}✗ OCR JSON 文件太小 (${FILE_SIZE} 字节)${NC}"
    exit 1
fi

echo -e "${GREEN}✓ OCR JSON 文件存在${NC}"
echo "  文件大小: $FILE_SIZE 字节"
echo ""

# 7. 验证 JSON 格式
echo "7. 验证 JSON 格式..."
if python3 -c "import json; json.load(open('$OCR_JSON_PATH'))" 2>/dev/null; then
    echo -e "${GREEN}✓ JSON 格式正确${NC}"
else
    echo -e "${RED}✗ JSON 格式错误${NC}"
    exit 1
fi
echo ""

echo "========================================"
echo -e "${GREEN}✅ Step 5 验收测试全部通过！${NC}"
echo "========================================"
echo ""
echo "验收标准达成情况："
echo "  ✓ OCR 任务状态轮询成功"
echo "  ✓ OCR JSON 结果获取成功"
echo "  ✓ OCR JSON 文件保存成功: $OCR_JSON_PATH"
echo "  ✓ 任务状态更新为 ocr_done"
echo "  ✓ JSON 格式验证通过"
echo ""
echo "任务信息："
echo "  任务 ID: $TASK_ID"
echo "  Job ID:  $JOB_ID"
echo "  状态:    $STATUS"
echo "  JSON 路径: $OCR_JSON_PATH"
echo ""
