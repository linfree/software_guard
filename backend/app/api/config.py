from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..core.database import get_db
from ..core.deps import require_ops
from ..models.user import User
from ..models.config import Config
from ..schemas.config import ConfigCreate, ConfigUpdate, ConfigResponse

router = APIRouter(prefix="/configs", tags=["配置管理"])


@router.post("", response_model=ConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_config(
    config_data: ConfigCreate,
    current_user: User = Depends(require_ops),
    db: Session = Depends(get_db)
):
    """创建配置"""
    # 检查配置键是否存在
    existing = db.query(Config).filter(Config.key == config_data.key).first()
    if existing:
        raise HTTPException(status_code=400, detail="配置键已存在")

    config = Config(
        key=config_data.key,
        value=config_data.value,
        description=config_data.description
    )
    db.add(config)
    db.commit()
    db.refresh(config)

    return config


@router.get("", response_model=List[ConfigResponse])
async def list_configs(
    current_user: User = Depends(require_ops),
    db: Session = Depends(get_db)
):
    """获取配置列表"""
    configs = db.query(Config).all()
    return configs


@router.get("/{config_key}", response_model=ConfigResponse)
async def get_config(
    config_key: str,
    current_user: User = Depends(require_ops),
    db: Session = Depends(get_db)
):
    """获取配置"""
    config = db.query(Config).filter(Config.key == config_key).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")

    return config


@router.put("/{config_key}", response_model=ConfigResponse)
async def update_config(
    config_key: str,
    config_data: ConfigUpdate,
    current_user: User = Depends(require_ops),
    db: Session = Depends(get_db)
):
    """更新配置"""
    config = db.query(Config).filter(Config.key == config_key).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")

    config.value = config_data.value
    if config_data.description is not None:
        config.description = config_data.description

    db.commit()
    db.refresh(config)

    return config


@router.delete("/{config_key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_config(
    config_key: str,
    current_user: User = Depends(require_ops),
    db: Session = Depends(get_db)
):
    """删除配置"""
    config = db.query(Config).filter(Config.key == config_key).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")

    db.delete(config)
    db.commit()

    return None