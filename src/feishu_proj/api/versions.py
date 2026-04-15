"""版本 API"""

from feishu_proj.client import FeishuProjClient


def get_versions(
    project_key: str,
    page_size: int = 20,
    page_num: int = 1,
    user_key: str | None = None,
    keyword: str | None = None,
) -> dict:
    client = FeishuProjClient(user_key=user_key)
    return client.get_versions(
        project_key=project_key,
        page_size=page_size,
        page_num=page_num,
        keyword=keyword,
    )


def get_version_detail(
    project_key: str,
    version_id: str,
    user_key: str | None = None,
) -> dict:
    """获取版本详情"""
    client = FeishuProjClient(user_key=user_key)
    return client.query_work_item_detail(
        project_key=project_key,
        work_item_type_key="version",
        work_item_ids=[version_id],
    )


def create_version(
    project_key: str,
    name: str,
    user_key: str | None = None,
    field_value_pairs: list | None = None,
    template_id: int | None = None,
) -> dict:
    """创建版本"""
    client = FeishuProjClient(user_key=user_key)
    return client.create_work_item(
        project_key=project_key,
        work_item_type_key="version",
        name=name,
        field_value_pairs=field_value_pairs,
        template_id=template_id,
    )


def update_version(
    project_key: str,
    version_id: int,
    update_fields: list,
    user_key: str | None = None,
) -> dict:
    """更新版本"""
    client = FeishuProjClient(user_key=user_key)
    return client.update_work_item(
        project_key=project_key,
        work_item_type_key="version",
        work_item_id=version_id,
        update_fields=update_fields,
    )
