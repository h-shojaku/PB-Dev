# DEV-TASK-0012 — Initializer安全バイパス撤去・Runtime Reset完全化・最終受入

## 0. Role

あなたはこのRepositoryの **Builder** です。

本Taskは、DEV-TASK-0011のPlanner独立検証で残った不具合を修正する
**PB-Dev初期構築フェーズの最終受入Task**です。

DEV-TASK-0011では多くのFail-Closed化が実装されましたが、
PlannerがHandoff ZIPを別環境で展開し、追加の実動作検証を行った結果、
DEV-TASK-0011自身のInstruction / Acceptance Criteriaと一致していない箇所が残っています。

本Taskでは新しい設計を追加せず、
以下の残課題だけを修正してください。

1. `--force` / `-Force` によるProduct SSOT破壊バイパス撤去
2. PowerShell InitializerをPython Canonical Implementationの薄いwrapperへ統一
3. EXISTING_PRODUCT Analysis Templateの必須Preflight
4. Runtime State Resetの再帰的完全化
5. Final Post-condition Verificationの完全化
6. Integration Testを個別Test Caseへ分離
7. 実成果物とREPORT Evidenceの一致

本TaskがPlanner ReviewでACCEPTEDになれば、
Planner / Builder AI Development Standardの初期構築フェーズを完了とします。

---

# 1. Previous Task

Previous Task:

```text
DEV-TASK-0011
```

Planner Review:

```text
CHANGES_REQUIRED
```

過去Completed Task本文はimmutableです。

```text
tasks/completed/DEV-TASK-0011.md
```

を修正せず、本Taskで追跡してください。

---

# 2. What Passed

Planner側で以下は再確認済みです。

```text
Handoff ZIP extraction: PASS
ZIP entry count: 45
Backslash entries: 0
Absolute entries: 0
Parent traversal entries: 0
create_handoff.py --test: PASS
Python initializer test suite: exit PASS
Git remote update basic behavior: PASS
Non-Git rejection: PASS
Missing remote rejection: PASS
Placeholder remote rejection: PASS
Missing NEW_PRODUCT template rejection: PASS
```

これらは維持してください。

---

# 3. Planner Independent Findings

Plannerは添付されたDEV-TASK-0011 Handoff内の
`scripts/initialize_project.py` をLinux上で直接importし、
Temporary Git Repositoryで追加検証しました。

---

## 3.1 Finding A — `--force` Is Still a Production Safety Bypass

DEV-TASK-0011 Instructionには明示的に以下があります。

```text
## No Force-overwrite Flag

--force のような破壊回避を無効化するflagを追加しない。
必要なら人間が先に状態を整理する。
```

しかし現在の実装には、

```text
--force
-Force
```

が残っています。

Planner独立検証：

```text
docs/product/00_PRODUCT_OVERVIEW.md
= IMPORTANT EXISTING
```

の状態で、

```python
initialize_project(
    ...,
    mode="NEW_PRODUCT",
    force=True
)
```

を実行すると、

```text
Result: SUCCESS
Existing Product SSOT: overwritten
```

を再現しました。

これは直接的なAcceptance Criteria違反です。

---

## 3.2 Finding B — EXISTING_PRODUCT Analysis Template Missing Can Succeed

Planner独立検証で、

```text
templates/product/EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md
```

を削除したTemporary Git Repositoryに対して、

```text
Mode = EXISTING_PRODUCT
```

を実行しました。

結果：

```text
Result: SUCCESS
reports/analysis/EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md: absent
```

でした。

EXISTING_PRODUCTの初期状態としてBaseline Analysis入口が成立していないのに
successになっています。

---

## 3.3 Finding C — Runtime State Reset Is Not Recursive

Temporary Git Repositoryで、

```text
tasks/active/nested/x.md
```

を配置してEXISTING_PRODUCT Initializationを実行しました。

結果：

```text
Result: SUCCESS
tasks/active/nested/: still exists
```

でした。

現在のScriptは`tasks/active/` / `tasks/completed/` の
直下通常ファイルだけを削除し、subdirectoryを残します。

Runtime State Resetは、

```text
tasks/active/
tasks/completed/
受け渡し/
```

について内容を完全に空へする必要があります。

---

## 3.4 Finding D — PowerShell Still Duplicates Business Logic

DEV-TASK-0011では、

```text
scripts/initialize_project.py
= 唯一のCanonical Implementation

scripts/initialize_project.ps1
= Python版を呼び出す薄いwrapper
```

を原則として指定しました。

しかし現在の`initialize_project.ps1`には、

- validation
- remote操作
- profile生成
- runtime reset
- Product SSOT copy
- final verification

のbusiness logicが再実装されています。

これは、

```text
Python / PowerShellのロジック二重管理を廃止
```

という目的を満たしていません。

---

## 3.5 Finding E — Tests Are Still Too Coarse

現在のPython Testは4 Test Methodsです。

特に、

```text
test_negative_cases_fail_closed
```

1件の中へ、

- not git
- missing remote
- placeholder remote
- invalid prefix
- invalid name
- missing template
- existing Product SSOT

をまとめています。

DEV-TASK-0011では、

```text
「4 tests PASS」だけで内部複数条件をまとめすぎず、
失敗箇所を容易に特定できる構造
```

を要求しています。

各Safety Ruleを独立Test Caseとして確認できる形へ分離してください。

---

## 3.6 Finding F — Final Post-condition Verification Is Incomplete

現在のFinal Verificationは主に、

```text
PROJECT_PROFILE exists
CURRENT_STATE exists
TASK_REGISTER exists
NEW_PRODUCT docs/product count >= 6
```

のみです。

しかしTask要件では成功前に最低限、

```text
actual origin == Canonical Remote
tasks/active empty
tasks/completed empty
TASK_REGISTER history empty
CURRENT_STATE = IDLE
CURRENT_STATE Current Task = None
受け渡し delivery artifacts = 0
```

も確認する必要があります。

「処理したつもり」ではなく、
**最終状態を検証してからsuccess**にしてください。

---

# 4. Objective

以下を完了する。

1. `--force` / `-Force`を完全撤去
2. Existing Product SSOTをNEW_PRODUCTで絶対に自動上書きしない
3. Pythonを唯一のInitializer business logicにする
4. PowerShellをPythonを呼び出す薄いwrapperへ変更
5. EXISTING_PRODUCT Analysis Templateを必須Preflight化
6. Runtime State Resetを再帰的に完全化
7. Final Post-condition Verificationを要件どおり完全化
8. Negative Testsを個別Test Methodへ分離
9. Test Suite名だけで失敗Ruleを特定可能にする
10. Dry Runも同じPreflightを通す
11. Python / PowerShellで同じCLI結果になる
12. Integration Testを実Temporary Git Repositoryで実施
13. REPORT Evidenceを実測値と一致させる
14. DEV-TASK-0012を通常Lifecycleで完了
15. GitHubへcommit / push
16. 最新Handoff ZIP 1個を生成

---

# 5. Canonical Initializer Architecture

本Taskでは曖昧にしません。

## Canonical Implementation

```text
scripts/initialize_project.py
```

のみがInitialization business logicを持つ。

---

## PowerShell

```text
scripts/initialize_project.ps1
```

は**薄いwrapper**とする。

役割：

1. 引数を受け取る
2. Python executableを検出する
3. `initialize_project.py` へ同じ引数を渡す
4. Python processのexit codeをそのまま返す

以下をPowerShell側へ実装しない。

- Remote validation logic
- Git remote update logic
- Runtime Reset logic
- Product SSOT validation
- Product SSOT copy
- CURRENT_STATE生成
- PROJECT_PROFILE生成
- Final Post-condition Verification

---

# 6. Remove Force Completely

以下をすべて撤去する。

```text
--force
-Force
force=False
force=True
Force parameter
```

対象：

```text
scripts/initialize_project.py
scripts/initialize_project.ps1
scripts/test_initialize_project.py
scripts/test_initialize_project.ps1
scripts/README.md
current Development SSOT
```

過去Completed Task Instruction Recordは修正しない。

---

## 6.1 Required Behavior

NEW_PRODUCTで`docs/product/`に既存の実内容がある場合：

```text
Initialization FAILED
```

のみ。

人間が既存内容を整理してから再実行する。

Initializerから破壊安全装置を解除する手段を提供しない。

---

# 7. Existing Product SSOT Detection

最低限、

```text
docs/product/
```

内の通常ファイル / subdirectoryを確認する。

既存Product SSOTまたは未知の内容が存在し、
安全にTemplate placeholderと断定できない場合：

```text
FAIL
```

とする。

単に`.md`のsize > 0だけでなく、
未知ファイルを無視して上書きする設計にしない。

---

# 8. NEW_PRODUCT Template Preflight

変更開始前に以下6ファイルをすべて確認。

```text
00_PRODUCT_OVERVIEW.md
01_PRODUCT_PLAN.md
02_REQUIREMENTS.md
03_UI_STRUCTURE.md
04_IMPLEMENTATION_SPEC.md
05_OPERATION_RULES.md
```

不足：

```text
FAIL
No mutation
```

---

# 9. EXISTING_PRODUCT Template Preflight

EXISTING_PRODUCTでは変更開始前に、

```text
templates/product/EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md
```

が存在することを必須確認。

不足：

```text
FAIL
No mutation
```

---

# 10. Recursive Runtime State Reset

派生Project Initializationでは、

```text
tasks/active/
tasks/completed/
受け渡し/
```

の**配下内容をすべて削除**する。

通常ファイルだけでなく、

```text
subdirectory
nested file
temporary directory
```

も対象。

Directory自体は必要に応じて残してよい。

---

## 10.1 Safety Boundary

削除対象は上記3つのRuntime directory配下に限定。

以下を削除しない。

```text
src/
app/
tests/
docs/development/
templates/
.git/
```

---

# 11. Final Post-condition Verification

success表示前に実際の状態を再取得し、
最低限以下をassertする。

## Common

```text
PROJECT_PROFILE exists
PROJECT_PROFILE Project Name == input
PROJECT_PROFILE Mode == input
PROJECT_PROFILE Prefix == input
PROJECT_PROFILE Canonical Remote == input

actual git origin == input Canonical Remote

tasks/active recursive item count == 0
tasks/completed recursive item count == 0
受け渡し recursive item count == 0

TASK_REGISTER Current Active Task == none
TASK_REGISTER Task History row count == 0

CURRENT_STATE Workflow Phase == IDLE
CURRENT_STATE Current Task == None
CURRENT_STATE Latest Completed Task == None
CURRENT_STATE Canonical Remote == input
CURRENT_STATE Task Prefix == input
```

---

## 11.1 NEW_PRODUCT

追加：

```text
docs/product required file count == 6
required filename set == exact 00〜05
```

不要な未知ファイルをTemplate初期化で残さない前提では、
exact set確認を推奨。

---

## 11.2 EXISTING_PRODUCT

追加：

```text
reports/analysis/EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md exists
```

source code preservationはIntegration Testで証明する。

---

# 12. Preflight Before Mutation

以下をMutation前に完了。

```text
1. Input validation
2. Git Repository validation
3. Canonical Remote validation
4. NEW_PRODUCT required templates
5. NEW_PRODUCT existing Product SSOT safety
6. EXISTING_PRODUCT analysis template
7. Planned Runtime Reset boundary validation
```

Preflight Failure時：

```text
No Project Profile change
No Remote change
No Runtime Reset
No Product SSOT mutation
```

---

# 13. Remote Mutation Ordering

可能な限りfilesystem destructive mutation前にPreflightを完了する。

Remote変更自体もmutationなので、
Remote設定後に他のValidation failureが起きないよう
必要Validationを先に済ませる。

---

# 14. Test Suite Structure

`scripts/test_initialize_project.py` を、
少なくとも以下の独立Test Methodsへ分離する。

```text
test_new_product_real_git_integration
test_existing_product_real_git_integration
test_not_git_rejected
test_missing_remote_rejected
test_placeholder_remote_rejected
test_invalid_prefix_rejected
test_invalid_name_rejected
test_missing_new_product_template_rejected_without_mutation
test_missing_existing_analysis_template_rejected_without_mutation
test_existing_product_ssot_rejected_without_mutation
test_nested_active_runtime_is_fully_reset
test_nested_completed_runtime_is_fully_reset
test_dry_run_has_no_mutation
test_remote_post_condition_matches_profile
```

名称は多少変更可。

最低でも各Safety Ruleの失敗箇所がTest名から分かる構造にする。

---

# 15. No Force Test

以下を追加。

```text
assert CLI help does not expose --force
assert initialize_project API has no force bypass argument
assert PowerShell help / parameters have no -Force
```

単なるgrepでもよいが、
自動Testとして再発防止する。

---

# 16. PowerShell Wrapper Test

Windows環境では、

```text
initialize_project.ps1
→ initialize_project.py
```

であることを確認。

最低限：

```text
PowerShell wrapper contains no initialization business logic
Python exit code propagates
NEW_PRODUCT success path works
negative path returns non-zero
```

可能なら`test_initialize_project.ps1`もPython Test Suiteを呼ぶ薄いwrapperへできる。

---

# 17. Dry Run

Dry Runは通常Preflightをすべて実行する。

以下のmutationは0。

```text
Remote URL change
Profile write
Task reset
Product SSOT copy
Analysis template copy
Handoff cleanup
```

実行前後でfilesystem / originを比較してTestする。

---

# 18. REPORT Accuracy

Handoff生成後に実測し、

```text
Initializer test count
passed
failed
actual ZIP entry count
backslash count
absolute count
parent traversal count
delivery file count
```

をREPORTへ反映。

推測・手入力固定値にしない。

---

# 19. Documentation Alignment

必要に応じて以下を更新。

```text
docs/development/PROJECT_INITIALIZATION_RULES.md
docs/development/DEFINITION_OF_DONE.md
scripts/README.md
README.md
```

現行SSOTに、

```text
--force
-Force
```

を推奨する記述を残さない。

過去Completed Taskはimmutableなので検索除外可能。

---

# 20. Independent Verification Scenario

Builder自身でPlannerが行った以下3ケースを必ず再現する。

---

## Scenario A — Existing SSOT

```text
docs/product/00_PRODUCT_OVERVIEW.md
= IMPORTANT EXISTING
```

Expected：

```text
FAIL
content unchanged
origin unchanged
runtime unchanged
```

---

## Scenario B — Missing EXISTING_PRODUCT Analysis Template

```text
templates/product/EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md
= absent
```

Expected：

```text
FAIL
origin unchanged
runtime unchanged
```

---

## Scenario C — Nested Runtime

```text
tasks/active/nested/x.md
tasks/completed/nested/y.md
```

Valid initialization Expected：

```text
SUCCESS
tasks/active recursive count = 0
tasks/completed recursive count = 0
```

---

# 21. Task Lifecycle

DEV-TASK-0012を正式Lifecycleで処理する。

```text
Task Intake
↓
tasks/active/DEV-TASK-0012.md
↓
TASK_REGISTER = ACTIVE
↓
CURRENT_STATE = ACTIVE
↓
Intake commit / push
↓
修正
↓
Integration Tests
↓
Task completion
↓
tasks/completed/DEV-TASK-0012.md
↓
TASK_REGISTER = COMPLETED
↓
CURRENT_STATE = AWAITING_PLANNER_REVIEW
↓
Final commit / push
↓
Handoff生成
```

---

# 22. Git / GitHub

PB-Dev：

```text
Canonical Remote:
https://github.com/h-shojaku/PB-Dev.git

Branch:
main
```

Task IDを含むcommit。

例：

```text
DEV-TASK-0012: register task
DEV-TASK-0012: finalize safe project initializer
```

origin/mainへpush。

---

# 23. Required Verification

最低限：

```text
python scripts/test_initialize_project.py
python scripts/create_handoff.py --test
git diff --check
git status
git remote -v
git log -1
```

WindowsではPowerShell wrapperも確認。

---

# 24. Handoff

Planner提出物は、

```text
受け渡し/DEV-TASK-0012_PLANNER_HANDOFF.zip
```

**1個のみ**。

500MB以内。

標準Generator使用。

Portable Verification PASS。

最低限：

```text
DEV-TASK-0012_PLANNER_HANDOFF.zip
├── REPORT.md
├── MANIFEST.md
└── files/
    ├── PROJECT_PROFILE.md
    ├── CURRENT_STATE.md
    ├── tasks/
    │   ├── TASK_REGISTER.md
    │   └── completed/
    │       └── DEV-TASK-0012.md
    ├── scripts/
    │   ├── initialize_project.py
    │   ├── initialize_project.ps1
    │   ├── test_initialize_project.py
    │   ├── test_initialize_project.ps1
    │   ├── create_handoff.py
    │   └── README.md
    └── docs/
        └── development/
            ├── PROJECT_INITIALIZATION_RULES.md
            └── DEFINITION_OF_DONE.md
```

実際に変更した関連ファイルも含める。

---

# 25. REPORT Required Sections

通常項目に加えて：

```text
## DEV-TASK-0011 Planner Independent Findings
## Force Bypass Removal
## Canonical Python / PowerShell Wrapper
## NEW_PRODUCT Template Preflight
## EXISTING_PRODUCT Analysis Preflight
## Recursive Runtime Reset
## Final Post-condition Verification
## Individual Test Matrix
## Independent Scenario Reproduction
## Handoff Evidence Accuracy
## Final Acceptance Evidence
```

---

# 26. REPORT Concrete Evidence

最低限実値：

```text
Initializer test count:
Initializer passed:
Initializer failed:

Force:
- Python --force exposed: NO
- PowerShell -Force exposed: NO

NEW_PRODUCT:
- actual origin:
- active recursive items:
- completed recursive items:
- handoff recursive items:
- product SSOT required files:
- Task Register history rows:
- CURRENT_STATE phase:

EXISTING_PRODUCT:
- actual origin:
- analysis template exists:
- source hash mismatch:
- runtime recursive items:

Negative:
- existing Product SSOT:
- missing NEW_PRODUCT template:
- missing EXISTING_PRODUCT analysis template:
- not git:
- missing remote:
- placeholder remote:
- invalid prefix:
- invalid name:
- dry run mutation count:

Handoff:
- actual ZIP entries:
- REPORT ZIP entries:
- evidence match:
```

---

# 27. Acceptance Criteria

以下をすべて満たせばCOMPLETE。

- [ ] DEV-TASK-0011のPlanner指摘を新Taskで追跡
- [ ] `--force` がPython CLIから完全撤去
- [ ] `-Force` がPowerShellから完全撤去
- [ ] Python APIにもforce bypassがない
- [ ] Existing Product SSOTをNEW_PRODUCTで自動上書きする経路がない
- [ ] Pythonが唯一のInitializer business logic
- [ ] PowerShellはPython thin wrapper
- [ ] PowerShellにInitialization business logic重複なし
- [ ] NEW_PRODUCT required 00〜05をPreflight
- [ ] NEW_PRODUCT Template不足時No Mutation
- [ ] EXISTING_PRODUCT Analysis TemplateをPreflight
- [ ] Analysis Template不足時No Mutation
- [ ] `tasks/active/` を再帰的に空へreset
- [ ] `tasks/completed/` を再帰的に空へreset
- [ ] `受け渡し/` を再帰的に空へreset
- [ ] Runtime Reset対象外のsourceを削除しない
- [ ] Final Post-conditionでactual originを再確認
- [ ] Final Post-conditionでRuntime directory空を確認
- [ ] Final Post-conditionでTASK_REGISTERを確認
- [ ] Final Post-conditionでCURRENT_STATEを確認
- [ ] Final Post-conditionでNEW_PRODUCT 6ファイルを確認
- [ ] Final Post-conditionでEXISTING_PRODUCT Analysis Templateを確認
- [ ] successはFinal Post-condition PASS後のみ
- [ ] Negative Testが個別Test Methodへ分離
- [ ] Test名から各Safety Ruleを特定可能
- [ ] Existing SSOT Scenario FAIL・No Mutation
- [ ] Missing Analysis Scenario FAIL・No Mutation
- [ ] Nested Runtime Scenario SUCCESS・完全reset
- [ ] Dry Run mutation count = 0
- [ ] 実Temporary Git Repository Integration Test PASS
- [ ] Handoff Generator self-test PASS
- [ ] REPORT実値とZIP実値一致
- [ ] `git diff --check` PASS
- [ ] GitHub commit / push完了
- [ ] tracked working tree clean
- [ ] `受け渡し/` にDEV-TASK-0012 ZIP 1個のみ
- [ ] Handoff portable verification PASS
- [ ] Builder最終回答がZIP絶対パス案内で終了

---

# 28. Builder Final Response

最低限：

```text
Task: DEV-TASK-0012
Status: COMPLETE / BLOCKED

Initializer Final Verification:
- Force bypass removed: PASS / FAIL
- Python canonical implementation: PASS / FAIL
- PowerShell thin wrapper: PASS / FAIL
- NEW_PRODUCT real git: PASS / FAIL
- EXISTING_PRODUCT real git: PASS / FAIL
- Existing SSOT protection: PASS / FAIL
- Missing analysis rejection: PASS / FAIL
- Recursive runtime reset: PASS / FAIL
- Final post-condition: PASS / FAIL
- Individual tests: <actual passed>/<actual total>

Handoff Evidence:
- Actual ZIP Entries: <actual>
- REPORT ZIP Entries: <actual>
- Evidence Match: PASS / FAIL

Task Lifecycle:
- Intake commit: ...
- Final commit: ...
- Register: ...
- Workflow Phase: ...

Git:
- Remote: https://github.com/h-shojaku/PB-Dev.git
- Branch: main
- Push: ...
- Working tree: ...

人間判断:
- 不要
または
- 必要: ...

これをPlannerに渡してください: <実際の絶対パス>\受け渡し\DEV-TASK-0012_PLANNER_HANDOFF.zip
```

**最後の1文より後には何も記載しないこと。**

---

# 29. Final Goal

PB-DevのProject Initializerは、
「危険な状態でもオプションで突破できる便利Script」ではなく、

**「安全条件を満たす場合だけProjectを初期化し、満たさない場合は何も壊さず停止するFail-Closed Bootstrap」**

であること。

DEV-TASK-0012がPlanner ReviewでACCEPTEDになれば、
Planner / Builder AI Development Standardの初期構築フェーズを完了とします。
