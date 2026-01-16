/**
 * 表格渲染组件
 * 支持合并单元格
 */
import type { TableSheet, CellData } from '../../types';
import './TableRenderer.css';

interface TableRendererProps {
  sheet: TableSheet;
}

export default function TableRenderer({ sheet }: TableRendererProps) {
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
            if (dr === 0 && dc === 0) continue; // 跳过主单元格本身
            if (r + dr < sheet.rows && c + dc < sheet.cols) {
              renderGrid[r + dr][c + dc] = { cell, skip: true };
            }
          }
        }
      }
    }
  }

  return (
    <div className="table-renderer">
      <table className="excel-table">
        <tbody>
          {renderGrid.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {row.map((cellInfo, colIndex) => {
                if (!cellInfo || cellInfo.skip) {
                  return null; // 跳过被合并的单元格
                }
                
                const { cell } = cellInfo;
                const className = `excel-cell ${cell.is_header ? 'header' : ''}`;
                
                return (
                  <td
                    key={colIndex}
                    className={className}
                    rowSpan={cell.rowspan}
                    colSpan={cell.colspan}
                  >
                    {cell.text}
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
