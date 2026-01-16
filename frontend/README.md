# 前端工程

OCR PNG to Excel 的前端项目，基于 React + TypeScript + Vite 构建。

## 技术栈

- **React 19.2.0** - UI 框架
- **TypeScript 5.9.3** - 类型系统
- **Vite 7.2.4** - 构建工具
- **CSS3** - 样式

## 项目结构

```
frontend/
├── src/
│   ├── components/         # 组件
│   │   ├── UploadArea/    # 上传区域组件
│   │   └── ExcelArea/     # Excel 编辑区域组件
│   ├── services/          # API 服务
│   ├── types/             # TypeScript 类型定义
│   ├── App.tsx            # 主应用组件
│   ├── App.css            # 主应用样式
│   ├── main.tsx           # 入口文件
│   └── index.css          # 全局样式
├── public/                # 静态资源
├── package.json           # 依赖配置
├── vite.config.ts         # Vite 配置
└── tsconfig.json          # TypeScript 配置
```

## 开发指南

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

服务启动后，访问：http://localhost:3000

### 构建生产版本

```bash
npm run build
```

### 预览生产构建

```bash
npm run preview
```

## 配置说明

### Vite 配置

- **端口**: 3000
- **代理**: `/api` 路径代理到后端 `http://localhost:8000`

### API 集成

前端通过 `/api/v1` 前缀调用后端接口，Vite 会自动代理到后端服务。

## 组件说明

### UploadArea（上传区域）

**功能**：
- 拖拽上传图片
- 选择文件上传
- 显示文件信息
- 触发 OCR 识别

**Props**：
- `onUploadSuccess?: (taskId: string) => void` - 上传成功回调

### ExcelArea（Excel 编辑区域）

**功能**：
- 显示表格数据
- 多 Sheet 切换
- 表格编辑（Step 11 实现）
- 下载 Excel

**Props**：
- `taskId?: string` - 任务 ID

## 开发进度

### ✅ Step 8 - 前端基础工程初始化（已完成）

- [x] React + TypeScript + Vite 工程搭建
- [x] 基础页面布局
- [x] UploadArea 组件骨架
- [x] ExcelArea 组件骨架
- [x] 基础样式和 UI

### 🚧 Step 9 - 前端上传 + 状态展示（待开发）

- [ ] 实现文件上传逻辑
- [ ] OCR 状态实时展示
- [ ] 错误处理和提示

### 🚧 Step 10 - 前端表格预览（待开发）

- [ ] 表格数据渲染
- [ ] 多 Sheet 切换
- [ ] 表格样式优化

### 🚧 Step 11 - 前端编辑 + 保存（待开发）

- [ ] 表格单元格编辑
- [ ] 数据保存
- [ ] Excel 下载

## 样式设计

### 配色方案

- **主色**: `#1890ff` (蓝色)
- **成功色**: `#52c41a` (绿色)
- **警告色**: `#faad14` (橙色)
- **错误色**: `#ff4d4f` (红色)
- **背景色**: `#f0f2f5` (浅灰)

### 布局特点

- 响应式设计
- 卡片式布局
- 渐变色头部
- 清晰的视觉层次

## 注意事项

1. **开发前确保后端服务已启动**
   ```bash
   cd backend
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

2. **端口占用**
   - 前端默认端口：3000
   - 后端默认端口：8000

3. **API 调用**
   - 使用 `/api/v1` 前缀
   - Vite 自动代理到后端

## 常见问题

### Q: 启动失败，端口被占用？

A: 修改 `vite.config.ts` 中的 `server.port` 配置。

### Q: API 请求失败？

A: 检查后端服务是否启动，确认端口是 8000。

### Q: 样式不生效？

A: 检查 CSS 文件是否正确导入。

## License

MIT
