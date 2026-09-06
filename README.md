# Support Troubleshooting

面向技术支持工单的 Codex 插件。它优先利用用户已经提供的内容快速判断，只有证据不足或明确要求归档时才调用 MCP；大日志直接在本地分析。所有客户命令都必须有可复核来源。

## 能力

- `support-ticket-triage`：在快速分析、按需 MCP 和本地日志三条路径间选择并分流。
- `support-performance-investigation`：分析延迟、吞吐、容量和资源饱和问题。
- `support-incident-investigation`：分析不可用、崩溃、5xx、超时和数据错误。
- `support-customer-reply`：根据排查产物生成简短、礼貌、可操作的客户回复。

性能与故障使用不同的调查方法。混合场景先恢复可用性，再分析持续的性能退化。

## 安装

这是公开 GitHub 仓库。使用 MCP 路径时，仍需具备 `ticket-investigation` 服务的网络和认证权限。

```bash
codex plugin marketplace add huruizhi/support-troubleshooting --ref main
codex plugin add support-troubleshooting@huruizhi-support
```

安装后新建一个 Codex 任务，使新的 skills 生效。上述 marketplace 命令来自 [Codex 官方插件文档](https://developers.openai.com/plugins/build/plugins#add-a-marketplace-from-the-cli)。

## 推荐用法

- “获取并分流工单 SP-xxxxxxxx-xxxxx。”
- “根据下面粘贴的工单内容快速判断，不调用 MCP。”
- “分析这个工单的性能问题，并与正常时段对比。”
- “分析这次服务不可用的故障时间线和失效机制。”
- “根据排查结果生成给客户的简短回复。”

## 三种输入路径

- `quick`：已有正文、错误、截图文字或日志片段时默认使用；不调用 MCP，不创建目录。
- `mcp`：只有工单号、关键证据缺失或明确要求完整归档时使用；附件按需读取。
- `local-log`：日志已在本地或超过 MCP 大小限制时使用；MCP 最多补充必要元数据。

只有工单分流 skill 声明 `ticket-investigation` MCP 依赖，实际调用是惰性的。调查 skills 可以直接处理粘贴内容和本地日志；客户回复 skill 可以直接使用快速初判或正式调查结果。

只有保存、归档或深度排查时才创建 `support-cases/<case-id>/`，有工单号时直接用工单号。原始工单、附件、证据索引、调查结果、命令来源和客户回复分开保存。

## 命令来源规则

客户命令只能来自以下来源：

1. 目标程序当前版本的 CLI help 或 man page。
2. 与产品版本和部署方式匹配的厂商官方文档。
3. 厂商维护的官方仓库或随产品发布的脚本。
4. 有负责人和修订版本的组织批准 runbook。

命令在进入回复前必须写入 `analysis/command-sources.json`，并通过 `scripts/validate_command_sources.py --customer-ready`。工单正文、评论和模型记忆只能作为线索，不能作为命令来源。

## fast-stats

`scripts/run_fast_stats.py` 支持 `summary`、`errors`、`top` 和 `compare` 四种模式。运行前会读取本机 `fast-stats` 版本和 help，核对参数，并为结果生成 provenance 旁车文件。当前适配已在 `fast-stats 0.8.5` 上验证。
