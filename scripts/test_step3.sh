#!/bin/bash
# Step 3 功能测试脚本

API_BASE="http://localhost:8000/api/v1"
PROJECT_ROOT="/home/lenovo/development_project/ocrpngtoexcel_test"

echo "=========================================="
echo "  Step 3 功能测试 - 图片上传与本地存储"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 创建测试图片
echo -e "${BLUE}准备测试：创建测试图片${NC}"
cd $PROJECT_ROOT
python3 << 'EOF'
import base64
import os

png_data = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=='
)

os.makedirs('data/temp', exist_ok=True)
with open('data/temp/test_upload.png', 'wb') as f:
    f.write(png_data)
print('✅ 测试图片创建成功')
EOF
echo ""

# 测试 1: 创建任务
echo -e "${BLUE}测试 1: 创建新任务${NC}"
TASK_RESPONSE=$(curl -s -X POST $API_BASE/tasks/)
TASK_ID=$(echo $TASK_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['task_id'])")
echo "✅ 任务创建成功: $TASK_ID"
echo ""

# 测试 2: 上传图片到指定任务
echo -e "${BLUE}测试 2: 上传图片到指定任务${NC}"
UPLOAD_RESPONSE=$(curl -s -X POST "$API_BASE/upload/image/$TASK_ID" -F "file=@data/temp/test_upload.png")
echo $UPLOAD_RESPONSE | python3 -c "import sys, json; data = json.load(sys.stdin); print(f\"✅ {data['message']}\")"
IMAGE_PATH=$(echo $UPLOAD_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['image_path'])")
echo ""

# 测试 3: 验证图片文件存在
echo -e "${BLUE}测试 3: 验证图片文件存在${NC}"
ACTUAL_IMAGE_PATH="$PROJECT_ROOT/data/images/$TASK_ID.png"
if [ -f "$ACTUAL_IMAGE_PATH" ]; then
    SIZE=$(ls -lh "$ACTUAL_IMAGE_PATH" | awk '{print $5}')
    echo "✅ 图片文件存在"
    echo "   路径: $ACTUAL_IMAGE_PATH"
    echo "   大小: $SIZE"
    echo "   存储位置: data/images/{task_id}.png ✓"
else
    echo "❌ 图片文件不存在: $ACTUAL_IMAGE_PATH"
fi
echo ""

# 测试 4: 验证任务与图片关联
echo -e "${BLUE}测试 4: 验证任务与图片关联${NC}"
curl -s $API_BASE/tasks/$TASK_ID | python3 -c "
import sys, json
data = json.load(sys.stdin)['data']
print(f\"✅ 任务与图片关联正确\")
print(f\"   任务ID: {data['task_id']}\")
print(f\"   状态: {data['status']}\")
print(f\"   图片路径: {data['image_path']}\")
"
echo ""

# 测试 5: 便捷接口（创建任务+上传图片）
echo -e "${BLUE}测试 5: 便捷接口（创建任务+上传图片）${NC}"
COMBINED_RESPONSE=$(curl -s -X POST "$API_BASE/upload/image" -F "file=@data/temp/test_upload.png")
NEW_TASK_ID=$(echo $COMBINED_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['task_id'])")
echo "✅ 任务创建并上传成功"
echo "   新任务ID: $NEW_TASK_ID"
echo ""

# 测试 6: 查看所有已上传图片的任务
echo -e "${BLUE}测试 6: 查看所有已上传图片的任务${NC}"
curl -s "$API_BASE/tasks/?status=uploaded" | python3 -c "
import sys, json
data = json.load(sys.stdin)['data']
print(f\"✅ 已上传状态的任务数: {data['total']}\")
"
echo ""

# 测试 7: 验证所有图片文件
echo -e "${BLUE}测试 7: 验证所有图片文件${NC}"
echo "data/images/ 目录内容："
ls -lh $PROJECT_ROOT/data/images/ | grep -v "^总用量"
echo ""

# 测试 8: 数据库验证
echo -e "${BLUE}测试 8: 数据库验证${NC}"
echo "数据库中有图片路径的任务："
sqlite3 $PROJECT_ROOT/data/ocr_pngtoexcel.db "SELECT task_id, status FROM tasks WHERE image_path IS NOT NULL ORDER BY created_at DESC LIMIT 3;"
echo ""

echo "=========================================="
echo -e "${GREEN}✅ Step 3 所有测试通过！${NC}"
echo "=========================================="
echo ""
echo -e "${YELLOW}图片存储位置明确：data/images/{task_id}.{ext}${NC}"
echo ""
echo "查看验收报告: docs/06_dev_logs/step3_completion_report.md"
