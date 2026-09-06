# 命令溯源规范

客户执行的命令必须可复核、版本匹配且逐字来自权威来源。工单正文、评论、聊天记录、搜索摘要和模型记忆都是线索，不是命令权威来源。

## 可接受来源

按优先级选择：

1. 当前环境中目标程序的 `--help` 或 man page，且记录程序版本。
2. 对应产品版本和部署方式的厂商官方文档。
3. 厂商维护的官方仓库、随产品发布的脚本或 runbook。
4. 有负责人和修订版本的组织批准 runbook。

来源必须能支持完整命令，包括子命令、参数、参数顺序、适用版本、部署方式和权限。不得把来自不同版本或不同安装方式的片段拼成一条命令。

## 验证流程

1. 先取得产品版本、操作系统或容器环境、安装方式和执行权限。
2. 打开来源原文或本机 help，核对完整命令。
3. 优先选择只读命令。变更性或破坏性命令同时需要风险、回退步骤、执行窗口和成功判据。
4. 把每条命令写入 `analysis/command-sources.json`，并用插件的 [validate_command_sources.py](../scripts/validate_command_sources.py) 校验。
5. 客户回复只能引用状态为 `verified` 的条目，并保持命令逐字一致。

无法验证时，输出要达到的诊断目的和缺失的版本/部署信息，请求补充信息；不输出占位命令或“常见写法”。

## 字段

每条命令包含：

- `id`: 稳定编号，例如 `CMD-001`
- `command`: 将交给客户的精确文本
- `purpose`: 为什么执行
- `status`: `verified`、`needs-verification` 或 `rejected`
- `risk`: `read-only`、`mutating` 或 `destructive`
- `product`、`version`、`installation_method`、`platform`
- `source`: `type`、`label`、`locator`、`verified_at`
- `expected_result`: 客户应回传什么或怎样判断成功
- `warning` 与 `rollback`: 变更性或破坏性命令必填

完整机器可读约束见 [command-sources.schema.json](command-sources.schema.json)。
