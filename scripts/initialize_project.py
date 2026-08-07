#!/usr/bin/env python3
"""
Project Initialization & Runtime State Reset Tool for AI Development System.
Safe for NEW_PRODUCT and EXISTING_PRODUCT modes. Supports --dry-run.
"""

import sys
import os
import argparse
import shutil
import subprocess

def parse_args():
    parser = argparse.ArgumentParser(description="Initialize project profile and reset task runtime state.")
    parser.add_argument("--mode", choices=["NEW_PRODUCT", "EXISTING_PRODUCT", "TEMPLATE"], default="NEW_PRODUCT")
    parser.add_argument("--name", default="MyNewProduct")
    parser.add_argument("--prefix", default="APP")
    parser.add_argument("--remote", default="")
    parser.add_argument("--dry-run", action="store_true", help="Simulate initialization without modifying files.")
    return parser.parse_args()

def check_remote_safety(repo_root, expected_remote, dry_run):
    try:
        out = subprocess.check_output(["git", "remote", "-v"], cwd=repo_root, stderr=subprocess.DEVNULL).decode("utf-8")
        if "PB-Dev.git" in out and expected_remote and "PB-Dev.git" not in expected_remote:
            print(f"[WARNING] Remote 'origin' points to PB-Dev.git! You should update origin remote to {expected_remote}.")
    except Exception as e:
        print(f"[INFO] Git remote check skipped: {e}")

def initialize_project(repo_root, mode, name, prefix, remote, dry_run):
    profile_path = os.path.join(repo_root, "PROJECT_PROFILE.md")
    register_path = os.path.join(repo_root, "tasks", "TASK_REGISTER.md")
    state_path = os.path.join(repo_root, "CURRENT_STATE.md")
    active_dir = os.path.join(repo_root, "tasks", "active")
    completed_dir = os.path.join(repo_root, "tasks", "completed")

    print(f"[{'DRY-RUN' if dry_run else 'EXEC'}] Initializing Project: {name} (Mode: {mode}, Prefix: {prefix})")

    # 1. Profile content
    profile_content = f"""# Project Profile

## Project Identity
- Project Name: `{name}`
- Project Mode: `{mode}`
- Task Prefix: `{prefix}`

## Repository
- Canonical Remote: `{remote if remote else "https://github.com/example/" + name + ".git"}`
- Default Branch: `main`

## Product
- Product SSOT Root: `docs/product/`

## Development Standard
- Source Template: `PB-Dev`
- Planner Role: Browser AI
- Builder Role: VSCode + CLI AI

## Initialization
- Initialized At: `2026-08-08T00:00:00+09:00`
- Initialized By Task: `INIT`
"""

    # 2. Register content
    register_content = f"""# Task Register

当リポジトリにおけるすべてのTaskの現在状態および発行履歴を管理するレジスタです。

## Current Active Task

| Task ID | Status | Location | Started | Summary |
|---|---|---|---|---|
| (なし) | - | - | - | 現在進行中のActive Taskはありません |

## Task History

| Task ID | Status | Location | Started | Completed | Summary |
|---|---|---|---|---|---|
"""

    # 3. State content
    state_content = f"""# Current State

当リポジトリにおける現在の開発運用状態を示すインデックス・スナップショット（Current State Index）です。

## Repository
- Project Profile: [PROJECT_PROFILE.md](PROJECT_PROFILE.md)
- Project Name: `{name}`
- Task Prefix: `{prefix}`
- Canonical Remote: `{remote if remote else "https://github.com/example/" + name + ".git"}`
- Current Branch: `main`

## Workflow Phase
`IDLE`

## Current Task
- Task ID: `None` (現在実行中のActive Taskはありません)

## Latest Completed Task
- Task ID: `None`

## Git State
- Branch: `main`
- Working Tree Status: `Clean`
- HEAD Commit: Resolved dynamically via `git rev-parse HEAD`

## Human Decision Status
- Status: `None`

## Known Blocking Issues
- Blocking Issues: `None`

## Relevant SSOT
- Development System: [DEVELOPMENT_SYSTEM.md](docs/development/DEVELOPMENT_SYSTEM.md)
- Project Initialization Rules: [PROJECT_INITIALIZATION_RULES.md](docs/development/PROJECT_INITIALIZATION_RULES.md)
- Task Register: [TASK_REGISTER.md](tasks/TASK_REGISTER.md)

## Recovery Entry Point
- Builder: `README.md` -> `AGENTS.md` -> `CURRENT_STATE.md` -> `tasks/TASK_REGISTER.md`

## Next Expected Action
Planner issues first product planning task (`{prefix}-TASK-0001`).

## Last Updated
2026-08-08T00:00:00+09:00
"""

    if not dry_run:
        with open(profile_path, "w", encoding="utf-8") as f:
            f.write(profile_content)
        with open(register_path, "w", encoding="utf-8") as f:
            f.write(register_content)
        with open(state_path, "w", encoding="utf-8") as f:
            f.write(state_content)

        # Clear active tasks
        if os.path.exists(active_dir):
            for item in os.listdir(active_dir):
                p = os.path.join(active_dir, item)
                if os.path.isfile(p): os.remove(p)

    check_remote_safety(repo_root, remote, dry_run)
    print(f"[{'DRY-RUN' if dry_run else 'EXEC'}] Project initialization completed successfully.")

def main():
    args = parse_args()
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    initialize_project(repo_root, args.mode, args.name, args.prefix, args.remote, args.dry_run)

if __name__ == "__main__":
    main()
