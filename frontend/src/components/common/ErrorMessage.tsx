/**
 * 错误消息组件
 * 统一的错误显示组件，提供友好的错误提示
 */
import { ErrorType, handleError } from '../../utils/errorHandler';
import './ErrorMessage.css';

interface ErrorMessageProps {
  error: any;
  onRetry?: () => void;
  onDismiss?: () => void;
}

export default function ErrorMessage({ error, onRetry, onDismiss }: ErrorMessageProps) {
  const handled = handleError(error);
  
  // 根据错误类型选择图标
  const getIcon = (type: ErrorType): string => {
    switch (type) {
      case ErrorType.NETWORK:
        return '🌐';
      case ErrorType.UPLOAD:
        return '📤';
      case ErrorType.OCR:
        return '🔍';
      case ErrorType.TIMEOUT:
        return '⏱️';
      case ErrorType.VALIDATION:
        return '⚠️';
      case ErrorType.SERVER:
        return '🔧';
      default:
        return '❌';
    }
  };
  
  return (
    <div className={`error-message error-message-${handled.type}`}>
      <div className="error-message-header">
        <span className="error-message-icon">{getIcon(handled.type)}</span>
        <span className="error-message-title">操作失败</span>
        {onDismiss && (
          <button 
            className="error-message-close" 
            onClick={onDismiss}
            aria-label="关闭"
          >
            ×
          </button>
        )}
      </div>
      
      <div className="error-message-body">
        <p className="error-message-text">{handled.message}</p>
        <p className="error-message-suggestion">{handled.suggestion}</p>
      </div>
      
      {onRetry && (
        <div className="error-message-footer">
          <button 
            className="error-message-retry" 
            onClick={onRetry}
          >
            🔄 重试
          </button>
        </div>
      )}
    </div>
  );
}
