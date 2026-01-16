# ocr_pngtoexcel 项目文件结构规划

本文档用于约定本项目的目录结构与命名规范，确保与 PRD/技术方案一致，便于开发、维护与扩展。

主链路（对齐 `docs/01_prd/PRD.md`）：**图片表格 OCR → JSON → Excel → 在线编辑 → 下载**  
外部 OCR 服务流程（对齐 `docs/03_architecture/ocr_integration.md`）：**上传创建 job → 长轮询状态 → 获取 result/json**

---

## 1. 设计原则（必须遵守）

- **JSON 是中间格式**：OCR 输出以 `result/json` 为主，作为“JSON→Excel”的数据来源；Markdown 仅作可选对照/调试，不作为主链路依赖。
- **前后端解耦**：前端只关心 `task_id`、状态与“可编辑表格 JSON”；后端负责 OCR 对接、落盘与转换。
- **任务（Task）为核心**：所有文件/结果都归档到 `task_id` 维度，便于追溯与清理。
- **运行数据不进 Git**：`data/` 为运行态目录，仅后端读写。

---

## 2. 项目整体目录结构（建议）

```
ocr_pngtoexcel/
├── frontend/                 # 前端（Vue3 + Vite + TS + Naive UI + Pinia）
├── backend/                  # 后端（FastAPI + Tortoise ORM + MySQL）
├── data/                     # 运行时数据（images / ocr_json / excel 等）
├── docs/                     # 项目文档中枢（推荐：按 00~06 规范化）
├── md文档/                    # 旧文档目录（历史保留，建议逐步迁移到 docs/）
├── scripts/                  # 本地开发/运维脚本
└── README.md                 # 项目说明
```

---

## 3. 前端项目结构（frontend）

前端围绕两个区域（UploadArea + ExcelArea）组织，数据以 task 为中心（Pinia）。

```
frontend/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
└── src/
    ├── main.ts
    ├── App.vue
    ├── router/
    │   └── index.ts           # Hash 路由
    ├── store/
    │   └── task.ts            # 当前 task_id、状态、表格 JSON（多 Sheet）
    ├── api/
    │   ├── upload.ts          # 创建任务/上传图片
    │   ├── task.ts            # 查询任务状态
    │   ├── table.ts           # 获取/提交表格 JSON（预览/编辑/保存）
    │   └── download.ts        # 下载 Excel
    ├── pages/
    │   └── Home/
    │       ├── index.vue
    │       └── components/
    │           ├── UploadArea.vue
    │           ├── ExcelArea.vue
    │           ├── SheetTabs.vue
    │           ├── EditableTable.vue
    │           └── ActionBar.vue
    ├── components/
    │   ├── LoadingStatus.vue
    │   ├── EmptyState.vue
    │   └── ErrorTip.vue
    ├── types/
    │   ├── task.ts
    │   ├── table.ts           # “可编辑表格 JSON”结构（多 Sheet）
    │   └── api.ts
    └── utils/
        ├── file.ts
        └── status.ts
```

---

## 4. 后端项目结构（backend）

后端按“路由层 / 服务层 / 外部客户端 / 工具 / 后台任务”分层，避免业务逻辑散落到路由层。

```
backend/
├── app/
│   ├── main.py                   # FastAPI 入口
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── logging.py
│   ├── models/
│   │   └── task.py               # Task（task_id、ocr_job_id、路径、状态等）
│   ├── schemas/
│   │   ├── task.py
│   │   ├── table.py              # 前端表格 JSON 的 Pydantic schema
│   │   ├── excel.py
│   │   └── common.py
│   ├── api/
│   │   └── v1/
│   │       ├── upload.py         # 上传图片/创建任务
│   │       ├── task.py           # 查询任务状态
│   │       ├── table.py          # 获取/保存表格 JSON
│   │       └── download.py       # 下载 Excel
│   ├── services/
│   │   ├── task_service.py
│   │   ├── upload_service.py
│   │   ├── ocr_service.py        # job 创建、状态轮询、拉取 result/json、落盘
│   │   ├── convert_service.py    # OCR JSON → Excel；表格 JSON → Excel
│   │   └── table_service.py      # Excel → 表格 JSON（多 Sheet）/ 校验/归一化
│   ├── clients/
│   │   └── ocr_client.py         # 封装外部 OCR 服务（参考 ocr_integration.md）
│   ├── utils/
│   │   ├── file.py
│   │   └── excel_parser.py       # 读写 Excel、Sheet/单元格处理
│   └── tasks/
│       └── ocr_polling.py        # 后台轮询/长轮询封装（可选）
│
├── aerich/                       # 迁移（如使用）
├── requirements.txt
└── README.md
```

---

## 5. 运行数据目录（data）

以 `task_id` 为核心进行落盘。主链路必须包含：**图片**、**OCR JSON**、**最新 Excel**。

```
data/
├── images/                       # 原始上传图片
│   └── {task_id}.{ext}
├── ocr_json/                     # OCR 原始 JSON（主链路、可追溯）
│   └── {task_id}.json
├── excel/                        # Excel 导出结果
│   ├── {task_id}/
│   │   ├── latest.xlsx           # 最新版本（下载用）
│   │   └── versions/             # 可选：历史版本
│   │       ├── v1.xlsx
│   │       └── v2.xlsx
└── temp/                         # 临时文件（可选，可定期清理）
```

说明：
- **Markdown 输出（可选）**：如需对照/调试，可额外增加 `data/ocr_markdown/{task_id}.md`，但不作为主流程依赖。

---

## 6. 文档目录（docs：推荐的“文档中枢”结构）

参考“项目文档工程化”结构，建议使用 `docs/` 作为唯一入口，把“愿景/PRD/设计/架构/任务/决策/开发日志”分层沉淀，避免信息碎片化。

```
docs/
├── 00_project_vision.md          # 项目宪法：一句话说清“做什么/价值”
├── 01_prd/                       # 产品需求文档（PRD）
│   ├── PRD.md
│   └── user_stories.md           # 可选：用户故事/验收标准
├── 02_design/                    # 设计文档（UI/UX/流程/原型）
│   └── README.md                 # 放设计链接、流程图、截图等
├── 03_architecture/              # 架构设计（技术选型/模块/数据流/API）
│   ├── architecture_overview.md
│   ├── api_spec.md
│   ├── data_flow.md
│   ├── ocr_integration.md
│   └── project_structure.md
├── 04_tasks/                     # 任务拆解（可交付给 AI 的小任务）
│   ├── roadmap.md
│   └── backlog.md
├── 05_decisions_log.md           # 决策日志：记录关键决策与原因
└── 06_dev_logs/                  # AI 开发日志：每次交互的 Prompt/输出/结论
    └── README.md
```

---

## 7. 脚本与部署（scripts）

```
scripts/
├── init_db.sh                    # 初始化数据库（如需要）
├── clean_data.sh                 # 清理 data（按 task_id/按日期）
└── start_dev.sh                  # 一键启动本地开发环境（可选）
```

---

## 8. 结构总结

- **OCR 可替换**：只需替换 `clients/ocr_client.py` 与部分 `ocr_service.py` 逻辑
- **多表/多 Sheet 天然支持**：表格 JSON 以 Sheet 为单位组织
- **可追溯**：保留 OCR 原始 JSON + Excel 版本（可选）

