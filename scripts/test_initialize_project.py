#!/usr/bin/env python3
"""
Comprehensive Integration & Negative Tests for Project Initializer.
Asserts actual filesystem state and safety rules.
"""

import sys
import os
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from initialize_project import initialize_project, validate_remote, validate_prefix, validate_name

class TestProjectInitializer(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_init_")
        # Prepare mock template structure
        os.makedirs(os.path.join(self.test_dir, "tasks", "active"), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, "tasks", "completed"), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, "受け渡し"), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, "templates", "product"), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, "reports", "analysis"), exist_ok=True)

        # Place dummy files representing PB-Dev state before initialization
        with open(os.path.join(self.test_dir, "tasks", "active", "DEV-TASK-0009.md"), "w") as f:
            f.write("# Dummy Active Task")
        with open(os.path.join(self.test_dir, "tasks", "completed", "DEV-TASK-0008.md"), "w") as f:
            f.write("# Dummy Completed Task")
        with open(os.path.join(self.test_dir, "受け渡し", "DEV-TASK-0008_PLANNER_HANDOFF.zip"), "w") as f:
            f.write("Dummy ZIP")

        # Place Product SSOT templates
        for i in range(6):
            fname = f"0{i}_" + ["PRODUCT_OVERVIEW.md", "PRODUCT_PLAN.md", "REQUIREMENTS.md", "UI_STRUCTURE.md", "IMPLEMENTATION_SPEC.md", "OPERATION_RULES.md"][i]
            with open(os.path.join(self.test_dir, "templates", "product", fname), "w") as f:
                f.write(f"# Template {fname}")
        with open(os.path.join(self.test_dir, "templates", "product", "EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md"), "w") as f:
            f.write("# Analysis Template")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_new_product_initialization(self):
        remote = "https://github.com/myorg/NewApp.git"
        res = initialize_project(self.test_dir, "NEW_PRODUCT", "NewApp", "APP", remote, dry_run=False, allow_mismatch=True)
        self.assertTrue(res)

        # Filesystem assertions
        active_files = os.listdir(os.path.join(self.test_dir, "tasks", "active"))
        completed_files = os.listdir(os.path.join(self.test_dir, "tasks", "completed"))
        handoff_files = os.listdir(os.path.join(self.test_dir, "受け渡し"))
        product_files = os.listdir(os.path.join(self.test_dir, "docs", "product"))

        self.assertEqual(len(active_files), 0, "tasks/active must be empty after initialization")
        self.assertEqual(len(completed_files), 0, "tasks/completed must be reset and empty after initialization")
        self.assertEqual(len(handoff_files), 0, "受け渡し must be empty after initialization")
        self.assertEqual(len(product_files), 6, "docs/product/ must contain all 6 Product SSOT templates")

        # Profile content assertion
        with open(os.path.join(self.test_dir, "PROJECT_PROFILE.md"), "r", encoding="utf-8") as f:
            profile_txt = f.read()
        self.assertIn("NewApp", profile_txt)
        self.assertIn("NEW_PRODUCT", profile_txt)
        self.assertIn("APP", profile_txt)
        self.assertIn(remote, profile_txt)

        # Current state content assertion
        with open(os.path.join(self.test_dir, "CURRENT_STATE.md"), "r", encoding="utf-8") as f:
            state_txt = f.read()
        self.assertIn("Workflow Phase\n`IDLE`", state_txt)
        self.assertIn("APP-TASK-0001", state_txt)

    def test_existing_product_initialization(self):
        # Create existing source files
        src_dir = os.path.join(self.test_dir, "src")
        os.makedirs(src_dir, exist_ok=True)
        main_file = os.path.join(src_dir, "main.py")
        with open(main_file, "w") as f:
            f.write("print('Hello Legacy')")

        remote = "https://github.com/myorg/LegacyApp.git"
        res = initialize_project(self.test_dir, "EXISTING_PRODUCT", "LegacyApp", "LEG", remote, dry_run=False, allow_mismatch=True)
        self.assertTrue(res)

        # Assert existing source is completely preserved
        self.assertTrue(os.path.exists(main_file))
        with open(main_file, "r") as f:
            self.assertEqual(f.read(), "print('Hello Legacy')")

        # Assert runtime task state is reset
        active_files = os.listdir(os.path.join(self.test_dir, "tasks", "active"))
        completed_files = os.listdir(os.path.join(self.test_dir, "tasks", "completed"))
        self.assertEqual(len(active_files), 0)
        self.assertEqual(len(completed_files), 0)

        # Assert analysis template is placed
        analysis_tpl = os.path.join(self.test_dir, "reports", "analysis", "EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md")
        self.assertTrue(os.path.exists(analysis_tpl))

    def test_negative_cases(self):
        # 1. Missing remote in NEW_PRODUCT mode -> FAIL
        self.assertFalse(initialize_project(self.test_dir, "NEW_PRODUCT", "App", "APP", "", dry_run=False, allow_mismatch=True))

        # 2. Placeholder remote in NEW_PRODUCT mode -> FAIL
        self.assertFalse(initialize_project(self.test_dir, "NEW_PRODUCT", "App", "APP", "https://github.com/example/App.git", dry_run=False, allow_mismatch=True))
        self.assertFalse(initialize_project(self.test_dir, "NEW_PRODUCT", "App", "APP", "TODO", dry_run=False, allow_mismatch=True))

        # 3. Invalid Prefix -> FAIL
        self.assertFalse(initialize_project(self.test_dir, "NEW_PRODUCT", "App", "invalid-prefix", "https://github.com/myorg/App.git", dry_run=False, allow_mismatch=True))

        # 4. Invalid Name -> FAIL
        self.assertFalse(initialize_project(self.test_dir, "NEW_PRODUCT", "Bad Name!", "APP", "https://github.com/myorg/App.git", dry_run=False, allow_mismatch=True))

    def test_dry_run(self):
        remote = "https://github.com/myorg/DryRunApp.git"
        res = initialize_project(self.test_dir, "NEW_PRODUCT", "DryRunApp", "DRY", remote, dry_run=True, allow_mismatch=True)
        self.assertTrue(res)

        # Assert mock active file was NOT deleted in dry-run
        active_files = os.listdir(os.path.join(self.test_dir, "tasks", "active"))
        self.assertIn("DEV-TASK-0009.md", active_files)

if __name__ == "__main__":
    unittest.main()
