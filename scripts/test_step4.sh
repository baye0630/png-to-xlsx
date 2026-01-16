#!/bin/bash
# Step 4 验收测试脚本
# 测试 OCR 接入（创建 job_id）

set -e

echo "========================================"
echo "Step 4 验收测试开始"
echo "========================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
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

# 4. 验证任务状态
echo "4. 验证任务状态..."
TASK_STATUS=$(curl -s "http://localhost:8000/api/v1/tasks/$TASK_ID")

STATUS=$(echo "$TASK_STATUS" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['status'])" 2>/dev/null || echo "")
DB_JOB_ID=$(echo "$TASK_STATUS" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['ocr_job_id'])" 2>/dev/null || echo "")

if [ "$STATUS" != "ocr_processing" ]; then
    echo -e "${RED}✗ 任务状态错误: $STATUS${NC}"
    exit 1
fi

if [ "$DB_JOB_ID" != "$JOB_ID" ]; then
    echo -e "${RED}✗ job_id 未正确写入数据库${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 任务状态正确${NC}"
echo "  状态: $STATUS"
echo "  数据库 job_id: $DB_JOB_ID"
echo ""

echo "========================================"
echo -e "${GREEN}✅ Step 4 验收测试全部通过！${NC}"
echo "========================================"
echo ""
echo "验收标准达成情况："
echo "  ✓ 成功获取 job_id: $JOB_ID"
echo "  ✓ 写入 task 数据库"
echo "  ✓ 状态为 ocr_processing"
echo "  ✓ TOKEN 认证成功"
echo ""
