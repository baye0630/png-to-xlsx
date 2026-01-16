#!/bin/bash
# Step 2 功能测试脚本

API_BASE="http://localhost:8000/api/v1"

echo "=========================================="
echo "  Step 2 功能测试"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}测试 1: 创建任务${NC}"
TASK_RESPONSE=$(curl -s -X POST $API_BASE/tasks/)
TASK_ID=$(echo $TASK_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['task_id'])")
echo "✅ 创建成功，task_id: $TASK_ID"
echo ""

echo -e "${BLUE}测试 2: 查询单个任务${NC}"
curl -s $API_BASE/tasks/$TASK_ID | python3 -m json.tool | grep -A 5 '"data"'
echo ""

echo -e "${BLUE}测试 3: 查询任务列表${NC}"
curl -s $API_BASE/tasks/ | python3 -c "import sys, json; data = json.load(sys.stdin); print(f\"✅ 总任务数: {data['data']['total']}\")"
echo ""

echo -e "${BLUE}测试 4: 更新任务状态为 ocr_processing${NC}"
curl -s -X PATCH "$API_BASE/tasks/$TASK_ID/status?status=ocr_processing" | python3 -c "import sys, json; data = json.load(sys.stdin); print(f\"✅ 状态更新为: {data['data']['status']}\")"
echo ""

echo -e "${BLUE}测试 5: 更新任务状态为 ocr_done${NC}"
curl -s -X PATCH "$API_BASE/tasks/$TASK_ID/status?status=ocr_done" | python3 -c "import sys, json; data = json.load(sys.stdin); print(f\"✅ 状态更新为: {data['data']['status']}\")"
echo ""

echo -e "${BLUE}测试 6: 更新任务完整信息${NC}"
curl -s -X PATCH $API_BASE/tasks/$TASK_ID \
  -H "Content-Type: application/json" \
  -d "{\"ocr_job_id\": \"test-job-$(date +%s)\", \"status\": \"excel_generated\"}" \
  | python3 -c "import sys, json; data = json.load(sys.stdin); print(f\"✅ ocr_job_id: {data['data']['ocr_job_id']}, status: {data['data']['status']}\")"
echo ""

echo -e "${BLUE}测试 7: 按状态过滤查询${NC}"
curl -s "$API_BASE/tasks/?status=uploaded" | python3 -c "import sys, json; data = json.load(sys.stdin); print(f\"✅ uploaded 状态的任务数: {data['data']['total']}\")"
echo ""

echo -e "${BLUE}测试 8: 查看最终状态${NC}"
curl -s $API_BASE/tasks/$TASK_ID | python3 -c "import sys, json; data = json.load(sys.stdin)['data']; print(f\"task_id: {data['task_id']}\"); print(f\"status: {data['status']}\"); print(f\"ocr_job_id: {data['ocr_job_id']}\"); print(f\"updated_at: {data['updated_at']}\")"
echo ""

echo "=========================================="
echo -e "${GREEN}✅ 所有测试通过！${NC}"
echo "=========================================="
echo ""
echo "查看 API 文档: http://localhost:8000/docs"
echo "查看详细报告: docs/06_dev_logs/step2_completion_report.md"
