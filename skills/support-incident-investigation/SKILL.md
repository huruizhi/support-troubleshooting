---
name: support-incident-investigation
description: 排查不可用、报错、崩溃、5xx、超时、数据错误或服务中断的技术支持工单。用于故障定位、影响面评估和恢复验证；仅表现为慢或容量退化时交给 support-performance-investigation。
---

# Support Incident Investigation

目标是还原故障时间线、失效机制和恢复证据。只有工单号时先使用 `$support-ticket-triage`；已有本地工单目录或日志时直接工作。

## 工作流

1. 读取 [共享产物契约](../../references/artifact-contracts.md) 和 [故障排查方法](references/incident-method.md)。确定首次异常、最后正常、恢复时间、时区、影响范围和当前状态。
2. 建立跨组件时间线：用户错误、入口层、应用、异步任务、数据库、缓存、存储、操作系统以及发布和配置变更。保留原始时间戳并显式换算时区。
3. 聚类错误签名，区分首发异常与后续连锁错误。核查重启、OOM、磁盘/文件句柄耗尽、连接池或线程池耗尽、健康检查失败以及依赖不可达。
4. 分别记录 `trigger`、`failure_mechanism`、`contributing_factors` 和 `symptoms`。没有证据时保持未知，不能把症状改写成根因。
5. 验证恢复：错误率、成功请求、积压、资源水位和客户可见功能都恢复后，才标记 `recovered`；仅进程存活不足以证明恢复。
6. 将 `facts`、`hypotheses`、`gaps`、影响面、时间线、恢复证据和复发风险写入 `analysis/investigation-result.json`。
7. 需要给客户命令时先读取 [命令溯源规范](../../references/command-provenance.md)，并写入 `analysis/command-sources.json`。任何变更性动作必须包含风险、回退和成功判据。

若故障恢复后仍存在持续性能退化，再使用 `$support-performance-investigation` 处理性能分支。

## 完成条件

首发异常、影响范围、失效机制、恢复状态和证据链都有明确记录；每个结论引用证据；相互竞争的假设列出反证；下一步能够证伪至少一个高优先级假设。
