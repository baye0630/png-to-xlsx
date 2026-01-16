# OCR PNG to Excel (png-to-xlsx)

一个支持 **图片表格 OCR → JSON → Excel → 在线编辑 → 下载** 的 Web 应用。

项目文档统一入口在 `docs/`（`md文档/` 为历史入口，不再维护正文）。

## 开发进度

### ✅ Step 1 - 后端基础工程初始化（已完成）

- [x] FastAPI 工程可启动
- [x] Health 接口可用
- [x] 数据库连通（SQLite）
- [x] 任务模型已创建

验收报告：`docs/06_dev_logs/step1_completion_report.md`

### ✅ Step 2 - 任务模型与状态体系（已完成）

- [x] 支持创建任务（POST /api/v1/tasks/）
- [x] 支持查询任务（GET /api/v1/tasks/{task_id}）
- [x] 支持查询任务列表（GET /api/v1/tasks/）
- [x] 支持更新任务状态（PATCH /api/v1/tasks/{task_id}/status）
- [x] 支持更新任务信息（PATCH /api/v1/tasks/{task_id}）
- [x] 完整的服务层封装
- [x] 自动生成的 API 文档

验收报告：`docs/06_dev_logs/step2_completion_report.md`

### ✅ Step 3 - 图片上传与本地存储（已完成）

- [x] 图片上传接口（POST /api/v1/upload/image/{task_id}）
- [x] 便捷接口（POST /api/v1/upload/image - 创建任务+上传）
- [x] 图片存储位置明确：**`data/images/{task_id}.{ext}`**
- [x] 支持多种图片格式（PNG, JPEG, GIF, BMP, WebP）
- [x] 异步文件处理
- [x] 完整的文件验证
- [x] 任务与图片自动关联
- [x] 状态自动更新为 uploaded

验收报告：`docs/06_dev_logs/step3_completion_report.md`

### ✅ Step 4 - OCR 接入（创建 job_id）（已完成）

- [x] OCR 客户端封装（httpx 异步请求）
- [x] OCR 服务层（业务逻辑）
- [x] OCR API 接口（POST /api/v1/ocr/start/{task_id}）
- [x] OCR 健康检查（GET /api/v1/ocr/health）
- [x] Bearer Token 认证
- [x] 创建 OCR 任务并获取 job_id
- [x] 写入 task.ocr_job_id
- [x] 状态更新为 ocr_processing
- [x] 完整的错误处理

验收报告：`docs/06_dev_logs/step4_completion_report.md`

**注意**：需要配置有效的 `OCR_TOKEN` 才能调用真实 OCR 服务

### ✅ Step 5 - 任务状态获取 + 拉取 OCR JSON（已完成）

- [x] OCR 任务状态轮询接口（POST /api/v1/ocr/poll/{task_id}）
- [x] 自动拉取 OCR JSON 结果
- [x] 保存到 `data/ocr_json/{task_id}.json`
- [x] 状态自动更新为 ocr_done
- [x] 异步任务闭环（直到 finished/failed）
- [x] 完整的错误处理

验收报告：`docs/06_dev_logs/step5_completion_report.md`

### ✅ Step 6 - OCR JSON → Excel（多 Sheet）（已完成）

- [x] Excel 生成服务（excel_service.py）
- [x] HTML 表格解析器（HTMLTableParser）
- [x] 合并单元格处理算法
- [x] 多表格 → 多 Sheet 支持
- [x] Excel 样式美化（表头、边框、对齐）
- [x] API 接口（POST /api/v1/excel/generate/{task_id}）
- [x] 状态更新为 excel_generated

验收报告：`docs/06_dev_logs/step6_completion_report.md`

### ✅ Step 7 - Excel → 表格 JSON（供前端预览/编辑）（已完成）

- [x] 表格数据服务（table_service.py）
- [x] 直接从 OCR JSON 提取数据（无需 Excel 转换）
- [x] 完整的表格数据结构（CellData, TableSheet）
- [x] 两级 API 设计（完整数据 + 元数据）
- [x] GET /api/v1/table/data/{task_id} - 获取完整表格数据
- [x] GET /api/v1/table/metadata/{task_id} - 获取表格元数据
- [x] 状态自动更新为 editable

验收报告：`docs/06_dev_logs/step7_completion_report.md`

### ✅ Step 8 - 前端基础工程初始化 + 页面骨架（已完成）

- [x] React 19 + TypeScript 5.9 + Vite 7 工程搭建
- [x] UploadArea 组件（拖拽上传、文件选择）
- [x] ExcelArea 组件（Sheet 标签、表格预览区）
- [x] 主应用布局（头部、主体、页脚）
- [x] API 服务层封装（services/api.ts）
- [x] 完整的类型定义（types/index.ts）
- [x] 页面可访问（http://localhost:3000）
- [x] 代理配置（/api → :8000）

验收报告：`docs/06_dev_logs/step8_completion_report.md`

### ✅ Step 9 - 前端上传 + 状态展示（已完成）

- [x] 实现真实的文件上传逻辑
- [x] 自动启动 OCR 识别
- [x] OCR 状态自动轮询（每 2 秒）
- [x] 实时状态展示（上传中、OCR 处理中、成功、失败）
- [x] 加载动画和进度提示
- [x] 完善的错误处理和用户提示
- [x] 按钮智能禁用（防止重复提交）
- [x] 重新上传功能

验收报告：`docs/06_dev_logs/step9_completion_report.md`

### ✅ Step 10 - 前端表格预览（只读）+ 多 Sheet 切换（已完成）

- [x] 从后端获取表格数据（useEffect + API）
- [x] 实现表格渲染组件（TableRenderer）
- [x] 支持合并单元格（rowspan, colspan）
- [x] Sheet 标签切换功能
- [x] 表格样式美化（边框、表头、悬停效果）
- [x] 加载和错误状态展示
- [x] 滚动条美化
- [x] 响应式设计

验收报告：`docs/06_dev_logs/step10_completion_report.md`

### ✅ Step 11 - 前端编辑 + 保存（表格 JSON → Excel）（已完成）

- [x] 实现可编辑表格渲染器（EditableTableRenderer）
- [x] 双击单元格进入编辑模式
- [x] 支持键盘操作（Enter 保存，Esc 取消）
- [x] 实时修改状态跟踪（isModified）
- [x] 保存编辑数据到后端
- [x] 从编辑数据重新生成 Excel
- [x] 实现下载 Excel 功能
- [x] 完善用户提示和反馈

验收报告：`docs/06_dev_logs/step11_completion_report.md`

### 🎉 **核心功能已全部完成！主链路打通！**

```
图片上传 → OCR识别 → 表格预览 → 在线编辑 → 保存更新 → 下载Excel
```

### 📋 下一步：Step 12 - 异常处理与稳定性优化

详见：`docs/04_tasks/roadmap.md`

## Docs

- `docs/00_project_vision.md`
- `docs/01_prd/PRD.md`
- `docs/03_architecture/architecture_overview.md`
- `docs/03_architecture/ocr_integration.md`
- `docs/03_architecture/project_structure.md`
- `docs/04_tasks/roadmap.md`

## Project Structure

```
/home/lenovo/development_project/ocrpngtoexcel_test
├── backend/
├── frontend/
├── data/
├── docs/
└── md文档/ (legacy)
```

## Prerequisites

- Python 3.11+
- Node.js 22+ (已安装 v22.19.0)
- npm 11+ (已安装 v11.6.0)

## 快速开始

### 后端服务

1. **创建虚拟环境**（如果还没有）：
   ```bash
   python3.11 -m venv venv
   ```

2. **安装依赖**：
   ```bash
   ./venv/bin/pip install -r backend/requirements.txt
   ```

3. **配置环境变量**：
   ```bash
   cp backend/.env.example backend/.env
   # 根据需要修改配置（默认使用 SQLite，无需配置数据库密码）
   ```

4. **启动服务**：
   ```bash
   ./scripts/start_backend.sh
   ```

5. **验证服务**：
   - 根路径: http://localhost:8000/
   - Health 检查: http://localhost:8000/health
   - API 文档: http://localhost:8000/docs

详细说明见：`backend/README.md`

### 前端服务

1. **安装依赖**：
   ```bash
   cd frontend
   npm install
   ```

2. **启动开发服务器**：
   ```bash
   npm run dev
   ```

3. **访问页面**：
   - 前端页面: http://localhost:3000
   - 自动代理 `/api` 到后端 `:8000`

详细说明见：`frontend/README.md`

## 环境配置

### 后端配置 (.env)

主要配置项（详见 `backend/.env.example`）：

```env
# 数据库类型（sqlite 或 mysql）
DB_TYPE=sqlite

# OCR 服务配置
OCR_BASE_URL=http://10.119.133.236:8806
OCR_TOKEN=your_token_here

# 数据存储目录
DATA_DIR=../data
```

**注意**：
- 开发环境默认使用 SQLite，无需额外配置
- 生产环境可切换到 MySQL，需先创建数据库并配置密码

### 前端配置

前端使用 Vite 配置文件（`frontend/vite.config.ts`）：
- 端口：3000
- 代理：`/api` → `http://localhost:8000`

## API Endpoints

- 以 `task_id` 为核心的任务接口（上传/状态/获取表格 JSON/保存/下载），详见：
  - `docs/01_prd/PRD.md`
  - `docs/03_architecture/api_spec.md`

## Features

- Image upload (PNG, JPG, JPEG)
- OCR processing (external OCR service)
- **OCR JSON → Excel** conversion (supports multiple tables / multiple sheets)
- Online Excel editing (cell content, add/remove rows/columns)
- Save and download Excel files

## License

This project is licensed under the MIT License.
