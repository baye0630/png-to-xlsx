# PaddleOCR 表格识别服务（接口与调用流程）

> 本文档用于说明**外部 OCR 服务**的调用方式。本项目的主链路使用 **OCR JSON** 作为中间格式：  
> **图片表格 OCR → JSON → Excel → 在线编辑 → 下载**

## 1. 基本信息

- **Base URL**：`http://10.119.133.236:8806`
- **鉴权**：`Authorization: Bearer <TOKEN>`

## 2. 接口一览（外部 OCR 服务）

| 类型 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/health` | 健康检查：队列长度、worker 状态等 |
| POST | `/jobs-from-uploading` | 上传图片并创建识别任务，返回 `job_id` |
| GET | `/longpoll/jobs/{job_id}?since_seq=0&timeout_ms=25000&max_events=50` | 长轮询获取任务事件流（queued/running/finished/failed） |
| GET | `/result/json/jobs/{job_id}` | 获取 OCR **JSON 结果**（本项目主要使用） |
| GET | `/result/markdown/jobs/{job_id}` | 获取 Markdown/HTML 片段（可选） |
| GET | `/result/images/jobs/{job_id}` | 获取输出图片 zip（可选） |

## 3. 推荐调用流程（本项目使用）

1. **健康检查**（可选）
2. **上传图片创建任务** → 得到 `job_id`
3. **长轮询任务状态**，直到 `done=true` 或出现失败事件
4. **拉取 OCR JSON**：`/result/json/jobs/{job_id}`
5. **后端处理**：将 OCR JSON 归一化为前端表格 JSON，并生成 Excel（保存/下载时）

## 4. 最小可复制示例（curl）

### 4.1 健康检查

```bash
curl -s "http://10.119.133.236:8806/health"
```

### 4.2 上传图片创建任务（返回 job_id）

```bash
TOKEN="<YOUR_TOKEN>"
curl -X POST "http://10.119.133.236:8806/jobs-from-uploading" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/abs/path/to/your-image.jpg"
```

### 4.3 长轮询任务事件（直到 done=true）

```bash
TOKEN="<YOUR_TOKEN>"
ID="<JOB_ID>"
SINCE=0
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://10.119.133.236:8806/longpoll/jobs/$ID?since_seq=$SINCE&timeout_ms=25000&max_events=50"
```

### 4.4 获取 OCR JSON（核心）

```bash
TOKEN="<YOUR_TOKEN>"
ID="<JOB_ID>"
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://10.119.133.236:8806/result/json/jobs/$ID"
```

## 5. 返回数据关键字段（便于后端对接）

### 5.1 longpoll（事件流）

- **`events[]`**：事件列表（有序），常见 `type`：
  - `queued`：进入队列
  - `running`：处理中（可含 page 进度）
  - `finished`：处理完成
  - `failed`：处理失败（通常在 payload 或后续 final 中有错误信息）
- **`last_seq`**：本次返回的最后事件序号（下次可用作 `since_seq`）
- **`done`**：是否已完成（完成/失败均可能为 true）

### 5.2 result/json（OCR JSON）

- **`job_id`**：任务 id
- **`final.status`**：任务最终状态（如 `finished`）
- **`final.error_message`**：错误信息（失败时关注）
- **`pages[]`**：分页结果（通常图片为 1 页）
- **`pages[].parsing_res_list[]`**：识别到的结构块列表
  - 常见 `block_label`：`table`（表格块）
  - `block_content`：表格内容（可能为 HTML table 等结构化文本）
  - `block_bbox`：在原图中的位置（用于定位/调试）

## 6. 本项目对接约定（建议）

- **优先使用**：`/result/json/jobs/{job_id}` 作为后续“JSON→Excel”的数据来源。
- **可选能力**：
  - `/result/markdown/...`：用于展示/对照（不作为主链路依赖）
  - `/result/images/...`：用于调试/可视化定位

<details>
<summary>历史 demo 输出（可折叠）</summary>

历史 demo 属于一次性验证材料，默认不纳入主文档正文。若后续需要，可从版本历史中恢复或在此补充更短的“最小可复制示例”。

</details>

