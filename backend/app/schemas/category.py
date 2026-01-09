"""
软件类型相关的 Pydantic 模型
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CategoryBase(BaseModel):
    """软件类型基础模型"""
    name: str = Field(..., min_length=1, max_length=50, description="类型名称")
    description: Optional[str] = Field(None, max_length=200, description="类型描述")
    sort_order: int = Field(0, description="排序顺序")


class CategoryCreate(CategoryBase):
    """创建软件类型"""
    pass


class CategoryUpdate(BaseModel):
    """更新软件类型"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    sort_order: Optional[int] = None


class CategoryResponse(CategoryBase):
    """软件类型响应"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CategoryListResponse(BaseModel):
    """软件类型列表响应"""
    id: int
    name: str
    description: Optional[str] = None
    sort_order: int
    software_count: int = 0  # 该类型下的软件数量

    class Config:
        from_attributes = True
