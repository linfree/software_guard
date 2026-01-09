from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Generic, TypeVar
from datetime import datetime
from urllib.parse import urlparse
from ..models.request import RequestStatus

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """通用分页响应模型"""
    total: int
    items: List[T]


class SoftwareRequestBase(BaseModel):
    software_name: str
    version: str
    download_url: str
    description: Optional[str] = None
    category: Optional[str] = None
    logo: Optional[str] = None
    official_url: Optional[str] = None

    @field_validator('logo', 'official_url', mode='before')
    @classmethod
    def validate_url(cls, v):
        if not v or v.strip() == "":
            return None
        try:
            result = urlparse(v)
            # 允许相对路径（以/api开头）或完整URL
            if v.startswith('/api/') or (result.scheme and result.netloc):
                return v
            else:
                raise ValueError("Invalid URL")
        except Exception:
            raise ValueError(f"Invalid URL: {v}")


class SoftwareRequestCreate(SoftwareRequestBase):
    pass


class SoftwareRequestReview(BaseModel):
    status: RequestStatus
    comment: Optional[str] = None


class SoftwareRequestResponse(SoftwareRequestBase):
    id: int
    status: RequestStatus
    applicant_id: int
    applicant_name: str
    reviewer_id: Optional[int] = None
    reviewer_name: Optional[str] = None
    review_comment: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True