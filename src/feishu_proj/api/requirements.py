"""需求 API"""

from typing import Optional
from feishu_proj.client import FeishuProjClient


def get_requirements(
    project_key: str,
    user_key: Optional[str] = None,
    page_size: int = 50,
    page_num: int = 1,
    status: Optional[str] = None,
) -> dict:
    client = FeishuProjClient(user_key=user_key)
    return client.get_requirements(
        project_key=project_key,
        page_size=page_size,
        page_num=page_num,
        status=status,
    )


def get_requirement_detail(
    project_key: str,
    requirement_id: str,
    user_key: Optional[str] = None,
) -> dict:
    client = FeishuProjClient(user_key=user_key)
    return client.get_requirement_detail(
        project_key=project_key,
        requirement_id=requirement_id,
    )