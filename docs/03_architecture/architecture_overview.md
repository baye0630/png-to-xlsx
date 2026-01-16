# 开发实现思路与开发顺序（技术文档）

本文档整合了：
- **开发实现思路**：整体架构、数据流、模块职责、核心数据/状态
- **开发顺序（Roadmap）**：按可验证产出拆分的推进顺序

主链路以 PRD 为准：**图片表格 OCR → JSON → Excel → 在线编辑 → 下载**。  
外部 OCR 服务调用细节参考：`docs/03_architecture/ocr_integration.md`。

---

## 1. 总体技术方案

### 1.1 技术栈

- **前端**：Vue3 + Vite + TypeScript + Naive UI + Pinia（Hash 路由）
- **后端**：Python + FastAPI + Tortoise ORM + MySQL
- **OCR（外部服务）**：异步任务（`job_id`）+ JSON 结果（主用）+ Markdown/图片（可选）

### 1.2 端到端核心流程（对齐 PRD）

```
上传图片 → 创建任务(task_id)
  → 后端上传至 OCR 服务 → 获取 job_id
  → 轮询/长轮询任务状态
  → finished 后拉取 OCR JSON（raw）
  → JSON → Excel（生成初版，多 Sheet）
  → Excel → 表格 JSON（供前端预览/编辑）
  → 前端编辑表格 JSON → 保存 → 生成新 Excel
  → 下载最新 Excel
```

---

## 2. 模块职责划分

### 2.1 前端（页面与交互）

- **UploadArea**：图片选择/上传、OCR 状态展示、失败重试入口
- **ExcelArea**：
  - Sheet 切换（Tab/下拉）
  - 表格预览与编辑（单元格编辑、行列增删）
  - 显式保存（不自动保存）
  - 下载

### 2.2 后端（任务、文件与转换）

- **任务管理**：创建任务、状态流转、任务查询
- **文件存储**：上传图片落盘、OCR 原始 JSON 落盘、Excel 版本落盘
- **OCR 适配层**：对接外部 OCR 服务（上传/长轮询/取 JSON）
- **数据转换层**：
  - OCR JSON → Excel（生成初版）
  - Excel → 表格 JSON（给前端）
  - 表格 JSON → Excel（保存时生成新版本）
- **下载服务**：下载最新 Excel（校验 task 有效性）

---

## 3. 核心数据设计（建议）

### 3.1 任务模型（Task）

平台统一以「任务」为核心（一个任务对应一次图片识别与编辑导出）：

- **task_id**：平台唯一
- **image_path**：上传图片落盘路径
- **ocr_job_id**：外部 OCR 任务 id
- **ocr_json_path**：OCR 原始 JSON 结果落盘路径（主链路）
- **excel_path**：当前最新 Excel 文件路径
- **status**：任务状态（见下）
- **error_message**：失败原因（可选）
- **created_at / updated_at**

### 3.2 状态机（对齐 PRD）

主流程：

```
uploaded → ocr_processing → ocr_done → excel_generated → editable
```

异常：

```
ocr_failed / excel_failed
```

---

## 4. OCR 对接要点（后端）

### 4.1 与 OCR 服务的交互（摘要）

```
POST /jobs-from-uploading  → job_id
GET  /longpoll/jobs/{job_id} → events + done
GET  /result/json/jobs/{job_id} → OCR JSON（主用）
```

### 4.2 结果选择策略

- **主用**：`result/json`（结构化、便于“JSON→Excel”）
- **可选**：`result/markdown`、`result/images`（对照/调试用，不作为主链路依赖）

---

## 5. 前后端接口（本项目后端，对前端）

> 仅给出建议的最小集合，便于开发与联调；具体路径可按实际实现调整。

- **上传并创建任务**：返回 `task_id`，触发 OCR
- **查询任务状态**：返回 `status`、必要进度/错误信息
- **获取可编辑表格数据**：返回“表格 JSON（多 Sheet）”
- **保存**：前端提交表格 JSON，后端生成新 Excel（更新 `excel_path`）
- **下载**：下载最新 Excel

---

## 6. 开发顺序（Roadmap）

Roadmap 已抽取到：
- `docs/04_tasks/roadmap.md`

