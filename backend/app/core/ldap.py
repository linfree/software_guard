import logging
from typing import Optional

from ldap3 import Server, Connection, ALL, SUBTREE
from ldap3.core.exceptions import LDAPException
from sqlalchemy.orm import Session

from ..models.user import User, UserRole
from ..core.security import get_password_hash
import secrets

logger = logging.getLogger(__name__)

LDAP_CONFIG_KEYS = [
    "ldap_enabled",
    "ldap_server_url",
    "ldap_bind_dn",
    "ldap_bind_password",
    "ldap_base_dn",
    "ldap_user_filter",
    "ldap_default_role",
]


def _get_ldap_config(db: Session) -> dict:
    """从数据库读取 LDAP 配置"""
    from ..models.config import Config
    configs = db.query(Config).filter(Config.key.in_(LDAP_CONFIG_KEYS)).all()
    return {c.key: c.value for c in configs}


def ldap_authenticate(username: str, password: str, db: Session) -> Optional[User]:
    """
    通过 LDAP/AD 认证用户。
    成功返回 User 对象（自动创建/更新本地记录），失败返回 None。
    """
    config = _get_ldap_config(db)

    if config.get("ldap_enabled", "false").lower() != "true":
        return None

    server_url = config.get("ldap_server_url", "").strip()
    bind_dn = config.get("ldap_bind_dn", "").strip()
    bind_password = config.get("ldap_bind_password", "").strip()
    base_dn = config.get("ldap_base_dn", "").strip()
    user_filter = config.get("ldap_user_filter", "(sAMAccountName={username})").strip()
    default_role = config.get("ldap_default_role", "user").strip()

    if not all([server_url, base_dn]):
        logger.warning("LDAP 配置不完整，缺少 server_url 或 base_dn")
        return None

    try:
        server = Server(server_url, get_info=ALL, connect_timeout=10)

        # 1. 用绑定账号连接并搜索用户
        search_filter = user_filter.replace("{username}", username)

        if bind_dn and bind_password:
            admin_conn = Connection(server, user=bind_dn, password=bind_password, auto_bind=True, receive_timeout=10)
        else:
            # 匿名绑定
            admin_conn = Connection(server, auto_bind=True, receive_timeout=10)

        admin_conn.search(
            search_base=base_dn,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=["mail"]
        )

        if not admin_conn.entries:
            logger.info(f"LDAP 搜索未找到用户: {username}")
            admin_conn.unbind()
            return None

        user_entry = admin_conn.entries[0]
        user_dn = user_entry.entry_dn
        user_mail = str(user_entry.mail.value) if hasattr(user_entry, 'mail') and user_entry.mail.value else None

        admin_conn.unbind()

        # 2. 用用户的 DN + 密码做 bind 验证
        user_conn = Connection(server, user=user_dn, password=password, auto_bind=True, receive_timeout=10)
        user_conn.unbind()

        # 3. 认证成功，创建或更新本地用户
        role_map = {"admin": UserRole.ADMIN, "ops": UserRole.OPS, "user": UserRole.USER}
        role = role_map.get(default_role, UserRole.USER)

        local_user = db.query(User).filter(User.username == username).first()
        if local_user:
            # 更新已有用户的信息
            if user_mail and not local_user.email:
                local_user.email = user_mail
            local_user.auth_source = "ldap"
        else:
            # 创建新用户
            local_user = User(
                username=username,
                hashed_password=get_password_hash(secrets.token_hex(32)),
                email=user_mail,
                role=role,
                auth_source="ldap"
            )
            db.add(local_user)

        db.commit()
        db.refresh(local_user)
        logger.info(f"LDAP 用户认证成功: {username}")
        return local_user

    except LDAPException as e:
        logger.warning(f"LDAP 认证失败 ({username}): {e}")
        return None
    except Exception as e:
        logger.error(f"LDAP 认证异常 ({username}): {e}")
        return None
