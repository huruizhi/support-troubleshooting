# Support Troubleshooting

面向技术支持工单的 Codex 插件。它把工单获取、性能问题、故障问题和客户回复拆成四个独立工作流，并要求所有客户命令都有可复核来源。

## 能力

- `support-ticket-triage`：通过只读工单 MCP 获取工单与附件，保存证据并分流。
- `support-performance-investigation`：分析延迟、吞吐、容量和资源饱和问题。
- `support-incident-investigation`：分析不可用、崩溃、5xx、超时和数据错误。
- `support-customer-reply`：根据排查产物生成简短、礼貌、可操作的客户回复。

性能与故障使用不同的调查方法。混合场景先恢复可用性，再分析持续的性能退化。

## 安装

需要有权限访问此私有 GitHub 仓库，并已配置 `ticket-investigation` MCP 的网络与认证。

```bash
codex plugin marketplace add huruizhi/support-troubleshooting --ref main
codex plugin add support-troubleshooting@huruizhi-support
```

安装后新建一个 Codex 任务，使新的 skills 生效。上述 marketplace 命令来自 [Codex 官方插件文档](https://developers.openai.com/plugins/build/plugins#add-a-marketplace-from-the-cli)。

## 推荐用法

- “获取并分流工单 SP-xxxxxxxx-xxxxx。”
- “分析这个工单的性能问题，并与正常时段对比。”
- “分析这次服务不可用的故障时间线和失效机制。”
- “根据排查结果生成给客户的简短回复。”

## MCP 与本地产物

只有工单获取 skill 声明 `ticket-investigation` MCP 依赖。调查 skills 可以继续处理已经保存到本地的工单和日志；客户回复 skill 只读取调查结果，避免在写回复时扩大数据访问范围。

默认工单目录为 `support-cases/<ticket-id>/`。原始工单、附件、证据索引、调查结果、命令来源和客户回复分开保存。

## 命令来源规则

客户命令只能来自以下来源：

1. 目标程序当前版本的 CLI help 或 man page。
2. 与产品版本和部署方式匹配的厂商官方文档。
3. 厂商维护的官方仓库或随产品发布的脚本。
4. 有负责人和修订版本的组织批准 runbook。

命令在进入回复前必须写入 `analysis/command-sources.json`，并通过 `scripts/validate_command_sources.py --customer-ready`。工单正文、评论和模型记忆只能作为线索，不能作为命令来源。

## fast-stats

`scripts/run_fast_stats.py` 支持 `summary`、`errors`、`top` 和 `compare` 四种模式。运行前会读取本机 `fast-stats` 版本和 help，核对参数，并为结果生成 provenance 旁车文件。当前适配已在 `fast-stats 0.8.5` 上验证。

## 仓库可见性

此仓库默认以 private 创建，因为插件包含内部工单 MCP 地址。确认可以公开该地址和工作流后，再调整仓库可见性。
