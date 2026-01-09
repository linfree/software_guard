from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class Software(Base):
    """软件模型"""
    __tablename__ = "software"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text)
    category = Column(String(50), index=True)
    icon_url = Column(String(255))
    logo = Column(String(255))
    official_url = Column(String(255))
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    creator = relationship("User", foreign_keys=[created_by], back_populates="uploaded_software")
    versions = relationship("SoftwareVersion", back_populates="software", cascade="all, delete-orphan")
    requests = relationship("SoftwareRequest", back_populates="software")
    vulnerabilities = relationship("Vulnerability", back_populates="software")


class SoftwareVersion(Base):
    """软件版本模型"""
    __tablename__ = "software_versions"

    id = Column(Integer, primary_key=True, index=True)
    software_id = Column(Integer, ForeignKey("software.id"), nullable=False)
    version = Column(String(50), nullable=False)
    file_path = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(BigInteger)  # 字节
    file_hash = Column(String(64))   # SHA256
    upload_time = Column(DateTime(timezone=True), server_default=func.now())
    uploader_id = Column(Integer, ForeignKey("users.id"))
    download_count = Column(Integer, default=0)
    release_notes = Column(Text)

    # 关系
    software = relationship("Software", back_populates="versions")
    uploader = relationship("User", back_populates="uploaded_versions")
    download_logs = relationship("DownloadLog", back_populates="software_version")
