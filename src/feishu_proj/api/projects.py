"""项目 API"""

from typing import Optional
from feishu_proj.client import FeishuProjClient


def get_projects(
    user_key: Optional[str] = None,
    page_size: int = 50,
    page_token: str = "",
) -> dict:
    client = FeishuProjClient(user_key=user_key)
    return client.get_projects(
        page_size=page_size,
        page_token=page_token,
    )