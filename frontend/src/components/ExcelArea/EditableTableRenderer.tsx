/**
 * 可编辑表格渲染组件
 * 支持合并单元格和单元格编辑
 */
import { useState } from 'react';
import type { TableSheet, CellData } from '../../types';
import './TableRenderer.css';

interface EditableTableRendererProps {
  sheet: TableSheet;
  onCellEdit: (rowIndex: number, colIndex: number, newValue: string) => void;
}

export default function EditableTableRenderer({ sheet, onCellEdit }: EditableTableRendererProps) {
  const [editingCell, setEditingCell] = useState<{ row: number; col: number } | null>(null);
  const [editValue, setEditValue] = useState('');

  // 构建单元格渲染信息（处理合并单元格）
  const renderGrid: Array<Array<{ cell: CellData; skip: boolean } | null>> = [];

  // 初始化网格
  for (let r = 0; r < sheet.rows; r++) {
    renderGrid[r] = [];
    for (let c = 0; c < sheet.cols; c++) {
      renderGrid[r][c] = null;
    }
  }

  // 填充网格，标记跳过的单元格
  for (let r = 0; r < sheet.data.length; r++) {
    for (let c = 0; c < sheet.data[r].length; c++) {
      const cell = sheet.data[r][c];
      
      // 主单元格
      if (renderGrid[r][c] === null) {
        renderGrid[r][c] = { cell, skip: false };
        
        // 标记被合并的单元格为跳过
        for (let dr = 0; dr < cell.rowspan; dr++) {
          for (let dc = 0; dc < cell.colspan; dc++) {
            if (dr === 0 && dc === 0) continue;
            if (r + dr < sheet.rows && c + dc < sheet.cols) {
              renderGrid[r + dr][c + dc] = { cell, skip: true };
            }
          }
        }
      }
    }
  }

  // 开始编辑
  const handleCellClick = (rowIndex: number, colIndex: number, cellText: string) => {
    setEditingCell({ row: rowIndex, col: colIndex });
    setEditValue(cellText);
  };

  // 完成编辑
  const handleEditComplete = (rowIndex: number, colIndex: number) => {
    if (editingCell && (editValue !== sheet.data[rowIndex][colIndex].text)) {
      onCellEdit(rowIndex, colIndex, editValue);
    }
    setEditingCell(null);
    setEditValue('');
  };

  // 取消编辑
  const handleEditCancel = () => {
    setEditingCell(null);
    setEditValue('');
  };

  // 处理键盘事件
  const handleKeyDown = (e: React.KeyboardEvent, rowIndex: number, colIndex: number) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleEditComplete(rowIndex, colIndex);
    } else if (e.key === 'Escape') {
      handleEditCancel();
    }
  };

  return (
    <div className="table-renderer">
      <table className="excel-table">
        <tbody>
          {renderGrid.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {row.map((cellInfo, colIndex) => {
                if (!cellInfo || cellInfo.skip) {
                  return null;
                }
                
                const { cell } = cellInfo;
                const isEditing = editingCell?.row === rowIndex && editingCell?.col === colIndex;
                const className = `excel-cell ${cell.is_header ? 'header' : ''} ${isEditing ? 'editing' : ''}`;
                
                return (
                  <td
                    key={colIndex}
                    className={className}
                    rowSpan={cell.rowspan}
                    colSpan={cell.colspan}
                    onDoubleClick={() => !isEditing && handleCellClick(rowIndex, colIndex, cell.text)}
                  >
                    {isEditing ? (
                      <input
                        type="text"
                        className="cell-edit-input"
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        onBlur={() => handleEditComplete(rowIndex, colIndex)}
                        onKeyDown={(e) => handleKeyDown(e, rowIndex, colIndex)}
                        autoFocus
                      />
                    ) : (
                      <span className="cell-content">{cell.text}</span>
                    )}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
