# 🐦 鸟类识别系统 (Bird Recognition System)

基于 YOLOv8 深度学习模型的智能鸟类图像识别系统，提供鸟类识别、鸟类百科、识别历史管理等功能。

## 📖 项目简介

本项目是一个前后端分离的鸟类识别 Web 应用，用户可以上传鸟类图片进行智能识别，系统会自动检测图片中的鸟类并返回识别结果。主要功能包括：

- **鸟类识别**：上传图片，系统自动识别图片中的鸟类种类，并在图片上标注检测框
- **鸟类百科**：浏览和查询鸟类信息，了解各种鸟类的详细介绍
- **识别历史**：查看历史识别记录，方便回顾和管理
- **用户系统**：支持用户注册、登录，管理个人识别记录
- **管理后台**：管理员可管理用户、鸟类信息、数据集，以及训练模型

## 🛠️ 技术栈

### 后端
| 技术 | 说明 |
|------|------|
| Python 3.11+ | 编程语言 |
| FastAPI | 高性能 Web 框架 |
| SQLAlchemy 2.0 | ORM 数据库框架 |
| MySQL | 关系型数据库 |
| Redis | 缓存数据库 |
| YOLOv8 | 目标检测模型 |
| JWT | 用户认证 |
| Uvicorn | ASGI 服务器 |

### 前端
| 技术 | 说明 |
|------|------|
| Vue 3 | 前端框架 |
| Vite 5 | 构建工具 |
| Vue Router 4 | 路由管理 |
| Pinia | 状态管理 |
| Element Plus | UI 组件库 |
| Axios | HTTP 请求库 |
| ECharts | 数据可视化 |

## 📁 项目结构

```
Bird Recognition System/
├── bird-recognition-system-backend/    # 后端项目
│   ├── models/                         # 数据模型
│   ├── routers/                        # API 路由
│   ├── schemas/                        # 数据验证模式
│   ├── services/                       # 业务逻辑层
│   ├── yolo/                           # YOLO 模型相关
│   ├── config.py                       # 配置文件
│   ├── database.py                     # 数据库连接
│   ├── main.py                         # 应用入口
│   └── requirements.txt                # Python 依赖
│
└── bird-recognitionsystem-frontend/    # 前端项目
    ├── src/
    │   ├── api/                        # API 接口
    │   ├── components/                 # 公共组件
    │   ├── router/                     # 路由配置
    │   ├── stores/                     # 状态管理
    │   ├── utils/                      # 工具函数
    │   ├── views/                      # 页面视图
    │   ├── App.vue                     # 根组件
    │   └── main.js                     # 入口文件
    ├── index.html
    ├── package.json
    └── vite.config.js
```

## 🚀 安装指南

### 环境要求

- Python 3.11 或更高版本
- Node.js 18 或更高版本
- MySQL 8.0 或更高版本
- Redis 5.0 或更高版本（可选，用于缓存）

### 1. 克隆项目

```bash
git clone <repository-url>
cd "Bird Recognition System"
```

### 2. 后端安装

```bash
# 进入后端目录
cd bird-recognition-system-backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装 YOLOv8，如需真实识别功能
pip install ultralytics
```

### 3. 前端安装

```bash
# 进入前端目录
cd bird-recognitionsystem-frontend

# 安装依赖
npm install
```

### 4. 数据库配置

1. 创建 MySQL 数据库：

```sql
CREATE DATABASE bird_recognition CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 配置环境变量（可选）：

创建 `.env` 文件或设置系统环境变量：

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=bird_recognition

REDIS_HOST=localhost
REDIS_PORT=6379

JWT_SECRET_KEY=your-secret-key
```

> 如不设置环境变量，将使用 `config.py` 中的默认配置。

## 📖 使用说明

### 启动后端服务

```bash
cd bird-recognition-system-backend

# 激活虚拟环境
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 启动服务
python main.py
# 或使用 uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

后端服务启动后：
- API 地址：http://localhost:8000
- API 文档：http://localhost:8000/docs
- ReDoc 文档：http://localhost:8000/redoc

### 启动前端服务

```bash
cd bird-recognitionsystem-frontend

# 开发模式启动
npm run dev
```

前端服务启动后访问：http://localhost:5173

### 生产构建

```bash
# 前端构建
cd bird-recognitionsystem-frontend
npm run build
```

构建产物位于 `dist/` 目录。

## 🔧 功能使用

### 用户功能

1. **注册/登录**：访问首页，点击注册创建账号，或使用已有账号登录
2. **鸟类识别**：登录后进入"鸟类识别"页面，上传鸟类图片进行识别
3. **查看结果**：识别完成后查看标注图片和识别到的鸟类信息
4. **鸟类百科**：浏览"鸟类百科"页面，了解各种鸟类详情
5. **识别历史**：在"识别历史"页面查看历史识别记录

### 管理员功能

管理员账号可访问后台管理系统：

- **仪表盘**：查看系统统计数据
- **用户管理**：管理系统用户
- **鸟类管理**：增删改查鸟类信息
- **数据集管理**：管理训练数据集，训练和更新识别模型

## 🌐 API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/auth/register` | POST | 用户注册 |
| `/api/auth/login` | POST | 用户登录 |
| `/api/recognize` | POST | 图片识别 |
| `/api/birds` | GET | 获取鸟类列表 |
| `/api/birds/{id}` | GET | 获取鸟类详情 |
| `/api/records` | GET | 获取识别记录 |
| `/api/admin/stats` | GET | 获取统计数据 |

完整 API 文档请访问：http://localhost:8000/docs

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m 'Add some feature'`
4. 推送分支：`git push origin feature/your-feature`
5. 提交 Pull Request

### 代码规范

- 后端代码遵循 PEP 8 规范
- 前端代码使用 ESLint 进行检查
- 提交信息请使用清晰的描述

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

## 📞 联系方式

如有问题或建议，欢迎提交 Issue 或 Pull Request。

---

**感谢使用鸟类识别系统！** 🐦
