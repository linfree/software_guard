"""
软件类型管理 API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.deps import require_ops
from ..models.user import User
from ..models.category import SoftwareCategory
from ..models.software import Software
from ..schemas.category import (
    CategoryCreate, CategoryUpdate, CategoryResponse, CategoryListResponse
)

router = APIRouter(prefix="/categories", tags=["软件类型管理"])


@router.get("", response_model=List[CategoryListResponse])
async def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """获取软件类型列表"""
    categories = db.query(SoftwareCategory)\
        .order_by(SoftwareCategory.sort_order.asc(), SoftwareCategory.id.asc())\
        .offset(skip)\
        .limit(limit)\
        .all()

    result = []
    for cat in categories:
        # 统计该类型下的软件数量
        software_count = db.query(Software).filter(Software.category == cat.name).count()
        result.append(CategoryListResponse(
            id=cat.id,
            name=cat.name,
            description=cat.description,
            sort_order=cat.sort_order,
            software_count=software_count
        ))

    return result


@router.get("/all", response_model=List[str])
async def get_all_category_names(db: Session = Depends(get_db)):
    """获取所有软件类型名称（用于下拉列表）"""
    categories = db.query(SoftwareCategory)\
        .order_by(SoftwareCategory.sort_order.asc(), SoftwareCategory.id.asc())\
        .all()
    return [cat.name for cat in categories]


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """获取软件类型详情"""
    category = db.query(SoftwareCategory).filter(SoftwareCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="软件类型不存在")
    return category


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(require_ops),
    db: Session = Depends(get_db)
):
    """创建软件类型"""
    # 检查类型名是否已存在
    existing = db.query(SoftwareCategory).filter(SoftwareCategory.name == category_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="软件类型名称已存在")

    category = SoftwareCategory(
        name=category_data.name,
        description=category_data.description,
        sort_order=category_data.sort_order
    )
    db.add(category)
    db.commit()
    db.refresh(category)

    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_user: User = Depends(require_ops),
    db: Session = Depends(get_db)
):
    """更新软件类型"""
    category = db.query(SoftwareCategory).filter(SoftwareCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="软件类型不存在")

    # 如果修改名称，检查新名称是否被其他类型占用
    if category_data.name and category_data.name != category.name:
        existing = db.query(SoftwareCategory).filter(SoftwareCategory.name == category_data.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="软件类型名称已存在")

    # 更新字段
    if category_data.name is not None:
        category.name = category_data.name
        # 同步更新所有使用该类型的软件
        db.query(Software).filter(Software.category == category.name).update({
            "category": category_data.name
        })
    if category_data.description is not None:
        category.description = category_data.description
    if category_data.sort_order is not None:
        category.sort_order = category_data.sort_order

    db.commit()
    db.refresh(category)

    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    current_user: User = Depends(require_ops),
    db: Session = Depends(get_db)
):
    """删除软件类型"""
    category = db.query(SoftwareCategory).filter(SoftwareCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="软件类型不存在")

    # 检查是否有软件使用该类型
    software_count = db.query(Software).filter(Software.category == category.name).count()
    if software_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"该类型下还有 {software_count} 个软件，无法删除"
        )

    db.delete(category)
    db.commit()

    return None
