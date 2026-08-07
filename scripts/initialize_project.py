#!/usr/bin/env python3
"""
Project Initializer for AI Development System (Canonical Python Implementation).
Ensures safe initialization for NEW_PRODUCT and EXISTING_PRODUCT modes.
"""

import sys
import os
import re
import argparse
import shutil
import subprocess
from datetime import datetime, timezone

INVALID_REMOTE_PATTERNS = [
    r"example\.com",
    r"github\.com/example/",
    r"^TODO$",
    r"^TBD$",
    r"^$"
]

UNSAFE_PREFIX_PATTERN = r"^[A-Z0-9]{2,10}$"
UNSAFE_NAME_PATTERN = r"^[a-zA-Z0-9_\-]{2,50}$"

def parse_args():
    parser = argparse.ArgumentParser(description="Initialize project profile and reset task runtime state.")
    parser.add_argument("--mode", choices=["NEW_PRODUCT", "EXISTING_PRODUCT", "TEMPLATE"], default="NEW_PRODUCT")
    parser.add_argument("--name", default="MyNewProduct")
    parser.add_argument("--prefix", default="APP")
    parser.add_argument("--remote", default="")
    parser.add_argument("--allow-remote-mismatch", action="store_true", help="Allow origin remote mismatch during tests/bootstrap.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate initialization without modifying files.")
    return parser.parse_args()

def validate_remote(remote_url, mode):
    if mode == "TEMPLATE":
        return True
    if not remote_url:
        print("[ERROR] --remote is required for NEW_PRODUCT and EXISTING_PRODUCT modes.")
        return False
    for pat in INVALID_REMOTE_PATTERNS:
        if re.search(pat, remote_url, re.IGNORECASE):
            print(f"[ERROR] Invalid placeholder remote URL detected: '{remote_url}'")
            return False
    if not (remote_url.startswith("https://") or remote_url.startswith("git@") or remote_url.startswith("ssh://")):
        print(f"[ERROR] Remote URL must be a valid Git URL (https:// or git@): '{remote_url}'")
        return False
    return True

def validate_prefix(prefix):
    if not re.match(UNSAFE_PREFIX_PATTERN, prefix):
        print(f"[ERROR] Invalid Task Prefix: '{prefix}'. Must be 2-10 uppercase alphanumeric characters (e.g. APP, SE, E6).")
        return False
    return True

def validate_name(name):
    if not re.match(UNSAFE_NAME_PATTERN, name):
        print(f"[ERROR] Invalid Project Name: '{name}'. Must be 2-50 alphanumeric, underscore, or hyphen characters.")
        return False
    return True

def check_remote_safety(repo_root, mode, remote_url, allow_mismatch=False):
    if mode == "TEMPLATE" or allow_mismatch:
        return True
    try:
        out = subprocess.check_output(["git", "remote", "-v"], cwd=repo_root, stderr=subprocess.DEVNULL).decode("utf-8")
        if "https://github.com/h-shojaku/PB-Dev.git" in out and "PB-Dev.git" not in remote_url:
            print("[ERROR] Safety Guard: git origin remote points to PB-Dev.git! You cannot initialize a derived product repository while origin points to PB-Dev template remote.")
            return False
    except Exception:
        pass
    return True

def initialize_project(repo_root, mode, name, prefix, remote_url, dry_run=False, allow_mismatch=False):
    if not validate_prefix(prefix):
        return False
    if not validate_name(name):
        return False
    if not validate_remote(remote_url, mode):
        return False
    if not check_remote_safety(repo_root, mode, remote_url, allow_mismatch):
        return False

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    profile_path = os.path.join(repo_root, "PROJECT_PROFILE.md")
    register_path = os.path.join(repo_root, "tasks", "TASK_REGISTER.md")
    state_path = os.path.join(repo_root, "CURRENT_STATE.md")
    active_dir = os.path.join(repo_root, "tasks", "active")
    completed_dir = os.path.join(repo_root, "tasks", "completed")
    handoff_dir = os.path.join(repo_root, "受け渡し")
    product_docs_dir = os.path.join(repo_root, "docs", "product")
    product_templates_dir = os.path.join(repo_root, "templates", "product")
    reports_analysis_dir = os.path.join(repo_root, "reports", "analysis")

    print(f"[{'DRY-RUN' if dry_run else 'EXEC'}] Initializing Project: {name} (Mode: {mode}, Prefix: {prefix})")

    profile_content = f"""# Project Profile

## Project Identity
- Project Name: `{name}`
- Project Mode: `{mode}`
- Task Prefix: `{prefix}`

## Repository
- Canonical Remote: `{remote_url}`
- Default Branch: `main`

## Product
- Product SSOT Root: `docs/product/`

## Development Standard
- Source Template: `PB-Dev`
- Planner Role: Browser AI
- Builder Role: VSCode + CLI AI

## Initialization
- Initialized At: `{now_iso}`
- Initialized By Task: `INIT`
"""

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

    next_action_msg = f"Planner issues first product planning task (`{prefix}-TASK-0001`)." if mode == "NEW_PRODUCT" else f"Planner issues first Baseline Analysis task (`{prefix}-TASK-0001`)."

    state_content = f"""# Current State

当リポジトリにおける現在の開発運用状態を示すインデックス・スナップショット（Current State Index）です。

## Repository
- Project Profile: [PROJECT_PROFILE.md](PROJECT_PROFILE.md)
- Project Name: `{name}`
- Task Prefix: `{prefix}`
- Canonical Remote: `{remote_url}`
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
{next_action_msg}

## Last Updated
{now_iso}
"""

    if not dry_run:
        # Write Profile, Register, Current State
        with open(profile_path, "w", encoding="utf-8") as f:
            f.write(profile_content)
        with open(register_path, "w", encoding="utf-8") as f:
            f.write(register_content)
        with open(state_path, "w", encoding="utf-8") as f:
            f.write(state_content)

        # Clear tasks/active/
        if os.path.exists(active_dir):
            for item in os.listdir(active_dir):
                p = os.path.join(active_dir, item)
                if os.path.isfile(p): os.remove(p)

        # Clear tasks/completed/ for derived projects
        if mode in ["NEW_PRODUCT", "EXISTING_PRODUCT"] and os.path.exists(completed_dir):
            for item in os.listdir(completed_dir):
                p = os.path.join(completed_dir, item)
                if os.path.isfile(p): os.remove(p)

        # Clear 受け渡し/ delivery dir
        if os.path.exists(handoff_dir):
            for item in os.listdir(handoff_dir):
                p = os.path.join(handoff_dir, item)
                if os.path.isfile(p): os.remove(p)
                elif os.path.isdir(p): shutil.rmtree(p)

        # NEW_PRODUCT: Populate Product SSOT in docs/product/
        if mode == "NEW_PRODUCT":
            os.makedirs(product_docs_dir, exist_ok=True)
            for i in range(6):
                fname = f"0{i}_" + ["PRODUCT_OVERVIEW.md", "PRODUCT_PLAN.md", "REQUIREMENTS.md", "UI_STRUCTURE.md", "IMPLEMENTATION_SPEC.md", "OPERATION_RULES.md"][i]
                src = os.path.join(product_templates_dir, fname)
                dst = os.path.join(product_docs_dir, fname)
                if os.path.exists(src):
                    shutil.copy2(src, dst)

        # EXISTING_PRODUCT: Ensure reports/analysis/ exists with template
        if mode == "EXISTING_PRODUCT":
            os.makedirs(reports_analysis_dir, exist_ok=True)
            src_analysis = os.path.join(product_templates_dir, "EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md")
            dst_analysis = os.path.join(reports_analysis_dir, "EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md")
            if os.path.exists(src_analysis):
                shutil.copy2(src_analysis, dst_analysis)

    print(f"[{'DRY-RUN' if dry_run else 'EXEC'}] Project initialization completed successfully.")
    return True

def main():
    args = parse_args()
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    success = initialize_project(repo_root, args.mode, args.name, args.prefix, args.remote, args.dry_run, args.allow_remote_mismatch)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
