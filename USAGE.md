# 飞书项目 CLI 使用指南

## 前置配置

```bash
# 安装依赖
uv sync

# 配置 .env（FEISHU_USER_KEY 每人不同）
cp .env.example .env
# 编辑 .env，填入你的 user_key
```

获取 `user_key` 的方式：访问飞书项目 → 左下角双击个人头像 → 复制 `user_key`。

验证配置是否生效：

```bash
feishu-proj auth show-config
```

---

## 命令总览

| 命令 | 说明 | 写操作 |
|------|------|--------|
| `projects list` | 获取项目列表 | ❌ |
| `requirements list/get` | 需求列表/详情 | ❌ |
| `bugs list/get` | 缺陷列表/详情 | ❌ |
| `bugs create` | 创建缺陷 | ✅ |
| `bugs update` | 更新缺陷 | ✅ |
| `bugs delete` | 删除缺陷（不可恢复） | ✅ |
| `stories list/get` | 需求/故事列表/详情 | ❌ |
| `stories create` | 创建需求 | ✅ |
| `stories update` | 更新需求 | ✅ |
| `stories delete` | 删除需求（不可恢复） | ✅ |
| `versions list/get` | 版本列表/详情 | ❌ |
| `versions create` | 创建版本 | ✅ |
| `versions update` | 更新版本 | ✅ |
| `work-items list/get` | 工作项列表/详情（通用） | ❌ |
| `work-items meta` | 创建工作项的可用字段 | ❌ |
| `work-items create` | 创建工作项（通用） | ✅ |
| `work-items update` | 更新工作项字段或流转状态 | ✅ |
| `work-items delete` | 删除工作项（通用，不可恢复） | ✅ |
| `work-items transitions` | 查看可用状态流转列表 | ❌ |
| `work-item-types list` | 工作项类型列表 | ❌ |
| `users get` | 按 user_key 或邮箱查询用户（支持多值） | ❌ |
| `users search` | 按精确邮箱查询用户（`get --email` 快捷方式） | ❌ |
| `auth show-config` | 显示当前配置 | ❌ |

---

## 查询类命令

### projects list

```bash
feishu-proj projects list
feishu-proj projects list --format table
```

返回的 `data` 是项目 ID 列表（如 `["<PROJECT_KEY>"]`），不是对象数组。后续命令的 `--project-key` 就用这个 ID。

### work-items list

```bash
# 列出需求（默认 type-key=story）
feishu-proj work-items list --project-key <KEY>

# 列出缺陷
feishu-proj work-items list --project-key <KEY> --type-key issue

# 按关键字搜索
feishu-proj work-items list --project-key <KEY> --keyword "登录"

# 按状态筛选（逗号分隔多个状态）
feishu-proj work-items list --project-key <KEY> --status DONE,CLOSED

# 按负责人筛选
feishu-proj work-items list --project-key <KEY> --owner <user_key>

# 按版本筛选
feishu-proj work-items list --project-key <KEY> --planning-version <version_id>
```

`--type-key` 可选值：`story`（需求）、`issue`（缺陷）、`version`（版本）、`task`（任务）。

### work-items get

```bash
feishu-proj work-items get --project-key <KEY> --id <ID> --type-key issue
```

返回完整的工作项 JSON，包含 `fields` 数组。每个 field 有 `field_key`、`field_alias`、`field_value`、`field_type_key` 等属性。

### bugs / stories / versions — list / get

这些是针对各类型的专属命令，预设了 `--type-key`，比通用的 `work-items` 命令更简洁。

```bash
# 列表（支持 --keyword / --status / --owner 筛选）
feishu-proj bugs list --project-key <KEY> --keyword "崩溃"
feishu-proj stories list --project-key <KEY> --status DONE
feishu-proj versions list --project-key <KEY>

# 详情（返回完整 JSON，含 fields 数组）
feishu-proj bugs get --project-key <KEY> --id <ID>
feishu-proj stories get --project-key <KEY> --id <ID>
feishu-proj versions get --project-key <KEY> --id <ID>
```

> **注意** ：`bugs list` 默认只显示 `OPEN` 和 `RESOLVED` 状态的缺陷。如需查看所有状态，传 `--status "OPEN,RESOLVED,DONE,CLOSED"`。

### users get / users search

```bash
# 按 user_key 查询（可多次传 --user-key）
feishu-proj users get --user-key <USER_KEY>
feishu-proj users get --user-key <USER_KEY> --user-key <USER_KEY>

# 按邮箱查询（可多次传 --email）
feishu-proj users get --email <EMAIL> --email <EMAIL>

# search 是 get --email 的快捷方式，接受精确邮箱
feishu-proj users search --keyword <EMAIL>
```

返回 `user_key`、姓名、邮箱，`user_key` 用于创建/更新工作项时指定负责人。

---

## 写操作命令

### bugs / stories / versions — create / update

专属命令与通用 `work-items create/update` 等价，但不需要传 `--type-key`，语义更直观。

```bash
# 创建缺陷
feishu-proj bugs create \
  --project-key <KEY> \
  --name "缺陷标题" \
  --fields '[{"field_key":"issue_reporter","field_value":["你的user_key"]},{"field_key":"issue_stage","field_value":"stage_first"}]'

# 创建需求
feishu-proj stories create \
  --project-key <KEY> \
  --name "需求标题"

# 创建版本
feishu-proj versions create \
  --project-key <KEY> \
  --name "v1.2.0"

# 更新缺陷名称
feishu-proj bugs update \
  --project-key <KEY> \
  --id <ID> \
  --fields '[{"field_key":"name","field_value":"新标题"}]'

# 更新需求状态
feishu-proj stories update \
  --project-key <KEY> \
  --id <ID> \
  --fields '[{"field_key":"sub_stage","field_value":"DONE","target_state":{"state_key":"DONE","transition_id":1}}]'

# 更新版本名称
feishu-proj versions update \
  --project-key <KEY> \
  --id <ID> \
  --fields '[{"field_key":"name","field_value":"v1.2.1"}]'
```

```bash
# 删除缺陷（不可恢复）
feishu-proj bugs delete --project-key <KEY> --id <ID>

# 删除需求（不可恢复）
feishu-proj stories delete --project-key <KEY> --id <ID>

# 删除任意类型工作项（通用）
feishu-proj work-items delete --project-key <KEY> --type-key issue --id <ID>
```

> ⚠️ **删除不可恢复**，建议先 `--dry-run` 确认目标再执行。

所有写操作均支持 `--dry-run`，预览请求参数而不实际执行：

```bash
feishu-proj bugs create --project-key <KEY> --name "测试" --dry-run
feishu-proj stories update --project-key <KEY> --id <ID> --fields '[...]' --dry-run
```

> **何时用专属命令 vs 通用命令**：操作单一类型时优先用专属命令（更简洁）；需要操作 `task` 等没有专属命令的类型时，使用 `work-items` 通用命令。

---

### work-items meta — 查看可用字段

创建工作项前，**务必先执行此命令** ，了解目标项目有哪些字段、哪些是必填、字段类型是什么。

```bash
feishu-proj work-items meta --project-key <KEY> --type-key issue
feishu-proj work-items meta --project-key <KEY> --type-key issue --format table
```

table 格式输出示例：

```
field_key                      | field_alias                    | field_type           | required
----------------------------------------------------------------------------------------------------
name                           | name                           | text                 | 是
issue_reporter                 | issue_reporter                 | multi_user           | 是
issue_stage                    | issue_stage                    | select               | 是
description                    | description                    | multi_text           | 是
owner                          | owner                          | user                 | 否
```

**关键字段说明** ：

| field_type_key | 含义 | field_value 格式 |
|----------------|------|-----------------|
| `text` | 单行文本 | `"字符串"` |
| `multi_text` | 多行文本 | `"字符串"` |
| `user` | 单选用户 | `"user_key"` |
| `multi_user` | 多选用户 | `["user_key1", "user_key2"]` |
| `select` | 单选下拉 | `"option_value"` （不是 label，是 value） |
| `multi_select` | 多选下拉 | `["value1", "value2"]` |
| `date` | 日期 | `时间戳毫秒` |
| `number` | 数字 | `123` |
| `bool` | 布尔 | `true` / `false` |
| `work_item_related_select` | 关联单选 | `id` |
| `work_item_related_multi_select` | 关联多选 | `[id1, id2]` |
| `work_item_template` | 流程模板 | `{"id": 123, "version": 1}` |

### work-items create — 创建工作项

```bash
# 最简创建（仅名称）
feishu-proj work-items create \
  --project-key <KEY> \
  --type-key issue \
  --name "缺陷标题"

# 带字段创建
feishu-proj work-items create \
  --project-key <KEY> \
  --type-key issue \
  --name "缺陷标题" \
  --fields '[{"field_key":"issue_reporter","field_value":["<USER_KEY>"]}]'

# 指定流程模板
feishu-proj work-items create \
  --project-key <KEY> \
  --type-key story \
  --name "需求标题" \
  --template-id 25883

# dry-run 预览（不实际创建）
feishu-proj work-items create \
  --project-key <KEY> \
  --type-key issue \
  --name "测试" \
  --dry-run
```

**`--fields` JSON 格式** ：

```json
[
  {
    "field_key": "字段标识",
    "field_value": "字段值",
    "field_alias": "字段别名（可选，与 field_key 二选一）",
    "field_type_key": "字段类型（可选）",
    "target_state": {
      "state_key": "目标状态",
      "transition_id": 1
    }
  }
]
```

创建成功后返回：

```json
{
  "err_code": 0,
  "data": 6962242070
}
```

`data` 就是新建工作项的 ID。

### work-items update — 更新工作项字段或状态

```bash
# 更新名称
feishu-proj work-items update \
  --project-key <KEY> --type-key issue --id 6962242070 \
  --fields '[{"field_key":"name","field_value":"新名称"}]'

# 更新描述
feishu-proj work-items update \
  --project-key <KEY> --type-key issue --id 6962242070 \
  --fields '[{"field_key":"description","field_value":"新的详细描述"}]'

# 状态流转（推荐 --status，自动查找 transition_id）
feishu-proj work-items update \
  --project-key <KEY> --type-key issue --id 6962242070 --status CLOSED

# dry-run 预览状态流转
feishu-proj work-items update \
  --project-key <KEY> --type-key issue --id 6962242070 --status CLOSED --dry-run
```

### work-items transitions — 查看可用状态流转

```bash
feishu-proj work-items transitions --project-key <KEY> --type-key issue --id <ID>
```

输出示例：

```
transition_id    | from                           | to
---------------------------------------------------------------------------
3180982          | OPEN                           | IN PROGRESS
3180983          | OPEN                           | RESOLVED
3180984          | OPEN                           | bug_state_wont_fix
3180996          | RESOLVED                       | CLOSED
3180997          | CLOSED                         | REOPENED
```

**`--fields` JSON 格式**（只更新普通字段时使用，状态流转统一用 `--status`）：

```json
[
  {
    "field_key": "字段标识",
    "field_value": "新值"
  }
]
```

---

## 常见易错点

### 1. project-key 不是项目名称

`--project-key` 是项目的内部 ID（如 `<PROJECT_KEY>`），不是你在界面上看到的项目显示名。通过 `projects list` 获取。

### 2. user_key 不是用户名

负责人、报告人等用户字段传的是 `user_key`（一串数字，如 `<USER_KEY>`），不是姓名。通过 `users search --keyword "姓名"` 获取。

### 3. select 字段传 value 而非 label

下拉选择字段的 `field_value` 必须传选项的 `value`（如 `"stage_first"`），不能传 `label`（如 `"测试阶段"`）。通过 `work-items meta` 查看字段的 `options` 列表获取合法 value。

**错误** ：

```bash
--fields '[{"field_key":"issue_stage","field_value":"测试阶段"}]'
```

**正确** ：

```bash
--fields '[{"field_key":"issue_stage","field_value":"stage_first"}]'
```

### 4. multi_user 字段值是数组

`issue_reporter`、`watchers` 等多选用户字段的值是数组，即使只有一个用户也要传数组：

**错误** ：

```json
{"field_key": "issue_reporter", "field_value": "<USER_KEY>"}
```

**正确** ：

```json
{"field_key": "issue_reporter", "field_value": ["<USER_KEY>"]}
```

### 5. 状态流转必须用 `--status` 或专用接口，不能直接传 `work_item_status` 字段

飞书项目状态是**状态机**，不是普通字段，有以下限制：

- `update_fields` 中传 `work_item_status` 字段 → 报错 `"field [work_item_status] is illegal"`
- 正确做法是通过专用接口执行状态流转（`POST /workflow/:type/:id/node/state_change`）

**推荐用法（自动处理 transition_id）**：

```bash
# 关闭 issue（当前状态必须是 RESOLVED，否则先 RESOLVED 再 CLOSED）
feishu-proj bugs update --project-key <KEY> --id <ID> --status CLOSED

# 查看当前状态可流转到哪些状态
feishu-proj work-items transitions --project-key <KEY> --type-key issue --id <ID>
```

`transit_work_item_to_state` 方法只支持**单步**流转（当前状态直接到目标状态）。如果需要跨多个状态（如 OPEN → RESOLVED → CLOSED），需分两次执行：

```bash
feishu-proj bugs update --project-key <KEY> --id <ID> --status RESOLVED
feishu-proj bugs update --project-key <KEY> --id <ID> --status CLOSED
```

### 10. story 不支持 `--status` 状态流转

`story` 类型使用**节点流（Node）** 模式工作流，而 `issue` 类型使用**状态机（State）** 模式。`--status` 参数只支持 State 模式。

对 story 执行 `--status` 会报错：

```
错误: 工作项 <ID>（story）使用节点流（Node）模式工作流，CLI 的 --status 参数仅支持状态机（State）模式（如 issue 类型）。Node 模式的工作项请通过飞书项目 Web 界面手动推进节点。
```

story 的字段更新（如修改名称、负责人）仍然正常工作：

```bash
feishu-proj stories update --project-key <KEY> --id <ID> \
  --fields '[{"field_key":"name","field_value":"新标题"}]'
```

### 6. --fields JSON 在 shell 中需要正确转义

JSON 字符串在 shell 中必须用单引号包裹（防止双引号被 shell 解析），且确保 JSON 本身合法：

```bash
# ✅ 正确：单引号包裹
--fields '[{"field_key":"name","field_value":"测试"}]'

# ❌ 错误：双引号包裹，shell 会解析内部双引号
--fields "[{\"field_key\":\"name\",\"field_value\":\"测试\"}]"
```

### 11. bugs list 默认过滤状态

`bugs list` 默认只返回 `OPEN` 和 `RESOLVED` 状态的缺陷。如果想看全部（包括 `DONE`、`CLOSED` 等），需要显式传 `--status`：

```bash
feishu-proj bugs list --project-key <KEY> --status "OPEN,RESOLVED,DONE,CLOSED"
```

### 12. work-items get 的 type-key 必须匹配

如果工作项是 `issue` 类型，`--type-key` 必须传 `issue`，传 `story` 会查不到。不确定类型时，可以先用 `work-items list` 加 `--keyword` 搜索。

### 13. 创建时缺少必填字段

不同项目的必填字段不同。创建失败时，先用 `work-items meta` 查看哪些字段 `required=是`，确保 `--fields` 中包含所有必填字段。常见必填字段：`name`（已通过 `--name` 传入）、`issue_reporter`（缺陷报告人）、`issue_stage`（发现阶段）。

---

## 使用技巧

### 1. 先 dry-run 再执行

写操作命令都支持 `--dry-run`，会打印实际发送的请求参数而不执行。养成先 dry-run 再执行的习惯：

```bash
feishu-proj work-items create --project-key <KEY> --type-key issue --name "测试" --dry-run
# 确认参数无误后去掉 --dry-run
feishu-proj work-items create --project-key <KEY> --type-key issue --name "测试"
```

### 2. 用 meta 命令探索字段

不确定某个字段怎么填时，先查 meta：

```bash
feishu-proj work-items meta --project-key <KEY> --type-key issue --format table
```

重点关注 `field_type_key`（决定值格式）和 `options`（下拉选项的合法值）。

### 3. 用 get 命令确认更新结果

更新后用 `get` 命令确认字段已正确变更：

```bash
feishu-proj work-items get --project-key <KEY> --type-key issue --id <ID>
```

### 4. 用 jq 过滤输出

所有命令默认输出 JSON，可以配合 `jq` 提取需要的字段：

```bash
# 提取工作项 ID 和名称
feishu-proj work-items list --project-key <KEY> --type-key issue \
  | jq '.data[] | {id, name, status: .sub_stage}'

# 提取某个字段的值
feishu-proj work-items get --project-key <KEY> --type-key issue --id <ID> \
  | jq '.fields[] | select(.field_key == "owner") | .field_value'
```

### 5. 批量操作用 Python SDK

CLI 适合交互式使用。如需批量创建/更新，直接用 Python SDK 更高效（共享 client 实例，避免重复获取 token）：

```python
from feishu_proj.client import FeishuProjClient

client = FeishuProjClient()

# 批量创建
for name in ["缺陷A", "缺陷B", "缺陷C"]:
    result = client.create_work_item(
        project_key="<PROJECT_KEY>",
        work_item_type_key="issue",
        name=name,
        field_value_pairs=[
            {"field_key": "issue_reporter", "field_value": [client.user_key]},
        ],
    )
    print(f"创建: {name} -> ID={result.get('data')}")
```

### 6. 批量查询 story 详情（含角色/时间节点）

CLI 的 `stories get` 每次只能查单条，脚本中批量查详情请用 `query_work_item_detail`：

```python
from feishu_proj.client import FeishuProjClient
client = FeishuProjClient()

PROJECT_KEY = "<PROJECT_KEY>"

# Step 1：获取列表（client.get_stories 返回 filter 结果，包含基础字段）
stories = client.get_stories(PROJECT_KEY, page_size=50).get("data", [])
id_list = [s["id"] for s in stories]

# Step 2：分批查详情（每批 ≤20，超出可能被限流）
details = []
for i in range(0, len(id_list), 20):
    resp = client.query_work_item_detail(PROJECT_KEY, "story", id_list[i:i+20])
    details.extend(resp.get("data", []))

# Step 3：提取角色负责人
def get_role_owners(item, role_key):
    for f in item.get("fields", []):
        if f.get("field_key") == "role_owners":
            for ro in (f.get("field_value") or []):
                if ro.get("role") == role_key:
                    return [str(x) for x in (ro.get("owners") or [])]
    return []

for d in details:
    pm_keys  = get_role_owners(d, "PM")
    qa_keys  = get_role_owners(d, "role_qa_leader")
    dev_keys = (get_role_owners(d, "role_dev_client_leader")
              + get_role_owners(d, "role_dev_act_leader"))

    # Step 4：从 state_times 读取各阶段起止时间
    state_map = {s["state_key"]: (s["start_time"], s["end_time"])
                 for s in d.get("state_times", [])}
    dev_start  = state_map.get("develop", (0, 0))[0]   # 开发开始（ms 时间戳）
    test_start = state_map.get("test",    (0, 0))[0]   # 测试开始
```

**story 常见 state_key**：`start`（准备开始）→ `develop`（开发制作）→ `test`（QA测试）→ `end`（结束）。`end_time=0` 表示当前仍在该节点。

### 6. field_key 与 field_alias 二选一

`--fields` 中可以用 `field_alias` 代替 `field_key`。alias 通常更可读（如 `owner`、`description`），但有些字段没有 alias（显示为空），此时只能用 `field_key`（如 `field_f606b4`）。

### 7. 查看完整 API 响应结构

API 返回的 `err_code` 为 0 表示成功，非 0 表示失败。失败时查看 `err_msg` 和 `err` 字段获取详细错误信息。

---

## 典型工作流

### 创建一个缺陷

```bash
PROJECT_KEY="<YOUR_PROJECT_KEY>"

# 1. 查看可用字段
feishu-proj work-items meta --project-key $PROJECT_KEY --type-key issue --format table

# 2. 搜索自己的 user_key
feishu-proj users search --keyword "你的姓名"

# 3. dry-run 预览
feishu-proj bugs create \
  --project-key $PROJECT_KEY \
  --name "[测试]示例缺陷" \
  --fields '[{"field_key":"issue_reporter","field_value":["你的user_key"]},{"field_key":"issue_stage","field_value":"stage_first"}]' \
  --dry-run

# 4. 确认后执行
feishu-proj bugs create \
  --project-key $PROJECT_KEY \
  --name "[测试]示例缺陷" \
  --fields '[{"field_key":"issue_reporter","field_value":["你的user_key"]},{"field_key":"issue_stage","field_value":"stage_first"}]'

# 5. 记录返回的 ID，验证创建结果
feishu-proj bugs get --project-key $PROJECT_KEY --id <返回的ID>
```

### 更新缺陷状态

```bash
# 1. 查看当前状态和可用流转
feishu-proj work-items transitions --project-key $PROJECT_KEY --type-key issue --id <ID>

# 2. 直接流转到目标状态（推荐）
feishu-proj bugs update --project-key $PROJECT_KEY --id <ID> --status RESOLVED
feishu-proj bugs update --project-key $PROJECT_KEY --id <ID> --status CLOSED

# 注意：如果当前是 OPEN，不能直接到 CLOSED，需两步：
# OPEN → RESOLVED → CLOSED
```

### 查找需求并更新

```bash
# 1. 搜索需求
feishu-proj stories list --project-key $PROJECT_KEY --keyword "登录" --format table

# 2. 查看详情
feishu-proj stories get --project-key $PROJECT_KEY --id <ID>

# 3. 更新负责人
feishu-proj stories update \
  --project-key $PROJECT_KEY \
  --id <ID> \
  --fields '[{"field_key":"owner","field_value":"新的user_key"}]'
```

### 创建版本

```bash
feishu-proj versions create \
  --project-key $PROJECT_KEY \
  --name "v1.2.0" \
  --dry-run

# 确认后去掉 --dry-run 执行
feishu-proj versions create --project-key $PROJECT_KEY --name "v1.2.0"
```
