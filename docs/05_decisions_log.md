# 决策日志（Decisions Log）

用于记录关键技术决策与原因，避免遗忘或重复踩坑。

模板：

## YYYY-MM-DD - 决策标题

- **背景**：
- **决策**：
- **原因**：
- **影响范围**：
- **替代方案**：

## 2026-01-16 - 保存/下载 Excel 相关 Debug 记录

- **背景**：用户反馈保存失败、下载内容不同步、下载文件名不符合要求。
- **决策**：集中修复保存/下载链路的后端异常与前端调用顺序，并统一下载文件名规则。
- **原因**：
  - 保存失败源于配置字段错误与合并单元格写入方式不兼容。
  - 下载内容不同步由前端保存后重复调用从 OCR 生成 Excel 覆盖编辑结果。
  - 下载文件名需要符合“图片名称_修改时间”的业务要求。
- **影响范围**：后端 `excel_service.py`、`table_service.py`、`excel.py`；前端 `api.ts`、`ExcelArea.tsx`；用户手册下载说明。
- **替代方案**：保存时不自动生成 Excel、仅在下载前生成；或将文件名改为“任务名_时间”。

### Debug 问题与解决方法

1. **保存失败：Bad Request**
   - **原因**：`table_service.py` 使用 `settings.DATA_DIR`（不存在），导致保存编辑 JSON 失败。
   - **解决**：改用 `settings.data_dir`。

2. **保存失败：'MergedCell' object attribute 'value' is read-only**
   - **原因**：写入 Excel 时对合并单元格的被覆盖单元格重复赋值。
   - **解决**：写入时跳过 `MergedCell`。

3. **保存失败：'MergedCell' object has no attribute 'column_letter'**
   - **原因**：列宽计算中直接访问 `cell.column_letter`，遇到 `MergedCell` 报错。
   - **解决**：按列索引遍历，跳过 `MergedCell`，用 `get_column_letter`。

4. **保存成功但下载内容未同步**
   - **原因**：前端保存后又调用 `generateExcel`（从 OCR JSON 重建）覆盖编辑结果。
   - **解决**：保存仅调用 `saveTableData`，不再二次生成。

5. **下载文件名不符合要求**
   - **原因**：默认使用 `table_{task_id}.xlsx`。
   - **解决**：下载接口改为 `图片名称_修改时间.xlsx`（并做安全字符清洗）。

6. **下载失败提示不清晰**
   - **原因**：前端未解析后端 `detail/message`。
   - **解决**：前端统一解析错误并展示具体原因。
