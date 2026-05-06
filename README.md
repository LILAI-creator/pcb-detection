# PCB 缺陷检测系统

基于 YOLOv8 的 Web 端 PCB 板缺陷检测系统，支持上传 PCB 图像进行实时缺陷检测与可视化。

## 项目结构

```
pcb-detector/
├── frontend/                — 前端（HTML + CSS + JS）
│   ├── index.html           — 检测页
│   ├── history.html         — 历史记录页
│   ├── stats.html           — 统计面板页
│   ├── css/style.css        — 全局样式
│   └── js/                  — 前端逻辑
│       ├── api.js           — API 请求封装
│       ├── upload.js        — 上传逻辑
│       ├── canvas.js        — Canvas 标注绘制
│       └── detect.js        — 检测交互
├── backend/                 — 后端（FastAPI）
│   ├── app/
│   │   ├── main.py          — 应用入口
│   │   ├── config.py        — 配置文件
│   │   ├── api/             — API 路由
│   │   ├── models/          — 数据模型
│   │   └── services/        — 业务逻辑
│   │       ├── detector.py  — YOLOv8 推理服务
│   │       └── storage.py   — 文件存储与历史管理
│   ├── weights/             — 模型权重文件目录
│   ├── uploads/             — 上传图像存储
│   ├── results/             — 检测结果图像存储
│   └── requirements.txt     — Python 依赖
└── PRD-WebPCBDefectDetection-202605062145.md
```

## 环境依赖

### 系统要求

| 项目 | 要求 |
|------|------|
| 操作系统 | Windows / Linux / macOS |
| Python | 3.9+ |
| Conda | Miniconda 或 Anaconda |
| GPU（可选） | CUDA 11.8+，用于推理加速 |

### Python 依赖

| 包名 | 版本 | 说明 |
|------|------|------|
| fastapi | 0.115.0 | Web 框架 |
| uvicorn | 0.30.6 | ASGI 服务器 |
| python-multipart | 0.0.9 | 文件上传支持 |
| pydantic | 2.9.2 | 数据校验 |
| numpy | 1.26.4 | 数值计算 |
| opencv-python-headless | 4.10.0.84 | 图像处理 |
| ultralytics | 8.3.0 | YOLOv8 推理框架 |

### Conda 环境配置

项目在 `yolo` 环境下开发运行：

```bash
# 创建 conda 环境（如尚未创建）
conda create -n yolo python=3.9 -y

# 激活环境
conda activate yolo
```

## 部署步骤

### 1. 克隆项目

```bash
cd /path/to/workspace
# 项目目录为 challenge/
```

### 2. 激活 Conda 环境

```bash
conda activate yolo
```

### 3. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

如需 GPU 推理加速，额外安装 CUDA 版 PyTorch：

```bash
# CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### 4. 放置 YOLOv8 模型

将训练好的 YOLOv8 模型权重文件放入 `backend/weights/` 目录：

```bash
cp /path/to/your/best.pt backend/weights/best.pt
```

默认加载 `weights/best.pt`，可通过环境变量指定：

```bash
export PCB_MODEL_NAME=your_model.pt
```

> 如果未放置模型文件，系统将以 **Mock 模式** 启动，返回模拟检测结果，用于前端调试。

### 5. 配置（可选）

通过环境变量调整配置：

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `PCB_MODEL_NAME` | `best.pt` | 模型权重文件名 |
| `PCB_CONF_THRESHOLD` | `0.25` | 置信度阈值 |
| `PCB_IOU_THRESHOLD` | `0.45` | IOU 阈值 |
| `PCB_HOST` | `0.0.0.0` | 服务监听地址 |
| `PCB_PORT` | `8000` | 服务监听端口 |
| `PCB_CORS_ORIGINS` | `*` | CORS 允许的源 |

## 运行指南

### 启动服务

```bash
conda activate yolo
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

启动成功后终端输出：

```
INFO:     Loading YOLOv8 model...
INFO:     YOLOv8 model loaded from: .../weights/best.pt
INFO:     Uvicorn running on http://0.0.0.0:8000
```

或（Mock 模式）：

```
WARNING:  No model loaded - running in mock mode
```

### 访问页面

| 页面 | 地址 | 说明 |
|------|------|------|
| 检测页 | http://localhost:8000/ | 上传图像、执行检测、查看结果 |
| 历史记录 | http://localhost:8000/history.html | 查看检测历史、筛选、详情 |
| 统计面板 | http://localhost:8000/stats.html | 缺陷分布、趋势图表 |
| API 文档 | http://localhost:8000/docs | Swagger UI 接口文档 |

### 使用流程

1. 打开检测页，点击或拖拽上传 PCB 板图像（JPG/PNG/BMP，最大 20MB）
2. 上传后原图立即显示，系统自动执行检测
3. 检测完成后，图像上叠加缺陷边界框和标签
4. 右侧缺陷列表展示每个缺陷的类别、置信度、坐标
5. 鼠标悬停列表项，对应边界框高亮
6. 支持鼠标滚轮缩放、拖拽平移查看细节
7. 可导出标注后图像（PNG）或检测结果（JSON）

### API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/detect` | 上传图像并执行检测 |
| GET | `/api/history` | 获取检测历史（支持分页、筛选） |
| GET | `/api/history/{id}` | 获取单条检测记录详情 |
| GET | `/api/stats` | 获取统计数据 |
| GET | `/api/stats/trend` | 获取趋势数据 |
| GET | `/api/defect-classes` | 获取缺陷类别列表 |

### 检测结果示例

```json
{
  "id": "a1b2c3d4",
  "image_url": "/uploads/xxx.jpg",
  "result_image_url": "/results/yyy.jpg",
  "timestamp": "2026-05-06T22:42:38.123456",
  "defects": [
    {
      "class": "short",
      "confidence": 0.80,
      "bbox": { "x": 981, "y": 1287, "width": 49, "height": 48 }
    }
  ]
}
```

### 缺陷类别

| 编号 | 类名 | 中文 |
|------|------|------|
| 0 | missing_hole | 缺孔 |
| 1 | mouse_bite | 鼠咬 |
| 2 | open_circuit | 断路 |
| 3 | short | 短路 |
| 4 | spur | 毛刺 |
| 5 | spurious_copper | 杂铜 |

## 常见问题

**Q: 启动时报 `ModuleNotFoundError: No module named 'ultralytics'`**

确保已激活正确的 conda 环境并安装依赖：
```bash
conda activate yolo
pip install -r requirements.txt
```

**Q: 启动后显示 `No model loaded - running in mock mode`**

模型文件未找到，将 `.pt` 权重文件放入 `backend/weights/` 目录后重启服务。

**Q: 检测速度慢**

- CPU 推理较慢，建议安装 CUDA 版 PyTorch 使用 GPU 加速
- 单图 GPU 推理通常 < 1s，CPU 推理约 3-5s

**Q: 前端页面样式丢失**

确保通过后端访问（`http://localhost:8000/`），不要直接用文件协议打开 HTML。
