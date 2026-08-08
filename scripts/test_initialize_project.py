#!/usr/bin/env python3
"""
Real Git Integration & Fail-Closed Negative Tests for Project Initializer.
Asserts actual git remote settings, filesystem state, and safety rules.
"""

import sys
import os
import shutil
import tempfile
import subprocess
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from initialize_project import initialize_project

class TestProjectInitializerRealGit(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_git_init_")

        # 1. Initialize real git repository
        subprocess.check_call(["git", "init"], cwd=self.test_dir, stderr=subprocess.DEVNULL)
        subprocess.check_call(["git", "config", "user.name", "TestUser"], cwd=self.test_dir, stderr=subprocess.DEVNULL)
        subprocess.check_call(["git", "config", "user.email", "test@example.com"], cwd=self.test_dir, stderr=subprocess.DEVNULL)
        subprocess.check_call(["git", "remote", "add", "origin", "https://github.com/temp/Initial.git"], cwd=self.test_dir, stderr=subprocess.DEVNULL)

        # 2. Prepare mock template structure
        os.makedirs(os.path.join(self.test_dir, "tasks", "active"), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, "tasks", "completed"), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, "受け渡し"), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, "templates", "product"), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, "reports", "analysis"), exist_ok=True)

        # Place dummy runtime task files
        with open(os.path.join(self.test_dir, "tasks", "active", "DEV-TASK-0010.md"), "w") as f:
            f.write("# Active Task")
        with open(os.path.join(self.test_dir, "tasks", "completed", "DEV-TASK-0009.md"), "w") as f:
            f.write("# Completed Task")
        with open(os.path.join(self.test_dir, "受け渡し", "DEV-TASK-0009_PLANNER_HANDOFF.zip"), "w") as f:
            f.write("Dummy ZIP")

        # Copy actual templates from repository root to mock repo
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        actual_tpl_dir = os.path.join(repo_root, "templates", "product")
        if os.path.exists(actual_tpl_dir):
            for item in os.listdir(actual_tpl_dir):
                s = os.path.join(actual_tpl_dir, item)
                d = os.path.join(self.test_dir, "templates", "product", item)
                if os.path.isfile(s):
                    shutil.copy2(s, d)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_real_git_new_product_initialization(self):
        remote = "https://github.com/myorg/RealApp.git"
        res = initialize_project(self.test_dir, "NEW_PRODUCT", "RealApp", "APP", remote, dry_run=False)
        self.assertTrue(res)

        # Assert actual git origin remote was updated and matches requested remote
        actual_origin = subprocess.check_output(["git", "remote", "get-url", "origin"], cwd=self.test_dir).decode("utf-8").strip()
        self.assertEqual(actual_origin, remote)

        # Assert runtime state reset
        self.assertEqual(len(os.listdir(os.path.join(self.test_dir, "tasks", "active"))), 0)
        self.assertEqual(len(os.listdir(os.path.join(self.test_dir, "tasks", "completed"))), 0)
        self.assertEqual(len(os.listdir(os.path.join(self.test_dir, "受け渡し"))), 0)

        # Assert product SSOT files copied (00 ~ 05)
        product_docs = os.listdir(os.path.join(self.test_dir, "docs", "product"))
        self.assertEqual(len(product_docs), 6)

        # Assert PROJECT_PROFILE.md content
        with open(os.path.join(self.test_dir, "PROJECT_PROFILE.md"), "r", encoding="utf-8") as f:
            txt = f.read()
        self.assertIn("RealApp", txt)
        self.assertIn("NEW_PRODUCT", txt)
        self.assertIn("APP", txt)
        self.assertIn(remote, txt)

    def test_real_git_existing_product_initialization(self):
        src_file = os.path.join(self.test_dir, "app.py")
        with open(src_file, "w") as f:
            f.write("print('Existing Code')")

        remote = "https://github.com/myorg/LegacyApp.git"
        res = initialize_project(self.test_dir, "EXISTING_PRODUCT", "LegacyApp", "LEG", remote, dry_run=False)
        self.assertTrue(res)

        # Assert existing code remains intact
        self.assertTrue(os.path.exists(src_file))
        with open(src_file) as f:
            self.assertEqual(f.read(), "print('Existing Code')")

        # Assert git origin remote set
        actual_origin = subprocess.check_output(["git", "remote", "get-url", "origin"], cwd=self.test_dir).decode("utf-8").strip()
        self.assertEqual(actual_origin, remote)

        # Assert analysis template placed
        analysis_file = os.path.join(self.test_dir, "reports", "analysis", "EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md")
        self.assertTrue(os.path.exists(analysis_file))

    def test_fail_non_git_repository(self):
        non_git_dir = tempfile.mkdtemp(prefix="non_git_")
        try:
            os.makedirs(os.path.join(non_git_dir, "templates", "product"), exist_ok=True)
            self.assertFalse(initialize_project(non_git_dir, "NEW_PRODUCT", "App", "APP", "https://github.com/org/App.git"))
        finally:
            shutil.rmtree(non_git_dir)

    def test_fail_missing_remote(self):
        self.assertFalse(initialize_project(self.test_dir, "NEW_PRODUCT", "App", "APP", ""))

    def test_fail_placeholder_remote(self):
        self.assertFalse(initialize_project(self.test_dir, "NEW_PRODUCT", "App", "APP", "https://github.com/example/App.git"))
        self.assertFalse(initialize_project(self.test_dir, "NEW_PRODUCT", "App", "APP", "TODO"))

    def test_fail_invalid_prefix(self):
        self.assertFalse(initialize_project(self.test_dir, "NEW_PRODUCT", "App", "invalid-prefix", "https://github.com/org/App.git"))

    def test_fail_invalid_name(self):
        self.assertFalse(initialize_project(self.test_dir, "NEW_PRODUCT", "Bad Name!", "APP", "https://github.com/org/App.git"))

    def test_fail_missing_product_ssot_template(self):
        missing_tpl_repo = tempfile.mkdtemp(prefix="missing_tpl_")
        try:
            subprocess.check_call(["git", "init"], cwd=missing_tpl_repo, stderr=subprocess.DEVNULL)
            os.makedirs(os.path.join(missing_tpl_repo, "templates", "product"), exist_ok=True)
            with open(os.path.join(missing_tpl_repo, "templates", "product", "00_PRODUCT_OVERVIEW.md"), "w") as f:
                f.write("test")
            self.assertFalse(initialize_project(missing_tpl_repo, "NEW_PRODUCT", "App", "APP", "https://github.com/org/App.git"))
        finally:
            shutil.rmtree(missing_tpl_repo)

    def test_fail_missing_analysis_template(self):
        missing_analysis_repo = tempfile.mkdtemp(prefix="missing_analysis_")
        try:
            subprocess.check_call(["git", "init"], cwd=missing_analysis_repo, stderr=subprocess.DEVNULL)
            os.makedirs(os.path.join(missing_analysis_repo, "templates", "product"), exist_ok=True)
            # Do NOT copy EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md
            self.assertFalse(initialize_project(missing_analysis_repo, "EXISTING_PRODUCT", "App", "APP", "https://github.com/org/App.git"))
        finally:
            shutil.rmtree(missing_analysis_repo)

    def test_fail_existing_product_ssot_protection(self):
        docs_p = os.path.join(self.test_dir, "docs", "product")
        os.makedirs(docs_p, exist_ok=True)
        with open(os.path.join(docs_p, "00_PRODUCT_OVERVIEW.md"), "w") as f:
            f.write("Important Custom Spec")
        self.assertFalse(initialize_project(self.test_dir, "NEW_PRODUCT", "App", "APP", "https://github.com/org/App.git"))

    def test_recursive_runtime_reset(self):
        # Create nested runtime directories and files
        nested_active = os.path.join(self.test_dir, "tasks", "active", "nested", "deep")
        nested_completed = os.path.join(self.test_dir, "tasks", "completed", "sub")
        nested_handoff = os.path.join(self.test_dir, "受け渡し", "sub_dir")
        os.makedirs(nested_active, exist_ok=True)
        os.makedirs(nested_completed, exist_ok=True)
        os.makedirs(nested_handoff, exist_ok=True)
        with open(os.path.join(nested_active, "x.md"), "w") as f: f.write("active")
        with open(os.path.join(nested_completed, "y.md"), "w") as f: f.write("completed")
        with open(os.path.join(nested_handoff, "z.zip"), "w") as f: f.write("zip")

        remote = "https://github.com/myorg/RecResetApp.git"
        res = initialize_project(self.test_dir, "NEW_PRODUCT", "RecResetApp", "REC", remote)
        self.assertTrue(res)

        # Assert recursively empty
        self.assertEqual(len(os.listdir(os.path.join(self.test_dir, "tasks", "active"))), 0)
        self.assertEqual(len(os.listdir(os.path.join(self.test_dir, "tasks", "completed"))), 0)
        self.assertEqual(len(os.listdir(os.path.join(self.test_dir, "受け渡し"))), 0)

    def test_dry_run_no_mutation(self):
        remote = "https://github.com/myorg/DryRun.git"
        res = initialize_project(self.test_dir, "NEW_PRODUCT", "DryRun", "DRY", remote, dry_run=True)
        self.assertTrue(res)

        # Assert active task file was NOT deleted during dry run
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "tasks", "active", "DEV-TASK-0010.md")))

if __name__ == "__main__":
    unittest.main()
