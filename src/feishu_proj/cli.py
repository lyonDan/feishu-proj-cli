"""CLI 命令接口

使用 click 实现的命令行工具，支持以下命令:
- feishu-proj projects list
- feishu-proj requirements list/get
- feishu-proj bugs list/get
- feishu-proj stories list
- feishu-proj versions list
- feishu-proj work-item-types list
- feishu-proj work-items list/get/create/update/meta
- feishu-proj users get/search
- feishu-proj auth show-config/get-user-key
"""

import json
from typing import Optional

import click

from feishu_proj.api.bugs import create_bug, get_bug_detail, get_bugs, update_bug
from feishu_proj.api.projects import get_projects
from feishu_proj.api.requirements import get_requirement_detail, get_requirements
from feishu_proj.api.stories import create_story, get_stories, get_story_detail, update_story
from feishu_proj.api.versions import (
    create_version,
    get_version_detail,
    get_versions,
    update_version,
)
from feishu_proj.api.work_items import (
    create_work_item,
    delete_work_item,
    get_work_item_meta,
    update_work_item,
)


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """飞书项目 CLI 工具"""
    pass


@cli.group()
def projects():
    """项目管理命令"""
    pass


@projects.command("list")
@click.option("--page-size", default=50, help="每页数量")
@click.option("--page-token", default="", help="分页令牌")
@click.option("--format", type=click.Choice(["json", "table"]), default="json", help="输出格式")
def projects_list(page_size: int, page_token: str, format: str):
    """获取项目列表"""
    try:
        data = get_projects(
            page_size=page_size,
            page_token=page_token,
        )
        if format == "json":
            click.echo(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            _print_table(data.get("data", {}).get("items", []), ["name", "status"])
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        raise SystemExit(1)


@cli.group()
def requirements():
    """需求管理命令"""
    pass


@requirements.command("list")
@click.option("--project-key", required=True, help="项目 Key")
@click.option("--page-size", default=50, help="每页数量")
@click.option("--page-num", default=1, help="分页页码")
@click.option("--status", default=None, help="状态筛选")
@click.option("--format", type=click.Choice(["json", "table"]), default="json", help="输出格式")
def requirements_list(project_key: str, page_size: int, page_num: int, status: Optional[str], format: str):
    """获取需求列表"""
    try:
        data = get_requirements(
            project_key=project_key,
            page_size=page_size,
            page_num=page_num,
            status=status,
        )
        if format == "json":
            click.echo(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            _print_table(data.get("data", {}).get("items", []), ["name", "status"])
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        raise SystemExit(1)


@requirements.command("get")
@click.option("--project-key", required=True, help="项目 Key")
@click.option("--id", "requirement_id", required=True, help="需求 ID")
@click.option("--format", type=click.Choice(["json", "table"]), default="json", help="输出格式")
def requirements_get(project_key: str, requirement_id: str, format: str):
    """获取需求详情"""
    try:
        data = get_requirement_detail(
            project_key=project_key,
            requirement_id=requirement_id,
        )
        if format == "json":
            click.echo(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            _print_dict(data.get("data", {}))
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        raise SystemExit(1)


@cli.group()
def bugs():
    """缺陷管理命令"""
    pass


@bugs.command("list")
@click.option("--project-key", required=True, help="项目 Key")
@click.option("--page-size", default=50, help="每页数量")
@click.option("--page-num", default=1, help="分页页码")
@click.option("--status", default=None, help="状态筛选，默认只显示 OPEN 和 RESOLVED")
@click.option("--owner", default=None, help="负责人 user_key")
@click.option("--keyword", default=None, help="关键字搜索")
@click.option("--format", type=click.Choice(["json", "table"]), default="json", help="输出格式")
def bugs_list(project_key, page_size, page_num, status, owner, keyword, format):
    """获取缺陷列表"""
    try:
        # Default to open statuses if not specified
        if not status:
            status = "OPEN,RESOLVED"
        
        data = get_bugs(
            project_key=project_key,
            page_size=page_size,
            page_num=page_num,
            status=status,
            owner=owner,
            keyword=keyword,
        )
        if format == "json":
            click.echo(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            items = data.get("data", [])
            _print_table(items, ["name", "sub_stage"])
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        raise SystemExit(1)


@bugs.command("get")
@click.option("--project-key", required=True, help="项目 Key")
@click.option("--id", "bug_id", required=True, help="缺陷 ID")
@click.option("--format", type=click.Choice(["json", "table"]), default="json", help="输出格式")
def bugs_get(project_key: str, bug_id: str, format: str):
    """获取缺陷详情"""
    try:
        data = get_bug_detail(
            project_key=project_key,
            bug_id=bug_id,
        )
        if format == "json":
            click.echo(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            _print_dict(data.get("data", {}))
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        raise SystemExit(1)


@bugs.command("create")
@click.option("--project-key", required=True, help="项目 Key")
@click.option("--name", required=True, help="缺陷标题")
@click.option(
    "--fields",
    "fields_json",
    default=None,
    help='字段值 JSON 数组，例: \'[{"field_key":"owner","field_value":"user_key_xxx"}]\'',
)
@click.option("--template-id", default=None, type=int, help="流程模板 ID")
@click.option("--dry-run", is_flag=True, default=False, help="仅预览请求参数，不实际创建")
def bugs_create(
    project_key: str,
    name: str,
    fields_json: Optional[str],
    template_id: Optional[int],
    dry_run: bool,
):
    """创建缺陷"""
    try:
        field_value_pairs = json.loads(fields_json) if fields_json else None
        if dry_run:
            payload: dict = {"work_item_type_key": "issue", "name": name}
            if field_value_pairs:
                payload["field_value_pairs"] = field_value_pairs
            if template_id is not None:
                payload["template_id"] = template_id
            click.echo("[DRY RUN] 将创建缺陷，请求参数:")
            click.echo(json.dumps(payload, indent=2, ensure_ascii=False))
            return
        data = create_bug(
            project_key=project_key,
            name=name,
            field_value_pairs=field_value_pairs,
            template_id=template_id,
        )
        click.echo(json.dumps(data, indent=2, ensure_ascii=False))
    except json.JSONDecodeError as e:
        click.echo(f"JSON 解析错误: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        raise SystemExit(1)


@bugs.command("update")
@click.option("--project-key", required=True, help="项目 Key")
@click.option("--id", "bug_id", required=True, type=int, help="缺陷 ID")
@click.option(
    "--fields",
    "fields_json",
    default=None,
    help='更新字段 JSON 数组，例: \'[{"field_key":"name","field_value":"新标题"}]\'',
)
@click.option(
    "--status",
    default=None,
    help="目标状态 key，例: CLOSED / RESOLVED / OPEN / REOPENED",
)
@click.option("--dry-run", is_flag=True, default=False, help="仅预览请求参数，不实际更新")
def bugs_update(
    project_key: str, bug_id: int, fields_json: Optional[str], status: Optional[str], dry_run: bool
):
    """更新缺陷字段或流转状态

    流转状态示例:
      feishu-proj bugs update --project-key KEY --id ID --status CLOSED
      feishu-proj bugs update --project-key KEY --id ID --status RESOLVED

    更新字段示例:
      feishu-proj bugs update --project-key KEY --id ID --fields '[{"field_key":"name","field_value":"x"}]'
    """  # noqa: E501
    if not fields_json and not status:
        click.echo("错误: 必须提供 --fields 或 --status 之一", err=True)
        raise SystemExit(1)

    try:
        from feishu_proj.client import FeishuProjClient
        if status:
            if dry_run:
                click.echo(f"[DRY RUN] 将流转缺陷 {bug_id} 状态到 {status}")
                return
            client = FeishuProjClient()
            data = client.transit_work_item_to_state(
                project_key=project_key,
                work_item_type_key="issue",
                work_item_id=bug_id,
                target_state_key=status,
            )
            click.echo(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            update_fields = json.loads(fields_json)  # type: ignore[arg-type]
            if dry_run:
                click.echo(f"[DRY RUN] 将更新缺陷 {bug_id}，请求参数:")
                click.echo(
                    json.dumps({"update_fields": update_fields}, indent=2, ensure_ascii=False)
                )
                return
            data = update_bug(
                project_key=project_key,
                bug_id=bug_id,
                update_fields=update_fields,
            )
            click.echo(json.dumps(data, indent=2, ensure_ascii=False))
    except json.JSONDecodeError as e:
        click.echo(f"JSON 解析错误: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        raise SystemExit(1)


@bugs.command("delete")
@click.option("--project-key", required=True, help="项目 Key")
@click.option("--id", "bug_id", required=True, type=int, help="缺陷 ID")
@click.option("--dry-run", is_flag=True, default=False, help="仅预览，不实际删除")
def bugs_delete(project_key: str, bug_id: int, dry_run: bool):
    """删除缺陷（不可恢复，请谨慎操作）"""
    if dry_run:
        click.echo(f"[DRY RUN] 将删除缺陷 {bug_id}（project={project_key}）")
        return
    try:
        from feishu_proj.client import FeishuProjClient
        client = FeishuProjClient()
        data = client.delete_work_item(
            project_key=project_key,
            work_item_type_key="issue",
            work_item_id=bug_id,
        )
        click.echo(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        raise SystemExit(1)


def _print_table(items: list, keys: list):
    """打印表格"""
    if not items:
        click.echo("无数据")
        return
    for item in items:
        row = [str(item.get(k, "")) for k in keys]
        click.echo(" | ".join(row))


def _print_dict(data: dict):
    """打印字典"""
    if not data:
        click.echo("无数据")
        return
    for key, value in data.items():
        click.echo(f"{key}: {value}")


def _print_work_items(data, format):
    items = data.get("data", [])
    if format == "json":
        click.echo(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        rows = []
        for item in items:
            name = item.get("name", "")[:40]
            wid = item.get("id", "")
            sub_stage = item.get("sub_stage", "")
            wtype = item.get("work_item_type_key", "")
            owner_val = ""
            for f in item.get("fields", []):
                if f.get("field_key") == "owner":
                    owner_val = f.get("field_value", "")
                    break
            rows.append({"ID": str(wid), "name": name, "type": wtype, "status": sub_stage, "owner": owner_val})
        if not rows:
            click.echo("无数据")
        else:
            click.echo(f"{'ID'.ljust(14)} | {'name'.ljust(42)} | {'type'.ljust(10)} | {'status'.ljust(16)} | {'owner'}")
            click.echo("-" * 95)
            for r in rows:
                click.echo(f"{r['ID'].ljust(14)} | {r['name'].ljust(42)} | {r['type'].ljust(10)} | {r['status'].ljust(16)} | {r['owner']}")
            click.echo(f"\n共 {len(rows)} 条")


@cli.group()
def work_item_types():
    """工作项类型管理命令"""
    pass


@work_item_types.command("list")
@click.option("--format", type=click.Choice(["json", "table"]), default="json", help="输出格式")
def work_item_types_list(format: str):
    """获取工作项类型列表"""
    try:
        from feishu_proj.client import FeishuProjClient
        client = FeishuProjClient()
        types = client.get_work_item_types()
        if format == "json":
            click.echo(json.dumps(types, indent=2, ensure_ascii=False))
        else:
            _print_table(types, ["key", "name"])
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        raise SystemExit(1)


@cli.group()
def versions():
    """版本管理命令"""
    pass


@versions.command("list")
@click.option("--project-key", required=True, help="项目 Key")
@click.option("--page-size", default=20, help="每页数量")
@click.option("--page-num", default=1, help="分页页码")
@click.option("--keyword", default=None, help="关键字搜索")
@click.option("--format", type=click.Choice(["json", "table"]), default="json", help="输出格式")
def versions_list(project_key: str, page_size: int, page_num: int, keyword: Optional[str], format: str):
    """获取版本列表"""
    try:
        data = get_versions(
            project_key=project_key,
            page_size=page_size,
            page_num=page_num,
            keyword=keyword,
        )
        if format == "json":
            click.echo(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            items = data.get("data", [])
            _print_table(items, ["name", "id"])
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        raise SystemExit(1)


@versions.command("get")
@click.option("--project-key", required=True, help="项目 Key")
@click.option("--id", "version_id", required=True, help="版本 ID")
@click.option(
    "--format", type=click.Choice(["json", "table"]), default="json", help="输出格式"
)
def versions_get(project_key: str, version_id: str, format: str):
    """获取版本详情"""
    try:
        data = get_version_detail(project_key=project_key, version_id=version_id)
        if format == "json":
            click.echo(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            _print_dict(data.get("data", {}))
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        raise SystemExit(1)


@versions.command("create")
@click.option("--project-key", required=True, help="项目 Key")
@click.option("--name", required=True, help="版本名称")
@click.option(
    "--fields",
    "fields_json",
    default=None,
    help='字段值 JSON 数组，例: \'[{"field_key":"owner","field_value":"user_key_xxx"}]\'',
)
@click.option("--template-id", default=None, type=int, help="流程模板 ID")
@click.option("--dry-run", is_flag=True, default=False, help="仅预览请求参数，不实际创建")
def versions_create(
    project_key: str,
    name: str,
    fields_json: Optional[str],
    template_id: Optional[int],
    dry_run: bool,
):
    """创建版本"""
    try:
        field_value_pairs = json.loads(fields_json) if fields_json else None
        if dry_run:
            payload: dict = {"work_item_type_key": "version", "name": name}
            if field_value_pairs:
                payload["field_value_pairs"] = field_value_pairs
            if template_id is not None:
                payload["template_id"] = template_id
            click.echo("[DRY RUN] 将创建版本，请求参数:")
            click.echo(json.dumps(payload, indent=2, ensure_ascii=False))
            return
        data = create_version(
            project_key=project_key,
            name=name,
            field_value_pairs=field_value_pairs,
            template_id=template_id,
        )
        click.echo(json.dumps(data, indent=2, ensure_ascii=False))
    except json.JSONDecodeError as e:
        click.echo(f"JSON 解析错误: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        raise SystemExit(1)


@versions.command("update")
@click.option("--project-key", required=True, help="项目 Key")
@click.option("--id", "version_id", required=True, type=int, help="版本 ID")
@click.option(
    "--fields",
    "fields_json",
    required=True,
    help='更新字段 JSON 数组，例: \'[{"field_key":"name","field_value":"v2.0"}]\'',
)
@click.option("--dry-run", is_flag=True, default=False, help="仅预览请求参数，不实际更新")
def versions_update(project_key: str, version_id: int, fields_json: str, dry_run: bool):
    """更新版本"""
    try:
        update_fields = json.loads(fields_json)
        if dry_run:
            click.echo(f"[DRY RUN] 将更新版本 {version_id}，请求参数:")
            click.echo(
                json.dumps({"update_fields": update_fields}, indent=2, ensure_ascii=False)
            )
            return
        data = update_version(
            project_key=project_key,
            version_id=version_id,
            update_fields=update_fields,
        )
        click.echo(json.dumps(data, indent=2, ensure_ascii=False))
    except json.JSONDecodeError as e:
        click.echo(f"JSON 解析错误: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        raise SystemExit(1)


@cli.group()
def stories():
    """需求管理命令"""
    pass


@stories.command("list")
@click.option("--project-key", required=True, help="项目 Key")
@click.option("--page-size", default=50, help="每页数量")
@click.option("--page-num", default=1, help="分页页码")
@click.option("--planning-version", default=None, help="按版本 ID 筛选")
@click.option("--status", default=None, help="状态筛选")
@click.option("--owner", default=None, help="负责人 user_key")
@click.option("--keyword", default=None, help="关键字搜索")
@click.option("--format", type=click.Choice(["json", "table"]), default="table", help="输出格式")
def stories_list(project_key, page_size, page_num, planning_version, status, owner, keyword, format):
    """获取需求/story 列表"""
    try:
        data = get_stories(
            project_key=project_key,
            page_size=page_size,
            page_num=page_num,
            planning_version=planning_version,
            status=status,
            owner=owner,
            keyword=keyword,
        )
        if format == "json":
            click.echo(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            items = data.get("data", [])
            rows = []
            for item in items:
                name = item.get("name", "")[:40]
                wid = item.get("id", "")
                sub_stage = item.get("sub_stage", "")
                owner_val = ""
                for f in item.get("fields", []):
                    if f.get("field_key") == "owner":
                        owner_val = f.get("field_value", "")
                        break
                rows.append({"ID": str(wid), "name": name, "status": sub_stage, "owner": owner_val})
            if not rows:
                click.echo("无数据")
            else:
                click.echo(f"{'ID'.ljust(14)} | {'name'.ljust(42)} | {'status'.ljust(16)} | {'owner'}")
                click.echo("-" * 90)
                for r in rows:
                    click.echo(f"{r['ID'].ljust(14)} | {r['name'].ljust(42)} | {r['status'].ljust(16)} | {r['owner']}")
                click.echo(f"\n共 {len(rows)} 条")
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        raise SystemExit(1)


@stories.command("get")
@click.option("--project-key", required=True, help="项目 Key")
@click.option("--id", "story_id", required=True, help="需求 ID")
@click.option(
    "--format", type=click.Choice(["json", "table"]), default="json", help="输出格式"
)
def stories_get(project_key: str, story_id: str, format: str):
    """获取需求详情"""
    try:
        data = get_story_detail(project_key=project_key, story_id=story_id)
        if format == "json":
            click.echo(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            _print_dict(data.get("data", {}))
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        raise SystemExit(1)


@stories.command("create")
@click.option("--project-key", required=True, help="项目 Key")
@click.option("--name", required=True, help="需求标题")
@click.option(
    "--fields",
    "fields_json",
    default=None,
    help='字段值 JSON 数组，例: \'[{"field_key":"owner","field_value":"user_key_xxx"}]\'',
)
@click.option("--template-id", default=None, type=int, help="流程模板 ID")
@click.option("--dry-run", is_flag=True, default=False, help="仅预览请求参数，不实际创建")
def stories_create(
    project_key: str,
    name: str,
    fields_json: Optional[str],
    template_id: Optional[int],
    dry_run: bool,
):
    """创建需求"""
    try:
        field_value_pairs = json.loads(fields_json) if fields_json else None
        if dry_run:
            payload: dict = {"work_item_type_key": "story", "name": name}
            if field_value_pairs:
                payload["field_value_pairs"] = field_value_pairs
            if template_id is not None:
                payload["template_id"] = template_id
            click.echo("[DRY RUN] 将创建需求，请求参数:")
            click.echo(json.dumps(payload, indent=2, ensure_ascii=False))
            return
        data = create_story(
            project_key=project_key,
            name=name,
            field_value_pairs=field_value_pairs,
            template_id=template_id,
        )
        click.echo(json.dumps(data, indent=2, ensure_ascii=False))
    except json.JSONDecodeError as e:
        click.echo(f"JSON 解析错误: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        raise SystemExit(1)


@stories.command("update")
@click.option("--project-key", required=True, help="项目 Key")
@click.option("--id", "story_id", required=True, type=int, help="需求 ID")
@click.option(
    "--fields",
    "fields_json",
    required=True,
    help='更新字段 JSON 数组，例: \'[{"field_key":"name","field_value":"新标题"}]\'',
)
@click.option("--dry-run", is_flag=True, default=False, help="仅预览请求参数，不实际更新")
def stories_update(project_key: str, story_id: int, fields_json: str, dry_run: bool):
    """更新需求

    状态流转示例:
    '[{"field_key":"sub_stage","field_value":"DONE","target_state":{"state_key":"DONE","transition_id":1}}]'
    """
    try:
        update_fields = json.loads(fields_json)
        if dry_run:
            click.echo(f"[DRY RUN] 将更新需求 {story_id}，请求参数:")
            click.echo(
                json.dumps({"update_fields": update_fields}, indent=2, ensure_ascii=False)
            )
            return
        data = update_story(
            project_key=project_key,
            story_id=story_id,
            update_fields=update_fields,
        )
        click.echo(json.dumps(data, indent=2, ensure_ascii=False))
    except json.JSONDecodeError as e:
        click.echo(f"JSON 解析错误: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        raise SystemExit(1)


@stories.command("delete")
@click.option("--project-key", required=True, help="项目 Key")
@click.option("--id", "story_id", required=True, type=int, help="需求 ID")
@click.option("--dry-run", is_flag=True, default=False, help="仅预览，不实际删除")
def stories_delete(project_key: str, story_id: int, dry_run: bool):
    """删除需求（不可恢复，请谨慎操作）"""
    if dry_run:
        click.echo(f"[DRY RUN] 将删除需求 {story_id}（project={project_key}）")
        return
    try:
        from feishu_proj.client import FeishuProjClient
        client = FeishuProjClient()
        data = client.delete_work_item(
            project_key=project_key,
            work_item_type_key="story",
            work_item_id=story_id,
        )
        click.echo(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        raise SystemExit(1)


@cli.group()
def auth():
    """认证相关命令"""
    pass


@auth.command("get-user-key")
@click.option("--code", "auth_code", required=True, help="授权码")
def auth_get_user_key(auth_code: str):
    """通过授权码获取 user_key
    
    授权码需要通过飞书 OAuth 流程获取。
    也可以直接访问 project.feishu.cn，左下角双击头像获取 user_key。
    """
    try:
        from feishu_proj.client import FeishuProjClient
        client = FeishuProjClient()
        result = client.get_user_key_by_code(auth_code)
        
        if result.get("error", {}).get("code") == 0:
            data = result.get("data", {})
            click.echo(f"user_key: {data.get('user_key')}")
            click.echo(f"user_access_token: {data.get('user_access_token', '')[:20]}...")
        else:
            click.echo(f"错误: {result.get('error', {}).get('msg')}", err=True)
            raise SystemExit(1)
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        raise SystemExit(1)


@auth.command("show-config")
def auth_show_config():
    """显示当前配置（不包含敏感信息）"""
    from feishu_proj.client import FeishuProjClient
    try:
        client = FeishuProjClient()
        click.echo(f"API URL: {client.api_url}")
        click.echo(f"Plugin ID: {client.plugin_id}")
        click.echo(f"Has User Key: {'是' if client.user_key else '否'}")
        if client.user_key:
            click.echo(f"User Key: {client.user_key}")
    except ValueError as e:
        click.echo(f"配置错误: {e}", err=True)
        raise SystemExit(1)


@cli.group()
def work_items():
    pass


@work_items.command("list")
@click.option("--project-key", required=True, help="项目 Key")
@click.option("--type-key", default="story", help="工作项类型: story, issue, version, task")
@click.option("--keyword", default=None, help="关键字搜索")
@click.option("--page-size", default=20, help="每页数量")
@click.option("--page-num", default=1, help="分页页码")
@click.option("--planning-version", default=None, help="按版本 ID 筛选")
@click.option("--status", default=None, help="状态筛选")
@click.option("--owner", default=None, help="负责人 user_key")
@click.option("--format", type=click.Choice(["json", "table"]), default="table", help="输出格式")
def work_items_list(project_key, type_key, keyword, page_size, page_num, planning_version, status, owner, format):
    try:
        from feishu_proj.client import FeishuProjClient
        client = FeishuProjClient()
        result = client.filter_work_items(
            project_key=project_key,
            work_item_type_keys=[type_key],
            keyword=keyword,
            page_size=page_size,
            page_num=page_num,
            planning_version=planning_version,
            status=status,
            owner=owner,
        )
        _print_work_items(result, format)
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        raise SystemExit(1)


@work_items.command("get")
@click.option("--project-key", required=True, help="项目 Key")
@click.option("--id", required=True, help="工作项 ID")
@click.option("--type-key", default="story", help="工作项类型")
@click.option("--format", type=click.Choice(["json", "table"]), default="json", help="输出格式")
def work_items_get(project_key, id, type_key, format):
    try:
        from feishu_proj.client import FeishuProjClient
        client = FeishuProjClient()
        result = client.filter_work_items(
            project_key=project_key,
            work_item_type_keys=[type_key],
            work_item_ids=[int(id)],
            page_size=1,
            page_num=1,
        )
        items = result.get("data", [])
        if items:
            if format == "json":
                click.echo(json.dumps(items[0], indent=2, ensure_ascii=False))
            else:
                for key, value in items[0].items():
                    if key == "fields":
                        for f in value:
                            alias = f.get("field_alias") or f.get("field_key")
                            val = f.get("field_value")
                            click.echo(f"  {alias}: {val}")
                    else:
                        click.echo(f"{key}: {value}")
        else:
            click.echo("未找到该工作项")
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        raise SystemExit(1)


@work_items.command("create")
@click.option("--project-key", required=True, help="项目 Key")
@click.option("--type-key", required=True, help="工作项类型: story, issue, task, version")
@click.option("--name", required=True, help="工作项名称")
@click.option("--fields", "fields_json", default=None, help="字段值 JSON (数组格式)")
@click.option("--template-id", default=None, type=int, help="流程模板 ID")
@click.option("--dry-run", is_flag=True, default=False, help="仅预览请求参数，不实际创建")
def work_items_create(project_key, type_key, name, fields_json, template_id, dry_run):
    """创建工作项

    --fields 示例: '[{"field_key":"owner","field_value":"user_key_xxx"}]'
    """
    try:
        field_value_pairs = None
        if fields_json:
            field_value_pairs = json.loads(fields_json)

        if dry_run:
            payload = {
                "work_item_type_key": type_key,
                "name": name,
            }
            if field_value_pairs:
                payload["field_value_pairs"] = field_value_pairs
            if template_id is not None:
                payload["template_id"] = template_id
            click.echo("[DRY RUN] 将创建工作项，请求参数:")
            click.echo(json.dumps(payload, indent=2, ensure_ascii=False))
            return

        data = create_work_item(
            project_key=project_key,
            work_item_type_key=type_key,
            name=name,
            field_value_pairs=field_value_pairs,
            template_id=template_id,
        )
        click.echo(json.dumps(data, indent=2, ensure_ascii=False))
    except json.JSONDecodeError as e:
        click.echo(f"JSON 解析错误: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        raise SystemExit(1)


@work_items.command("update")
@click.option("--project-key", required=True, help="项目 Key")
@click.option("--type-key", required=True, help="工作项类型: story, issue, task, version")
@click.option("--id", "work_item_id", required=True, type=int, help="工作项 ID")
@click.option("--fields", "fields_json", default=None, help="更新字段 JSON (数组格式)")
@click.option("--status", default=None, help="目标状态 key，例: CLOSED / RESOLVED / end / doing")
@click.option("--dry-run", is_flag=True, default=False, help="仅预览请求参数，不实际更新")
def work_items_update(project_key, type_key, work_item_id, fields_json, status, dry_run):
    """更新工作项字段或流转状态

    流转状态示例:
      feishu-proj work-items update --project-key KEY --type-key issue --id ID --status CLOSED

    更新字段示例:
      feishu-proj work-items update --project-key KEY --type-key issue --id ID --fields '[{"field_key":"name","field_value":"x"}]'
    """  # noqa: E501
    if not fields_json and not status:
        click.echo("错误: 必须提供 --fields 或 --status 之一", err=True)
        raise SystemExit(1)
    try:
        from feishu_proj.client import FeishuProjClient
        if status:
            if dry_run:
                click.echo(f"[DRY RUN] 将流转工作项 {type_key}/{work_item_id} 状态到 {status}")
                return
            client = FeishuProjClient()
            data = client.transit_work_item_to_state(
                project_key=project_key,
                work_item_type_key=type_key,
                work_item_id=work_item_id,
                target_state_key=status,
            )
            click.echo(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            update_fields = json.loads(fields_json)  # type: ignore[arg-type]
            if dry_run:
                click.echo(f"[DRY RUN] 将更新工作项 {type_key}/{work_item_id}，请求参数:")
                click.echo(
                    json.dumps({"update_fields": update_fields}, indent=2, ensure_ascii=False)
                )
                return
            data = update_work_item(
                project_key=project_key,
                work_item_type_key=type_key,
                work_item_id=work_item_id,
                update_fields=update_fields,
            )
            click.echo(json.dumps(data, indent=2, ensure_ascii=False))
    except json.JSONDecodeError as e:
        click.echo(f"JSON 解析错误: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        raise SystemExit(1)


@work_items.command("transitions")
@click.option("--project-key", required=True, help="项目 Key")
@click.option("--type-key", required=True, help="工作项类型: story, issue, task")
@click.option("--id", "work_item_id", required=True, type=int, help="工作项 ID")
@click.option("--format", type=click.Choice(["json", "table"]), default="table", help="输出格式")
def work_items_transitions(project_key, type_key, work_item_id, format):
    """查看工作项可用的状态流转列表"""
    try:
        from feishu_proj.client import FeishuProjClient
        client = FeishuProjClient()
        conns = client.get_work_item_transitions(
            project_key=project_key,
            work_item_type_key=type_key,
            work_item_id=work_item_id,
        )
        if format == "json":
            click.echo(json.dumps(conns, indent=2, ensure_ascii=False))
        else:
            if not conns:
                click.echo("无可用流转")
                return
            click.echo(f"{'transition_id'.ljust(16)} | {'from'.ljust(30)} | to")
            click.echo("-" * 75)
            for c in conns:
                tid = str(c.get("transition_id", ""))
                src = c.get("source_state_key", "")
                tgt = c.get("target_state_key", "")
                click.echo(f"{tid.ljust(16)} | {src.ljust(30)} | {tgt}")
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        raise SystemExit(1)


@work_items.command("meta")
@click.option("--project-key", required=True, help="项目 Key")
@click.option("--type-key", default="story", help="工作项类型")
@click.option("--format", type=click.Choice(["json", "table"]), default="json", help="输出格式")
def work_items_meta(project_key, type_key, format):
    """获取创建工作项的元数据（可用字段列表）"""
    try:
        data = get_work_item_meta(
            project_key=project_key,
            work_item_type_key=type_key,
        )
        if format == "json":
            click.echo(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            fields = data.get("data", [])
            if isinstance(fields, dict):
                fields = fields.get("fields", [])
            if not fields:
                click.echo("无数据")
                return
            hdr = (
                f"{'field_key'.ljust(30)} | "
                f"{'field_alias'.ljust(30)} | "
                f"{'field_type'.ljust(20)} | required"
            )
            click.echo(hdr)
            click.echo("-" * 100)
            for f in fields:
                fk = f.get("field_key", "")
                fa = f.get("field_alias", "")
                ft = f.get("field_type_key", "")
                req = "是" if f.get("is_required") else "否"
                click.echo(f"{fk.ljust(30)} | {fa.ljust(30)} | {ft.ljust(20)} | {req}")
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        raise SystemExit(1)


@work_items.command("delete")
@click.option("--project-key", required=True, help="项目 Key")
@click.option("--type-key", required=True, help="工作项类型: story, issue, task, version")
@click.option("--id", "work_item_id", required=True, type=int, help="工作项 ID")
@click.option("--dry-run", is_flag=True, default=False, help="仅预览，不实际删除")
def work_items_delete(project_key: str, type_key: str, work_item_id: int, dry_run: bool):
    """删除工作项（不可恢复，请谨慎操作）"""
    if dry_run:
        click.echo(f"[DRY RUN] 将删除 {type_key}/{work_item_id}（project={project_key}）")
        return
    try:
        data = delete_work_item(
            project_key=project_key,
            work_item_type_key=type_key,
            work_item_id=work_item_id,
        )
        click.echo(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        raise SystemExit(1)


@cli.group()
def users():
    """用户管理命令"""
    pass


def _print_users(items: list, fmt: str) -> None:
    if fmt == "json":
        click.echo(json.dumps(items, indent=2, ensure_ascii=False))
    else:
        if not items:
            click.echo("无数据")
            return
        hdr = f"{'user_key'.ljust(22)} | {'姓名'.ljust(10)} | email"
        click.echo(hdr)
        click.echo("-" * 70)
        for u in items:
            uk   = str(u.get("user_key", "")).ljust(22)
            name = str(u.get("name_cn") or u.get("name", {}).get("default", "")).ljust(10)
            email = u.get("email", "")
            click.echo(f"{uk} | {name} | {email}")
        click.echo(f"\n共 {len(items)} 条")


@users.command("get")
@click.option("--user-key", "user_keys", multiple=True, help="user_key（可多次传入）")
@click.option("--email", "emails", multiple=True, help="邮箱（可多次传入）")
@click.option("--format", type=click.Choice(["json", "table"]), default="table", help="输出格式")
def users_get(user_keys: tuple, emails: tuple, format: str) -> None:
    """按 user_key 或邮箱查询用户信息（可多值）。

    示例：
      feishu-proj users get --user-key <USER_KEY>
      feishu-proj users get --email <EMAIL> --email <EMAIL>
    """
    if not user_keys and not emails:
        click.echo("错误：请至少提供一个 --user-key 或 --email", err=True)
        raise SystemExit(1)
    try:
        from feishu_proj.client import FeishuProjClient
        client = FeishuProjClient()
        items = client.query_users(
            user_keys=list(user_keys) or None,
            emails=list(emails) or None,
        )
        _print_users(items, format)
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        raise SystemExit(1)


@users.command("search")
@click.option("--keyword", required=True, help="邮箱关键字（精确邮箱地址或前缀）")
@click.option("--format", type=click.Choice(["json", "table"]), default="table", help="输出格式")
def users_search(keyword: str, format: str) -> None:
    """按邮箱查询用户信息（调用 /user/query?emails）。

    注意：/user/search 接口在当前企业域不可用，本命令改为按邮箱精确查询。

    示例：
      feishu-proj users search --keyword <EMAIL>
    """
    try:
        from feishu_proj.client import FeishuProjClient
        client = FeishuProjClient()
        items = client.query_users(emails=[keyword])
        _print_users(items, format)
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    cli()