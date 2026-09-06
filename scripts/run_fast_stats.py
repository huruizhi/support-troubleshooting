#!/usr/bin/env python3
"""Run a help-verified fast-stats analysis and record its provenance."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


REQUIRED_HELP = {
    "summary": (None, ["--format <FORMAT>"]),
    "errors": ("errors", ["--format <FORMAT>"]),
    "top": ("top", ["--format <FORMAT>", "--sort-by <SORT_BY>"]),
    "compare": (None, ["--format <FORMAT>", "--compare <COMPARE_FILE>"]),
}
LOG_TYPES = (
    "api",
    "api_dur_ms",
    "gitaly",
    "gitaly_unstructured",
    "production",
    "production_dur_ms",
    "sidekiq",
    "sidekiq_dur_ms",
    "sidekiq_unstructured",
)


def run_checked(argv: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, check=True, text=True, capture_output=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", required=True, choices=sorted(REQUIRED_HELP))
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--log-type", choices=LOG_TYPES)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(f"input log does not exist: {args.input}")
    if args.mode == "compare" and (args.baseline is None or not args.baseline.is_file()):
        parser.error("compare mode requires an existing --baseline log")
    if args.mode != "compare" and args.baseline is not None:
        parser.error("--baseline is only valid with compare mode")
    if args.log_type is not None and args.mode not in {"summary", "compare"}:
        parser.error("--log-type is supported only by summary and compare modes")

    tool = shutil.which("fast-stats")
    if tool is None:
        print("fast-stats is not available on PATH", file=sys.stderr)
        return 1

    try:
        version = run_checked([tool, "--version"]).stdout.strip()
        subcommand, required_tokens = REQUIRED_HELP[args.mode]
        help_argv = [tool] + ([subcommand] if subcommand else []) + ["--help"]
        help_text = run_checked(help_argv).stdout
    except subprocess.CalledProcessError as exc:
        print(exc.stderr or str(exc), file=sys.stderr)
        return exc.returncode or 1

    if not version.startswith("fast-stats "):
        print(f"unexpected version output: {version}", file=sys.stderr)
        return 1
    missing = [token for token in required_tokens if token not in help_text]
    if args.log_type is not None and "--type <LOG_TYPE>" not in help_text:
        missing.append("--type <LOG_TYPE>")
    if missing:
        print(f"fast-stats help no longer contains: {', '.join(missing)}", file=sys.stderr)
        return 1

    input_path = str(args.input.resolve())
    type_args = ["--type", args.log_type] if args.log_type else []
    if args.mode == "summary":
        command = [tool, "--format", "json", *type_args, input_path]
    elif args.mode == "errors":
        command = [tool, "errors", "--format", "json", input_path]
    elif args.mode == "top":
        command = [tool, "top", "--format", "json", "--sort-by", "duration", input_path]
    else:
        command = [
            tool,
            "--format",
            "json",
            "--compare",
            str(args.baseline.resolve()),
            *type_args,
            input_path,
        ]

    try:
        result = run_checked(command)
    except subprocess.CalledProcessError as exc:
        print(exc.stderr or str(exc), file=sys.stderr)
        return exc.returncode or 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result.stdout, encoding="utf-8")
    verified_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    provenance = {
        "tool": "fast-stats",
        "version": version,
        "source_type": "cli-help",
        "source_locator": f"local-cli-help:{tool}@{version.removeprefix('fast-stats ')}",
        "help_argv": help_argv,
        "executed_argv": command,
        "verified_at": verified_at,
        "output": str(args.output.resolve()),
    }
    provenance_path = Path(f"{args.output}.provenance.json")
    provenance_path.write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(provenance, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
