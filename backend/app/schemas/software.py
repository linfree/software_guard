from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from urllib.parse import urlparse


class SoftwareBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = None
    icon_url: Optional[str] = None
    logo: Optional[str] = None
    official_url: Optional[str] = None

    @field_validator('icon_url', 'logo', 'official_url', mode='before')
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


class SoftwareCreate(SoftwareBase):
    pass


class SoftwareUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = None
    icon_url: Optional[str] = None
    logo: Optional[str] = None
    official_url: Optional[str] = None

    @field_validator('icon_url', 'logo', 'official_url', mode='before')
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


class SoftwareVersionBase(BaseModel):
    version: str = Field(..., min_length=1)
    release_notes: Optional[str] = None


class SoftwareVersionCreate(SoftwareVersionBase):
    software_id: int


class VersionInfo(BaseModel):
    id: int
    version: str
    file_name: str
    file_size: int
    file_hash: Optional[str]
    upload_time: datetime
    download_count: int
    release_notes: Optional[str]
    original_download_url: Optional[str] = None  # 添加原始下载地址字段

    class Config:
        from_attributes = True


class SoftwareResponse(SoftwareBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    versions: List[VersionInfo] = []

    class Config:
        from_attributes = True


class SoftwareVersionResponse(SoftwareVersionBase):
    id: int
    software_id: int
    file_name: str
    file_size: int
    file_hash: Optional[str]
    upload_time: datetime
    download_count: int
    software_name: str

    class Config:
        from_attributes = True


class SoftwareListResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    category: Optional[str]
    icon_url: Optional[str]
    logo: Optional[str]
    official_url: Optional[str]
    latest_version: Optional[str]
    version_count: int
    total_downloads: int

    class Config:
        from_attributes = True


class SoftwareListWithTotal(BaseModel):
    total: int
    items: List[SoftwareListResponse]