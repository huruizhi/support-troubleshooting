# 工单排查产物契约

一个工单对应一个目录。默认布局：

```text
support-cases/<ticket-id>/
├── ticket.json
├── ticket-context.json
├── artifacts/
├── evidence-index.md
├── routing.json
├── analysis/
│   ├── investigation-result.json
│   ├── command-sources.json
│   └── fast-stats/
└── customer-reply.md
```

保持 MCP 原始字段，规范化内容写入单独的分析产物。不要用推断值回填原始数据。

## evidence-index.md

每项证据必须有稳定编号，例如 `E-001`，并记录：来源类型、原始标识或相对路径、采集时间、证据覆盖时间、时区、完整性、脱敏状态。分析结论通过编号引用证据。

## routing.json

至少包含：

- `ticket_id`
- `classification`: `performance`、`incident` 或 `mixed`
- `confidence`: `low`、`medium` 或 `high`
- `reasons`: 带 `evidence_refs` 的理由
- `gaps`
- `blockers`
- `next_skill`

## investigation-result.json

至少包含：

- `schema_version`: 当前值 `1.0`
- `ticket_id`
- `problem_class`: `performance` 或 `incident`
- `status`: `preliminary`、`confirmed` 或 `blocked`
- `time_window`: `start`、`end`、`timezone`
- `symptom` 与 `impact`
- `facts`: 每项包含 `statement` 和非空 `evidence_refs`
- `hypotheses`: 每项包含 `statement`、`supporting_evidence_refs`、`contradicting_evidence_refs`、`confidence` 和 `next_test`
- `findings`
- `actions`: 每项包含动作、目的、负责人、成功判据和可选 `command_source_ids`
- `gaps` 与 `blockers`
- `customer_safe_summary`

故障结果额外记录 `timeline`、`trigger`、`failure_mechanism`、`contributing_factors` 和 `recovery_status`。性能结果额外记录 `baseline_window`、`metric_deltas`、`top_contributors` 和 `causal_chain`。

## command-sources.json

遵循 [命令溯源规范](command-provenance.md) 和 [JSON Schema](command-sources.schema.json)。该文件是客户回复中命令的唯一允许来源。
