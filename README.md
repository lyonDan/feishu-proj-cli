# feishu-proj-cli

飞书项目 Python SDK & CLI，供 skill 和脚本调用。

本项目参考飞书官方 MCP 文档实现，基于 [飞书官方 OpenAPI 文档](https://project.feishu.cn/helpcenter/1ykiuvvj/19wmvt8b) 开发。

## ⚠️ 首要原则：CLI 优先

**任何飞书项目操作，必须先确认 CLI 命令是否已覆盖，有 CLI 就用 CLI，不要写 Python 脚本打补丁。**

| 场景 | 正确做法 | 错误做法 |
|------|---------|---------|
| 查询用户姓名 | `feishu-proj users get --user-key <KEY>` | 写脚本调 `client._request("/user/query", ...)` |
| 获取 story 详情 | `feishu-proj stories get --project-key <KEY> --id <ID>` | 直接实例化 `FeishuProjClient` 手写请求 |
| 更新工作项状态 | `feishu-proj work-items update --status CLOSED` | 手动调 `transit_work_item_state()` |

**CLI 不支持的场景才用 Python SDK**（批量循环、多步组合、结果二次加工等）。

## Setup

```bash
uv sync          # 安装依赖（使用 uv，不是 pip/poetry）
```

`.env` 中配置：
- `FEISHU_USER_KEY`（每人不同）。获取方式：访问飞书项目 → 左下角双击个人头像 → 复制 user_key。
- `PLUGIN_ID` 和 `PLUGIN_SECRET`：从飞书开放平台获取

## 命令概览

```bash
# 项目
feishu-proj projects list

# 用户查询
feishu-proj users get --user-key <USER_KEY>
feishu-proj users get --email <EMAIL>
feishu-proj users search --keyword <EMAIL>

# Stories
feishu-proj stories list --project-key <KEY>
feishu-proj stories get --project-key <KEY> --id <ID>
feishu-proj stories create --project-key <KEY> --name "标题" [--fields JSON] [--dry-run]
feishu-proj stories update --project-key <KEY> --id <ID> --fields JSON [--dry-run]
feishu-proj stories delete --project-key <KEY> --id <ID> [--dry-run]

# Bugs
feishu-proj bugs list --project-key <KEY>
feishu-proj bugs get --project-key <KEY> --id <ID>
feishu-proj bugs create --project-key <KEY> --name "标题" [--fields JSON] [--dry-run]
feishu-proj bugs update --project-key <KEY> --id <ID> --fields JSON [--dry-run]
feishu-proj bugs delete --project-key <KEY> --id <ID> [--dry-run]

# Versions
feishu-proj versions list --project-key <KEY>
feishu-proj versions get --project-key <KEY> --id <ID>
feishu-proj versions create --project-key <KEY> --name "标题" [--fields JSON] [--dry-run]
feishu-proj versions update --project-key <KEY> --id <ID> --fields JSON [--dry-run]

# 通用工作项
feishu-proj work-items list --project-key <KEY> --type-key story
feishu-proj work-items create --project-key <KEY> --type-key issue --name "标题" [--dry-run]
feishu-proj work-items update --project-key <KEY> --type-key issue --id <ID> --fields JSON [--dry-run]
feishu-proj work-items update --project-key <KEY> --type-key issue --id <ID> --status CLOSED   # 状态流转
feishu-proj work-items delete --project-key <KEY> --type-key issue --id <ID> [--dry-run]
feishu-proj work-items transitions --project-key <KEY> --type-key issue --id <ID>   # 查看可用状态流转
feishu-proj work-items meta --project-key <KEY> --type-key issue
```

## 架构

```
src/feishu_proj/
├── config.py          # plugin_id/plugin_secret 从环境变量读取
├── client.py          # FeishuProjClient — token 管理 + 所有 API 方法
├── tools.py           # Skill 工具接口，返回 {success, data, error}
├── cli.py             # Click CLI 入口
└── api/               # 薄封装层，每个函数新建 FeishuProjClient 实例
    ├── projects.py
    ├── requirements.py
    ├── bugs.py
    ├── versions.py
    ├── stories.py
    └── work_items.py
```

## Lint & Type Check

```bash
uv run ruff check src/
uv run mypy src/
```

## 参考资源

| 资源 | URL |
|------|-----|
| 飞书官方 OpenAPI 文档 | https://project.feishu.cn/helpcenter/1ykiuvvj/19wmvt8b |
| 飞书项目 MCP (im47cn) | https://github.com/im47cn/feishu-project-mcp |
| 飞书项目 MCP (Roland0511) | https://github.com/Roland0511/mcp-feishu-proj |
| 飞书官方 OpenAPI MCP | https://github.com/larksuite/lark-openapi-mcp |

## 许可证

MIT License - 宽松授权，欢迎使用。
