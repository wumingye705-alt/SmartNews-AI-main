from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles  # 导入静态文件服务
from fastapi.security import HTTPBearer
from starlette.middleware.cors import CORSMiddleware

from config.redis_config import redis_client
from utils.exception_handlers import register_exception_handlers
from dotenv import load_dotenv

# 首先加载.env文件
load_dotenv()

# 然后再导入可能使用环境变量的模块
from routers import favorite, news, users, history
from config.db_config import init_db  # 导入初始化函数

# 创建Bearer令牌安全方案
bearer_scheme = HTTPBearer()

app = FastAPI(
    title="AI News API",
    description="AI News API Documentation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 配置静态文件服务
app.mount("/avatar", StaticFiles(directory="avatar"), name="avatar")

# 在应用启动时初始化数据库
@app.on_event("startup")
async def startup_event():
    await init_db()

# 在应用启动时测试
@app.on_event("startup")
async def test_redis_connection():
    try:
        await redis_client.ping()
        print("Redis 连接成功")
    except Exception as e:
        print(f"Redis 连接失败: {e}")

app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)
app.include_router(history.router)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 允许访问的源
    allow_credentials=True, # 允许携带cookie
    allow_methods=["*"], # 允许的请求方法
    allow_headers=["*"], # 允许的请求头
)

register_exception_handlers(app)


@app.get("/")
async def root():
    return {"message": "Hello World"}