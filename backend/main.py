from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.core.database import engine, Base
from app.api import (
    auth_router,
    software_router,
    request_router,
    download_router,
    vulnerability_router,
    user_router,
    category_router
)
from app.api.stats import router as stats_router
from app.api.config import router as config_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时创建数据库表
    Base.metadata.create_all(bind=engine)

    # 创建初始管理员账号（如果不存在）
    from app.core.database import SessionLocal
    from app.models.user import User, UserRole
    from app.core.security import get_password_hash

    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == settings.FIRST_ADMIN_USERNAME).first()
        if not admin:
            admin = User(
                username=settings.FIRST_ADMIN_USERNAME,
                hashed_password=get_password_hash(settings.FIRST_ADMIN_PASSWORD),
                email=settings.FIRST_ADMIN_EMAIL,
                role=UserRole.ADMIN
            )
            db.add(admin)
            db.commit()
            print(f"初始管理员账号已创建: {settings.FIRST_ADMIN_USERNAME}")
    finally:
        db.close()

    # 确保存储目录存在
    os.makedirs(settings.STORAGE_PATH, exist_ok=True)

    yield

    # 关闭时的清理工作
    pass


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（开发环境）
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router, prefix="/api")
app.include_router(software_router, prefix="/api")
app.include_router(request_router, prefix="/api")
app.include_router(download_router, prefix="/api")
app.include_router(vulnerability_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(stats_router, prefix="/api")
app.include_router(config_router, prefix="/api")
app.include_router(category_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}