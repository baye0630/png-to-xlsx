# OCR PNG to Excel - 后端服务

基于 FastAPI + Tortoise ORM 的后端服务。

## 技术栈

- **Web 框架**: FastAPI 0.109.0
- **Web 服务器**: Uvicorn 0.27.0
- **ORM**: Tortoise ORM 0.20.0
- **数据库**: SQLite (开发环境) / MySQL (生产环境)
- **HTTP 客户端**: httpx 0.26.0
- **Excel 处理**: openpyxl 3.1.2, pandas 2.2.0

## 项目结构

```
backend/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── core/                # 核心配置模块
│   │   ├── config.py        # 应用配置
│   │   ├── database.py      # 数据库配置
│   │   └── logging.py       # 日志配置
│   └── models/              # 数据模型
│       └── task.py          # 任务模型
├── requirements.txt         # Python 依赖
├── .env                     # 环境配置（不提交到 Git）
└── .env.example             # 环境配置示例

```

## 快速开始

### 1. 环境准备

确保已安装 Python 3.11：

```bash
python3.11 --version
```

### 2. 创建虚拟环境（如未创建）

在项目根目录：

```bash
python3.11 -m venv venv
```

### 3. 安装依赖

```bash
./venv/bin/pip install -r backend/requirements.txt
```

### 4. 配置环境变量

复制并编辑配置文件：

```bash
cp backend/.env.example backend/.env
# 根据需要修改配置
```

主要配置项：

- `DB_TYPE`: 数据库类型（sqlite 或 mysql，默认 sqlite）
- `DB_PASSWORD`: MySQL 密码（使用 MySQL 时需要）
- `OCR_BASE_URL`: OCR 服务地址
- `OCR_TOKEN`: OCR 服务认证令牌

### 5. 启动服务

**方式一：使用启动脚本（推荐）**

```bash
./scripts/start_backend.sh
```

**方式二：手动启动**

```bash
cd backend
PYTHONPATH=../backend:$PYTHONPATH ../venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 6. 验证服务

服务启动后，访问以下地址：

- **根路径**: http://localhost:8000/
- **Health 检查**: http://localhost:8000/health
- **API 文档**: http://localhost:8000/docs
- **ReDoc 文档**: http://localhost:8000/redoc

## 数据库配置

### 开发环境（SQLite）

默认配置，无需额外设置。数据库文件位于 `data/ocr_pngtoexcel.db`。

### 生产环境（MySQL）

1. 创建数据库：

```sql
CREATE DATABASE ocr_pngtoexcel CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 修改 `.env` 配置：

```env
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=ocr_pngtoexcel
```

## 数据模型

### Task 模型

任务是系统的核心实体，对应一次完整的图片识别与编辑导出流程。

字段说明：

- `task_id`: UUID，主键
- `image_path`: 上传图片的存储路径
- `ocr_json_path`: OCR 原始 JSON 结果路径
- `excel_path`: 当前最新 Excel 文件路径
- `ocr_job_id`: 外部 OCR 服务的任务 ID
- `status`: 任务状态（uploaded / ocr_processing / ocr_done / excel_generated / editable 等）
- `error_message`: 错误信息
- `created_at`: 创建时间
- `updated_at`: 更新时间

## 开发说明

### 添加新的 API 路由

在 `app/api/v1/` 目录下创建新文件，然后在 `app/main.py` 中注册路由。

### 数据库迁移

使用 Aerich 进行数据库迁移：

```bash
# 初始化迁移（首次）
aerich init -t app.core.database.TORTOISE_ORM

# 生成迁移文件
aerich migrate

# 执行迁移
aerich upgrade
```

### 日志

日志文件位于 `backend/logs/app.log`，同时也会输出到控制台。

## Step 1 验收结果

✅ **后端基础工程初始化完成**

- [x] FastAPI 工程可启动
- [x] Health 接口可用（`/health`）
- [x] 数据库连接正常
- [x] 数据目录自动创建
- [x] 任务模型（Task）已定义并创建表结构

验收命令：

```bash
# 测试根路径
curl http://localhost:8000/

# 测试 Health 接口
curl http://localhost:8000/health

# 验证数据库表
sqlite3 ../data/ocr_pngtoexcel.db "PRAGMA table_info(tasks);"
```

## 下一步

参考 `docs/04_tasks/roadmap.md` 中的 **Step 2：任务模型与状态体系**。
