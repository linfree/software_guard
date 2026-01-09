from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Generic, TypeVar
import os
from pydantic import BaseModel

from ..core.database import get_db
from ..core.deps import get_current_active_user
from ..models.user import User
from ..models.download import DownloadLog
from ..models.software import SoftwareVersion
from ..schemas.download import DownloadLogResponse, DownloadStatsResponse

router = APIRouter(prefix="/downloads", tags=["下载管理"])

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """通用分页响应模型"""
    total: int
    items: List[T]


# 具体路由必须在通配符路由之前定义
@router.get("/logs", response_model=PaginatedResponse[DownloadLogResponse])
async def get_download_logs(
    skip: int = 0,
    limit: int = 50,
    version_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取下载日志"""
    # 普通用户只能看到自己的下载记录
    query = db.query(DownloadLog)
    if current_user.role.value == "user":
        query = query.filter(DownloadLog.user_id == current_user.id)

    # 按版本筛选
    if version_id:
        query = query.filter(DownloadLog.software_version_id == version_id)

    # 获取总数
    total = query.count()

    logs = query.order_by(DownloadLog.download_time.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

    result = []
    for log in logs:
        user = db.query(User).filter(User.id == log.user_id).first()
        version = db.query(SoftwareVersion).filter(SoftwareVersion.id == log.software_version_id).first()
        from ..models.software import Software
        software = db.query(Software).filter(Software.id == version.software_id).first() if version else None

        result.append(DownloadLogResponse(
            id=log.id,
            user_id=log.user_id,
            username=user.username if user else "",
            software_name=software.name if software else "",
            version=version.version if version else "",
            download_time=log.download_time,
            ip_address=log.ip_address
        ))

    return PaginatedResponse(total=total, items=result)


@router.get("/stats", response_model=DownloadStatsResponse)
async def get_download_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取下载统计"""
    from ..models.software import Software
    from sqlalchemy import func, desc

    # 总下载次数
    total_downloads = db.query(DownloadLog).count()

    # 唯一用户数
    unique_users = db.query(DownloadLog.user_id).distinct().count()

    # 热门软件 TOP 10
    top_software = db.query(
        Software.name,
        func.count(DownloadLog.id).label("count")
    ).join(SoftwareVersion, Software.id == SoftwareVersion.software_id)\
     .join(DownloadLog, DownloadLog.software_version_id == SoftwareVersion.id)\
     .group_by(Software.name)\
     .order_by(desc("count"))\
     .limit(10)\
     .all()

    return DownloadStatsResponse(
        total_downloads=total_downloads,
        unique_users=unique_users,
        top_software=[{"name": s[0], "count": s[1]} for s in top_software]
    )


@router.get("/{version_id}")
async def download_software(
    version_id: int,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """下载软件文件"""
    version = db.query(SoftwareVersion).filter(SoftwareVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="版本不存在")

    file_path = version.file_path
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    # 记录下载日志
    download_log = DownloadLog(
        user_id=current_user.id,
        software_version_id=version_id,
        ip_address=request.client.host
    )
    db.add(download_log)

    # 更新下载计数
    version.download_count += 1
    db.commit()

    return FileResponse(
        path=file_path,
        filename=version.file_name,
        media_type="application/octet-stream"
    )