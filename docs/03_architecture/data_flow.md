# 数据流（占位）

建议输出两张图：
- **端到端数据流**：上传图片 → OCR job → OCR JSON → Excel → 表格 JSON → 保存/下载
- **落盘结构**：images / ocr_json / excel(latest + versions)

当前数据流说明参考：
- `docs/01_prd/PRD.md`（核心流程/数据来源）
- `docs/03_architecture/architecture_overview.md`（后端落盘与转换策略）

