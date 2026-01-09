from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from ..core.database import Base


class UserRole(str, PyEnum):
    """用户角色枚举"""
    ADMIN = "admin"       # 管理员
    OPS = "ops"           # 运维人员
    USER = "user"         # 普通用户


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, index=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))

    # 关系
    uploaded_software = relationship("Software", back_populates="creator")
    uploaded_versions = relationship("SoftwareVersion", back_populates="uploader")
    requests = relationship("SoftwareRequest", foreign_keys="SoftwareRequest.applicant_id", back_populates="applicant")
    reviewed_requests = relationship("SoftwareRequest", foreign_keys="SoftwareRequest.reviewer_id", back_populates="reviewer")
    download_logs = relationship("DownloadLog", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
