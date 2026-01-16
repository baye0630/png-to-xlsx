"""
表格数据服务层
直接从 OCR JSON 提取表格数据，转换为前端需要的格式
"""
import json
import logging
from pathlib import Path
from typing import Optional, List, Tuple
from uuid import UUID

from app.models.task import Task, TaskStatus
from app.services.task_service import TaskService
from app.services.excel_service import HTMLTableParser  # 复用 HTML 解析器
from app.schemas.table import CellData, TableSheet, TableDataResponse, TableMetadata
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class TableService:
    """表格数据服务类"""
    
    @staticmethod
    def parse_html_table_to_cells(html_content: str) -> Tuple[List[List[CellData]], int, int]:
        """
        解析 HTML 表格为单元格数组（展开合并单元格）
        
        Args:
            html_content: HTML 表格内容
            
        Returns:
            (展开后的单元格数组, 行数, 列数)
        """
        # 使用 HTMLTableParser 解析
        parser = HTMLTableParser()
        parser.feed(html_content)
        rows_data = parser.get_table_data()
        
        if not rows_data:
            return [], 0, 0
        
        # 计算最大列数（考虑 colspan）
        max_cols = 0
        for row in rows_data:
            col_count = sum(cell['colspan'] for cell in row)
            max_cols = max(max_cols, col_count)
        
        # 展开合并单元格为二维数组
        expanded_rows = []
        rowspan_tracker = {}  # {col_idx: (remaining_rows, CellData)}
        
        for row_idx, row in enumerate(rows_data):
            expanded_row = [None] * max_cols  # 先初始化为 None
            
            # 1. 首先填充之前行的 rowspan
            cols_to_delete = []
            for col_idx, (remaining, cell_data) in rowspan_tracker.items():
                expanded_row[col_idx] = cell_data
                if remaining > 1:
                    rowspan_tracker[col_idx] = (remaining - 1, cell_data)
                else:
                    cols_to_delete.append(col_idx)
            
            # 删除已完成的 rowspan
            for col_idx in cols_to_delete:
                del rowspan_tracker[col_idx]
            
            # 2. 处理当前行的单元格
            col_idx = 0
            for cell in row:
                # 找到下一个空位置
                while col_idx < max_cols and expanded_row[col_idx] is not None:
                    col_idx += 1
                
                if col_idx >= max_cols:
                    break
                
                # 创建 CellData 对象
                cell_data = CellData(
                    text=cell['text'],
                    rowspan=cell['rowspan'],
                    colspan=cell['colspan'],
                    is_header=cell['is_header']
                )
                
                # 填充 colspan（主单元格）
                expanded_row[col_idx] = cell_data
                
                # 填充 colspan（后续位置用相同数据，但标记为合并单元格的一部分）
                for i in range(1, cell['colspan']):
                    if col_idx + i < max_cols:
                        # 合并单元格的后续列，保留原始单元格引用但文本为空
                        expanded_row[col_idx + i] = CellData(
                            text="",  # 合并单元格的后续位置不显示文本
                            rowspan=1,
                            colspan=1,
                            is_header=cell['is_header']
                        )
                
                # 记录 rowspan（如果大于 1）
                if cell['rowspan'] > 1:
                    for i in range(cell['colspan']):
                        if col_idx + i < max_cols:
                            rowspan_tracker[col_idx + i] = (cell['rowspan'] - 1, cell_data)
                
                col_idx += cell['colspan']
            
            # 3. 填充剩余的空单元格
            for i in range(max_cols):
                if expanded_row[i] is None:
                    expanded_row[i] = CellData(text="", rowspan=1, colspan=1, is_header=False)
            
            expanded_rows.append(expanded_row)
        
        # 继续处理剩余的 rowspan
        while rowspan_tracker:
            expanded_row = [None] * max_cols
            cols_to_delete = []
            
            for col_idx, (remaining, cell_data) in rowspan_tracker.items():
                expanded_row[col_idx] = cell_data
                if remaining > 1:
                    rowspan_tracker[col_idx] = (remaining - 1, cell_data)
                else:
                    cols_to_delete.append(col_idx)
            
            for col_idx in cols_to_delete:
                del rowspan_tracker[col_idx]
            
            # 填充空单元格
            for i in range(max_cols):
                if expanded_row[i] is None:
                    expanded_row[i] = CellData(text="", rowspan=1, colspan=1, is_header=False)
            
            expanded_rows.append(expanded_row)
        
        return expanded_rows, len(expanded_rows), max_cols
    
    @staticmethod
    def extract_tables_from_ocr_json(ocr_json_path: str) -> List[TableSheet]:
        """
        从 OCR JSON 文件中提取所有表格
        
        Args:
            ocr_json_path: OCR JSON 文件路径
            
        Returns:
            TableSheet 列表
        """
        try:
            with open(ocr_json_path, 'r', encoding='utf-8') as f:
                ocr_data = json.load(f)
        except Exception as e:
            logger.error(f"读取 OCR JSON 失败: {e}")
            return []
        
        sheets = []
        sheet_id = 1
        
        # 遍历所有页面
        pages = ocr_data.get('pages', [])
        for page in pages:
            parsing_res_list = page.get('parsing_res_list', [])
            
            # 筛选 block_label == 'table' 的内容
            for block in parsing_res_list:
                if block.get('block_label') != 'table':
                    continue
                
                html_content = block.get('block_content', '')
                if not html_content:
                    continue
                
                # 解析 HTML 表格为单元格数组
                try:
                    cells, rows, cols = TableService.parse_html_table_to_cells(html_content)
                    
                    if rows > 0 and cols > 0:
                        sheet = TableSheet(
                            sheet_id=sheet_id,
                            sheet_name=f"Table_{sheet_id}",
                            rows=rows,
                            cols=cols,
                            data=cells
                        )
                        sheets.append(sheet)
                        sheet_id += 1
                        
                except Exception as e:
                    logger.error(f"解析表格失败: {e}")
                    continue
        
        return sheets
    
    @staticmethod
    async def get_table_data(task_id: UUID) -> Tuple[bool, str, Optional[TableDataResponse]]:
        """
        获取任务的表格数据（供前端预览/编辑）
        
        Args:
            task_id: 任务 ID
            
        Returns:
            (成功标志, 消息, 表格数据)
        """
        # 1. 获取任务
        task = await TaskService.get_task(task_id)
        if not task:
            return False, f"任务不存在: {task_id}", None
        
        # 2. 检查任务状态（允许 ocr_done, excel_generated, editable）
        allowed_statuses = [
            TaskStatus.OCR_DONE,
            TaskStatus.EXCEL_GENERATED,
            TaskStatus.EDITABLE
        ]
        if task.status not in allowed_statuses:
            return False, f"任务状态错误: {task.status}，需要 OCR 完成后才能获取表格数据", None
        
        # 3. 检查 OCR JSON 是否存在
        if not task.ocr_json_path or not Path(task.ocr_json_path).exists():
            return False, f"OCR JSON 文件不存在: {task.ocr_json_path}", None
        
        # 4. 提取表格数据
        try:
            sheets = TableService.extract_tables_from_ocr_json(task.ocr_json_path)
            
            if not sheets:
                return False, "未找到表格数据", None
            
            # 5. 更新任务状态为 editable（如果还不是）
            if task.status != TaskStatus.EDITABLE:
                task.status = TaskStatus.EDITABLE
                await task.save()
                logger.info(f"任务 {task_id} 状态更新为 editable")
            
            # 6. 构建响应
            response = TableDataResponse(
                task_id=str(task.task_id),
                status=task.status.value,
                total_sheets=len(sheets),
                sheets=sheets
            )
            
            return True, f"成功获取 {len(sheets)} 个表格", response
            
        except Exception as e:
            logger.error(f"获取表格数据失败: {e}", exc_info=True)
            return False, f"获取表格数据失败: {str(e)}", None
    
    @staticmethod
    async def get_table_metadata(task_id: UUID) -> Tuple[bool, str, Optional[TableMetadata]]:
        """
        获取表格元数据（不包含完整数据，用于快速预览）
        
        Args:
            task_id: 任务 ID
            
        Returns:
            (成功标志, 消息, 表格元数据)
        """
        # 1. 获取任务
        task = await TaskService.get_task(task_id)
        if not task:
            return False, f"任务不存在: {task_id}", None
        
        # 2. 检查任务状态
        allowed_statuses = [
            TaskStatus.OCR_DONE,
            TaskStatus.EXCEL_GENERATED,
            TaskStatus.EDITABLE
        ]
        if task.status not in allowed_statuses:
            return False, f"任务状态错误: {task.status}", None
        
        # 3. 检查 OCR JSON 是否存在
        if not task.ocr_json_path or not Path(task.ocr_json_path).exists():
            return False, f"OCR JSON 文件不存在", None
        
        # 4. 提取表格元数据
        try:
            sheets = TableService.extract_tables_from_ocr_json(task.ocr_json_path)
            
            if not sheets:
                return False, "未找到表格数据", None
            
            # 构建轻量级元数据
            sheets_info = [
                {
                    "sheet_id": sheet.sheet_id,
                    "sheet_name": sheet.sheet_name,
                    "rows": sheet.rows,
                    "cols": sheet.cols
                }
                for sheet in sheets
            ]
            
            metadata = TableMetadata(
                task_id=str(task.task_id),
                status=task.status.value,
                total_sheets=len(sheets),
                sheets_info=sheets_info
            )
            
            return True, f"成功获取 {len(sheets)} 个表格元数据", metadata
            
        except Exception as e:
            logger.error(f"获取表格元数据失败: {e}", exc_info=True)
            return False, f"获取表格元数据失败: {str(e)}", None
    
    @staticmethod
    async def save_table_data(task_id: UUID, table_data: TableDataResponse) -> Tuple[bool, str]:
        """
        保存编辑后的表格数据
        
        将编辑后的数据保存到文件，并重新生成 Excel
        
        Args:
            task_id: 任务 ID
            table_data: 编辑后的表格数据
            
        Returns:
            (成功标志, 消息)
        """
        from app.services.excel_service import ExcelService
        
        # 1. 获取任务
        task = await TaskService.get_task(task_id)
        if not task:
            return False, f"任务不存在: {task_id}"
        
        # 2. 保存编辑后的数据到文件（JSON 格式）
        try:
            edited_data_dir = Path(settings.data_dir) / "edited"
            edited_data_dir.mkdir(parents=True, exist_ok=True)
            
            edited_json_path = edited_data_dir / f"{task_id}_edited.json"
            
            # 将 TableDataResponse 转换为字典并保存
            with open(edited_json_path, 'w', encoding='utf-8') as f:
                json.dump(table_data.model_dump(), f, ensure_ascii=False, indent=2)
            
            logger.info(f"保存编辑数据到: {edited_json_path}")
            
        except Exception as e:
            logger.error(f"保存编辑数据失败: {e}", exc_info=True)
            return False, f"保存编辑数据失败: {str(e)}"
        
        # 3. 从编辑后的数据重新生成 Excel
        try:
            success, message, excel_path = await ExcelService.generate_excel_from_table_data(
                task_id, table_data
            )
            
            if not success:
                return False, f"重新生成 Excel 失败: {message}"
            
            logger.info(f"成功重新生成 Excel: {excel_path}")
            
            return True, "保存成功，Excel 已更新"
            
        except Exception as e:
            logger.error(f"重新生成 Excel 失败: {e}", exc_info=True)
            return False, f"重新生成 Excel 失败: {str(e)}"