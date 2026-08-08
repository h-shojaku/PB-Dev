#!/usr/bin/env python3
"""
Project Initializer for AI Development System (Canonical Python Implementation).
Ensures safe, fail-closed initialization for NEW_PRODUCT and EXISTING_PRODUCT modes.
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

REQUIRED_PRODUCT_TEMPLATES = [
    "00_PRODUCT_OVERVIEW.md",
    "01_PRODUCT_PLAN.md",
    "02_REQUIREMENTS.md",
    "03_UI_STRUCTURE.md",
    "04_IMPLEMENTATION_SPEC.md",
    "05_OPERATION_RULES.md"
]

def parse_args():
    parser = argparse.ArgumentParser(description="Initialize project profile and reset task runtime state.")
    parser.add_argument("--mode", choices=["NEW_PRODUCT", "EXISTING_PRODUCT", "TEMPLATE"], default="NEW_PRODUCT")
    parser.add_argument("--name", default="MyNewProduct")
    parser.add_argument("--prefix", default="APP")
    parser.add_argument("--remote", default="")
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

def check_git_repository(repo_root):
    try:
        out = subprocess.check_output(["git", "rev-parse", "--is-inside-work-tree"], cwd=repo_root, stderr=subprocess.DEVNULL).decode("utf-8").strip()
        if out == "true":
            return True
    except Exception:
        pass
    print("[ERROR] Not a Git Repository: Project Initialization requires a valid Git repository with .git directory.")
    return False

def apply_git_remote(repo_root, mode, remote_url, dry_run=False):
    if mode == "TEMPLATE" or not remote_url:
        return True
    try:
        remotes_out = subprocess.check_output(["git", "remote"], cwd=repo_root, stderr=subprocess.DEVNULL).decode("utf-8")
        existing_remotes = [r.strip() for r in remotes_out.splitlines() if r.strip()]

        if "origin" in existing_remotes:
            if not dry_run:
                subprocess.check_call(["git", "remote", "set-url", "origin", remote_url], cwd=repo_root, stderr=subprocess.DEVNULL)
        else:
            if not dry_run:
                subprocess.check_call(["git", "remote", "add", "origin", remote_url], cwd=repo_root, stderr=subprocess.DEVNULL)

        if not dry_run:
            actual_origin = subprocess.check_output(["git", "remote", "get-url", "origin"], cwd=repo_root, stderr=subprocess.DEVNULL).decode("utf-8").strip()
            if actual_origin != remote_url:
                print(f"[ERROR] Remote Mismatch: git origin '{actual_origin}' does not match requested remote '{remote_url}'")
                return False
        return True
    except Exception as e:
        print(f"[ERROR] Failed to set/verify git origin remote: {e}")
        return False

def check_templates_and_ssot_protection(repo_root, mode):
    product_tpl_dir = os.path.join(repo_root, "templates", "product")
    product_docs_dir = os.path.join(repo_root, "docs", "product")

    if mode == "NEW_PRODUCT":
        # 1. Preflight NEW_PRODUCT templates check
        for tpl in REQUIRED_PRODUCT_TEMPLATES:
            tpl_path = os.path.join(product_tpl_dir, tpl)
            if not os.path.exists(tpl_path):
                print(f"[ERROR] Missing Product Template: '{tpl}' in templates/product/")
                return False

        # 2. Existing Product SSOT protection (Fail-closed if docs/product/ is not empty)
        if os.path.exists(product_docs_dir):
            items = os.listdir(product_docs_dir)
            if len(items) > 0:
                print(f"[ERROR] Existing Product SSOT detected: 'docs/product/' contains {len(items)} item(s). Clean 'docs/product/' before initializing.")
                return False

    if mode == "EXISTING_PRODUCT":
        # Preflight EXISTING_PRODUCT analysis template check
        analysis_tpl = os.path.join(product_tpl_dir, "EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md")
        if not os.path.exists(analysis_tpl):
            print("[ERROR] Missing Product Template: 'EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md' in templates/product/")
            return False

    return True

def clear_directory_recursively(target_dir):
    if not os.path.exists(target_dir):
        return
    for item in os.listdir(target_dir):
        p = os.path.join(target_dir, item)
        if os.path.isfile(p) or os.path.islink(p):
            os.remove(p)
        elif os.path.isdir(p):
            shutil.rmtree(p)

def count_items_recursively(target_dir):
    if not os.path.exists(target_dir):
        return 0
    total = 0
    for root, dirs, files in os.walk(target_dir):
        total += len(dirs) + len(files)
    return total

def initialize_project(repo_root, mode, name, prefix, remote_url, dry_run=False):
    # Preflight validations
    if not check_git_repository(repo_root):
        return False
    if not validate_prefix(prefix):
        return False
    if not validate_name(name):
        return False
    if not validate_remote(remote_url, mode):
        return False
    if not check_templates_and_ssot_protection(repo_root, mode):
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
        # Apply git remote
        if not apply_git_remote(repo_root, mode, remote_url, dry_run=False):
            return False

        # Write Profile, Register, Current State
        with open(profile_path, "w", encoding="utf-8") as f:
            f.write(profile_content)
        with open(register_path, "w", encoding="utf-8") as f:
            f.write(register_content)
        with open(state_path, "w", encoding="utf-8") as f:
            f.write(state_content)

        # Recursive Runtime State Reset
        clear_directory_recursively(active_dir)
        if mode in ["NEW_PRODUCT", "EXISTING_PRODUCT"]:
            clear_directory_recursively(completed_dir)
        clear_directory_recursively(handoff_dir)

        # NEW_PRODUCT: Populate Product SSOT in docs/product/
        if mode == "NEW_PRODUCT":
            os.makedirs(product_docs_dir, exist_ok=True)
            for fname in REQUIRED_PRODUCT_TEMPLATES:
                src = os.path.join(product_templates_dir, fname)
                dst = os.path.join(product_docs_dir, fname)
                shutil.copy2(src, dst)

        # EXISTING_PRODUCT: Ensure reports/analysis/ exists with template
        if mode == "EXISTING_PRODUCT":
            os.makedirs(reports_analysis_dir, exist_ok=True)
            src_analysis = os.path.join(product_templates_dir, "EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md")
            dst_analysis = os.path.join(reports_analysis_dir, "EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md")
            shutil.copy2(src_analysis, dst_analysis)

        # Final Post-condition Verification
        if not os.path.exists(profile_path) or not os.path.exists(state_path) or not os.path.exists(register_path):
            print("[ERROR] Final Post-Condition Failed: Required initialization files were not created.")
            return False

        # Parse and verify PROJECT_PROFILE.md content
        with open(profile_path, "r", encoding="utf-8") as f:
            prof_txt = f.read()
        if f"Project Name: `{name}`" not in prof_txt or f"Project Mode: `{mode}`" not in prof_txt or f"Task Prefix: `{prefix}`" not in prof_txt or f"Canonical Remote: `{remote_url}`" not in prof_txt:
            print("[ERROR] Final Post-Condition Failed: PROJECT_PROFILE.md content verification failed.")
            return False

        # Parse and verify TASK_REGISTER.md content
        with open(register_path, "r", encoding="utf-8") as f:
            reg_txt = f.read()
        if "(なし)" not in reg_txt or "| DEV-TASK-" in reg_txt or f"| {prefix}-TASK-" in reg_txt:
            print("[ERROR] Final Post-Condition Failed: TASK_REGISTER.md content verification failed.")
            return False

        # Parse and verify CURRENT_STATE.md content
        with open(state_path, "r", encoding="utf-8") as f:
            st_txt = f.read()
        if "`IDLE`" not in st_txt or "Task ID: `None`" not in st_txt or f"Task Prefix: `{prefix}`" not in st_txt or f"Canonical Remote: `{remote_url}`" not in st_txt:
            print("[ERROR] Final Post-Condition Failed: CURRENT_STATE.md content verification failed.")
            return False

        # Verify git origin
        if mode != "TEMPLATE":
            actual_origin = subprocess.check_output(["git", "remote", "get-url", "origin"], cwd=repo_root, stderr=subprocess.DEVNULL).decode("utf-8").strip()
            if actual_origin != remote_url:
                print(f"[ERROR] Final Post-Condition Failed: git origin '{actual_origin}' != requested '{remote_url}'.")
                return False

        # Verify recursive empty runtime directories
        if count_items_recursively(active_dir) > 0:
            print("[ERROR] Final Post-Condition Failed: tasks/active is not recursively empty.")
            return False
        if mode in ["NEW_PRODUCT", "EXISTING_PRODUCT"] and count_items_recursively(completed_dir) > 0:
            print("[ERROR] Final Post-Condition Failed: tasks/completed is not recursively empty.")
            return False
        if count_items_recursively(handoff_dir) > 0:
            print("[ERROR] Final Post-Condition Failed: delivery directory is not recursively empty.")
            return False

        # Verify NEW_PRODUCT docs/product
        if mode == "NEW_PRODUCT":
            copied = os.listdir(product_docs_dir) if os.path.exists(product_docs_dir) else []
            if sorted(copied) != sorted(REQUIRED_PRODUCT_TEMPLATES):
                print(f"[ERROR] Final Post-Condition Failed: docs/product expected exact 6 templates {REQUIRED_PRODUCT_TEMPLATES}, found {copied}.")
                return False

        # Verify EXISTING_PRODUCT analysis template
        if mode == "EXISTING_PRODUCT":
            dst_analysis = os.path.join(reports_analysis_dir, "EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md")
            if not os.path.exists(dst_analysis):
                print("[ERROR] Final Post-Condition Failed: EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md was not placed.")
                return False

    print(f"[{'DRY-RUN' if dry_run else 'EXEC'}] Project initialization completed successfully.")
    return True

def main():
    args = parse_args()
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    success = initialize_project(repo_root, args.mode, args.name, args.prefix, args.remote, args.dry_run)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
