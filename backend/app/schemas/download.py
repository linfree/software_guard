from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DownloadLogResponse(BaseModel):
    id: int
    user_id: int
    username: str
    software_name: str
    version: str
    download_time: datetime
    ip_address: Optional[str] = None

    class Config:
        from_attributes = True


class DownloadStatsResponse(BaseModel):
    total_downloads: int
    unique_users: int
    top_software: list
