/**
 * Excel 编辑区域组件
 */
import { useState, useEffect } from 'react';
import { getTableData, generateExcel, saveTableData, downloadExcel } from '../../services/api';
import type { TableDataResponse } from '../../types';
import EditableTableRenderer from './EditableTableRenderer';
import './ExcelArea.css';

interface ExcelAreaProps {
  taskId?: string;
}

export default function ExcelArea({ taskId }: ExcelAreaProps) {
  const [currentSheet, setCurrentSheet] = useState(0);
  const [tableData, setTableData] = useState<TableDataResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [isModified, setIsModified] = useState(false);
  const [saving, setSaving] = useState(false);

  // 获取表格数据
  useEffect(() => {
    if (!taskId) {
      setTableData(null);
      setCurrentSheet(0);
      setIsModified(false);
      return;
    }

    const fetchTableData = async () => {
      setLoading(true);
      setError('');
      
      try {
        const response = await getTableData(taskId);
        setTableData(response.data);
        setCurrentSheet(0);
        setIsModified(false);
      } catch (err) {
        console.error('获取表格数据失败:', err);
        setError(err instanceof Error ? err.message : '获取表格数据失败');
      } finally {
        setLoading(false);
      }
    };

    fetchTableData();
  }, [taskId]);

  const hasData = tableData !== null && tableData.sheets.length > 0;

  // 处理单元格编辑
  const handleCellEdit = (rowIndex: number, colIndex: number, newValue: string) => {
    if (!tableData) return;

    const updatedData = { ...tableData };
    updatedData.sheets[currentSheet].data[rowIndex][colIndex].text = newValue;
    setTableData(updatedData);
    setIsModified(true);
  };

  // 保存表格数据
  const handleSave = async () => {
    if (!taskId || !tableData || !isModified) return;
    
    setSaving(true);
    try {
      await saveTableData(taskId, tableData);
      setIsModified(false);
      alert('保存成功！Excel 已更新。');
    } catch (err) {
      console.error('保存失败:', err);
      alert('保存失败: ' + (err instanceof Error ? err.message : '未知错误'));
    } finally {
      setSaving(false);
    }
  };

  // 下载 Excel
  const handleDownload = async () => {
    if (!taskId || !tableData) return;
    
    try {
      // 如果有未保存的修改，先保存
      if (isModified) {
        const shouldSave = window.confirm('检测到未保存的修改，是否先保存？\n\n点击"确定"保存后下载，点击"取消"下载旧版本。');
        if (shouldSave) {
          await handleSave();
        }
      }
      
      // 尝试下载
      try {
        await downloadExcel(taskId);
      } catch (downloadErr) {
        // 如果下载失败（Excel文件不存在），先生成Excel再下载
        const errorMessage = downloadErr instanceof Error ? downloadErr.message : '';
        if (errorMessage.includes('Excel 文件尚未生成') || errorMessage.includes('Bad Request')) {
          // 只调用 generateExcel，不调用 saveTableData
          // generateExcel 会从 OCR JSON 生成 Excel
          console.log('Excel文件不存在，正在生成...');
          await generateExcel(taskId);
          
          // 等待一小段时间确保文件生成完成
          await new Promise(resolve => setTimeout(resolve, 500));
          
          // 再次尝试下载
          await downloadExcel(taskId);
        } else {
          throw downloadErr;
        }
      }
    } catch (err) {
      console.error('下载失败:', err);
      alert('下载失败: ' + (err instanceof Error ? err.message : '未知错误'));
    }
  };

  return (
    <div className="excel-area">
      <div className="excel-header">
        <h2 className="excel-title">表格编辑</h2>
        
        {hasData && (
          <div className="excel-actions">
            <button 
              className="excel-button excel-button-secondary"
              onClick={handleDownload}
            >
              下载 Excel
            </button>
            <button 
              className="excel-button excel-button-primary" 
              onClick={handleSave}
              disabled={!isModified || saving}
            >
              {saving ? '保存中...' : isModified ? '保存修改 *' : '保存修改'}
            </button>
          </div>
        )}
      </div>

      {loading ? (
        <div className="excel-loading">
          <div className="loading-spinner"></div>
          <p className="loading-text">加载表格数据中...</p>
        </div>
      ) : error ? (
        <div className="excel-error">
          <div className="error-icon">❌</div>
          <p className="error-text">{error}</p>
        </div>
      ) : !hasData ? (
        <div className="excel-empty">
          <div className="excel-empty-icon">📊</div>
          <p className="excel-empty-text">请先上传图片进行识别</p>
          <p className="excel-empty-hint">识别完成后，表格数据将在此处显示</p>
        </div>
      ) : (
        <>
          {/* Sheet 标签页 */}
          <div className="excel-tabs">
            {tableData.sheets.map((sheet, index) => (
              <button
                key={sheet.sheet_id}
                className={`excel-tab ${currentSheet === index ? 'active' : ''}`}
                onClick={() => setCurrentSheet(index)}
              >
                {sheet.sheet_name}
                <span className="excel-tab-info">
                  ({sheet.rows}×{sheet.cols})
                </span>
              </button>
            ))}
          </div>

          {/* 表格编辑区 */}
          <div className="excel-table-container">
            <div className="excel-hint">
              💡 双击单元格可编辑，Enter 保存，Esc 取消
            </div>
            <EditableTableRenderer 
              sheet={tableData.sheets[currentSheet]} 
              onCellEdit={handleCellEdit}
            />
          </div>
        </>
      )}
    </div>
  );
}
