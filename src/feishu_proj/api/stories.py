"""需求/故事 API"""
from typing import Optional
from feishu_proj.client import FeishuProjClient


def get_stories(
    project_key: str,
    user_key: Optional[str] = None,
    page_size: int = 50,
    page_num: int = 1,
    status: Optional[str] = None,
    planning_version: Optional[str] = None,
    owner: Optional[str] = None,
    keyword: Optional[str] = None,
) -> dict:
    client = FeishuProjClient(user_key=user_key)
    return client.get_stories(
        project_key=project_key,
        page_size=page_size,
        page_num=page_num,
        status=status,
        planning_version=planning_version,
        owner=owner,
        keyword=keyword,
    )


def get_story_detail(
    project_key: str,
    story_id: str,
    user_key: Optional[str] = None,
) -> dict:
    """获取需求详情"""
    client = FeishuProjClient(user_key=user_key)
    return client.query_work_item_detail(
        project_key=project_key,
        work_item_type_key="story",
        work_item_ids=[story_id],
    )


def create_story(
    project_key: str,
    name: str,
    user_key: Optional[str] = None,
    field_value_pairs: Optional[list] = None,
    template_id: Optional[int] = None,
) -> dict:
    """创建需求"""
    client = FeishuProjClient(user_key=user_key)
    return client.create_work_item(
        project_key=project_key,
        work_item_type_key="story",
        name=name,
        field_value_pairs=field_value_pairs,
        template_id=template_id,
    )


def update_story(
    project_key: str,
    story_id: int,
    update_fields: list,
    user_key: Optional[str] = None,
) -> dict:
    """更新需求"""
    client = FeishuProjClient(user_key=user_key)
    return client.update_work_item(
        project_key=project_key,
        work_item_type_key="story",
        work_item_id=story_id,
        update_fields=update_fields,
    )
