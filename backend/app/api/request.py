from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import httpx
import os
import aiofiles
import hashlib
from pathlib import Path

from ..core.database import get_db
from ..core.deps import get_current_active_user, require_ops
from ..core.config import settings
from ..models.user import User
from ..models.request import SoftwareRequest, RequestStatus
from ..models.software import Software, SoftwareVersion
from ..schemas.request import SoftwareRequestCreate, SoftwareRequestResponse, SoftwareRequestReview, PaginatedResponse
from ..services.ai_service import AIService

router = APIRouter(prefix="/requests", tags=["软件申请"])


async def download_software_from_url(url: str, software_id: int, version: str, uploader_id: int):
    """后台任务：从 URL 下载软件"""
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            content = response.content

        # 从 URL 提取文件名
        filename = Path(url).name or f"software_{software_id}"
        if '.' not in filename:
            filename += ".exe"

        # 计算文件哈希
        sha256_hash = hashlib.sha256()
        sha256_hash.update(content)
        file_hash = sha256_hash.hexdigest()

        # 保存文件
        software_dir = os.path.join(settings.STORAGE_PATH, str(software_id))
        os.makedirs(software_dir, exist_ok=True)
        file_path = os.path.join(software_dir, filename)

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        # 获取数据库会话
        from ..core.database import SessionLocal
        db = SessionLocal()
        try:
            # 创建版本记录
            software_version = SoftwareVersion(
                software_id=software_id,
                version=version,
                file_path=file_path,
                file_name=filename,
                file_size=len(content),
                file_hash=file_hash,
                uploader_id=uploader_id
            )
            db.add(software_version)
            db.commit()
        finally:
            db.close()

    except Exception as e:
        # 记录错误日志
        print(f"下载软件失败: {e}")


@router.post("", response_model=SoftwareRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_request(
    request_data: SoftwareRequestCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建软件申请"""
    software_request = SoftwareRequest(
        software_name=request_data.software_name,
        version=request_data.version,
        download_url=request_data.download_url,
        description=request_data.description,
        category=request_data.category,
        logo=request_data.logo,
        official_url=request_data.official_url,
        applicant_id=current_user.id
    )
    db.add(software_request)
    db.commit()
    db.refresh(software_request)

    # 启动AI自动审核（如果启用）
    ai_service = AIService(db)
    if ai_service.auto_review_enabled:
        background_tasks.add_task(auto_review_request, software_request.id, db)

    return SoftwareRequestResponse(
        id=software_request.id,
        software_name=software_request.software_name,
        version=software_request.version,
        download_url=software_request.download_url,
        description=software_request.description,
        category=software_request.category,
        logo=software_request.logo,
        official_url=software_request.official_url,
        status=software_request.status,
        applicant_id=software_request.applicant_id,
        applicant_name=current_user.username,
        created_at=software_request.created_at
    )


async def auto_review_request(request_id: int, db_session: Session):
    """自动审核请求的后台任务"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from ..core.config import settings as app_settings
    
    # 创建新的数据库会话用于后台任务
    engine = create_engine(app_settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 获取申请记录
        software_request = db.query(SoftwareRequest).filter(SoftwareRequest.id == request_id).first()
        if not software_request:
            return

        # 使用AI服务审核申请
        ai_service = AIService(db)
        request_data = {
            "software_name": software_request.software_name,
            "version": software_request.version,
            "download_url": software_request.download_url,
            "category": software_request.category,
            "description": software_request.description
        }
        
        review_result = await ai_service.review_software_request(request_data)
        
        if review_result.get("approved", False):
            # AI审核通过，自动批准申请
            from datetime import datetime
            from ..models.request import RequestStatus
            
            software_request.status = RequestStatus.APPROVED
            software_request.review_comment = f"AI自动审核通过: {review_result.get('reason', '自动批准')}"
            software_request.reviewer_id = 1  # 系统账户ID
            software_request.reviewed_at = datetime.utcnow()
            
            # 检查软件是否已存在
            existing_software = db.query(Software).filter(Software.name == software_request.software_name).first()

            if existing_software:
                # 软件已存在，使用现有软件
                software_request.software_id = existing_software.id
                db.commit()

                # 后台下载文件
                from ..core.config import settings
                import httpx
                import os
                import aiofiles
                import hashlib
                from pathlib import Path
                
                async def download_task():
                    try:
                        async with httpx.AsyncClient(timeout=300.0) as client:
                            response = await client.get(software_request.download_url)
                            response.raise_for_status()
                            content = response.content

                        # 从 URL 提取文件名
                        filename = Path(software_request.download_url).name or f"software_{existing_software.id}"
                        if '.' not in filename:
                            filename += ".exe"

                        # 计算文件哈希
                        sha256_hash = hashlib.sha256()
                        sha256_hash.update(content)
                        file_hash = sha256_hash.hexdigest()

                        # 保存文件
                        software_dir = os.path.join(settings.STORAGE_PATH, str(existing_software.id))
                        os.makedirs(software_dir, exist_ok=True)
                        file_path = os.path.join(software_dir, filename)

                        async with aiofiles.open(file_path, "wb") as f:
                            await f.write(content)

                        # 创建版本记录
                        software_version = SoftwareVersion(
                            software_id=existing_software.id,
                            version=software_request.version,
                            file_path=file_path,
                            file_name=filename,
                            file_size=len(content),
                            file_hash=file_hash,
                            uploader_id=1  # 系统账户ID
                        )
                        db.add(software_version)
                        db.commit()
                    except Exception as e:
                        print(f"AI自动下载软件失败: {e}")
                
                import asyncio
                await download_task()
            else:
                # 创建新软件
                software = Software(
                    name=software_request.software_name,
                    description=software_request.description,
                    category=software_request.category,
                    logo=software_request.logo,
                    official_url=software_request.official_url,
                    created_by=1  # 系统账户ID
                )
                db.add(software)
                db.flush()

                software_request.software_id = software.id
                db.commit()

                # 后台下载文件
                from ..core.config import settings
                import httpx
                import os
                import aiofiles
                import hashlib
                from pathlib import Path
                
                async def download_task():
                    try:
                        async with httpx.AsyncClient(timeout=300.0) as client:
                            response = await client.get(software_request.download_url)
                            response.raise_for_status()
                            content = response.content

                        # 从 URL 提取文件名
                        filename = Path(software_request.download_url).name or f"software_{software.id}"
                        if '.' not in filename:
                            filename += ".exe"

                        # 计算文件哈希
                        sha256_hash = hashlib.sha256()
                        sha256_hash.update(content)
                        file_hash = sha256_hash.hexdigest()

                        # 保存文件
                        software_dir = os.path.join(settings.STORAGE_PATH, str(software.id))
                        os.makedirs(software_dir, exist_ok=True)
                        file_path = os.path.join(software_dir, filename)

                        async with aiofiles.open(file_path, "wb") as f:
                            await f.write(content)

                        # 创建版本记录
                        software_version = SoftwareVersion(
                            software_id=software.id,
                            version=software_request.version,
                            file_path=file_path,
                            file_name=filename,
                            file_size=len(content),
                            file_hash=file_hash,
                            uploader_id=1  # 系统账户ID
                        )
                        db.add(software_version)
                        db.commit()
                    except Exception as e:
                        print(f"AI自动下载软件失败: {e}")
                
                import asyncio
                await download_task()
        else:
            # AI审核未通过，但仍然保持PENDING状态，以便人工审核
            # 只是添加AI的审核意见到评论中
            from datetime import datetime
            from ..models.request import RequestStatus
            
            # 保留原始状态为PENDING，只更新评论和审核人
            software_request.review_comment = f"AI自动审核建议拒绝: {review_result.get('reason', '自动拒绝原因未知')}\n{software_request.review_comment or ''}".strip()
            software_request.reviewer_id = 1  # 系统账户ID
            # 不改变状态，保持为PENDING，这样人工仍可以审核
            db.commit()
            
    finally:
        db.close()


@router.get("", response_model=PaginatedResponse[SoftwareRequestResponse])
async def list_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: RequestStatus = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取申请列表"""
    query = db.query(SoftwareRequest)

    # 普通用户只能看到自己的申请
    if current_user.role.value == "user":
        query = query.filter(SoftwareRequest.applicant_id == current_user.id)

    if status:
        query = query.filter(SoftwareRequest.status == status)

    # 获取总数（在应用过滤条件后）
    total = query.count()

    # 获取分页数据
    requests = query.order_by(SoftwareRequest.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

    result = []
    for req in requests:
        applicant = db.query(User).filter(User.id == req.applicant_id).first()
        reviewer = db.query(User).filter(User.id == req.reviewer_id).first() if req.reviewer_id else None

        result.append(SoftwareRequestResponse(
            id=req.id,
            software_name=req.software_name,
            version=req.version,
            download_url=req.download_url,
            description=req.description,
            category=req.category,
            logo=req.logo,
            official_url=req.official_url,
            status=req.status,
            applicant_id=req.applicant_id,
            applicant_name=applicant.username if applicant else "",
            reviewer_id=req.reviewer_id,
            reviewer_name=reviewer.username if reviewer else None,
            review_comment=req.review_comment,
            reviewed_at=req.reviewed_at,
            created_at=req.created_at
        ))

    return PaginatedResponse(total=total, items=result)


@router.post("/{request_id}/review", response_model=SoftwareRequestResponse)
async def review_request(
    request_id: int,
    review_data: SoftwareRequestReview,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_ops),
    db: Session = Depends(get_db)
):
    """审核软件申请"""
    software_request = db.query(SoftwareRequest).filter(SoftwareRequest.id == request_id).first()
    if not software_request:
        raise HTTPException(status_code=404, detail="申请不存在")

    if software_request.status != RequestStatus.PENDING:
        raise HTTPException(status_code=400, detail="该申请已被处理")

    from datetime import datetime
    software_request.status = review_data.status
    software_request.reviewer_id = current_user.id
    software_request.review_comment = review_data.comment
    software_request.reviewed_at = datetime.utcnow()

    # 如果批准，创建软件记录
    if review_data.status == RequestStatus.APPROVED:
        # 检查软件是否已存在
        existing_software = db.query(Software).filter(Software.name == software_request.software_name).first()

        if existing_software:
            # 软件已存在，使用现有软件
            software_request.software_id = existing_software.id
            db.commit()

            # 后台下载文件
            background_tasks.add_task(
                download_software_from_url,
                software_request.download_url,
                existing_software.id,
                software_request.version,
                current_user.id
            )
        else:
            # 创建新软件
            software = Software(
                name=software_request.software_name,
                description=software_request.description,
                category=software_request.category,
                logo=software_request.logo,
                official_url=software_request.official_url,
                created_by=current_user.id
            )
            db.add(software)
            db.flush()

            software_request.software_id = software.id
            db.commit()

            # 后台下载文件
            background_tasks.add_task(
                download_software_from_url,
                software_request.download_url,
                software.id,
                software_request.version,
                current_user.id
            )
    else:
        db.commit()

    # 返回更新后的申请
    applicant = db.query(User).filter(User.id == software_request.applicant_id).first()
    return SoftwareRequestResponse(
        id=software_request.id,
        software_name=software_request.software_name,
        version=software_request.version,
        download_url=software_request.download_url,
        description=software_request.description,
        category=software_request.category,
        logo=software_request.logo,
        official_url=software_request.official_url,
        status=software_request.status,
        applicant_id=software_request.applicant_id,
        applicant_name=applicant.username if applicant else "",
        reviewer_id=software_request.reviewer_id,
        reviewer_name=current_user.username,
        review_comment=software_request.review_comment,
        reviewed_at=software_request.reviewed_at,
        created_at=software_request.created_at
    )