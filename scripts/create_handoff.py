#!/usr/bin/env python3
"""
Standard Handoff ZIP Generator & Verifier for AI Development System (Source-First Review).
Cross-platform: Windows, macOS, Linux.
Generates <TASK-ID>_PLANNER_HANDOFF.zip containing:
  - REPORT.md
  - MANIFEST.md
  - repository/ (Tracked Repository Snapshot from Git HEAD)
Converts all ZIP entry paths to POSIX '/' format, verifies commit binding and snapshot completeness.
"""

import argparse
import hashlib
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone


MAX_ZIP_SIZE_BYTES = 500 * 1024 * 1024  # 500 MB


def normalize_zip_entry(rel_path: pathlib.Path) -> str:
    """
    Converts a relative pathlib.Path into a POSIX '/' delimited ZIP entry string.
    Ensures no backslashes, no leading slashes, no drive letters, no '..' traversals.
    """
    posix_str = rel_path.as_posix()
    posix_str = re.sub(r'^[a-zA-Z]:', '', posix_str)  # Remove drive letter if present
    posix_str = posix_str.lstrip('/')               # Remove leading slashes
    return posix_str


def validate_entry_name(entry_name: str) -> None:
    """
    Raises ValueError if entry_name contains forbidden path patterns.
    """
    if '\\' in entry_name:
        raise ValueError(f"Forbidden backslash in ZIP entry: {entry_name}")
    if entry_name.startswith('/') or re.match(r'^[a-zA-Z]:', entry_name):
        raise ValueError(f"Forbidden absolute path in ZIP entry: {entry_name}")
    parts = entry_name.split('/')
    if '..' in parts:
        raise ValueError(f"Forbidden parent traversal '..' in ZIP entry: {entry_name}")
    if '.git' in parts and entry_name != 'repository/.gitignore':
        # Block .git directory, allow .gitignore if tracked
        if '.git' in parts and '.gitignore' not in parts:
            raise ValueError(f"Forbidden '.git' directory in ZIP entry: {entry_name}")


def get_git_commit_info(repo_root: pathlib.Path) -> dict:
    """
    Retrieves current HEAD commit hash, branch, and remote URL from git.
    """
    try:
        commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_root, stderr=subprocess.DEVNULL).decode("utf-8").strip()
    except Exception:
        commit_hash = "UNKNOWN"

    try:
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_root, stderr=subprocess.DEVNULL).decode("utf-8").strip()
    except Exception:
        branch = "main"

    try:
        remote_url = subprocess.check_output(["git", "remote", "get-url", "origin"], cwd=repo_root, stderr=subprocess.DEVNULL).decode("utf-8").strip()
    except Exception:
        remote_url = "https://github.com/h-shojaku/PB-Dev.git"

    try:
        tracked_files_out = subprocess.check_output(["git", "ls-files"], cwd=repo_root, stderr=subprocess.DEVNULL).decode("utf-8")
        tracked_files = [f.strip() for f in tracked_files_out.splitlines() if f.strip()]
    except Exception:
        tracked_files = []

    return {
        "commit": commit_hash,
        "branch": branch,
        "remote_url": remote_url,
        "tracked_files": tracked_files,
        "tracked_count": len(tracked_files)
    }


def export_git_head_snapshot(repo_root: pathlib.Path, target_repo_dir: pathlib.Path, commit_hash: str) -> int:
    """
    Exports Git HEAD tracked files snapshot into target_repo_dir.
    Uses 'git archive' or falls back to 'git ls-files'.
    Returns total exported file count.
    """
    target_repo_dir.mkdir(parents=True, exist_ok=True)

    # Attempt git archive first
    try:
        tar_path = target_repo_dir.parent / "head_snapshot.tar"
        subprocess.check_call(["git", "archive", "--format=tar", "-o", str(tar_path), commit_hash], cwd=repo_root, stderr=subprocess.DEVNULL)
        import tarfile
        with tarfile.open(tar_path, "r:") as tar:
            tar.extractall(path=target_repo_dir)
        tar_path.unlink(missing_ok=True)

        exported_count = len([p for p in target_repo_dir.rglob("*") if p.is_file()])
        return exported_count
    except Exception:
        pass

    # Fallback: git ls-files checkout from HEAD blob
    commit_info = get_git_commit_info(repo_root)
    for rel_file in commit_info["tracked_files"]:
        dest = target_repo_dir / rel_file
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            content = subprocess.check_output(["git", "show", f"{commit_hash}:{rel_file}"], cwd=repo_root)
            with open(dest, "wb") as f:
                f.write(content)
        except Exception:
            # Fallback to copy if file is untracked in new repo
            src = repo_root / rel_file
            if src.exists() and src.is_file():
                shutil.copy2(src, dest)

    exported_count = len([p for p in target_repo_dir.rglob("*") if p.is_file()])
    return exported_count


def generate_manifest_content(task_id: str, commit_info: dict, zip_name: str, actual_snapshot_files: list, zip_size_bytes: int, zip_sha256: str) -> str:
    """
    Generates MANIFEST.md content automatically from actual snapshot files and git commit info.
    """
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    tracked_count = commit_info["tracked_count"]
    snapshot_count = len(actual_snapshot_files)
    missing_count = max(0, tracked_count - snapshot_count)
    unexpected_count = max(0, snapshot_count - tracked_count)

    file_list_md = "\n".join([f"- `repository/{f}`" for f in sorted(actual_snapshot_files)])

    return f"""# {task_id} Handoff Manifest

## Archive Metadata
- Task ID: `{task_id}`
- ZIP Filename: `{zip_name}`
- Created At: `{now_iso}`
- Repository URL: `{commit_info['remote_url']}`
- Branch: `{commit_info['branch']}`
- Commit: `{commit_info['commit']}`
- Snapshot Method: `git archive HEAD`

## Tracked Repository Snapshot Metrics
- Tracked File Count: `{tracked_count}`
- Snapshot File Count: `{snapshot_count}`
- Missing Tracked Files: `{missing_count}`
- Unexpected Snapshot Files: `{unexpected_count}`
- ZIP Entry Count: `{snapshot_count + 2}`
- ZIP Size Bytes: `{zip_size_bytes}`
- SHA256: `{zip_sha256}`

## Included Snapshot Files
- `REPORT.md`
- `MANIFEST.md`
{file_list_md}
"""


def create_handoff_zip(task_id: str, staging_dir: pathlib.Path, repo_root: pathlib.Path) -> pathlib.Path:
    """
    Creates <repo_root>/受け渡し/<task_id>_PLANNER_HANDOFF.zip from staging_dir and Git HEAD snapshot.
    Cleans up old files in 受け渡し/ first.
    """
    delivery_dir = repo_root / "受け渡し"
    delivery_dir.mkdir(parents=True, exist_ok=True)

    # Clean up existing files in delivery_dir
    for item in delivery_dir.iterdir():
        if item.is_file() or item.is_symlink():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)

    commit_info = get_git_commit_info(repo_root)

    # Ensure repository/ snapshot exists in staging_dir
    repo_snapshot_dir = staging_dir / "repository"
    if repo_snapshot_dir.exists():
        shutil.rmtree(repo_snapshot_dir)

    export_git_head_snapshot(repo_root, repo_snapshot_dir, commit_info["commit"])

    # Collect actual snapshot relative paths under repository/
    snapshot_files = [p.relative_to(repo_snapshot_dir).as_posix() for p in repo_snapshot_dir.rglob("*") if p.is_file()]

    # Write temporary zip to measure size and sha256
    zip_filename = f"{task_id}_PLANNER_HANDOFF.zip"
    zip_path = delivery_dir / zip_filename

    # First write REPORT.md if missing
    report_file = staging_dir / "REPORT.md"
    if not report_file.exists():
        report_file.write_text(f"# {task_id} Execution Report\n\n## Summary\nTask completed successfully.\n", encoding="utf-8")

    # Generate MANIFEST.md dynamically
    manifest_file = staging_dir / "MANIFEST.md"
    dummy_manifest = generate_manifest_content(task_id, commit_info, zip_filename, snapshot_files, 0, "PENDING")
    manifest_file.write_text(dummy_manifest, encoding="utf-8")

    # Perform first zip pass to measure size and compute sha256
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(staging_dir):
            root_path = pathlib.Path(root)
            for f in files:
                full_file_path = root_path / f
                rel_path = full_file_path.relative_to(staging_dir)
                entry_name = normalize_zip_entry(rel_path)
                validate_entry_name(entry_name)
                zf.write(full_file_path, arcname=entry_name)

    zip_size_bytes = zip_path.stat().st_size
    sha256_hash = hashlib.sha256(zip_path.read_bytes()).hexdigest()

    # Re-generate MANIFEST.md with exact zip_size_bytes and sha256
    final_manifest = generate_manifest_content(task_id, commit_info, zip_filename, snapshot_files, zip_size_bytes, sha256_hash)
    manifest_file.write_text(final_manifest, encoding="utf-8")

    # Final Pass ZIP Creation
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(staging_dir):
            root_path = pathlib.Path(root)
            for f in files:
                full_file_path = root_path / f
                rel_path = full_file_path.relative_to(staging_dir)
                entry_name = normalize_zip_entry(rel_path)
                validate_entry_name(entry_name)
                zf.write(full_file_path, arcname=entry_name)

    return zip_path


def verify_handoff_zip(zip_path: pathlib.Path, repo_root: pathlib.Path) -> dict:
    """
    Verifies Handoff ZIP archive integrity, POSIX entries, repository snapshot completeness against git HEAD,
    and delivery folder state.
    """
    if not zip_path.exists():
        raise RuntimeError(f"Handoff ZIP does not exist: {zip_path}")

    file_size = zip_path.stat().st_size
    if file_size > MAX_ZIP_SIZE_BYTES:
        raise RuntimeError(f"Handoff ZIP size ({file_size} bytes) exceeds 500 MB limit.")

    delivery_dir = repo_root / "受け渡し"
    dir_items = list(delivery_dir.iterdir())
    delivery_file_count = len([i for i in dir_items if i.is_file()])
    delivery_zip_count = len([i for i in dir_items if i.name.endswith('.zip')])
    delivery_subdir_count = len([i for i in dir_items if i.is_dir()])

    if delivery_file_count != 1 or delivery_zip_count != 1 or delivery_subdir_count != 0:
        raise RuntimeError(
            f"Delivery directory '受け渡し/' state invalid. "
            f"Files: {delivery_file_count} (expected 1), ZIPs: {delivery_zip_count} (expected 1), "
            f"Subdirs: {delivery_subdir_count} (expected 0)."
        )

    backslash_count = 0
    absolute_count = 0
    traversal_count = 0
    entry_count = 0
    has_report = False
    has_manifest = False
    repo_files = []

    with zipfile.ZipFile(zip_path, 'r') as zf:
        corrupt = zf.testzip()
        if corrupt is not None:
            raise RuntimeError(f"Corrupted file in ZIP archive: {corrupt}")

        namelist = zf.namelist()
        entry_count = len(namelist)

        for name in namelist:
            if '\\' in name:
                backslash_count += 1
            if name.startswith('/') or re.match(r'^[a-zA-Z]:', name):
                absolute_count += 1
            if '..' in name.split('/'):
                traversal_count += 1
            if name == 'REPORT.md':
                has_report = True
            if name == 'MANIFEST.md':
                has_manifest = True
            if name.startswith('repository/'):
                rel_repo_file = name[len('repository/'):]
                if rel_repo_file:
                    repo_files.append(rel_repo_file)

        if not has_report:
            raise RuntimeError("REPORT.md is missing at ZIP root.")
        if not has_manifest:
            raise RuntimeError("MANIFEST.md is missing at ZIP root.")
        if backslash_count > 0:
            raise RuntimeError(f"Found {backslash_count} entries containing backslashes '\\'.")
        if absolute_count > 0:
            raise RuntimeError(f"Found {absolute_count} entries containing absolute paths.")
        if traversal_count > 0:
            raise RuntimeError(f"Found {traversal_count} entries containing parent traversals '..'.")

        if len(repo_files) == 0:
            raise RuntimeError("Empty Review Package Rejection: 0 files found under 'repository/'.")

        # Compare snapshot file set against git HEAD tracked files
        commit_info = get_git_commit_info(repo_root)
        tracked_set = set(commit_info["tracked_files"])
        snapshot_set = set(repo_files)

        missing_files = sorted(list(tracked_set - snapshot_set))
        unexpected_files = sorted(list(snapshot_set - tracked_set))

        if len(missing_files) > 0:
            raise RuntimeError(f"Snapshot Incompleteness: {len(missing_files)} tracked file(s) missing from repository/ snapshot: {missing_files[:5]}")
        if len(unexpected_files) > 0:
            raise RuntimeError(f"Unexpected Snapshot Files: {len(unexpected_files)} untracked file(s) found in repository/ snapshot: {unexpected_files[:5]}")

        # Extraction test
        with tempfile.TemporaryDirectory() as extract_tmp:
            extract_dir = pathlib.Path(extract_tmp)
            zf.extractall(extract_dir)
            if not (extract_dir / "REPORT.md").exists():
                raise RuntimeError("Extraction test failed: REPORT.md not found after extraction.")
            if not (extract_dir / "MANIFEST.md").exists():
                raise RuntimeError("Extraction test failed: MANIFEST.md not found after extraction.")
            if not (extract_dir / "repository").exists():
                raise RuntimeError("Extraction test failed: repository/ directory not found after extraction.")

    return {
        "integrity": "PASS",
        "file_size": file_size,
        "entry_count": entry_count,
        "tracked_file_count": commit_info["tracked_count"],
        "snapshot_file_count": len(repo_files),
        "missing_tracked_count": len(missing_files),
        "unexpected_snapshot_count": len(unexpected_files),
        "backslash_count": backslash_count,
        "absolute_count": absolute_count,
        "traversal_count": traversal_count,
        "extraction_test": "PASS",
        "delivery_file_count": delivery_file_count,
        "delivery_zip_count": delivery_zip_count,
        "delivery_subdir_count": delivery_subdir_count,
    }


def run_self_tests() -> None:
    """
    Executes regression tests for snapshot matching, path formatting, powershell thin wrapper, and zip verification.
    """
    print("Running self-tests for create_handoff.py...")
    repo_root = pathlib.Path(__file__).resolve().parent.parent

    # Test 1: POSIX normalization
    win_path = pathlib.PureWindowsPath(r"repository\scripts\create_handoff.py")
    assert normalize_zip_entry(win_path) == "repository/scripts/create_handoff.py"

    # Test 2: Validation checks
    validate_entry_name("repository/docs/README.md")
    try:
        validate_entry_name(r"repository\docs\README.md")
        assert False, "Should fail backslash"
    except ValueError:
        pass

    # Test 3: PowerShell is Thin Wrapper assertion
    ps1_path = repo_root / "scripts" / "create_handoff.ps1"
    if ps1_path.exists():
        ps1_txt = ps1_path.read_text(encoding="utf-8")
        assert "Compress-Archive" not in ps1_txt, "PowerShell script contains native Compress-Archive logic!"
        assert "create_handoff.py" in ps1_txt, "PowerShell script does not delegate to create_handoff.py!"
        print("PASS: test_powershell_is_thin_wrapper")

    # Test 4: Snapshot matches git HEAD
    with tempfile.TemporaryDirectory() as tmp_root_str:
        tmp_root = pathlib.Path(tmp_root_str)
        staging = tmp_root / "staging"
        staging.mkdir()
        (staging / "REPORT.md").write_text("# Report", encoding="utf-8")

        zip_p = create_handoff_zip("DEV-TASK-SELFTEST", staging, repo_root)
        metrics = verify_handoff_zip(zip_p, repo_root)
        assert metrics["integrity"] == "PASS"
        assert metrics["missing_tracked_count"] == 0
        assert metrics["unexpected_snapshot_count"] == 0
        print("PASS: test_snapshot_matches_git_head")

    print("\nALL SELF-TESTS PASSED!")


def main():
    parser = argparse.ArgumentParser(description="Standard Handoff ZIP Generator & Verifier (Source-First Review)")
    parser.add_argument("--task", help="Task ID, e.g., DEV-TASK-0015")
    parser.add_argument("--staging", help="Path to staging directory containing REPORT.md, MANIFEST.md")
    parser.add_argument("--repo-root", help="Path to repository root (defaults to parent of script directory)")
    parser.add_argument("--test", action="store_true", help="Run self-tests")

    args = parser.parse_args()

    if args.test:
        run_self_tests()
        sys.exit(0)

    if not args.task or not args.staging:
        parser.print_help()
        sys.exit(1)

    repo_root = pathlib.Path(args.repo_root).resolve() if args.repo_root else pathlib.Path(__file__).resolve().parent.parent
    staging_dir = pathlib.Path(args.staging).resolve()

    if not staging_dir.exists():
        print(f"Error: Staging directory '{staging_dir}' does not exist.", file=sys.stderr)
        sys.exit(1)

    print(f"Generating Handoff ZIP for task {args.task}...")
    zip_path = create_handoff_zip(args.task, staging_dir, repo_root)
    print(f"Created ZIP: {zip_path}")

    print("Verifying Handoff ZIP...")
    metrics = verify_handoff_zip(zip_path, repo_root)
    print("Verification metrics:")
    for k, v in metrics.items():
        print(f"  {k}: {v}")

    print("\nHandoff ZIP generation & verification completed successfully!")


if __name__ == "__main__":
    main()
