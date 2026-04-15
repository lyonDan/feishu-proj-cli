# feishu-proj CLI 集成测试方案

> 面向生产环境的手工集成测试。所有写操作须走完完整生命周期后关闭，不遗留 OPEN 状态数据。
> versions 类型只查不改。

## 前置条件

```bash
cd feishu-proj-cli
uv sync
# 确认配置正常
uv run feishu-proj auth show-config
```

期望输出含 `Has User Key: 是`。

---

## T1 只读命令

### T1-1 projects list
```bash
uv run feishu-proj projects list
```
✅ 期望：`err_code=0`，`data` 为项目 ID 数组（如 `["<PROJECT_KEY>"]`）

### T1-2 work-item-types list
```bash
uv run feishu-proj work-item-types list --format table
```
✅ 期望：输出 4 行（story/issue/version/task）

### T1-3 users get by user_key
```bash
uv run feishu-proj users get --user-key <USER_KEY> --format table
```
✅ 期望：输出表格，含 user_key、姓名、email 列

### T1-4 users search by email
```bash
uv run feishu-proj users search --keyword <EMAIL> --format table
```
✅ 期望：返回对应用户信息

### T1-5 versions list（只读）
```bash
uv run feishu-proj versions list --project-key <PROJECT_KEY> --page-size 5 --format table
```
✅ 期望：输出 `版本名 | ID` 格式的表格

### T1-6 versions get（只读）
```bash
# 使用 T1-5 返回的任意版本 ID
uv run feishu-proj versions get --project-key <PROJECT_KEY> --id <VERSION_ID>
```
✅ 期望：JSON 中包含 `name`、`work_item_status.state_key`、`id`

### T1-7 bugs list table format（验证 Bug1 修复）
```bash
uv run feishu-proj bugs list --project-key <PROJECT_KEY> --page-size 3 --format table
```
✅ 期望：第二列是 `OPEN`/`RESOLVED` 等**字符串**，不是 `{...}` dict 对象

### T1-8 stories list table
```bash
uv run feishu-proj stories list --project-key <PROJECT_KEY> --page-size 3
```
✅ 期望：输出 `ID | name | status | owner` 格式表格

### T1-9 work-items meta
```bash
uv run feishu-proj work-items meta --project-key <PROJECT_KEY> --type-key issue --format table
```
✅ 期望：输出字段列表，含 `field_key | field_alias | field_type | required` 列

---

## T2 Bug 完整生命周期

**目标**：`OPEN → 更新字段 → RESOLVED → CLOSED`

### T2-1 创建
```bash
uv run feishu-proj bugs create \
  --project-key <PROJECT_KEY> \
  --name "[CLI-TEST] 自动化测试缺陷 $(date +%Y%m%d-%H%M%S)"
```
✅ 期望：`err_code=0`，`data` 为整数 ID  
📝 **记录返回的 BUG_ID**

### T2-2 查询详情
```bash
uv run feishu-proj bugs get --project-key <PROJECT_KEY> --id <BUG_ID>
```
✅ 期望：`work_item_status.state_key = "OPEN"`，`name` 与创建时一致

### T2-3 查看可用流转
```bash
uv run feishu-proj work-items transitions \
  --project-key <PROJECT_KEY> --type-key issue --id <BUG_ID>
```
✅ 期望：输出包含 `OPEN → RESOLVED` 等可用流转

### T2-4 更新字段
```bash
uv run feishu-proj bugs update \
  --project-key <PROJECT_KEY> \
  --id <BUG_ID> \
  --fields '[{"field_key":"name","field_value":"[CLI-TEST] 已更新标题"}]'
```
✅ 期望：`err_code=0`，`data={}`

### T2-5 流转 RESOLVED
```bash
uv run feishu-proj bugs update \
  --project-key <PROJECT_KEY> \
  --id <BUG_ID> \
  --status RESOLVED
```
✅ 期望：`err_code=0`

### T2-6 验证 RESOLVED
```bash
uv run feishu-proj bugs get --project-key <PROJECT_KEY> --id <BUG_ID> \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['data'][0]['work_item_status']['state_key'])"
```
✅ 期望：输出 `RESOLVED`

### T2-7 流转 CLOSED
```bash
uv run feishu-proj bugs update \
  --project-key <PROJECT_KEY> \
  --id <BUG_ID> \
  --status CLOSED
```
✅ 期望：`err_code=0`

### T2-8 最终验证
```bash
uv run feishu-proj bugs get --project-key <PROJECT_KEY> --id <BUG_ID> \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['data'][0]['work_item_status']['state_key'])"
```
✅ 期望：输出 `CLOSED`

---

## T3 Story 生命周期（含 Node 模式错误提示验证）

### T3-1 创建
```bash
uv run feishu-proj stories create \
  --project-key <PROJECT_KEY> \
  --name "[CLI-TEST] 自动化测试需求 $(date +%Y%m%d-%H%M%S)"
```
✅ 期望：`err_code=0`，`data` 为整数 ID  
📝 **记录返回的 STORY_ID**

### T3-2 查询详情
```bash
uv run feishu-proj stories get --project-key <PROJECT_KEY> --id <STORY_ID>
```
✅ 期望：`work_item_status.state_key = "waiting_for_start"`，`pattern = "Node"`

### T3-3 更新字段
```bash
uv run feishu-proj stories update \
  --project-key <PROJECT_KEY> \
  --id <STORY_ID> \
  --fields '[{"field_key":"name","field_value":"[CLI-TEST] 已更新标题"}]'
```
✅ 期望：`err_code=0`

### T3-4 验证 Node 模式错误提示（验证 Bug2 修复）
```bash
uv run feishu-proj work-items update \
  --project-key <PROJECT_KEY> \
  --type-key story \
  --id <STORY_ID> \
  --status doing
```
✅ 期望：报错信息包含 **"节点流（Node）模式"** 和 **"CLI 的 --status 参数仅支持状态机（State）模式"**（不再是 `400 Bad Request`）

### T3-5 清理
```bash
uv run feishu-proj stories delete \
  --project-key <PROJECT_KEY> \
  --id <STORY_ID>
```
✅ 期望：`err_code=0`，`data={}`

---

## T4 work-items 通用命令完整生命周期

### T4-1 创建
```bash
uv run feishu-proj work-items create \
  --project-key <PROJECT_KEY> \
  --type-key issue \
  --name "[CLI-TEST-WI] 通用工作项测试 $(date +%Y%m%d-%H%M%S)"
```
✅ 期望：`err_code=0`，返回整数 ID  
📝 **记录 WI_ID**

### T4-2 查询
```bash
uv run feishu-proj work-items get \
  --project-key <PROJECT_KEY> \
  --id <WI_ID> \
  --type-key issue
```
✅ 期望：返回工作项 JSON，state=OPEN

### T4-3 查看流转
```bash
uv run feishu-proj work-items transitions \
  --project-key <PROJECT_KEY> --type-key issue --id <WI_ID>
```
✅ 期望：输出包含 OPEN→RESOLVED 等多条流转

### T4-4 更新字段
```bash
uv run feishu-proj work-items update \
  --project-key <PROJECT_KEY> \
  --type-key issue --id <WI_ID> \
  --fields '[{"field_key":"name","field_value":"[CLI-TEST-WI] 字段已更新"}]'
```
✅ 期望：`err_code=0`

### T4-5 流转 RESOLVED
```bash
uv run feishu-proj work-items update \
  --project-key <PROJECT_KEY> \
  --type-key issue --id <WI_ID> --status RESOLVED
```
✅ 期望：`err_code=0`

### T4-6 流转 CLOSED
```bash
uv run feishu-proj work-items update \
  --project-key <PROJECT_KEY> \
  --type-key issue --id <WI_ID> --status CLOSED
```
✅ 期望：`err_code=0`

### T4-7 最终验证
```bash
uv run feishu-proj work-items get \
  --project-key <PROJECT_KEY> \
  --id <WI_ID> --type-key issue \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('work_item_status',{}).get('state_key'))"
```
✅ 期望：`CLOSED`

### T4-8 列表关键字搜索
```bash
uv run feishu-proj work-items list \
  --project-key <PROJECT_KEY> \
  --type-key issue --keyword "CLI-TEST" --page-size 5
```
✅ 期望：输出包含刚创建的工作项（状态为 CLOSED）

---

## T5 错误处理与 dry-run

| 编号 | 命令 | 期望结果 |
|------|------|---------|
| T5-1 | `bugs create --dry-run --name X` | 打印 `[DRY RUN]` 和 payload，不实际创建 |
| T5-2 | `bugs update --id 99 --status RESOLVED --dry-run` | 打印 `[DRY RUN] 将流转缺陷...` |
| T5-3 | `bugs update --id 99 --fields '[...]' --dry-run` | 打印 `[DRY RUN] 将更新缺陷...` |
| T5-4 | `work-items create --dry-run ...` | 打印 payload |
| T5-5 | `stories create --dry-run --name X` | 打印 payload |
| T5-6 | `versions update --id 99 --fields '[...]' --dry-run` | 打印 payload |
| T5-7 | `bugs update --project-key K --id 1`（缺 --fields/--status） | `错误: 必须提供 --fields 或 --status 之一`，exit=1 |
| T5-8 | `users get`（无参数） | `错误：请至少提供一个 --user-key 或 --email`，exit=1 |
| T5-9 | `bugs create --fields 'not-json'` | `JSON 解析错误:...`，exit=1 |
| T5-10 | 对已 CLOSED 的 issue 执行 `--status RESOLVED` | `错误: 当前状态 'CLOSED' 不能直接流转到 'RESOLVED'。可用目标状态: ['REOPENED']` |
| T5-11 | 对 story 执行 `--status doing` | `错误: ...节点流（Node）模式...CLI 的 --status 参数仅支持状态机（State）模式...` |
| T5-12 | `bugs delete --id 99 --dry-run` | `[DRY RUN] 将删除缺陷 99（project=<PROJECT_KEY>）` |
| T5-13 | `stories delete --id 99 --dry-run` | `[DRY RUN] 将删除需求 99（project=<PROJECT_KEY>）` |
| T5-14 | `work-items delete --type-key story --id 99 --dry-run` | `[DRY RUN] 将删除 story/99（project=<PROJECT_KEY>）` |

---

## 测试数据规范

- 名称格式：`[CLI-TEST] xxx $(date +%Y%m%d-%H%M%S)` 或 `[CLI-TEST-WI] xxx`
- issue 类型：必须走完 OPEN → RESOLVED → CLOSED 完整流转后结束
- story 类型：测试完后通过 SDK DELETE 接口删除
- 严禁修改 versions 数据（只读）
- 严禁修改非 CLI-TEST 前缀的现有工单
