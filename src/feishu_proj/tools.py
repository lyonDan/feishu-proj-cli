"""Skill 可调用的工具接口"""

import os

from feishu_proj.api.bugs import create_bug, get_bug_detail, get_bugs, update_bug
from feishu_proj.api.projects import get_projects
from feishu_proj.api.requirements import get_requirement_detail, get_requirements
from feishu_proj.api.stories import (
    create_story,
    get_stories,
    get_story_detail,
    update_story,
)
from feishu_proj.api.versions import (
    create_version,
    get_version_detail,
    get_versions,
    update_version,
)
from feishu_proj.api.work_items import create_work_item, get_work_item_meta, update_work_item


def get_projects_tool(
    page_size: int = 50,
    page_token: str = "",
) -> dict:
    try:
        user_key = os.getenv("FEISHU_USER_KEY")
        data = get_projects(
            user_key=user_key,
            page_size=page_size,
            page_token=page_token,
        )
        return {"success": True, "data": data, "error": None}
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}


def get_requirements_tool(
    project_key: str,
    page_size: int = 50,
    page_num: int = 1,
    status: str | None = None,
) -> dict:
    try:
        user_key = os.getenv("FEISHU_USER_KEY")
        data = get_requirements(
            project_key=project_key,
            user_key=user_key,
            page_size=page_size,
            page_num=page_num,
            status=status,
        )
        return {"success": True, "data": data, "error": None}
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}


def get_requirement_detail_tool(
    project_key: str,
    requirement_id: str,
) -> dict:
    try:
        user_key = os.getenv("FEISHU_USER_KEY")
        data = get_requirement_detail(
            project_key=project_key,
            requirement_id=requirement_id,
            user_key=user_key,
        )
        return {"success": True, "data": data, "error": None}
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}


def get_bugs_tool(
    project_key: str,
    page_size: int = 50,
    page_num: int = 1,
    status: str | None = None,
    owner: str | None = None,
) -> dict:
    try:
        user_key = os.getenv("FEISHU_USER_KEY")
        data = get_bugs(
            project_key=project_key,
            user_key=user_key,
            page_size=page_size,
            page_num=page_num,
            status=status,
            owner=owner,
        )
        return {"success": True, "data": data, "error": None}
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}


def get_bug_detail_tool(
    project_key: str,
    bug_id: str,
) -> dict:
    try:
        user_key = os.getenv("FEISHU_USER_KEY")
        data = get_bug_detail(
            project_key=project_key,
            bug_id=bug_id,
            user_key=user_key,
        )
        return {"success": True, "data": data, "error": None}
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}


def create_work_item_tool(
    project_key: str,
    work_item_type_key: str,
    name: str,
    field_value_pairs: list | None = None,
    template_id: int | None = None,
) -> dict:
    try:
        user_key = os.getenv("FEISHU_USER_KEY")
        data = create_work_item(
            project_key=project_key,
            work_item_type_key=work_item_type_key,
            name=name,
            user_key=user_key,
            field_value_pairs=field_value_pairs,
            template_id=template_id,
        )
        return {"success": True, "data": data, "error": None}
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}


def update_work_item_tool(
    project_key: str,
    work_item_type_key: str,
    work_item_id: int,
    update_fields: list,
) -> dict:
    try:
        user_key = os.getenv("FEISHU_USER_KEY")
        data = update_work_item(
            project_key=project_key,
            work_item_type_key=work_item_type_key,
            work_item_id=work_item_id,
            update_fields=update_fields,
            user_key=user_key,
        )
        return {"success": True, "data": data, "error": None}
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}


def get_work_item_meta_tool(
    project_key: str,
    work_item_type_key: str,
) -> dict:
    try:
        user_key = os.getenv("FEISHU_USER_KEY")
        data = get_work_item_meta(
            project_key=project_key,
            work_item_type_key=work_item_type_key,
            user_key=user_key,
        )
        return {"success": True, "data": data, "error": None}
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}


def create_bug_tool(
    project_key: str,
    name: str,
    field_value_pairs: list | None = None,
    template_id: int | None = None,
) -> dict:
    """创建缺陷"""
    try:
        user_key = os.getenv("FEISHU_USER_KEY")
        data = create_bug(
            project_key=project_key,
            name=name,
            user_key=user_key,
            field_value_pairs=field_value_pairs,
            template_id=template_id,
        )
        return {"success": True, "data": data, "error": None}
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}


def update_bug_tool(
    project_key: str,
    bug_id: int,
    update_fields: list,
) -> dict:
    """更新缺陷"""
    try:
        user_key = os.getenv("FEISHU_USER_KEY")
        data = update_bug(
            project_key=project_key,
            bug_id=bug_id,
            update_fields=update_fields,
            user_key=user_key,
        )
        return {"success": True, "data": data, "error": None}
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}


def get_stories_tool(
    project_key: str,
    page_size: int = 50,
    page_num: int = 1,
    status: str | None = None,
    planning_version: str | None = None,
    owner: str | None = None,
    keyword: str | None = None,
) -> dict:
    """获取需求列表"""
    try:
        user_key = os.getenv("FEISHU_USER_KEY")
        data = get_stories(
            project_key=project_key,
            user_key=user_key,
            page_size=page_size,
            page_num=page_num,
            status=status,
            planning_version=planning_version,
            owner=owner,
            keyword=keyword,
        )
        return {"success": True, "data": data, "error": None}
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}


def get_story_detail_tool(
    project_key: str,
    story_id: str,
) -> dict:
    """获取需求详情"""
    try:
        user_key = os.getenv("FEISHU_USER_KEY")
        data = get_story_detail(
            project_key=project_key,
            story_id=story_id,
            user_key=user_key,
        )
        return {"success": True, "data": data, "error": None}
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}


def create_story_tool(
    project_key: str,
    name: str,
    field_value_pairs: list | None = None,
    template_id: int | None = None,
) -> dict:
    """创建需求"""
    try:
        user_key = os.getenv("FEISHU_USER_KEY")
        data = create_story(
            project_key=project_key,
            name=name,
            user_key=user_key,
            field_value_pairs=field_value_pairs,
            template_id=template_id,
        )
        return {"success": True, "data": data, "error": None}
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}


def update_story_tool(
    project_key: str,
    story_id: int,
    update_fields: list,
) -> dict:
    """更新需求"""
    try:
        user_key = os.getenv("FEISHU_USER_KEY")
        data = update_story(
            project_key=project_key,
            story_id=story_id,
            update_fields=update_fields,
            user_key=user_key,
        )
        return {"success": True, "data": data, "error": None}
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}


def get_versions_tool(
    project_key: str,
    page_size: int = 20,
    page_num: int = 1,
    keyword: str | None = None,
) -> dict:
    """获取版本列表"""
    try:
        user_key = os.getenv("FEISHU_USER_KEY")
        data = get_versions(
            project_key=project_key,
            user_key=user_key,
            page_size=page_size,
            page_num=page_num,
            keyword=keyword,
        )
        return {"success": True, "data": data, "error": None}
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}


def get_version_detail_tool(
    project_key: str,
    version_id: str,
) -> dict:
    """获取版本详情"""
    try:
        user_key = os.getenv("FEISHU_USER_KEY")
        data = get_version_detail(
            project_key=project_key,
            version_id=version_id,
            user_key=user_key,
        )
        return {"success": True, "data": data, "error": None}
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}


def create_version_tool(
    project_key: str,
    name: str,
    field_value_pairs: list | None = None,
    template_id: int | None = None,
) -> dict:
    """创建版本"""
    try:
        user_key = os.getenv("FEISHU_USER_KEY")
        data = create_version(
            project_key=project_key,
            name=name,
            user_key=user_key,
            field_value_pairs=field_value_pairs,
            template_id=template_id,
        )
        return {"success": True, "data": data, "error": None}
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}


def update_version_tool(
    project_key: str,
    version_id: int,
    update_fields: list,
) -> dict:
    """更新版本"""
    try:
        user_key = os.getenv("FEISHU_USER_KEY")
        data = update_version(
            project_key=project_key,
            version_id=version_id,
            update_fields=update_fields,
            user_key=user_key,
        )
        return {"success": True, "data": data, "error": None}
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}
