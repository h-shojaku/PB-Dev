#!/usr/bin/env python3
"""
Standard Handoff ZIP Generator & Verifier for AI Development System.
Cross-platform: Windows, macOS, Linux.
Converts all ZIP entry paths to POSIX '/' format, verifies manifest integrity,
required review files, and archive completeness.
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


def parse_manifest_entries(manifest_content: str) -> list:
    """
    Parses file entries listed in MANIFEST.md content.
    Looks for paths matching 'files/...' in list items or inline text.
    """
    entries = []
    # Match entries starting with files/ in backticks or markdown bullet lists
    matches = re.findall(r'(?:`|- |\* )?(files/[a-zA-Z0-9_\-/\.]+)(?:`|\s|$)', manifest_content)
    for m in matches:
        clean = m.strip('`').strip()
        if clean and clean not in entries:
            entries.append(clean)
    return entries


def populate_staging_files_if_missing(staging_dir: pathlib.Path, repo_root: pathlib.Path) -> None:
    """
    Ensures staging_dir/files exists and contains essential repository review files.
    """
    files_dir = staging_dir / "files"
    files_dir.mkdir(parents=True, exist_ok=True)

    # Core review files to include in handoff package
    core_paths = [
        "README.md",
        "CURRENT_STATE.md",
        "PROJECT_PROFILE.md",
        "AGENTS.md",
        "CLAUDE.md",
        "GEMINI.md",
        "docs",
        "scripts",
        "tasks",
        "templates"
    ]

    for rel in core_paths:
        src = repo_root / rel
        dst = files_dir / rel
        if not src.exists():
            continue
        if src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        elif src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '*.zip', 'active'))


def create_handoff_zip(task_id: str, staging_dir: pathlib.Path, repo_root: pathlib.Path, auto_populate: bool = True) -> pathlib.Path:
    """
    Creates <repo_root>/受け渡し/<task_id>_PLANNER_HANDOFF.zip from staging_dir.
    Cleans up old files in 受け渡し/ first.
    """
    delivery_dir = repo_root / "受け渡し"
    delivery_dir.mkdir(parents=True, exist_ok=True)

    # Automatically populate staging_dir/files if missing or empty
    files_subdir = staging_dir / "files"
    if auto_populate and (not files_subdir.exists() or len(list(files_subdir.glob("**/*"))) == 0):
        populate_staging_files_if_missing(staging_dir, repo_root)

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


def verify_handoff_zip(zip_path: pathlib.Path, repo_root: pathlib.Path, required_files: list = None) -> dict:
    """
    Verifies Handoff ZIP archive integrity, POSIX entries, MANIFEST integrity, required files, and delivery folder state.
    Returns a dictionary of verification metrics.
    """
    if required_files is None:
        required_files = []

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
    files_entry_count = 0
    manifest_text = ""

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
                manifest_text = zf.read('MANIFEST.md').decode('utf-8', errors='replace')
            if name.startswith('files/'):
                files_entry_count += 1

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

        # 1. Empty Review Package Rejection
        if files_entry_count == 0:
            raise RuntimeError("Empty Review Package Rejection: ZIP contains only REPORT/MANIFEST and 0 files under 'files/'.")

        # 2. Manifest Integrity Verification (Phantom Entry Check)
        declared_entries = parse_manifest_entries(manifest_text)
        missing_declared = []
        for declared in declared_entries:
            if declared not in namelist:
                missing_declared.append(declared)

        if missing_declared:
            raise RuntimeError(
                f"Manifest Integrity Failure: {len(missing_declared)} entry/entries listed in MANIFEST.md were NOT found in the ZIP archive: {missing_declared[:5]}"
            )

        # 3. Required Review Files Verification
        missing_required = []
        for req in required_files:
            if req not in namelist:
                missing_required.append(req)

        if missing_required:
            raise RuntimeError(
                f"Required Review File Missing: {len(missing_required)} required file(s) missing from ZIP: {missing_required}"
            )

        # 4. Extraction test
        with tempfile.TemporaryDirectory() as extract_tmp:
            extract_dir = pathlib.Path(extract_tmp)
            zf.extractall(extract_dir)
            if not (extract_dir / "REPORT.md").exists():
                raise RuntimeError("Extraction test failed: REPORT.md not found after extraction.")
            if not (extract_dir / "MANIFEST.md").exists():
                raise RuntimeError("Extraction test failed: MANIFEST.md not found after extraction.")
            if not (extract_dir / "files").exists():
                raise RuntimeError("Extraction test failed: files/ directory not found after extraction.")

    return {
        "integrity": "PASS",
        "file_size": file_size,
        "entry_count": entry_count,
        "files_entry_count": files_entry_count,
        "manifest_declared_count": len(declared_entries),
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
    Executes unit tests for normalize_zip_entry, validate_entry_name, ZIP creation,
    and regression test cases 14.1 ~ 14.5.
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

    # --- REGRESSION TESTS (Section 14) ---

    # 14.1 Complete Package Success
    with tempfile.TemporaryDirectory() as tmp_root_str:
        tmp_root = pathlib.Path(tmp_root_str)
        staging = tmp_root / "staging"
        staging.mkdir()
        (staging / "REPORT.md").write_text("# Report\nEntry count: 4", encoding="utf-8")
        manifest_content = "# Manifest\nIncluded Files:\n- `files/a.txt`\n- `files/docs/b.md`\n"
        (staging / "MANIFEST.md").write_text(manifest_content, encoding="utf-8")
        f_dir = staging / "files" / "docs"
        f_dir.mkdir(parents=True)
        (staging / "files" / "a.txt").write_text("a", encoding="utf-8")
        (f_dir / "b.md").write_text("b", encoding="utf-8")

        zip_p = create_handoff_zip("DEV-TASK-TEST1", staging, tmp_root, auto_populate=False)
        metrics = verify_handoff_zip(zip_p, tmp_root)
        assert metrics["integrity"] == "PASS"
        assert metrics["files_entry_count"] == 2
        assert metrics["entry_count"] == 4
        print("PASS: 14.1 Complete Package Success")

    # 14.2 Manifest Phantom Entry Failure
    with tempfile.TemporaryDirectory() as tmp_root_str:
        tmp_root = pathlib.Path(tmp_root_str)
        staging = tmp_root / "staging"
        staging.mkdir()
        (staging / "REPORT.md").write_text("# Report", encoding="utf-8")
        manifest_content = "# Manifest\n- `files/a.txt`\n- `files/missing.txt`\n"
        (staging / "MANIFEST.md").write_text(manifest_content, encoding="utf-8")
        (staging / "files").mkdir()
        (staging / "files" / "a.txt").write_text("a", encoding="utf-8")

        zip_p = create_handoff_zip("DEV-TASK-TEST2", staging, tmp_root, auto_populate=False)
        try:
            verify_handoff_zip(zip_p, tmp_root)
            assert False, "Should fail on Manifest phantom entry"
        except RuntimeError as e:
            assert "Manifest Integrity Failure" in str(e)
            print("PASS: 14.2 Manifest Phantom Entry Failure")

    # 14.3 Required Review File Missing
    with tempfile.TemporaryDirectory() as tmp_root_str:
        tmp_root = pathlib.Path(tmp_root_str)
        staging = tmp_root / "staging"
        staging.mkdir()
        (staging / "REPORT.md").write_text("# Report", encoding="utf-8")
        (staging / "MANIFEST.md").write_text("# Manifest\n- `files/a.txt`\n", encoding="utf-8")
        (staging / "files").mkdir()
        (staging / "files" / "a.txt").write_text("a", encoding="utf-8")

        zip_p = create_handoff_zip("DEV-TASK-TEST3", staging, tmp_root, auto_populate=False)
        try:
            verify_handoff_zip(zip_p, tmp_root, required_files=["files/scripts/initialize_project.py"])
            assert False, "Should fail on required review file missing"
        except RuntimeError as e:
            assert "Required Review File Missing" in str(e)
            print("PASS: 14.3 Required Review File Missing")

    # 14.4 Empty Review Package Failure
    with tempfile.TemporaryDirectory() as tmp_root_str:
        tmp_root = pathlib.Path(tmp_root_str)
        staging = tmp_root / "staging"
        staging.mkdir()
        (staging / "REPORT.md").write_text("# Report", encoding="utf-8")
        (staging / "MANIFEST.md").write_text("# Manifest", encoding="utf-8")

        zip_p = create_handoff_zip("DEV-TASK-TEST4", staging, tmp_root, auto_populate=False)
        try:
            verify_handoff_zip(zip_p, tmp_root)
            assert False, "Should fail on empty review package"
        except RuntimeError as e:
            assert "Empty Review Package Rejection" in str(e)
            print("PASS: 14.4 Empty Review Package Failure")

    # 14.5 Entry Count Match
    with tempfile.TemporaryDirectory() as tmp_root_str:
        tmp_root = pathlib.Path(tmp_root_str)
        staging = tmp_root / "staging"
        staging.mkdir()
        (staging / "REPORT.md").write_text("# Report", encoding="utf-8")
        (staging / "MANIFEST.md").write_text("# Manifest\n- `files/1.txt`\n- `files/2.txt`\n", encoding="utf-8")
        (staging / "files").mkdir()
        (staging / "files" / "1.txt").write_text("1", encoding="utf-8")
        (staging / "files" / "2.txt").write_text("2", encoding="utf-8")

        zip_p = create_handoff_zip("DEV-TASK-TEST5", staging, tmp_root, auto_populate=False)
        metrics = verify_handoff_zip(zip_p, tmp_root)
        with zipfile.ZipFile(zip_p, 'r') as zf:
            actual_namelist_len = len(zf.namelist())
        assert metrics["entry_count"] == actual_namelist_len == 4
        print("PASS: 14.5 Entry Count Match")

    print("\nALL SELF-TESTS PASSED!")


def main():
    parser = argparse.ArgumentParser(description="Standard Handoff ZIP Generator & Verifier")
    parser.add_argument("--task", help="Task ID, e.g., DEV-TASK-0014")
    parser.add_argument("--staging", help="Path to staging directory containing REPORT.md, MANIFEST.md, files/")
    parser.add_argument("--repo-root", help="Path to repository root (defaults to parent of script directory)")
    parser.add_argument("--require", action="append", default=[], help="Specify required review file in ZIP (can be repeated)")
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
    zip_path = create_handoff_zip(args.task, staging_dir, repo_root, auto_populate=True)
    print(f"Created ZIP: {zip_path}")

    print("Verifying Handoff ZIP...")
    metrics = verify_handoff_zip(zip_path, repo_root, required_files=args.require)
    print("Verification metrics:")
    for k, v in metrics.items():
        print(f"  {k}: {v}")

    print("\nHandoff ZIP generation & verification completed successfully!")


if __name__ == "__main__":
    main()
