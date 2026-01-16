/**
 * 上传区域组件
 */
import { useState } from 'react';
import { uploadImage, startOCR, pollOCR, getTask } from '../../services/api';
import { TaskStatus } from '../../types';
import './UploadArea.css';

interface UploadAreaProps {
  onUploadSuccess?: (taskId: string) => void;
}

// 上传状态
type UploadStatus = 'idle' | 'uploading' | 'ocr_starting' | 'ocr_polling' | 'success' | 'error';

export default function UploadArea({ onUploadSuccess }: UploadAreaProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>('idle');
  const [statusMessage, setStatusMessage] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [currentTaskId, setCurrentTaskId] = useState<string>('');

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type.startsWith('image/')) {
      setFile(droppedFile);
      setErrorMessage('');
    } else {
      setErrorMessage('请选择有效的图片文件');
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setErrorMessage('');
    }
  };

  /**
   * 轮询 OCR 结果（递归）
   */
  const pollOCRResult = async (taskId: string, maxAttempts = 30): Promise<void> => {
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        // 获取任务状态
        const taskResponse = await getTask(taskId);
        const task = taskResponse.data;
        
        setStatusMessage(`OCR 处理中... (${attempt + 1}/${maxAttempts})`);

        if (task.status === TaskStatus.OCR_DONE) {
          setUploadStatus('success');
          setStatusMessage('OCR 识别完成！');
          if (onUploadSuccess) {
            onUploadSuccess(taskId);
          }
          return;
        } else if (task.status === TaskStatus.OCR_FAILED) {
          throw new Error(task.error_message || 'OCR 识别失败');
        }

        // 每 2 秒轮询一次
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // 调用 poll 接口尝试拉取结果
        await pollOCR(taskId);
      } catch (error) {
        console.error('轮询 OCR 失败:', error);
        setUploadStatus('error');
        setErrorMessage(error instanceof Error ? error.message : 'OCR 轮询失败');
        return;
      }
    }

    // 超时
    setUploadStatus('error');
    setErrorMessage('OCR 识别超时，请稍后重试');
  };

  /**
   * 处理文件上传
   */
  const handleUpload = async () => {
    if (!file) return;

    try {
      // 1. 上传图片
      setUploadStatus('uploading');
      setStatusMessage('正在上传图片...');
      setErrorMessage('');
      
      const uploadResponse = await uploadImage(file);
      const taskId = uploadResponse.data.task_id;
      setCurrentTaskId(taskId);
      
      console.log('上传成功，任务ID:', taskId);

      // 2. 启动 OCR
      setUploadStatus('ocr_starting');
      setStatusMessage('正在启动 OCR 识别...');
      
      await startOCR(taskId);
      console.log('OCR 启动成功');

      // 3. 开始轮询 OCR 结果
      setUploadStatus('ocr_polling');
      setStatusMessage('OCR 处理中，请稍候...');
      
      await pollOCRResult(taskId);

    } catch (error) {
      console.error('上传或 OCR 失败:', error);
      setUploadStatus('error');
      setErrorMessage(error instanceof Error ? error.message : '操作失败，请重试');
    }
  };

  /**
   * 重置状态
   */
  const handleReset = () => {
    setFile(null);
    setUploadStatus('idle');
    setStatusMessage('');
    setErrorMessage('');
    setCurrentTaskId('');
  };

  return (
    <div className="upload-area">
      <h2 className="upload-title">图片上传</h2>
      
      <div
        className={`upload-drop-zone ${isDragging ? 'dragging' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {file ? (
          <div className="upload-file-info">
            <div className="upload-file-icon">📄</div>
            <div className="upload-file-name">{file.name}</div>
            <div className="upload-file-size">
              {(file.size / 1024).toFixed(2)} KB
            </div>
          </div>
        ) : (
          <div className="upload-placeholder">
            <div className="upload-icon">📤</div>
            <p className="upload-text">拖拽图片到此处，或点击选择文件</p>
            <p className="upload-hint">支持 PNG、JPG、JPEG、GIF、BMP、WebP 格式</p>
          </div>
        )}
      </div>

      {/* 状态展示区域 */}
      {uploadStatus !== 'idle' && (
        <div className="upload-status">
          {uploadStatus === 'uploading' && (
            <div className="status-item status-uploading">
              <span className="status-icon">⏳</span>
              <span className="status-text">{statusMessage}</span>
            </div>
          )}
          
          {uploadStatus === 'ocr_starting' && (
            <div className="status-item status-processing">
              <span className="status-icon">🔄</span>
              <span className="status-text">{statusMessage}</span>
            </div>
          )}
          
          {uploadStatus === 'ocr_polling' && (
            <div className="status-item status-polling">
              <span className="status-icon">🔍</span>
              <span className="status-text">{statusMessage}</span>
              <div className="status-spinner"></div>
            </div>
          )}
          
          {uploadStatus === 'success' && (
            <div className="status-item status-success">
              <span className="status-icon">✅</span>
              <span className="status-text">{statusMessage}</span>
              {currentTaskId && (
                <span className="status-task-id">任务ID: {currentTaskId}</span>
              )}
            </div>
          )}
          
          {uploadStatus === 'error' && errorMessage && (
            <div className="status-item status-error">
              <span className="status-icon">❌</span>
              <span className="status-text">{errorMessage}</span>
            </div>
          )}
        </div>
      )}

      <div className="upload-actions">
        <label className="upload-button upload-button-select">
          <input
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
            disabled={uploadStatus === 'uploading' || uploadStatus === 'ocr_starting' || uploadStatus === 'ocr_polling'}
          />
          选择文件
        </label>

        <button
          className="upload-button upload-button-primary"
          onClick={handleUpload}
          disabled={!file || uploadStatus === 'uploading' || uploadStatus === 'ocr_starting' || uploadStatus === 'ocr_polling'}
        >
          {uploadStatus === 'uploading' || uploadStatus === 'ocr_starting' || uploadStatus === 'ocr_polling' 
            ? '处理中...' 
            : '开始识别'}
        </button>

        {(file || uploadStatus !== 'idle') && uploadStatus !== 'uploading' && uploadStatus !== 'ocr_starting' && uploadStatus !== 'ocr_polling' && (
          <button
            className="upload-button upload-button-secondary"
            onClick={handleReset}
          >
            重新上传
          </button>
        )}
      </div>
    </div>
  );
}
