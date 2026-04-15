# feishu-proj-cli

飞书项目 Python CLI & SDK，供 skill 和脚本调用。

## ⚠️ 首要原则：CLI 优先

**任何飞书项目操作，必须先确认 CLI 命令是否已覆盖，有 CLI 就用 CLI，不要写 Python 脚本打补丁。**

| 场景 | 正确做法 | 错误做法 |
|------|---------|---------|
| 查询用户姓名 | `feishu-proj users get --user-key <KEY>` | 写脚本调 `client._request("/user/query", ...)` |
| 获取 story 详情 | `feishu-proj stories get --project-key <KEY> --id <ID>` | 直接实例化 `FeishuProjClient` 手写请求 |
| 更新工作项状态 | `feishu-proj work-items update --status CLOSED` | 手动调 `transit_work_item_state()` |

**CLI 不支持的场景才用 Python SDK**（批量循环、多步组合、结果二次加工等）。即使用 SDK，也应优先调用 `client` 上已有的封装方法，而非直接用 `_request`。

如果遇到 CLI 命令缺失或不满足需求，**正确做法是补充 CLI 命令**（在 `cli.py` 实现），而不是在调用方写临时脚本绕过。

## Setup

```bash
uv sync          # 安装依赖（使用 uv，不是 pip/poetry）
```

`.env` 中配置：
- `FEISHU_USER_KEY`（每人不同）。获取方式：访问飞书项目 → 左下角双击个人头像 → 复制 user_key。
- `PLUGIN_ID` 和 `PLUGIN_SECRET`：从飞书开放平台获取

## Commands

```bash
# Lint
uv run ruff check src/

# Type check
uv run mypy src/

# CLI（安装后可用）
feishu-proj auth show-config
feishu-proj projects list
feishu-proj requirements list --project-key <KEY>
feishu-proj requirements get --project-key <KEY> --id <ID>
feishu-proj bugs list --project-key <KEY>
feishu-proj bugs get --project-key <KEY> --id <ID>
feishu-proj bugs create --project-key <KEY> --name "标题" [--fields JSON] [--dry-run]
feishu-proj bugs update --project-key <KEY> --id <ID> --fields JSON [--dry-run]
feishu-proj bugs update --project-key <KEY> --id <ID> --status CLOSED   # 状态流转（推荐）
feishu-proj bugs delete --project-key <KEY> --id <ID> [--dry-run]
feishu-proj stories list --project-key <KEY>
feishu-proj stories get --project-key <KEY> --id <ID>
feishu-proj stories create --project-key <KEY> --name "标题" [--fields JSON] [--dry-run]
feishu-proj stories update --project-key <KEY> --id <ID> --fields JSON [--dry-run]
feishu-proj stories delete --project-key <KEY> --id <ID> [--dry-run]
feishu-proj versions list --project-key <KEY>
feishu-proj versions get --project-key <KEY> --id <ID>
feishu-proj versions create --project-key <KEY> --name "标题" [--fields JSON] [--dry-run]
feishu-proj versions update --project-key <KEY> --id <ID> --fields JSON [--dry-run]
feishu-proj work-items list --project-key <KEY> --type-key story
feishu-proj work-items create --project-key <KEY> --type-key issue --name "标题" [--dry-run]
feishu-proj work-items update --project-key <KEY> --type-key issue --id <ID> --fields JSON [--dry-run]
feishu-proj work-items update --project-key <KEY> --type-key issue --id <ID> --status CLOSED   # 状态流转（推荐）
feishu-proj work-items delete --project-key <KEY> --type-key issue --id <ID> [--dry-run]
feishu-proj work-items transitions --project-key <KEY> --type-key issue --id <ID>   # 查看可用状态流转
feishu-proj work-items meta --project-key <KEY> --type-key issue
feishu-proj users get --user-key <USER_KEY>
feishu-proj users get --email <EMAIL>
feishu-proj users search --keyword <EMAIL>
```

## Architecture

```
src/feishu_proj/
├── config.py          # plugin_id/plugin_secret 从环境变量读取
├── client.py          # FeishuProjClient — token 管理 + 所有 API 方法
├── tools.py           # Skill 工具接口，返回 {success, data, error}
├── cli.py             # Click CLI 入口
└── api/               # 薄封装层，每个函数新建 FeishuProjClient 实例
    ├── projects.py
    ├── requirements.py
    ├── bugs.py        # get_bugs, get_bug_detail, create_bug, update_bug
    ├── versions.py    # get_versions, get_version_detail, create_version, update_version
    ├── stories.py     # get_stories, get_story_detail, create_story, update_story
    └── work_items.py  # 通用 create/update/meta（type_key 由调用方指定）
```

**调用链**: `tools.py` / `cli.py` → `api/*.py` → `client.py` → 飞书项目 API

## Key Constraints

- **api/ 层无共享 client**：每个函数调用都新建 `FeishuProjClient`，token 会重复获取；如需批量调用，直接用 `FeishuProjClient` 实例更高效
- **Token 自动刷新**：client 内置 token 缓存，过期前 60s 自动续期
- **无测试目录**：dev 依赖声明了 pytest/pytest-asyncio 但尚未编写测试
- **非 MCP**：这是纯 Python SDK，不是 MCP server（README.md 提到的 MCP 实现是外部项目参考）
- **`projects list` 返回 ID 列表**：`data` 字段是字符串数组（如 `["<PROJECT_KEY>"]`），即 project_key，后续所有命令的 `--project-key` 传这个值

## 状态流转（State Transition）

飞书项目工单分两种 pattern：`State`（状态机）和 `Flow`（流程节点）。

### 错误做法

在 `update_fields` 中传 `work_item_status` 作为 field_key → 报错 `"field [work_item_status] is illegal"`。

### 正确做法（两步）

**Step 1：获取 transition_id**（`client.get_work_item_transitions()`）

```
POST /open_api/:project_key/work_item/:type/:id/workflow/query
{"flow_type": 1}   # flow_type=1 = State 模式；0 = 节点流模式
```

返回 `connections` 数组，每项有 `source_state_key`、`target_state_key`、`transition_id`。

**Step 2：执行状态流转**（`client.transit_work_item_state()`）

```
POST /open_api/:project_key/workflow/:type/:id/node/state_change
{"transition_id": <id>}
```

### 一步到位（推荐）

`client.transit_work_item_to_state(project_key, type_key, work_item_id, target_state_key)` — 自动查询当前状态、找 transition_id、执行流转。

CLI 命令：`feishu-proj work-items update --status CLOSED`（或 `bugs update --status CLOSED`）

查看可用状态流转：`feishu-proj work-items transitions --project-key <KEY> --type-key issue --id <任意ID>`

## 用户查询

飞书项目的 `user_key` 是一串**数字 ID**（如 `<USER_KEY>`），不是邮箱前缀。

### CLI 命令

```bash
# 按 user_key 查询（支持多个）
feishu-proj users get --user-key <USER_KEY>
feishu-proj users get --user-key <USER_KEY> --user-key <USER_KEY>

# 按邮箱查询（支持多个）
feishu-proj users get --email <EMAIL>
feishu-proj users get --email <EMAIL> --email <EMAIL>

# search 子命令是 get --email 的快捷方式（按精确邮箱查询）
feishu-proj users search --keyword <EMAIL>
```

两个命令均支持 `--format json` 输出完整 JSON。

### Python SDK

```python
# 按 user_key 批量查姓名（推荐）
users = client.query_users(user_keys=["<USER_KEY>", "<USER_KEY>"])
for u in users:
    print(u["user_key"], u["name_cn"])

# 按 email 查 user_key
users = client.query_users(emails=["<EMAIL>"])
user_key = users[0]["user_key"]
```

### ⚠️ 常见路径错误（直接调用 _request 时）

`_request` 会自动拼 `/open_api` 前缀，不要重复写：

```python
# ❌ 错误 → /open_api/open_api/user/query → 404
client._request("POST", "/open_api/user/query", ...)

# ✅ 正确
client._request("POST", "/user/query", ...)
```

## Style

- Ruff: line-length=100, target py310, rules: E/F/W/I/N/UP/B/C4
- mypy: strict mode
- 中文注释和 docstring

## Story 工作项详细结构

story 类型工作项通过 `client.query_work_item_detail(project_key, "story", [id1, id2, ...])` 批量查询，响应 `data[]` 中每项的关键字段：

### 顶层字段

| 字段 | 说明 |
|------|------|
| `id` | 工作项 ID |
| `name` | 工作项名称 |
| `created_at` | 创建时间（毫秒时间戳） |
| `updated_at` | 最后更新时间（毫秒时间戳） |
| `work_item_status.state_key` | 当前状态：`doing`/`end`/`waiting_for_start` 等 |
| `state_times[]` | 各流程节点的进出时间（见下方） |
| `current_nodes[]` | 当前所处节点（`id`/`name`/`owners`） |
| `fields[]` | 所有自定义字段（`field_key`/`field_alias`/`field_value`） |

### state_times — 时间节点

```python
# 每项结构：{"state_key": "develop", "name": "开发制作", "start_time": 1776227336465, "end_time": 0}
# end_time=0 表示当前仍在该节点
state_map = {s["state_key"]: (s["start_time"], s["end_time"]) for s in item.get("state_times", [])}
dev_start  = state_map.get("develop", (0, 0))[0]   # 进入开发阶段的时间
test_start = state_map.get("test",    (0, 0))[0]   # 进入测试阶段的时间
```

常见 state_key：`start`（准备开始）、`develop`（开发制作）、`test`（QA测试）、`end`（结束）。

### role_owners — 角色负责人

`fields` 中 `field_key="role_owners"` 的 `field_value` 是角色数组，每项 `{"role": "<角色标识>", "owners": ["<USER_KEY>"]}`。

角色标识因项目而异，可通过 `work-items meta` 或实际查询 story 详情来了解本项目有哪些角色。

```python
def get_role_owners(item, role_key):
    for f in item.get("fields", []):
        if f.get("field_key") == "role_owners":
            for ro in (f.get("field_value") or []):
                if ro.get("role") == role_key:
                    return [str(x) for x in (ro.get("owners") or [])]
    return []
```

### 批量查询用法

```python
# 每批最多 20 个 ID，分批请求
details = []
for i in range(0, len(id_list), 20):
    resp = client.query_work_item_detail(project_key, "story", id_list[i:i+20])
    details.extend(resp.get("data", []))
```

> ⚠️ 单次 `query_work_item_detail` 建议不超过 20 个 ID，超出可能被限流或截断。

## References

| 资源 | URL |
|------|-----|
| 飞书项目 MCP (im47cn) | https://github.com/im47cn/feishu-project-mcp |
| 飞书项目 MCP (Roland0511) | https://github.com/Roland0511/mcp-feishu-proj |
| 飞书官方 OpenAPI MCP | https://github.com/larksuite/lark-openapi-mcp |
| 工具功能列表飞书官方文档 ｜ https://project.feishu.cn/b/helpcenter/1ykiuvvj/19wmvt8b |