"""飞书项目 API 客户端"""

import os
import time
from typing import Optional

import httpx
from dotenv import load_dotenv

from feishu_proj.config import PLUGIN_ID, PLUGIN_SECRET, API_URL

load_dotenv()


class FeishuProjClient:
    def __init__(
        self,
        user_key: Optional[str] = None,
    ):
        self.plugin_id = PLUGIN_ID
        self.plugin_secret = PLUGIN_SECRET
        self.user_key = user_key or os.getenv("FEISHU_USER_KEY")
        self.api_url = API_URL

        if not self.user_key:
            raise ValueError(
                "user_key 必须提供，或设置环境变量 FEISHU_USER_KEY"
            )

        self._token: Optional[str] = None
        self._token_expire: int = 0

    def _ensure_token(self) -> str:
        if self._token and int(time.time()) < self._token_expire - 60:
            return self._token

        url = f"{self.api_url}/open_api/authen/plugin_token"
        payload = {"plugin_id": self.plugin_id, "plugin_secret": self.plugin_secret}

        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            resp_data = response.json()

        error_info = resp_data.get("error", {})
        if error_info.get("code") != 0:
            raise RuntimeError(f"获取 token 失败: {error_info.get('msg')}")

        token_info = resp_data.get("data", {})
        self._token = token_info.get("token")
        self._token_expire = int(time.time()) + token_info.get("expire_time", 3600)

        return self._token

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        json_data: Optional[dict] = None,
    ) -> dict:
        token = self._ensure_token()
        headers = {
            "X-PLUGIN-TOKEN": token,
            "X-USER-KEY": self.user_key,
            "Content-Type": "application/json",
        }
        url = f"{self.api_url}/open_api{endpoint}"

        with httpx.Client(timeout=30.0) as client:
            response = client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
            )
            if response.is_error:
                # 优先从响应体中提取飞书 API 的 err_msg，让错误信息更易读
                try:
                    body = response.json()
                    api_err = body.get("err") or {}
                    api_msg = (
                        api_err.get("msg")
                        or body.get("err_msg")
                        or body.get("message")
                        or response.text
                    )
                    raise RuntimeError(
                        f"API 错误 {response.status_code}: {api_msg} (url={url})"
                    )
                except (ValueError, KeyError):
                    response.raise_for_status()
            return response.json()

    def get_projects(self, page_size: int = 50, page_token: str = "") -> dict:
        json_data = {"page_size": page_size, "user_key": self.user_key}
        if page_token:
            json_data["page_token"] = page_token

        return self._request("POST", "/projects", json_data=json_data)

    def get_requirements(
        self,
        project_key: str,
        page_size: int = 50,
        page_num: int = 1,
        status: Optional[str] = None,
    ) -> dict:
        json_data = {
            "project_key": project_key,
            "work_item_type_keys": ["story"],
            "page_size": page_size,
            "page_num": page_num,
            "user_key": self.user_key,
        }
        if status:
            json_data["work_item_status"] = [status]

        return self._request("POST", f"/{project_key}/work_item/filter", json_data=json_data)

    def get_requirement_detail(self, project_key: str, requirement_id: str) -> dict:
        json_data = {
            "project_key": project_key,
            "work_item_type_key": "story",
            "work_item_id": requirement_id,
            "user_key": self.user_key,
        }
        return self._request("POST", f"/{project_key}/work_item/get", json_data=json_data)

    def get_bugs(
        self,
        project_key: str,
        page_size: int = 50,
        page_num: int = 1,
        status: Optional[str] = None,
        owner: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> dict:
        json_data = {
            "project_key": project_key,
            "work_item_type_keys": ["issue"],
            "page_size": page_size,
            "page_num": page_num,
            "user_key": self.user_key,
        }
        if keyword:
            json_data["keyword"] = keyword

        result = self._request("POST", f"/{project_key}/work_item/filter", json_data=json_data)

        items = result.get("data", [])
        if status:
            status_list = [s.strip() for s in status.split(",")]
            items = [
                item for item in items
                if item.get("sub_stage") in status_list
            ]

        if owner:
            items = [
                item for item in items
                if owner in str(self._get_field(item, "owner", ""))
            ]

        result["data"] = items
        return result

    def get_bug_detail(self, project_key: str, bug_id: str) -> dict:
        json_data = {
            "project_key": project_key,
            "work_item_type_key": "issue",
            "work_item_id": bug_id,
            "user_key": self.user_key,
        }
        return self._request("POST", f"/{project_key}/work_item/get", json_data=json_data)

    def get_user_key_by_code(self, auth_code: str) -> dict:
        """通过授权码获取用户 user_key
        
        Args:
            auth_code: 授权码，通过飞书 OAuth 流程获取
            
        Returns:
            包含 user_key 的响应
        """
        token = self._ensure_token()
        headers = {
            "X-PLUGIN-TOKEN": token,
            "Content-Type": "application/json",
        }
        url = f"{self.api_url}/open_api/authen/user_plugin_token"
        payload = {"auth_code": auth_code}

        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()

    def get_current_user_key(self) -> str:
        """获取当前用户的 user_key
        
        通过飞书项目界面获取：左下角双击个人头像即可看到 user_key
        """
        if not self.user_key:
            raise ValueError(
                "user_key 未设置。请通过以下方式获取 user_key:\n"
                "1. 访问 https://project.feishu.cn\n"
                "2. 左下角双击你的个人头像\n"
                "3. 复制显示的 user_key 并设置为环境变量 FEISHU_USER_KEY"
            )
        return self.user_key

    def query_users(
        self,
        user_keys: list[str] | None = None,
        emails: list[str] | None = None,
    ) -> list[dict]:
        """按 user_key 或 email 批量查询用户信息。

        两种方式二选一，可一次传多个值（建议每批不超过 50 个）。

        Args:
            user_keys: user_key 列表（如 ``["<USER_KEY>"]``）
            emails:    邮箱列表（如 ``["<EMAIL>"]``）

        Returns:
            用户信息列表，每项包含 ``user_key`` / ``name_cn`` / ``email`` / ``avatar_url``。

        Raises:
            ValueError: user_keys 和 emails 均未提供时抛出。

        Note:
            ``/user/search``（按姓名关键字）在当前企业域返回空列表，不可用。
            需要查姓名时，请先从工作项字段中取 user_key，再调用本方法反查。
        """
        if not user_keys and not emails:
            raise ValueError("user_keys 或 emails 至少提供一个")

        payload: dict = {}
        if user_keys:
            payload["user_keys"] = list(user_keys)
        if emails:
            payload["emails"] = list(emails)

        resp = self._request("POST", "/user/query", json_data=payload)
        return resp.get("data", [])

    def get_versions(
        self,
        project_key: str,
        page_size: int = 20,
        page_num: int = 1,
        keyword: Optional[str] = None,
    ) -> dict:
        json_data = {
            "project_key": project_key,
            "work_item_type_keys": ["version"],
            "page_size": page_size,
            "page_num": page_num,
            "user_key": self.user_key,
        }
        if keyword:
            json_data["keyword"] = keyword
        return self._request("POST", f"/{project_key}/work_item/filter", json_data=json_data)

    def get_work_item_types(self) -> list:
        return [
            {"key": "story", "name": "需求"},
            {"key": "issue", "name": "缺陷"},
            {"key": "version", "name": "版本"},
            {"key": "task", "name": "任务"},
        ]

    def get_stories(
        self,
        project_key: str,
        page_size: int = 50,
        page_num: int = 1,
        status: Optional[str] = None,
        planning_version: Optional[str] = None,
        owner: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> dict:
        json_data = {
            "project_key": project_key,
            "work_item_type_keys": ["story"],
            "page_size": page_size,
            "page_num": page_num,
            "user_key": self.user_key,
        }
        if status:
            json_data["work_item_status"] = [s.strip() for s in status.split(",")]
        if keyword:
            json_data["keyword"] = keyword

        result = self._request("POST", f"/{project_key}/work_item/filter", json_data=json_data)

        items = result.get("data", [])
        vid = planning_version
        if vid:
            items = [
                item for item in items
                if any(
                    str(vid) in [str(v) for v in f.get("field_value", [])]
                    for f in item.get("fields", [])
                    if f.get("field_key") == "planning_version"
                )
            ]

        if owner:
            items = [
                item for item in items
                if owner in str(self._get_field(item, "owner", ""))
            ]

        result["data"] = items
        return result

    def filter_work_items(
        self,
        project_key: str,
        work_item_type_keys: list,
        keyword: Optional[str] = None,
        page_size: int = 20,
        page_num: int = 1,
        planning_version: Optional[str] = None,
        status: Optional[str] = None,
        owner: Optional[str] = None,
        work_item_ids: Optional[list] = None,
    ) -> dict:
        json_data = {
            "project_key": project_key,
            "work_item_type_keys": work_item_type_keys,
            "page_size": page_size,
            "page_num": page_num,
            "user_key": self.user_key,
        }
        if keyword:
            json_data["keyword"] = keyword
        if work_item_ids:
            json_data["work_item_ids"] = [int(i) for i in work_item_ids]
        if status:
            json_data["work_item_status"] = [s.strip() for s in status.split(",")]

        result = self._request("POST", f"/{project_key}/work_item/filter", json_data=json_data)

        items = result.get("data", [])
        
        # 客户端过滤: planning_version
        if planning_version:
            vid = planning_version
            items = [
                item for item in items
                if any(
                    str(vid) in [str(v) for v in f.get("field_value", [])]
                    for f in item.get("fields", [])
                    if f.get("field_key") == "planning_version"
                )
            ]

        # 客户端过滤: owner
        if owner:
            items = [
                item for item in items
                if owner in str(self._get_field(item, "owner", ""))
            ]

        result["data"] = items
        return result

    def create_work_item(
        self,
        project_key: str,
        work_item_type_key: str,
        name: str,
        field_value_pairs: Optional[list] = None,
        template_id: Optional[int] = None,
    ) -> dict:
        """创建工作项

        Args:
            project_key: 项目 Key
            work_item_type_key: 工作项类型 (story/issue/task/version)
            name: 工作项名称
            field_value_pairs: 字段值列表，每项为 dict:
                - field_key: 字段标识
                - field_value: 字段值
                - field_alias: 字段别名（可选，与 field_key 二选一）
                - field_type_key: 字段类型（可选）
                - target_state: 目标状态（可选），dict with state_key, transition_id
                - help_description: 帮助描述（可选）
            template_id: 流程模板 ID（可选）

        Returns:
            创建结果，包含工作项 ID 等信息
        """
        json_data: dict = {
            "work_item_type_key": work_item_type_key,
            "name": name,
        }
        if field_value_pairs:
            json_data["field_value_pairs"] = field_value_pairs
        if template_id is not None:
            json_data["template_id"] = template_id

        return self._request(
            "POST", f"/{project_key}/work_item/create", json_data=json_data
        )

    def update_work_item(
        self,
        project_key: str,
        work_item_type_key: str,
        work_item_id: int,
        update_fields: list,
    ) -> dict:
        """更新工作项

        Args:
            project_key: 项目 Key
            work_item_type_key: 工作项类型 (story/issue/task/version)
            work_item_id: 工作项 ID
            update_fields: 更新字段列表，每项为 dict:
                - field_key: 字段标识
                - field_value: 字段值
                - field_alias: 字段别名（可选，与 field_key 二选一）
                - field_type_key: 字段类型（可选）
                - target_state: 目标状态（可选），dict with state_key, transition_id
                - help_description: 帮助描述（可选）

        Returns:
            更新结果
        """
        json_data = {"update_fields": update_fields}
        return self._request(
            "PUT",
            f"/{project_key}/work_item/{work_item_type_key}/{work_item_id}",
            json_data=json_data,
        )

    def get_work_item_meta(
        self,
        project_key: str,
        work_item_type_key: str,
    ) -> dict:
        """获取创建工作项的元数据（可用字段列表）

        Args:
            project_key: 项目 Key
            work_item_type_key: 工作项类型 (story/issue/task/version)

        Returns:
            元数据，包含可用字段定义
        """
        return self._request(
            "GET",
            f"/{project_key}/work_item/{work_item_type_key}/meta",
        )

    def query_work_item_detail(
        self,
        project_key: str,
        work_item_type_key: str,
        work_item_ids: list,
        fields: Optional[list] = None,
    ) -> dict:
        """查询工作项详情（使用 query 接口，支持批量）

        Args:
            project_key: 项目 Key
            work_item_type_key: 工作项类型
            work_item_ids: 工作项 ID 列表
            fields: 需要返回的字段列表（可选）

        Returns:
            工作项详情列表
        """
        json_data: dict = {
            "work_item_ids": [int(i) for i in work_item_ids],
        }
        if fields:
            json_data["fields"] = fields

        return self._request(
            "POST",
            f"/{project_key}/work_item/{work_item_type_key}/query",
            json_data=json_data,
        )

    def get_work_item_transitions(
        self,
        project_key: str,
        work_item_type_key: str,
        work_item_id: int,
    ) -> list:
        """获取工作项可用的状态流转列表

        使用 workflow/query 接口（flow_type=1 对应 State 模式）。

        Args:
            project_key: 项目 Key
            work_item_type_key: 工作项类型 (story/issue/task)
            work_item_id: 工作项 ID

        Returns:
            connections 列表，每项包含 source_state_key/target_state_key/transition_id
        """
        result = self._request(
            "POST",
            f"/{project_key}/work_item/{work_item_type_key}/{work_item_id}/workflow/query",
            json_data={"fields": [], "flow_type": 1},
        )
        return result.get("data", {}).get("connections", [])

    def transit_work_item_state(
        self,
        project_key: str,
        work_item_type_key: str,
        work_item_id: int,
        transition_id: int,
        fields: Optional[list] = None,
    ) -> dict:
        """执行工作项状态流转

        使用 workflow/:type/:id/node/state_change 接口。

        Args:
            project_key: 项目 Key
            work_item_type_key: 工作项类型 (story/issue/task)
            work_item_id: 工作项 ID
            transition_id: 流转 ID，从 get_work_item_transitions() 获取
            fields: 流转时附带的字段更新（可选）

        Returns:
            API 响应
        """
        return self._request(
            "POST",
            f"/{project_key}/workflow/{work_item_type_key}/{work_item_id}/node/state_change",
            json_data={
                "transition_id": transition_id,
                "fields": fields or [],
                "role_owners": [],
            },
        )

    def transit_work_item_to_state(
        self,
        project_key: str,
        work_item_type_key: str,
        work_item_id: int,
        target_state_key: str,
    ) -> dict:
        """将工作项流转到指定状态（自动查找并执行流转链）

        会先查询当前状态，再从 connections 中找到 target_state_key 对应的 transition_id。
        如果当前状态不能直接流转到目标状态，会报错（不支持多跳自动链式流转）。

        Args:
            project_key: 项目 Key
            work_item_type_key: 工作项类型
            work_item_id: 工作项 ID
            target_state_key: 目标状态 key，如 'CLOSED'/'RESOLVED'/'OPEN' 等

        Returns:
            最后一次 API 响应

        Raises:
            ValueError: 当前状态不支持流转到目标状态时
        """
        result = self._request(
            "POST",
            f"/{project_key}/work_item/{work_item_type_key}/query",
            json_data={"work_item_ids": [work_item_id]},
        )
        items = result.get("data", [])
        if not items:
            raise ValueError(f"工作项 {work_item_id} 不存在")

        pattern = items[0].get("pattern", "")
        if pattern == "Node":
            raise ValueError(
                f"工作项 {work_item_id}（{work_item_type_key}）使用节点流（Node）模式工作流，"
                "CLI 的 --status 参数仅支持状态机（State）模式（如 issue 类型）。"
                "Node 模式的工作项请通过飞书项目 Web 界面手动推进节点。"
            )

        current_state = items[0].get("work_item_status", {}).get("state_key", "")

        if current_state == target_state_key:
            return {"already_in_target_state": True, "state_key": target_state_key}

        connections = self.get_work_item_transitions(
            project_key, work_item_type_key, work_item_id
        )
        matched = [
            c for c in connections
            if c.get("source_state_key") == current_state
            and c.get("target_state_key") == target_state_key
        ]
        if not matched:
            available = [
                c.get("target_state_key")
                for c in connections
                if c.get("source_state_key") == current_state
            ]
            raise ValueError(
                f"当前状态 '{current_state}' 不能直接流转到 '{target_state_key}'。"
                f"可用目标状态: {available}"
            )

        transition_id = matched[0]["transition_id"]
        return self.transit_work_item_state(
            project_key, work_item_type_key, work_item_id, transition_id
        )

    def delete_work_item(
        self,
        project_key: str,
        work_item_type_key: str,
        work_item_id: int,
    ) -> dict:
        return self._request(
            "DELETE",
            f"/{project_key}/work_item/{work_item_type_key}/{work_item_id}",
        )

    @staticmethod
    def _get_field(item: dict, field_key: str, default=None):
        for f in item.get("fields", []):
            if f.get("field_key") == field_key:
                return f.get("field_value", default)
        return default
