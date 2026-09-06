#!/usr/bin/env python3
"""Validate customer-facing command provenance without third-party packages."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


SOURCE_TYPES = {
    "cli-help",
    "man-page",
    "official-doc",
    "vendor-repository",
    "approved-runbook",
}
STATUSES = {"verified", "needs-verification", "rejected"}
RISKS = {"read-only", "mutating", "destructive"}
REQUIRED = {
    "id",
    "command",
    "purpose",
    "status",
    "risk",
    "product",
    "version",
    "installation_method",
    "platform",
    "source",
    "expected_result",
}
SOURCE_REQUIRED = {"type", "label", "locator", "verified_at"}


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(data: Any, customer_ready: bool = False) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["root must be a JSON object"]
    if data.get("schema_version") != "1.0":
        errors.append("schema_version must be '1.0'")
    commands = data.get("commands")
    if not isinstance(commands, list):
        return errors + ["commands must be an array"]

    seen_ids: set[str] = set()
    seen_commands: set[str] = set()
    for index, item in enumerate(commands):
        prefix = f"commands[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        missing = sorted(REQUIRED - item.keys())
        if missing:
            errors.append(f"{prefix} missing: {', '.join(missing)}")
        for field in REQUIRED - {"source"}:
            if field in item and not nonempty(item[field]):
                errors.append(f"{prefix}.{field} must be a non-empty string")

        command_id = item.get("id")
        if nonempty(command_id):
            if not re.fullmatch(r"CMD-[0-9]{3,}", command_id):
                errors.append(f"{prefix}.id must match CMD- followed by at least 3 digits")
            if command_id in seen_ids:
                errors.append(f"{prefix}.id duplicates {command_id}")
            seen_ids.add(command_id)

        command = item.get("command")
        if nonempty(command):
            if command in seen_commands:
                errors.append(f"{prefix}.command duplicates another command")
            seen_commands.add(command)

        status = item.get("status")
        if status not in STATUSES:
            errors.append(f"{prefix}.status is invalid")
        if customer_ready and status != "verified":
            errors.append(f"{prefix} is not verified for customer use")

        risk = item.get("risk")
        if risk not in RISKS:
            errors.append(f"{prefix}.risk is invalid")
        if risk in {"mutating", "destructive"}:
            if not nonempty(item.get("warning")):
                errors.append(f"{prefix}.warning is required for {risk} commands")
            if not nonempty(item.get("rollback")):
                errors.append(f"{prefix}.rollback is required for {risk} commands")

        source = item.get("source")
        if not isinstance(source, dict):
            errors.append(f"{prefix}.source must be an object")
            continue
        source_missing = sorted(SOURCE_REQUIRED - source.keys())
        if source_missing:
            errors.append(f"{prefix}.source missing: {', '.join(source_missing)}")
        if source.get("type") not in SOURCE_TYPES:
            errors.append(f"{prefix}.source.type is invalid")
        for field in SOURCE_REQUIRED - {"verified_at"}:
            if field in source and not nonempty(source[field]):
                errors.append(f"{prefix}.source.{field} must be a non-empty string")
        verified_at = source.get("verified_at")
        if not nonempty(verified_at):
            errors.append(f"{prefix}.source.verified_at must be an ISO-8601 date-time")
        else:
            try:
                datetime.fromisoformat(verified_at.replace("Z", "+00:00"))
            except ValueError:
                errors.append(f"{prefix}.source.verified_at must be an ISO-8601 date-time")
    return errors


def self_test() -> int:
    valid = {
        "schema_version": "1.0",
        "commands": [
            {
                "id": "CMD-001",
                "command": "example --version",
                "purpose": "Capture the installed version",
                "status": "verified",
                "risk": "read-only",
                "product": "example",
                "version": "1.0",
                "installation_method": "local executable",
                "platform": "test",
                "source": {
                    "type": "cli-help",
                    "label": "example 1.0 help",
                    "locator": "local-cli-help:example@1.0",
                    "verified_at": "2026-09-06T00:00:00Z",
                },
                "expected_result": "Version string",
            }
        ],
    }
    invalid = json.loads(json.dumps(valid))
    invalid["commands"][0]["status"] = "needs-verification"
    if validate(valid, customer_ready=True):
        print("self-test failed: valid fixture rejected", file=sys.stderr)
        return 1
    if not validate(invalid, customer_ready=True):
        print("self-test failed: invalid fixture accepted", file=sys.stderr)
        return 1
    print("self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path)
    parser.add_argument("--customer-ready", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.path is None:
        parser.error("path is required unless --self-test is used")
    try:
        data = json.loads(args.path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"invalid input: {exc}", file=sys.stderr)
        return 1
    errors = validate(data, customer_ready=args.customer_ready)
    if errors:
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"validated {len(data['commands'])} command source(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
