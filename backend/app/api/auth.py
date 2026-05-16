from typing import Optional
from collections import defaultdict
import time
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ..core.database import get_db
from ..core.security import verify_password, get_password_hash, create_access_token
from ..core.deps import get_current_active_user, require_ops, get_optional_current_user
from ..core.config import settings
from ..core.ldap import ldap_authenticate
from ..models.user import User, UserRole
from ..schemas.user import UserCreate, UserLogin, UserResponse, Token

router = APIRouter(prefix="/auth", tags=["认证"])

# 简单的内存速率限制器
_login_attempts: dict[str, list[float]] = defaultdict(list)


def _get_rate_limit_config(db: Session) -> tuple[int, int]:
    """从数据库读取速率限制配置，返回 (最大尝试次数, 时间窗口秒数)"""
    from ..models.config import Config
    max_cfg = db.query(Config).filter(Config.key == "login_rate_limit_max").first()
    window_cfg = db.query(Config).filter(Config.key == "login_rate_limit_window").first()
    max_attempts = int(max_cfg.value) if max_cfg else 5
    window = int(window_cfg.value) if window_cfg else 300
    return max_attempts, window


def _check_rate_limit(client_ip: str, db: Session):
    now = time.time()
    max_attempts, window = _get_rate_limit_config(db)
    attempts = _login_attempts[client_ip]
    _login_attempts[client_ip] = [t for t in attempts if now - t < window]
    if len(_login_attempts[client_ip]) >= max_attempts:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"登录尝试过多，请 {window // 60} 分钟后再试"
        )
    _login_attempts[client_ip].append(now)


def _is_registration_allowed(db: Session) -> bool:
    """检查是否允许开放注册：优先读数据库配置，否则用环境变量"""
    from ..models.config import Config
    db_config = db.query(Config).filter(Config.key == "allow_registration").first()
    if db_config:
        return db_config.value.lower() == "true"
    return settings.ALLOW_REGISTRATION


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """用户注册（allow_registration=True 时开放注册，否则需要 OPS/ADMIN 权限）"""
    if not _is_registration_allowed(db):
        if not current_user or current_user.role.value not in ("admin", "ops"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="注册功能已关闭，请联系管理员创建账号"
            )
    # 检查用户名是否存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 检查邮箱是否存在
    if user_data.email:
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )

    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        hashed_password=hashed_password,
        email=user_data.email,
        role=UserRole.USER
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """用户登录"""
    _check_rate_limit(request.client.host if request.client else "unknown", db)
    user = db.query(User).filter(User.username == form_data.username).first()

    authenticated = False
    if user and getattr(user, 'auth_source', 'local') == 'local':
        # 本地账号走本地密码验证
        if verify_password(form_data.password, user.hashed_password):
            authenticated = True
    else:
        # LDAP 用户或本地无此用户，尝试 LDAP 认证
        ldap_user = ldap_authenticate(form_data.username, form_data.password, db)
        if ldap_user:
            user = ldap_user
            authenticated = True

    if not authenticated or not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用"
        )

    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    db.commit()

    # 创建 Token（包含 token_version 用于失效校验）
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role.value, "tv": user.token_version}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """获取当前用户信息"""
    return current_user


@router.get("/ldap/test")
async def test_ldap_connection(
    current_user: User = Depends(require_ops),
    db: Session = Depends(get_db)
):
    """测试 LDAP 连接"""
    from ..core.ldap import _get_ldap_config
    from ldap3 import Server, Connection, ALL

    config = _get_ldap_config(db)
    server_url = config.get("ldap_server_url", "").strip()
    bind_dn = config.get("ldap_bind_dn", "").strip()
    bind_password = config.get("ldap_bind_password", "").strip()

    if not server_url:
        raise HTTPException(status_code=400, detail="未配置 LDAP 服务器地址")

    try:
        server = Server(server_url, get_info=ALL, connect_timeout=10)
        if bind_dn and bind_password:
            conn = Connection(server, user=bind_dn, password=bind_password, auto_bind=True, receive_timeout=10)
        else:
            conn = Connection(server, auto_bind=True, receive_timeout=10)
        info = server.info
        conn.unbind()
        return {"success": True, "message": f"已连接到 {info.other.get('serverName', [server_url])[0] if info and info.other else server_url}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"连接失败: {str(e)}")
