#!/usr/bin/env python3
"""
Standard Handoff ZIP Generator & Verifier for AI Development System.
Cross-platform: Windows, macOS, Linux.
Converts all ZIP entry paths to POSIX '/' format and verifies portability.
"""

import argparse
import os
import pathlib
import re
import shutil
import sys
import tempfile
import zipfile


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
    if '.git' in parts:
        raise ValueError(f"Forbidden '.git' directory in ZIP entry: {entry_name}")


def create_handoff_zip(task_id: str, staging_dir: pathlib.Path, repo_root: pathlib.Path) -> pathlib.Path:
    """
    Creates <repo_root>/受け渡し/<task_id>_PLANNER_HANDOFF.zip from staging_dir.
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

    zip_filename = f"{task_id}_PLANNER_HANDOFF.zip"
    zip_path = delivery_dir / zip_filename

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
    Verifies Handoff ZIP archive integrity, POSIX entries, and delivery folder state.
    Returns a dictionary of verification metrics.
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

        # Extraction test
        with tempfile.TemporaryDirectory() as extract_tmp:
            extract_dir = pathlib.Path(extract_tmp)
            zf.extractall(extract_dir)
            if not (extract_dir / "REPORT.md").exists():
                raise RuntimeError("Extraction test failed: REPORT.md not found after extraction.")
            if not (extract_dir / "MANIFEST.md").exists():
                raise RuntimeError("Extraction test failed: MANIFEST.md not found after extraction.")

    return {
        "integrity": "PASS",
        "file_size": file_size,
        "entry_count": entry_count,
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
    Executes unit tests for normalize_zip_entry, validate_entry_name, and ZIP creation.
    """
    print("Running self-tests for create_handoff.py...")

    # Test 1: Normalize Windows paths
    win_path = pathlib.PureWindowsPath(r"files\docs\development\HANDOFF_RULES.md")
    posix_result = normalize_zip_entry(win_path)
    assert posix_result == "files/docs/development/HANDOFF_RULES.md", f"Failed: {posix_result}"

    # Test 2: Normalize drive letter & leading slash
    win_abs_path = pathlib.PureWindowsPath(r"C:\Users\test\files\README.md")
    posix_abs_result = normalize_zip_entry(win_abs_path)
    assert not posix_abs_result.startswith("C:"), f"Failed drive removal: {posix_abs_result}"
    assert "\\" not in posix_abs_result, f"Failed backslash removal: {posix_abs_result}"

    # Test 3: Validation checks
    validate_entry_name("files/docs/README.md")  # Should pass
    
    try:
        validate_entry_name(r"files\docs\README.md")
        assert False, "Should fail on backslash"
    except ValueError:
        pass

    try:
        validate_entry_name("../files/README.md")
        assert False, "Should fail on traversal"
    except ValueError:
        pass

    # Test 4: End-to-end zip creation & verification in tmpdir
    with tempfile.TemporaryDirectory() as tmp_root_str:
        tmp_root = pathlib.Path(tmp_root_str)
        staging = tmp_root / "staging"
        staging.mkdir()
        (staging / "REPORT.md").write_text("# Report", encoding="utf-8")
        (staging / "MANIFEST.md").write_text("# Manifest", encoding="utf-8")
        files_dir = staging / "files" / "docs"
        files_dir.mkdir(parents=True)
        (files_dir / "test.md").write_text("Test content", encoding="utf-8")

        zip_p = create_handoff_zip("DEV-TASK-TEST", staging, tmp_root)
        metrics = verify_handoff_zip(zip_p, tmp_root)
        assert metrics["backslash_count"] == 0
        assert metrics["extraction_test"] == "PASS"

    print("ALL SELF-TESTS PASSED!")


def main():
    parser = argparse.ArgumentParser(description="Standard Handoff ZIP Generator & Verifier")
    parser.add_argument("--task", help="Task ID, e.g., DEV-TASK-0005")
    parser.add_argument("--staging", help="Path to staging directory containing REPORT.md, MANIFEST.md, files/")
    parser.add_argument("--repo-root", help="Path to repository root (defaults to parent of script directory)")
    parser.add_argument("--test", action="store_true", help="Run self-tests")

    args = parser.parse_args()

    if args.test:
        run_self_tests()
        sys.exit(0)

    if not args.task or not args.staging:
        parser.print_help()
        sys.exit(1)

    repo_root = pathlib.Path(args.repo-root).resolve() if args.repo_root else pathlib.Path(__file__).resolve().parent.parent
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
