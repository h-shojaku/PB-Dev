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
        self.repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        actual_tpl_dir = os.path.join(self.repo_root, "templates", "product")
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

    def test_actual_template_new_product_initialization(self):
        # Test cloning actual PB-Dev repository and initializing NEW_PRODUCT
        target = tempfile.mkdtemp(prefix="actual_pbdev_new_")
        try:
            # Copy entire PB-Dev repo excluding .git
            for item in os.listdir(self.repo_root):
                if item in [".git", "受け渡し"]:
                    continue
                s = os.path.join(self.repo_root, item)
                d = os.path.join(target, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)

            # Init git
            subprocess.check_call(["git", "init"], cwd=target, stderr=subprocess.DEVNULL)
            subprocess.check_call(["git", "remote", "add", "origin", "https://github.com/h-shojaku/PB-Dev.git"], cwd=target, stderr=subprocess.DEVNULL)

            remote = "https://github.com/myorg/ClonedApp.git"
            res = initialize_project(target, "NEW_PRODUCT", "ClonedApp", "CLO", remote)
            self.assertTrue(res)

            actual_origin = subprocess.check_output(["git", "remote", "get-url", "origin"], cwd=target).decode("utf-8").strip()
            self.assertEqual(actual_origin, remote)
            self.assertEqual(len(os.listdir(os.path.join(target, "docs", "product"))), 6)
        finally:
            shutil.rmtree(target)

    def test_actual_template_existing_product_initialization(self):
        target = tempfile.mkdtemp(prefix="actual_pbdev_exist_")
        try:
            for item in os.listdir(self.repo_root):
                if item in [".git", "受け渡し"]:
                    continue
                s = os.path.join(self.repo_root, item)
                d = os.path.join(target, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)

            subprocess.check_call(["git", "init"], cwd=target, stderr=subprocess.DEVNULL)
            subprocess.check_call(["git", "remote", "add", "origin", "https://github.com/h-shojaku/PB-Dev.git"], cwd=target, stderr=subprocess.DEVNULL)

            remote = "https://github.com/myorg/ClonedExisting.git"
            res = initialize_project(target, "EXISTING_PRODUCT", "ClonedExisting", "CLE", remote)
            self.assertTrue(res)

            actual_origin = subprocess.check_output(["git", "remote", "get-url", "origin"], cwd=target).decode("utf-8").strip()
            self.assertEqual(actual_origin, remote)
            self.assertTrue(os.path.exists(os.path.join(target, "reports", "analysis", "EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md")))
        finally:
            shutil.rmtree(target)

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
            self.assertFalse(initialize_project(missing_analysis_repo, "EXISTING_PRODUCT", "App", "APP", "https://github.com/org/App.git"))
        finally:
            shutil.rmtree(missing_analysis_repo)

    def test_fail_existing_product_ssot_protection(self):
        docs_p = os.path.join(self.test_dir, "docs", "product")
        os.makedirs(docs_p, exist_ok=True)
        with open(os.path.join(docs_p, "00_PRODUCT_OVERVIEW.md"), "w") as f:
            f.write("Important Custom Spec")
        self.assertFalse(initialize_project(self.test_dir, "NEW_PRODUCT", "App", "APP", "https://github.com/org/App.git"))

    def test_unknown_product_file_rejected_without_mutation(self):
        docs_p = os.path.join(self.test_dir, "docs", "product")
        os.makedirs(docs_p, exist_ok=True)
        unknown_file = os.path.join(docs_p, "notes.txt")
        with open(unknown_file, "w") as f:
            f.write("Unknown text file")

        res = initialize_project(self.test_dir, "NEW_PRODUCT", "App", "APP", "https://github.com/org/App.git")
        self.assertFalse(res)
        # Verify no mutation
        self.assertTrue(os.path.exists(unknown_file))
        self.assertEqual(len(os.listdir(docs_p)), 1)

    def test_unknown_product_subdirectory_rejected_without_mutation(self):
        docs_p = os.path.join(self.test_dir, "docs", "product")
        sub_dir = os.path.join(docs_p, "legacy")
        os.makedirs(sub_dir, exist_ok=True)
        unknown_file = os.path.join(sub_dir, "spec.txt")
        with open(unknown_file, "w") as f:
            f.write("Legacy spec")

        res = initialize_project(self.test_dir, "NEW_PRODUCT", "App", "APP", "https://github.com/org/App.git")
        self.assertFalse(res)
        # Verify no mutation
        self.assertTrue(os.path.exists(unknown_file))

    def test_powershell_is_thin_wrapper(self):
        ps1_path = os.path.join(self.repo_root, "scripts", "initialize_project.ps1")
        with open(ps1_path, "r", encoding="utf-8") as f:
            ps_code = f.read()

        # Assert PS1 does not contain business logic like writing PROJECT_PROFILE or clearing runtime
        self.assertNotIn("PROJECT_PROFILE.md", ps_code)
        self.assertNotIn("Set-Content", ps_code)
        self.assertIn("initialize_project.py", ps_code)

    def test_final_profile_postconditions(self):
        remote = "https://github.com/myorg/ProfilePostApp.git"
        res = initialize_project(self.test_dir, "NEW_PRODUCT", "ProfilePostApp", "PPA", remote)
        self.assertTrue(res)

        prof_p = os.path.join(self.test_dir, "PROJECT_PROFILE.md")
        with open(prof_p, "r", encoding="utf-8") as f:
            txt = f.read()
        self.assertIn("Project Name: `ProfilePostApp`", txt)
        self.assertIn("Project Mode: `NEW_PRODUCT`", txt)
        self.assertIn("Task Prefix: `PPA`", txt)
        self.assertIn(f"Canonical Remote: `{remote}`", txt)

    def test_final_register_postconditions(self):
        remote = "https://github.com/myorg/RegPostApp.git"
        res = initialize_project(self.test_dir, "NEW_PRODUCT", "RegPostApp", "RPA", remote)
        self.assertTrue(res)

        reg_p = os.path.join(self.test_dir, "tasks", "TASK_REGISTER.md")
        with open(reg_p, "r", encoding="utf-8") as f:
            txt = f.read()
        self.assertIn("(なし)", txt)
        self.assertNotIn("| DEV-TASK-", txt)
        self.assertNotIn("| RPA-TASK-", txt)

    def test_final_current_state_postconditions(self):
        remote = "https://github.com/myorg/StatePostApp.git"
        res = initialize_project(self.test_dir, "NEW_PRODUCT", "StatePostApp", "SPA", remote)
        self.assertTrue(res)

        st_p = os.path.join(self.test_dir, "CURRENT_STATE.md")
        with open(st_p, "r", encoding="utf-8") as f:
            txt = f.read()
        self.assertIn("`IDLE`", txt)
        self.assertIn("Task ID: `None`", txt)
        self.assertIn("Task Prefix: `SPA`", txt)
        self.assertIn(f"Canonical Remote: `{remote}`", txt)

    def test_recursive_runtime_reset(self):
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

        self.assertEqual(len(os.listdir(os.path.join(self.test_dir, "tasks", "active"))), 0)
        self.assertEqual(len(os.listdir(os.path.join(self.test_dir, "tasks", "completed"))), 0)
        self.assertEqual(len(os.listdir(os.path.join(self.test_dir, "受け渡し"))), 0)

    def test_dry_run_no_mutation(self):
        remote = "https://github.com/myorg/DryRun.git"
        res = initialize_project(self.test_dir, "NEW_PRODUCT", "DryRun", "DRY", remote, dry_run=True)
        self.assertTrue(res)

        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "tasks", "active", "DEV-TASK-0010.md")))

    # --- CLI IDENTITY TESTS (Section 26) ---

    def test_cli_missing_mode_fails(self):
        script_path = os.path.join(self.repo_root, "scripts", "initialize_project.py")
        proc = subprocess.run([sys.executable, script_path, "--name", "MyApp", "--prefix", "APP"], capture_output=True)
        self.assertNotEqual(proc.returncode, 0)

    def test_cli_missing_name_fails(self):
        script_path = os.path.join(self.repo_root, "scripts", "initialize_project.py")
        proc = subprocess.run([sys.executable, script_path, "--mode", "NEW_PRODUCT", "--prefix", "APP"], capture_output=True)
        self.assertNotEqual(proc.returncode, 0)

    def test_cli_missing_prefix_fails(self):
        script_path = os.path.join(self.repo_root, "scripts", "initialize_project.py")
        proc = subprocess.run([sys.executable, script_path, "--mode", "NEW_PRODUCT", "--name", "MyApp"], capture_output=True)
        self.assertNotEqual(proc.returncode, 0)

    def test_cli_remote_only_fails(self):
        script_path = os.path.join(self.repo_root, "scripts", "initialize_project.py")
        proc = subprocess.run([sys.executable, script_path, "--remote", "https://github.com/myorg/App.git"], capture_output=True)
        self.assertNotEqual(proc.returncode, 0)

if __name__ == "__main__":
    unittest.main()
