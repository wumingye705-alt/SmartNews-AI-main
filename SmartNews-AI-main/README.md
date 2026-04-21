# SmartNews-AI

## 项目简介

SmartNews-AI 是一个集新闻浏览、分类查看、AI 聊天、用户管理于一体的全栈应用。采用 FastAPI 构建后端 API，Vue.js 实现前端交互，为用户提供智能、高效的新闻获取与管理服务。

## 功能特性

### 核心功能
- 📰 **新闻浏览**：首页推荐、分类筛选、详情查看
- 🤖 **AI 聊天**：集成智能对话功能，提供新闻相关问答
- 🔐 **用户系统**：注册、登录、个人中心管理
- 💾 **个性化管理**：收藏夹、浏览历史记录
- 👤 **用户资料**：头像上传、个人信息编辑

### 技术亮点
- 前后端分离架构，响应式设计
- FastAPI 异步处理，高性能后端
- Vue.js 3 + Vite 构建现代化前端
- redis高速缓存，降低网络延迟
- JWT 令牌认证，安全的用户登录
- 模块化代码结构，易于扩展

## 技术栈

### 后端
- **框架**：FastAPI
- **语言**：Python 3.12+
- **数据库**：MySQL，redis
- **认证**：JWT
- **依赖管理**：pip

### 前端
- **框架**：Vue.js 3
- **构建工具**：Vite
- **状态管理**：Pinia
- **路由**：Vue Router
- **HTTP 客户端**：Axios
- **样式**：CSS3

## 项目结构

```
SmartNews-AI/
├── AiNewsFront/           # 前端项目
│   ├── public/            # 静态资源
│   ├── src/               # 源码目录
│   │   ├── assets/        # 图片、样式等资源
│   │   ├── components/    # 通用组件
│   │   ├── config/        # 配置文件
│   │   ├── router/        # 路由配置
│   │   ├── store/         # 状态管理
│   │   ├── views/         # 页面组件
│   │   ├── App.vue        # 根组件
│   │   └── main.js        # 入口文件
│   ├── package.json       # 依赖配置
│   └── vite.config.js     # Vite 配置
├── AiNewsProject/         # 后端项目
│   ├── avatar/            # 用户头像上传目录
│   ├── config/            # 配置文件
|   ├── cache/			   # redis缓存类与装饰器
│   ├── crud/              # 数据库操作
│   ├── dependence/        # 依赖工具
│   ├── models/            # 数据模型
│   ├── routers/           # API 路由
│   ├── schemas/           # 数据校验
│   ├── utils/             # 工具函数
│   ├── main.py            # 后端入口
└── README.md              # 项目说明
```

## 快速开始

### 环境要求
- **Python**：3.12 或更高版本
- **Node.js**：16.0 或更高版本
- **MySQL**：5.7 或更高版本
- **redis**：5.0 或更高版本

### 安装步骤

#### 1. 克隆仓库
```bash
git clone https://github.com/RMA-MUN/SmartNews-AI.git
cd SmartNews-AI
```

#### 2. 后端安装
```bash
# 进入后端目录
cd AiNewsProject

# 创建虚拟环境（可选）
python -m venv venv
# 激活虚拟环境
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
# 在后端根目录创建.env文件并完成配置
# 如
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=news_app
MYSQL_USER=root
MYSQL_PASSWORD=root

# 修改redis配置(配置文件位于config/redis_config.py里)
# 根据需求，自行修改

# JWT配置
JWT_SECRET_KEY=your-strong-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080

# 启动后端服务
uvicorn main:app --reload

# 添加新闻数据
# 可以自行往新闻表里添加一些数据
```

#### 3. 前端安装
```bash
# 进入前端目录
cd ../AiNewsFront

# 安装依赖
npm install

# 配置环境变量
# 复制 .env.example 为 .env 并修改 API 地址

# 开发模式启动
npm run dev

# 构建生产版本
npm run build
```

### 4. 访问应用
- **前端**：默认地址 `http://localhost:3000`
- **后端 API 文档**：`http://localhost:8000/docs`

## 环境变量配置

### 后端 (.env)
```env
# 数据库配置
DATABASE_URL="mysql+pymysql://username:password@localhost:3306/news_app"

# JWT 密钥
SECRET_KEY="your-secret-key-here"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 应用配置
APP_NAME="SmartNews-AI"
DEBUG=True
```

### 前端 (.env)
```env
# API 基础地址
VITE_API_BASE_URL="http://localhost:8000/api"

# 应用配置
VITE_APP_NAME="SmartNews-AI"
```

## API 文档

后端提供自动生成的 API 文档：
- **Swagger UI**：`http://localhost:8000/docs`
- **ReDoc**：`http://localhost:8000/redoc`

