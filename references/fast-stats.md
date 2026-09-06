# fast-stats 适配说明

当前机器已验证：

- 可执行文件：`/Users/rzhu/bin/fast-stats`
- 版本：`fast-stats 0.8.5`
- 来源：该可执行文件自身的 `--help`、`errors --help`、`top --help` 和 `--version` 输出
- 验证日期：2026-09-06（Asia/Shanghai）

插件的 [run_fast_stats.py](../scripts/run_fast_stats.py) 只封装 help 中明确存在的四种模式：

- `summary`: 日志总体统计，JSON 输出。
- `errors`: 错误摘要，JSON 输出。
- `top`: 按持续时间统计主要贡献者，JSON 输出。
- `compare`: 将问题日志与基线日志比较，JSON 输出。

调用包装脚本时传入模式、问题日志、输出文件；`compare` 还要传基线日志。自动识别失败时，`summary` 和 `compare` 可显式传入 help 列出的 `--log-type` 值；其他模式没有该参数，不能强行添加。包装脚本会重新读取本机版本和相应 help，确认所需参数存在后才运行，并把准确 argv、版本、help 来源和验证时间写入 `<output>.provenance.json`。

若本机版本或 help 接口变化，包装脚本会停止并报告缺失参数。此时重新依据新版本 help 更新适配，不要绕过验证或凭记忆修改参数。
