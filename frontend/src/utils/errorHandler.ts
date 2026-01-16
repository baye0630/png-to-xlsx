/**
 * 错误处理工具
 * 提供统一的错误处理和用户友好的错误提示
 */

/**
 * 错误类型
 */
export enum ErrorType {
  NETWORK = 'network',           // 网络错误
  UPLOAD = 'upload',             // 上传错误
  OCR = 'ocr',                   // OCR 错误
  VALIDATION = 'validation',     // 验证错误
  SERVER = 'server',             // 服务器错误
  TIMEOUT = 'timeout',           // 超时错误
  UNKNOWN = 'unknown'            // 未知错误
}

/**
 * 错误信息映射
 */
const ERROR_MESSAGES: Record<string, string> = {
  // 网络错误
  'Failed to fetch': '网络连接失败，请检查网络设置',
  'Network request failed': '网络请求失败，请稍后重试',
  'NetworkError': '网络错误，请检查您的网络连接',
  
  // 上传错误
  'File too large': '文件过大，请选择小于 10MB 的图片',
  'Invalid file type': '不支持的文件格式，请上传图片文件',
  'Upload failed': '上传失败，请重试',
  
  // OCR 错误
  'OCR task creation failed': 'OCR 任务创建失败，请稍后重试',
  'OCR recognition failed': 'OCR 识别失败，请尝试使用清晰度更高的图片',
  'OCR timeout': 'OCR 识别超时，请稍后重试',
  
  // 服务器错误
  '500': '服务器内部错误，请稍后重试',
  '502': '服务器网关错误，请稍后重试',
  '503': '服务暂时不可用，请稍后重试',
  
  // 客户端错误
  '400': '请求参数错误',
  '401': '未授权，请重新登录',
  '403': '没有权限访问',
  '404': '请求的资源不存在',
  '422': '请求参数验证失败',
};

/**
 * 解析错误类型
 */
export function parseErrorType(error: any): ErrorType {
  if (!error) return ErrorType.UNKNOWN;
  
  const message = error.message || error.toString();
  
  if (message.includes('fetch') || message.includes('Network')) {
    return ErrorType.NETWORK;
  }
  if (message.includes('upload') || message.includes('上传')) {
    return ErrorType.UPLOAD;
  }
  if (message.includes('OCR') || message.includes('识别')) {
    return ErrorType.OCR;
  }
  if (message.includes('timeout') || message.includes('超时')) {
    return ErrorType.TIMEOUT;
  }
  if (message.includes('validation') || message.includes('验证')) {
    return ErrorType.VALIDATION;
  }
  if (error.status >= 500) {
    return ErrorType.SERVER;
  }
  
  return ErrorType.UNKNOWN;
}

/**
 * 格式化错误消息
 * 将技术性错误转换为用户友好的提示
 */
export function formatErrorMessage(error: any): string {
  if (!error) return '未知错误';
  
  // 如果是字符串，直接返回
  if (typeof error === 'string') {
    return error;
  }
  
  // 如果有 message 属性
  if (error.message) {
    // 查找预定义的错误消息
    for (const [key, value] of Object.entries(ERROR_MESSAGES)) {
      if (error.message.includes(key)) {
        return value;
      }
    }
    return error.message;
  }
  
  // 如果有 status 状态码
  if (error.status) {
    const statusKey = error.status.toString();
    if (ERROR_MESSAGES[statusKey]) {
      return ERROR_MESSAGES[statusKey];
    }
    return `请求失败 (${error.status})`;
  }
  
  return '操作失败，请稍后重试';
}

/**
 * 获取错误建议
 * 根据错误类型提供操作建议
 */
export function getErrorSuggestion(errorType: ErrorType): string {
  switch (errorType) {
    case ErrorType.NETWORK:
      return '建议：检查网络连接后重试';
    case ErrorType.UPLOAD:
      return '建议：检查文件格式和大小，重新上传';
    case ErrorType.OCR:
      return '建议：使用清晰度更高的图片，或稍后重试';
    case ErrorType.TIMEOUT:
      return '建议：请稍后重试，或联系技术支持';
    case ErrorType.VALIDATION:
      return '建议：检查输入参数是否正确';
    case ErrorType.SERVER:
      return '建议：服务器正在处理中，请稍后重试';
    default:
      return '建议：刷新页面或联系技术支持';
  }
}

/**
 * 完整的错误处理
 * 返回格式化的错误信息和建议
 */
export function handleError(error: any): {
  type: ErrorType;
  message: string;
  suggestion: string;
  originalError: any;
} {
  const errorType = parseErrorType(error);
  const message = formatErrorMessage(error);
  const suggestion = getErrorSuggestion(errorType);
  
  // 记录到控制台（用于调试）
  console.error('[错误处理]', {
    type: errorType,
    message,
    suggestion,
    originalError: error
  });
  
  return {
    type: errorType,
    message,
    suggestion,
    originalError: error
  };
}

/**
 * 创建错误详情字符串
 */
export function createErrorDetails(error: any): string {
  const handled = handleError(error);
  return `${handled.message}\n${handled.suggestion}`;
}
