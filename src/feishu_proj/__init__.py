"""飞书项目 Python SDK"""

from feishu_proj.client import FeishuProjClient
from feishu_proj.tools import get_projects, get_requirements, get_bugs

__version__ = "0.1.0"
__all__ = [
    "FeishuProjClient",
    "get_projects",
    "get_requirements",
    "get_bugs",
    "cli",
]
