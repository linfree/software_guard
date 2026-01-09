from .auth import router as auth_router
from .software import router as software_router
from .request import router as request_router
from .download import router as download_router
from .vulnerability import router as vulnerability_router
from .user import router as user_router
from .config import router as config_router
from .category import router as category_router

__all__ = [
    "auth_router",
    "software_router",
    "request_router",
    "download_router",
    "vulnerability_router",
    "user_router",
    "config_router",
    "category_router",
]