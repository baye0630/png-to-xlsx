/**
 * 类型定义
 */

// 任务状态枚举
export enum TaskStatus {
  UPLOADED = 'uploaded',
  OCR_PROCESSING = 'ocr_processing',
  OCR_DONE = 'ocr_done',
  OCR_FAILED = 'ocr_failed',
  EXCEL_GENERATED = 'excel_generated',
  EXCEL_FAILED = 'excel_failed',
  EDITABLE = 'editable',
}

// 任务接口
export interface Task {
  task_id: string;
  status: TaskStatus;
  image_path: string | null;
  ocr_json_path: string | null;
  excel_path: string | null;
  ocr_job_id: string | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

// 单元格数据
export interface CellData {
  text: string;
  rowspan: number;
  colspan: number;
  is_header: boolean;
}

// 表格 Sheet
export interface TableSheet {
  sheet_id: number;
  sheet_name: string;
  rows: number;
  cols: number;
  data: CellData[][];
}

// 表格数据响应
export interface TableDataResponse {
  task_id: string;
  status: string;
  total_sheets: number;
  sheets: TableSheet[];
}

// API 响应基础结构
export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data: T;
}
