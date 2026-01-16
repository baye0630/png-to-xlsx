/**
 * 主应用组件
 */
import { useState } from 'react';
import UploadArea from './components/UploadArea/UploadArea';
import ExcelArea from './components/ExcelArea/ExcelArea';
import './App.css';

function App() {
  const [taskId, setTaskId] = useState<string>();

  const handleUploadSuccess = (newTaskId: string) => {
    setTaskId(newTaskId);
  };

  return (
    <div className="app">
      {/* 头部 */}
      <header className="app-header">
        <h1 className="app-title">📊 OCR PNG to Excel</h1>
        <p className="app-subtitle">图片表格识别与在线编辑工具</p>
      </header>

      {/* 主内容区 */}
      <main className="app-main">
        {/* 上传区域 */}
        <section className="app-section">
          <UploadArea onUploadSuccess={handleUploadSuccess} />
        </section>

        {/* Excel 编辑区域 */}
        <section className="app-section">
          <ExcelArea taskId={taskId} />
        </section>
      </main>

      {/* 页脚 */}
      <footer className="app-footer">
        <p>© 2026 OCR PNG to Excel - AI Powered Table Recognition</p>
      </footer>
    </div>
  );
}

export default App;
