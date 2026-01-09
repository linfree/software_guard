from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from ..core.database import Base


class RequestStatus(str, PyEnum):
    """申请状态枚举"""
    PENDING = "pending"    # 待审核
    APPROVED = "approved"  # 已批准
    REJECTED = "rejected"  # 已拒绝
    PROCESSING = "processing"  # 处理中（下载中）


class SoftwareRequest(Base):
    """软件申请模型"""
    __tablename__ = "software_requests"

    id = Column(Integer, primary_key=True, index=True)
    software_name = Column(String(100), nullable=False, index=True)
    version = Column(String(50), nullable=False)
    download_url = Column(String(500), nullable=False)
    description = Column(Text)
    category = Column(String(50))
    logo = Column(String(255))
    official_url = Column(String(255))

    # 申请信息
    applicant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(SQLEnum(RequestStatus), default=RequestStatus.PENDING, nullable=False)

    # 审核信息
    reviewer_id = Column(Integer, ForeignKey("users.id"))
    review_comment = Column(Text)
    reviewed_at = Column(DateTime(timezone=True))

    # 关联软件ID（审核通过后创建）
    software_id = Column(Integer, ForeignKey("software.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    applicant = relationship("User", foreign_keys=[applicant_id], back_populates="requests")
    reviewer = relationship("User", foreign_keys=[reviewer_id], back_populates="reviewed_requests")
    software = relationship("Software", back_populates="requests")
