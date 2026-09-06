---
name: support-performance-investigation
description: 排查系统仍可用但响应慢、吞吐下降、资源饱和或容量退化的技术支持工单。用于性能问题、性能回归和好坏时段对比；不可用、崩溃、5xx 或数据错误优先交给 support-incident-investigation。
---

# Support Performance Investigation

目标是形成可复核的性能因果链，而不是罗列慢请求。只有工单号时先使用 `$support-ticket-triage`；已有本地工单目录或日志时直接工作。

## 工作流

1. 读取 [共享产物契约](../../references/artifact-contracts.md) 和 [性能排查方法](references/performance-method.md)。确认坏时段、时区、正常基线、影响对象以及日志覆盖范围；缺一项就记入 `gaps`。
2. 先验证日志类型、时间戳、采样和截断情况。把长连接、流式请求、健康检查等会扭曲延迟统计的流量单独处理。
3. 对坏时段与基线计算吞吐、失败率、p50/p95/p99、队列等待和资源饱和度。只有一个时段时给出截面结论，不把它写成“回归”。
4. 从全局指标逐层收敛到接口、任务、项目、用户或后端依赖，按时间关联请求、队列、数据库、缓存、存储和系统资源。
5. 将内容分成 `facts`、`hypotheses` 和 `gaps`。每个事实引用证据编号；每个假设同时列支持证据、反证和下一项可证伪检查。
6. 形成触发条件 → 瓶颈机制 → 用户症状的因果链。仅有时间相关性时维持“待验证”，不升级为根因。
7. 写入 `analysis/investigation-result.json`。需要给客户命令时先读取 [命令溯源规范](../../references/command-provenance.md)，并写入 `analysis/command-sources.json`。

## fast-stats

需要分析支持的 GitLab 日志时，读取 [fast-stats 适配说明](../../references/fast-stats.md)，优先调用插件的 [run_fast_stats.py](../../scripts/run_fast_stats.py)。它会按本机 CLI help 验证参数并保存命令来源；不要凭记忆增加参数。

## 完成条件

结果中同时包含问题时段与时区、基线或基线缺失说明、量化差异、主要贡献者、证据化因果链、置信度、反证、下一步以及验证成功标准。没有达到这些条件时结论状态只能是 `preliminary` 或 `blocked`。
