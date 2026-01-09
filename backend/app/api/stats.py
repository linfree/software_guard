from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..core.database import get_db
from ..core.deps import get_current_active_user, require_ops
from ..models.user import User
from ..models.software import Software, SoftwareVersion
from ..models.request import SoftwareRequest, RequestStatus
from ..models.download import DownloadLog

router = APIRouter(prefix="/stats", tags=["统计数据"])


@router.get("/dashboard")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取首页统计数据"""
    # 软件总数
    software_count = db.query(func.count(Software.id)).scalar()

    # 总下载次数 - 统计下载日志表的记录总数，每次下载算一次
    total_downloads = db.query(func.count(DownloadLog.id)).scalar() or 0

    # 待审核申请数（只有运维人员可见）
    pending_requests = 0
    if current_user.role.value in ["admin", "ops"]:
        pending_requests = db.query(func.count(SoftwareRequest.id))\
            .filter(SoftwareRequest.status == RequestStatus.PENDING)\
            .scalar() or 0

    # 用户总数（只有运维人员可见）
    user_count = 0
    if current_user.role.value in ["admin", "ops"]:
        user_count = db.query(func.count(User.id)).scalar()

    return {
        "software_count": software_count,
        "total_downloads": total_downloads,
        "pending_requests": pending_requests,
        "user_count": user_count
    }