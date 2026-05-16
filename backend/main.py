from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pathlib import Path
from datetime import datetime
import os
import shutil

from app.core.config import settings
from app.core.database import engine, Base, get_db
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
from app.api.upload import router as upload_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时创建数据库表
    Base.metadata.create_all(bind=engine)

    # 自动迁移：为已有表补充新字段
    from sqlalchemy import text, inspect
    with engine.connect() as conn:
        inspector = inspect(engine)
        if 'users' in inspector.get_table_names():
            columns = [c['name'] for c in inspector.get_columns('users')]
            if 'token_version' not in columns:
                conn.execute(text('ALTER TABLE users ADD COLUMN token_version INTEGER DEFAULT 0'))
                conn.commit()
            if 'auth_source' not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN auth_source VARCHAR(10) DEFAULT 'local'"))
                conn.commit()
            # 兼容：如果 inspector 缓存导致遗漏，用 try/except 兜底
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN auth_source VARCHAR(10) DEFAULT 'local'"))
                conn.commit()
            except Exception:
                pass

    # 创建初始管理员账号（如果不存在）
    from app.core.database import SessionLocal
    from app.models.user import User, UserRole
    from app.core.security import get_password_hash
    from datetime import timedelta
    import shutil

    db = SessionLocal()
    try:
        # 清理 24 小时前的未完成上传会话
        from app.models.upload import UploadSession
        cutoff = datetime.utcnow() - timedelta(hours=24)
        stale = db.query(UploadSession).filter(
            UploadSession.status.in_(["pending", "uploading"]),
            UploadSession.created_at < cutoff
        ).all()
        for s in stale:
            shutil.rmtree(s.temp_dir, ignore_errors=True)
            s.status = "cancelled"
        if stale:
            db.commit()
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
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
app.include_router(upload_router, prefix="/api")
app.include_router(category_router, prefix="/api")


# 公开的站点信息接口（无需认证）
@app.get("/api/site/info")
async def site_info(db=Depends(get_db)):
    """获取站点名称和描述（公开接口）"""
    from app.models.config import Config
    from sqlalchemy.orm import Session as _Session
    name_cfg = db.query(Config).filter(Config.key == "site_name").first()
    desc_cfg = db.query(Config).filter(Config.key == "site_description").first()
    return {
        "name": name_cfg.value if name_cfg else settings.APP_NAME,
        "description": desc_cfg.value if desc_cfg else "公司内网软件下载站"
    }


# 挂载前端静态文件（Docker 部署时使用）
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="static-assets")

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    @app.get("/api")
    async def api_root():
        return {"message": "Software Guard API"}

    @app.get("/{full_path:path}")
    async def serve_frontend(request: Request, full_path: str):
        file_path = (Path(STATIC_DIR) / full_path).resolve()
        static_resolved = Path(STATIC_DIR).resolve()
        if not str(file_path).startswith(str(static_resolved) + os.sep) and file_path != static_resolved:
            return FileResponse(os.path.join(STATIC_DIR, "index.html"))
        if file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))
else:
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