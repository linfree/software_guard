from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import os
import hashlib
import aiofiles
from pathlib import Path

from ..core.database import get_db
from ..core.deps import get_current_active_user, require_ops
from ..core.config import settings
from ..models.user import User
from ..models.software import Software, SoftwareVersion
from ..models.vulnerability import Vulnerability
from ..models.request import SoftwareRequest
from ..schemas.software import (
    SoftwareCreate, SoftwareUpdate, SoftwareResponse,
    SoftwareVersionCreate, SoftwareVersionResponse, SoftwareListResponse, SoftwareListWithTotal, VersionInfo
)

router = APIRouter(prefix="/software", tags=["软件管理"])


def get_file_hash(file_path: str) -> str:
    """计算文件 SHA256 哈希"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


@router.get("", response_model=SoftwareListWithTotal)
async def list_software(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=1000),
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取软件列表"""
    query = db.query(Software)

    if category:
        query = query.filter(Software.category == category)
    if search:
        query = query.filter(Software.name.contains(search))

    # 获取总数（在应用过滤条件后）
    total = query.count()

    # 获取分页数据，按更新时间降序排序
    software_list = query.order_by(Software.updated_at.desc()).offset(skip).limit(limit).all()

    result = []
    for sw in software_list:
        latest_version = db.query(SoftwareVersion)\
            .filter(SoftwareVersion.software_id == sw.id)\
            .order_by(SoftwareVersion.upload_time.desc())\
            .first()

        versions = db.query(SoftwareVersion).filter(SoftwareVersion.software_id == sw.id).all()
        total_downloads = sum(v.download_count for v in versions)

        result.append(SoftwareListResponse(
            id=sw.id,
            name=sw.name,
            description=sw.description,
            category=sw.category,
            icon_url=sw.icon_url,
            logo=sw.logo,
            official_url=sw.official_url,
            latest_version=latest_version.version if latest_version else None,
            version_count=len(versions),
            total_downloads=total_downloads
        ))

    return SoftwareListWithTotal(total=total, items=result)


# Specific routes must be defined before parameterized routes
@router.get("/categories", response_model=List[str])
async def get_categories(db: Session = Depends(get_db)):
    """获取软件分类列表"""
    categories = db.query(Software.category)\
        .filter(Software.category.isnot(None))\
        .distinct()\
        .all()
    return [c[0] for c in categories if c[0]]


@router.get("/{software_id}", response_model=SoftwareResponse)
async def get_software(software_id: int, db: Session = Depends(get_db)):
    """获取软件详情"""
    software = db.query(Software).filter(Software.id == software_id).first()
    if not software:
        raise HTTPException(status_code=404, detail="软件不存在")

    # 获取版本信息，并关联原始下载地址
    versions = db.query(SoftwareVersion).filter(SoftwareVersion.software_id == software_id).all()
    
    # 获取该软件相关的申请记录，用于获取原始下载地址
    request_versions = {}
    requests = db.query(SoftwareRequest).filter(
        SoftwareRequest.software_id == software_id
    ).all()
    
    for req in requests:
        # 使用版本号作为键来映射原始下载地址
        request_versions[req.version] = req.download_url

    return SoftwareResponse(
        id=software.id,
        name=software.name,
        description=software.description,
        category=software.category,
        icon_url=software.icon_url,
        logo=software.logo,
        official_url=software.official_url,
        created_at=software.created_at,
        updated_at=software.updated_at,
        versions=[VersionInfo(
            id=v.id,
            version=v.version,
            file_name=v.file_name,
            file_size=v.file_size,
            file_hash=v.file_hash,
            upload_time=v.upload_time,
            download_count=v.download_count,
            release_notes=v.release_notes,
            original_download_url=request_versions.get(v.version)  # 添加原始下载地址
        ) for v in versions]
    )


@router.post("", response_model=SoftwareResponse, status_code=status.HTTP_201_CREATED)
async def create_software(
    software_data: SoftwareCreate,
    current_user: User = Depends(require_ops),
    db: Session = Depends(get_db)
):
    """创建软件"""
    # 检查软件名是否存在
    existing = db.query(Software).filter(Software.name == software_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="软件名称已存在")

    # 处理URL字段，将空字符串转换为None
    icon_url = str(software_data.icon_url) if software_data.icon_url else None
    logo = str(software_data.logo) if software_data.logo else None
    official_url = str(software_data.official_url) if software_data.official_url else None

    software = Software(
        name=software_data.name,
        description=software_data.description,
        category=software_data.category,
        icon_url=icon_url,
        logo=logo,
        official_url=official_url,
        created_by=current_user.id
    )
    db.add(software)
    db.commit()
    db.refresh(software)

    return SoftwareResponse(
        id=software.id,
        name=software.name,
        description=software.description,
        category=software.category,
        icon_url=software.icon_url,
        logo=software.logo,
        official_url=software.official_url,
        created_at=software.created_at,
        updated_at=software.updated_at,
        versions=[]
    )


@router.put("/{software_id}", response_model=SoftwareResponse)
async def update_software(
    software_id: int,
    software_data: SoftwareUpdate,
    current_user: User = Depends(require_ops),
    db: Session = Depends(get_db)
):
    """更新软件"""
    software = db.query(Software).filter(Software.id == software_id).first()
    if not software:
        raise HTTPException(status_code=404, detail="软件不存在")

    # 检查软件名是否被其他软件占用
    if software_data.name and software_data.name != software.name:
        existing = db.query(Software).filter(Software.name == software_data.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="软件名称已存在")

    if software_data.name:
        software.name = software_data.name
    if software_data.description is not None:
        software.description = software_data.description
    if software_data.category is not None:
        software.category = software_data.category
    
    # 处理URL字段，将空字符串转换为None
    if software_data.icon_url is not None:
        software.icon_url = str(software_data.icon_url) if software_data.icon_url else None
    if software_data.logo is not None:
        software.logo = str(software_data.logo) if software_data.logo else None
    if software_data.official_url is not None:
        software.official_url = str(software_data.official_url) if software_data.official_url else None

    db.commit()
    db.refresh(software)

    versions = db.query(SoftwareVersion)\
        .filter(SoftwareVersion.software_id == software_id)\
        .order_by(SoftwareVersion.upload_time.desc())\
        .all()

    # 获取该软件相关的申请记录，用于获取原始下载地址
    request_versions = {}
    requests = db.query(SoftwareRequest).filter(
        SoftwareRequest.software_id == software_id
    ).all()
    
    for req in requests:
        # 使用版本号作为键来映射原始下载地址
        request_versions[req.version] = req.download_url

    return SoftwareResponse(
        id=software.id,
        name=software.name,
        description=software.description,
        category=software.category,
        icon_url=software.icon_url,
        logo=software.logo,
        official_url=software.official_url,
        created_at=software.created_at,
        updated_at=software.updated_at,
        versions=[VersionInfo(
            id=v.id,
            version=v.version,
            file_name=v.file_name,
            file_size=v.file_size,
            file_hash=v.file_hash,
            upload_time=v.upload_time,
            download_count=v.download_count,
            release_notes=v.release_notes,
            original_download_url=request_versions.get(v.version)  # 添加原始下载地址
        ) for v in versions]
    )


@router.delete("/{software_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_software(
    software_id: int,
    current_user: User = Depends(require_ops),
    db: Session = Depends(get_db)
):
    """删除软件"""
    software = db.query(Software).filter(Software.id == software_id).first()
    if not software:
        raise HTTPException(status_code=404, detail="软件不存在")

    # 删除所有版本文件
    versions = db.query(SoftwareVersion).filter(SoftwareVersion.software_id == software_id).all()
    for version in versions:
        if os.path.exists(version.file_path):
            os.remove(version.file_path)
        db.delete(version)

    db.delete(software)
    db.commit()

    return None


@router.post("/{software_id}/versions", response_model=SoftwareVersionResponse)
async def upload_version(
    software_id: int,
    version: str = Form(...),
    file: UploadFile = File(...),
    release_notes: Optional[str] = Form(None),
    current_user: User = Depends(require_ops),
    db: Session = Depends(get_db)
):
    """上传软件版本"""
    software = db.query(Software).filter(Software.id == software_id).first()
    if not software:
        raise HTTPException(status_code=404, detail="软件不存在")

    # 检查文件扩展名 - 现在允许所有文件类型
    # 之前的限制: if file_ext not in settings.ALLOWED_EXTENSIONS:
    # 现在我们移除这个限制，允许所有文件类型

    # 检查文件大小
    content = await file.read()
    file_size = len(content)
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="文件大小超过限制")

    # 保存文件
    software_dir = os.path.join(settings.STORAGE_PATH, str(software_id))
    os.makedirs(software_dir, exist_ok=True)

    file_path = os.path.join(software_dir, file.filename)
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    # 计算文件哈希
    file_hash = get_file_hash(file_path)

    # 创建版本记录
    software_version = SoftwareVersion(
        software_id=software_id,
        version=version,
        file_path=file_path,
        file_name=file.filename,
        file_size=file_size,
        file_hash=file_hash,
        uploader_id=current_user.id,
        release_notes=release_notes
    )
    db.add(software_version)
    db.commit()
    db.refresh(software_version)

    return SoftwareVersionResponse(
        id=software_version.id,
        software_id=software_version.software_id,
        version=software_version.version,
        file_name=software_version.file_name,
        file_size=software_version.file_size,
        file_hash=software_version.file_hash,
        upload_time=software_version.upload_time,
        download_count=software_version.download_count,
        release_notes=software_version.release_notes,
        software_name=software.name
    )


@router.post("/{software_id}/logo", response_model=dict)
async def upload_logo(
    software_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(require_ops),
    db: Session = Depends(get_db)
):
    """上传软件Logo"""
    software = db.query(Software).filter(Software.id == software_id).first()
    if not software:
        raise HTTPException(status_code=404, detail="软件不存在")

    # 检查文件类型（只允许图片）
    allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico'}
    file_ext = os.path.splitext(file.filename)[1].lower() if file.filename else ''
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="只支持上传图片文件（png, jpg, jpeg, gif, svg, webp, ico）")

    # 检查文件大小（限制5MB）
    content = await file.read()
    file_size = len(content)
    max_logo_size = 5 * 1024 * 1024  # 5MB
    if file_size > max_logo_size:
        raise HTTPException(status_code=400, detail="Logo文件大小不能超过5MB")

    # 创建logo目录
    logo_dir = os.path.join(settings.STORAGE_PATH, "logos")
    os.makedirs(logo_dir, exist_ok=True)

    # 生成唯一的文件名
    import uuid
    file_extension = file_ext
    unique_filename = f"{software_id}_{uuid.uuid4().hex[:8]}{file_extension}"
    file_path = os.path.join(logo_dir, unique_filename)

    # 保存文件
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    # 删除旧的logo文件
    if software.logo and software.logo.startswith("/api/software/"):
        old_logo_path = os.path.join(settings.STORAGE_PATH, "logos", os.path.basename(software.logo))
        if os.path.exists(old_logo_path):
            try:
                os.remove(old_logo_path)
            except:
                pass

    # 更新软件的logo字段
    software.logo = f"/api/software/{software_id}/logo/file/{unique_filename}"
    db.commit()

    return {
        "logo": software.logo,
        "message": "Logo上传成功"
    }


@router.get("/{software_id}/logo/file/{filename}")
async def get_logo_file(
    software_id: int,
    filename: str,
    db: Session = Depends(get_db)
):
    """获取logo文件"""
    from fastapi.responses import FileResponse

    software = db.query(Software).filter(Software.id == software_id).first()
    if not software:
        raise HTTPException(status_code=404, detail="软件不存在")

    file_path = os.path.join(settings.STORAGE_PATH, "logos", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Logo文件不存在")

    return FileResponse(file_path)


@router.get("/logos/{filename}")
async def get_logo_file_direct(filename: str):
    """直接获取logo文件（不需要 software_id）"""
    from fastapi.responses import FileResponse

    file_path = os.path.join(settings.STORAGE_PATH, "logos", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Logo文件不存在")

    return FileResponse(file_path)


@router.delete("/{software_id}/versions/{version_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_software_version(
    software_id: int,
    version_id: int,
    current_user: User = Depends(require_ops),
    db: Session = Depends(get_db)
):
    """删除软件版本"""
    # 验证软件是否存在
    software = db.query(Software).filter(Software.id == software_id).first()
    if not software:
        raise HTTPException(status_code=404, detail="软件不存在")

    # 查找版本
    version = db.query(SoftwareVersion).filter(
        SoftwareVersion.id == version_id,
        SoftwareVersion.software_id == software_id
    ).first()

    if not version:
        raise HTTPException(status_code=404, detail="版本不存在")

    # 删除文件
    if os.path.exists(version.file_path):
        try:
            os.remove(version.file_path)
        except Exception as e:
            # 文件删除失败不影响数据库记录的删除
            pass

    # 删除数据库记录
    db.delete(version)
    db.commit()

    return None