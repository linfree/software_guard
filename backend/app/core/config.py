from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "Software Guard"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 数据库配置
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/software_guard"

    # JWT 配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # 文件存储配置
    STORAGE_PATH: str = "storage"
    MAX_UPLOAD_SIZE: int = 1024 * 1024 * 1024  # 1GB
    # 移除文件类型限制，允许所有文件类型
    # ALLOWED_EXTENSIONS: set = {".exe", ".msi", ".zip", ".rar", ".7z", ".dmg", ".pkg", ".deb", ".rpm"}

    # 首次运行创建管理员账号
    FIRST_ADMIN_USERNAME: str = "admin"
    FIRST_ADMIN_PASSWORD: str = "admin123"
    FIRST_ADMIN_EMAIL: str = "admin@company.com"

    class Config:
        env_file = ".env"


settings = Settings()