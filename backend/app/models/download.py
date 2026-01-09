from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class DownloadLog(Base):
    """下载记录模型"""
    __tablename__ = "download_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    software_version_id = Column(Integer, ForeignKey("software_versions.id"), nullable=False)
    download_time = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(45))  # IPv6 support

    # 关系
    user = relationship("User", back_populates="download_logs")
    software_version = relationship("SoftwareVersion", back_populates="download_logs")
