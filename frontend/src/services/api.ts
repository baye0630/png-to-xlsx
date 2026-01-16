/**
 * API 服务
 */
import type { ApiResponse, Task, TableDataResponse } from '../types';

const API_BASE = '/api/v1';

async function throwApiError(response: Response, fallbackMessage: string): Promise<never> {
  let message = fallbackMessage;
  try {
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      const data = await response.json();
      if (data?.detail) {
        message = data.detail;
      } else if (data?.message) {
        message = data.message;
      }
    } else {
      const text = await response.text();
      if (text) {
        message = text;
      }
    }
  } catch {
    // ignore parse errors and keep fallback message
  }
  throw new Error(message);
}

/**
 * 上传图片并创建任务
 */
export async function uploadImage(file: File): Promise<ApiResponse<Task>> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/upload/image`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    await throwApiError(response, `上传失败: ${response.statusText}`);
  }

  return response.json();
}

/**
 * 获取任务信息
 */
export async function getTask(taskId: string): Promise<ApiResponse<Task>> {
  const response = await fetch(`${API_BASE}/tasks/${taskId}`);

  if (!response.ok) {
    await throwApiError(response, `获取任务失败: ${response.statusText}`);
  }

  return response.json();
}

/**
 * 启动 OCR
 */
export async function startOCR(taskId: string): Promise<ApiResponse> {
  const response = await fetch(`${API_BASE}/ocr/start/${taskId}`, {
    method: 'POST',
  });

  if (!response.ok) {
    await throwApiError(response, `启动 OCR 失败: ${response.statusText}`);
  }

  return response.json();
}

/**
 * 轮询 OCR 结果
 */
export async function pollOCR(taskId: string): Promise<ApiResponse> {
  const response = await fetch(`${API_BASE}/ocr/poll/${taskId}`, {
    method: 'POST',
  });

  if (!response.ok) {
    await throwApiError(response, `获取 OCR 结果失败: ${response.statusText}`);
  }

  return response.json();
}

/**
 * 获取表格数据
 */
export async function getTableData(taskId: string): Promise<ApiResponse<TableDataResponse>> {
  const response = await fetch(`${API_BASE}/table/data/${taskId}`);

  if (!response.ok) {
    await throwApiError(response, `获取表格数据失败: ${response.statusText}`);
  }

  return response.json();
}

/**
 * 生成 Excel
 */
export async function generateExcel(taskId: string): Promise<ApiResponse> {
  const response = await fetch(`${API_BASE}/excel/generate/${taskId}`, {
    method: 'POST',
  });

  if (!response.ok) {
    await throwApiError(response, `生成 Excel 失败: ${response.statusText}`);
  }

  return response.json();
}

/**
 * 保存表格数据
 */
export async function saveTableData(taskId: string, tableData: TableDataResponse): Promise<ApiResponse> {
  const response = await fetch(`${API_BASE}/table/save/${taskId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(tableData),
  });

  if (!response.ok) {
    await throwApiError(response, `保存表格数据失败: ${response.statusText}`);
  }

  return response.json();
}

/**
 * 下载 Excel 文件
 */
export async function downloadExcel(taskId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/excel/download/${taskId}`);

  if (!response.ok) {
    await throwApiError(response, `下载 Excel 失败: ${response.statusText}`);
  }

  // 获取文件名
  const contentDisposition = response.headers.get('Content-Disposition');
  let filename = `table_${taskId}.xlsx`;
  if (contentDisposition) {
    const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(contentDisposition);
    if (matches != null && matches[1]) {
      filename = matches[1].replace(/['"]/g, '');
    }
  }

  // 下载文件
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}
