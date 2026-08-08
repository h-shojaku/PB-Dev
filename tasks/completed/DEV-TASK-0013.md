# DEV-TASK-0013 — 実Template Clone初期化・PowerShell完全Thin Wrapper・最終受入

## 0. Role

あなたはこのRepositoryの **Builder** です。

本TaskはDEV-TASK-0012のPlanner独立検証で発見された、
Template Repositoryとしての最終ブロッカーだけを修正する補正Taskです。

新しい仕組みを追加するTaskではありません。

今回のゴールは、

```text
現在のPB-Dev Repositoryそのもの
↓
一時コピー / local clone
↓
NEW_PRODUCT または EXISTING_PRODUCT 初期化
↓
安全条件を満たして成功
```

を実動作で証明することです。

本TaskがPlanner ReviewでACCEPTEDになれば、
PB-DevのAI Development Standard初期構築フェーズを完了とします。

---

# 1. Previous Task

Previous Task:

```text
DEV-TASK-0012
```

Planner Review:

```text
CHANGES_REQUIRED
```

過去Completed Taskはimmutableです。

```text
tasks/completed/DEV-TASK-0012.md
```

を修正せず、本Taskとして追跡してください。

---

# 2. What Passed in DEV-TASK-0012

Planner独立検証で以下はPASSしています。

```text
Handoff ZIP extraction: PASS
ZIP entries: 45
Backslash entries: 0
Absolute entries: 0
Parent traversal entries: 0
Archive integrity: PASS

python scripts/create_handoff.py --test: PASS

python scripts/test_initialize_project.py:
12 tests executed
12 tests passed
0 failed
```

以下の主要修正も機能しています。

```text
--force Python bypass: removed
NEW_PRODUCT required 00〜05 preflight: working
EXISTING_PRODUCT analysis template preflight: working
recursive tasks/active reset: working
recursive tasks/completed reset: working
recursive 受け渡し reset: working
non-Git rejection: working
remote required / placeholder rejection: working
actual origin update: working
```

これらを後退させないこと。

---

# 3. Planner Independent Findings

## 3.1 Actual PB-Dev Template Cannot Initialize as NEW_PRODUCT

現在のPB-Dev Repositoryには、

```text
docs/product/README.md
```

が存在します。

これはPB-Dev Template側のProduct Documentation Area説明ファイルです。

現在のInitializerはNEW_PRODUCT Preflightで、

```text
docs/product/*.md
```

に非空ファイルが1件でもあれば、

```text
Existing Product SSOT detected
```

としてFAILします。

つまり現在のPB-DevをそのままTemplateとして複製した場合、

```text
PB-Dev clone
↓
NEW_PRODUCT initialize
```

が正常開始できません。

これはTemplate Repositoryの最重要ユースケースに反します。

---

## 3.2 Unknown Product Content Is Not Fully Protected

現在のexisting Product SSOT検出は主に、

```text
docs/product/ 直下の非空 *.md
```

だけを確認しています。

Planner独立検証では以下が成功しました。

### Unknown file

```text
docs/product/notes.txt
```

が存在する状態：

```text
Initialization: SUCCESS
notes.txt: remains
00〜05: added
```

### Unknown subdirectory

```text
docs/product/legacy/spec.txt
```

が存在する状態：

```text
Initialization: SUCCESS
legacy/spec.txt: remains
00〜05: added
```

NEW_PRODUCT初期化では、
未知の既存Product内容を無視して混在させてはいけません。

---

## 3.3 PowerShell Is Still Not a Thin Wrapper

現在の、

```text
scripts/initialize_project.ps1
```

はPythonを最初に呼び出しますが、
Pythonが存在しない / Python実行が失敗した場合に、

```text
validation
Git remote変更
PROJECT_PROFILE生成
TASK_REGISTER生成
CURRENT_STATE生成
Runtime Reset
Product SSOT copy
Final verification
```

をPowerShell側で再実装するNative fallbackを持っています。

したがって、

```text
Python = Canonical business logic
PowerShell = thin wrapper
```

になっていません。

---

## 3.4 REPORT Test Count Is Incorrect

DEV-TASK-0012 `REPORT.md` では、

```text
Initializer test count: 11
Initializer passed: 11
```

とあります。

しかしPlannerが同梱Test Suiteを実行した実結果は、

```text
Ran 12 tests
OK
```

です。

REPORT内のIndividual Test Matrix自体も12項目あります。

Evidence Accuracy要件に反します。

---

## 3.5 Final Post-condition Verification Is Still Partial

現在のInitializerはFinal Verificationで、

```text
origin
Runtime directories
Product docs count
Analysis template existence
```

等は確認します。

しかしTaskで要求してきた以下の内容を
生成後ファイルから明示的に再読込して検証していません。

```text
PROJECT_PROFILE:
- Project Name
- Project Mode
- Task Prefix
- Canonical Remote

TASK_REGISTER:
- Current Active Task = none
- Task History rows = 0

CURRENT_STATE:
- Workflow Phase = IDLE
- Current Task = None
- Latest Completed Task = None
- Task Prefix = input
- Canonical Remote = input
```

成功判定前に実状態を確認してください。

---

# 4. Objective

以下だけを修正してください。

1. 実PB-Dev TemplateからNEW_PRODUCT初期化可能にする
2. Template固有placeholderと実Product SSOTを安全に区別する
3. unknown file / unknown subdirectoryをNEW_PRODUCTでFAILさせる
4. PowerShell InitializerからNative fallback business logicを完全削除
5. Python未検出 / Python失敗時はPowerShellも非0で終了
6. Final Post-condition Verificationを完全化
7. Test Suiteの実件数をREPORTへ正確に反映
8. 実Repositoryコピーを使うTemplate Clone Acceptance Testを追加
9. GitHub commit / push
10. 最新Handoff ZIP生成

---

# 5. Product Documentation Placeholder Strategy

現在のPB-Dev Templateにある、

```text
docs/product/README.md
```

の扱いを安全に解決してください。

推奨は以下のどちらかです。

---

## Option A — TemplateからREADMEを撤去

PB-Dev TemplateではProduct SSOT本体を、

```text
templates/product/
```

に保持しているため、

```text
docs/product/README.md
```

を削除し、
派生Project初期化時に`docs/product/`を生成する。

Gitは空Directoryを追跡しないため、
PB-Dev本体で`docs/product/`が存在しなくても正常とする。

必要な説明は、

```text
README.md
docs/development/PROJECT_INITIALIZATION_RULES.md
```

へ移す。

この方式を推奨します。

---

## Option B — Machine-recognizable Placeholder

READMEを残す必要がある場合のみ、
Initializerが安全に識別できる明示Markerを持たせる。

例：

```text
PB_DEV_PRODUCT_PLACEHOLDER
```

Initializerは**正確なMarkerを持つ既知placeholderだけ**を初期化前に除去可能。

Markerがない未知ファイルはFAIL。

曖昧な内容比較やfilenameだけで安全判定しない。

---

# 6. NEW_PRODUCT Safe State

NEW_PRODUCTで自動初期化可能な`docs/product/`状態は、
次のどれかだけとする。

```text
docs/product/ does not exist
```

または、

```text
docs/product/ is empty
```

またはOption B採用時のみ、

```text
known machine-recognizable template placeholder only
```

それ以外：

```text
FAIL
NO MUTATION
```

---

# 7. Unknown Product Content Protection

NEW_PRODUCT Preflightでは、

```text
docs/product/
```

を再帰的に確認する。

以下が1件でも存在し、
既知placeholderではない場合：

```text
normal file
unknown extension
subdirectory
nested file
symlink
```

原則：

```text
FAIL
NO MUTATION
```

---

## 7.1 Required Negative Scenarios

最低限：

```text
docs/product/notes.txt
```

Expected:

```text
FAIL
notes.txt unchanged
origin unchanged
runtime unchanged
```

および：

```text
docs/product/legacy/spec.txt
```

Expected:

```text
FAIL
legacy/spec.txt unchanged
origin unchanged
runtime unchanged
```

---

# 8. Actual PB-Dev Template Clone Acceptance Test

これまでのSynthetic fixtureだけでは不十分です。

本Taskでは現在のRepository内容を使い、
Temporary Directoryへ安全なコピーまたはlocal cloneを作成してください。

例：

```text
Current PB-Dev
↓
Temporary clone/copy
↓
git state prepared
↓
initialize_project
```

PB-Dev本体を変更するTestにしないこと。

---

## 8.1 NEW_PRODUCT From Actual Template

Temporary copy / local cloneで：

```text
Mode = NEW_PRODUCT
Name = TemplateTestApp
Prefix = TTA
Canonical Remote = https://github.com/test-org/TemplateTestApp.git
```

Expected：

```text
SUCCESS
origin == requested remote
tasks/active recursive count = 0
tasks/completed recursive count = 0
受け渡し recursive count = 0
TASK_REGISTER history = 0
CURRENT_STATE = IDLE
docs/product required files exactly 00〜05
PB-Dev DEV Task runtime history absent
```

このTestがPASSしなければCOMPLETEにしない。

---

## 8.2 EXISTING_PRODUCT From Actual Template

現在Repositoryを元にしたTemporary fixtureへ
dummy existing sourceを追加。

Expected：

```text
SUCCESS
source hash unchanged
origin == requested remote
runtime reset
analysis template placed
CURRENT_STATE = IDLE
```

---

# 9. PowerShell Must Be a True Thin Wrapper

`scripts/initialize_project.ps1` は以下だけにする。

```text
1. Parameters
2. Python executable discovery
3. initialize_project.py path resolution
4. CLI argument forwarding
5. Python process invocation
6. exact exit-code propagation
```

Pythonが見つからない場合：

```text
clear error
exit non-zero
```

Python initializerが失敗した場合：

```text
same non-zero exit code
```

---

## 9.1 Forbidden in PowerShell Wrapper

以下のInitialization logicを持たない。

```text
validate prefix
validate project name
validate remote
git remote set-url
write PROJECT_PROFILE
write CURRENT_STATE
write TASK_REGISTER
remove runtime files
copy Product SSOT
copy analysis template
Final Post-condition business verification
```

---

## 9.2 No Native Fallback

以下の発想を完全撤去する。

```text
Python failed
↓
PowerShell native initialization fallback
```

正：

```text
Python failed
↓
PowerShell exits failed
```

---

# 10. PowerShell Static Thinness Test

WindowsでPowerShellを実行できるかどうかに加え、
OS非依存のStatic TestもPython Test Suiteへ追加する。

最低限PowerShell wrapper内に、
以下のbusiness operationが存在しないことをassert。

例：

```text
git remote set-url
Set-Content PROJECT_PROFILE
Remove-Item Runtime
Copy-Item Product SSOT
```

実装に合わせて過度にfragileでない方法で検証する。

目的はNative fallbackの再導入防止。

---

# 11. Final Post-condition Verification

Initializer成功前に生成結果を**再読込して検証**する。

---

## 11.1 PROJECT_PROFILE

ファイルを読み、

```text
Project Name == input
Project Mode == input
Task Prefix == input
Canonical Remote == input
```

を確認。

---

## 11.2 TASK_REGISTER

ファイルを読み、

```text
Current Active Task = none
Task History data rows = 0
```

を確認。

Header rowはHistoryとして数えない。

---

## 11.3 CURRENT_STATE

ファイルを読み、

```text
Workflow Phase == IDLE
Current Task == None
Latest Completed Task == None
Task Prefix == input
Canonical Remote == input
```

を確認。

---

## 11.4 Git / Runtime

既存どおり：

```text
actual origin == input remote
tasks/active recursive count == 0
tasks/completed recursive count == 0
受け渡し recursive count == 0
```

---

## 11.5 NEW_PRODUCT

Required filename setをexact確認：

```text
00_PRODUCT_OVERVIEW.md
01_PRODUCT_PLAN.md
02_REQUIREMENTS.md
03_UI_STRUCTURE.md
04_IMPLEMENTATION_SPEC.md
05_OPERATION_RULES.md
```

未知ファイル / subdirectoryが混在していないこと。

---

## 11.6 EXISTING_PRODUCT

```text
reports/analysis/EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md exists
```

---

# 12. CLI Required Inputs

Template初期化時の誤操作防止として、
通常CLIでは最低限以下を明示入力とする。

```text
--mode
--name
--prefix
```

`NEW_PRODUCT` / `EXISTING_PRODUCT`では、

```text
--remote
```

も必須。

`MyNewProduct` / `APP`等のplaceholder defaultで
意図せず成功しないこと。

Function APIの内部Test利用は明示引数でよい。

---

# 13. Test Suite

既存12 Testを維持し、
最低限以下を追加する。

```text
test_actual_template_new_product_initialization
test_actual_template_existing_product_initialization
test_unknown_product_file_rejected_without_mutation
test_unknown_product_subdirectory_rejected_without_mutation
test_powershell_is_thin_wrapper
test_final_profile_postconditions
test_final_register_postconditions
test_final_current_state_postconditions
```

合理的に統合してもよいが、
失敗RuleがTest名から判別できること。

---

# 14. Test Count Must Be Measured

REPORTへTest件数を固定値で書かない。

Test runnerの実結果から取得し、

```text
actual total
actual passed
actual failed
```

を記載。

例：

```text
Ran 20 tests
20 passed
0 failed
```

実際の件数に合わせる。

---

# 15. No-Mutation Snapshot

Negative Testsでは、
単に`False`を返したことだけでなく、
Preflight前後の状態を比較する。

最低限：

```text
origin
PROJECT_PROFILE hash/existence
CURRENT_STATE hash/existence
TASK_REGISTER hash/existence
tasks/active tree
tasks/completed tree
docs/product tree
受け渡し tree
```

対象ケース：

```text
unknown product file
unknown product subdirectory
missing required template
missing analysis template
invalid input
```

---

# 16. Documentation Alignment

必要な場合のみ以下を更新。

```text
README.md
docs/development/PROJECT_INITIALIZATION_RULES.md
docs/development/DEFINITION_OF_DONE.md
scripts/README.md
```

現在のTemplateで`docs/product/README.md`を削除する場合は、
README等に、

```text
docs/product/ is created during Project Initialization
```

を明記する。

過去Completed Task本文は修正しない。

---

# 17. Task Lifecycle / Git

通常Lifecycleを適用。

```text
DEV-TASK-0013 Intake
↓
ACTIVE
↓
Intake commit / push
↓
修正
↓
Actual Template Clone Tests
↓
Completed
↓
Final commit / push
↓
Handoff生成
```

PB-Dev：

```text
Canonical Remote:
https://github.com/h-shojaku/PB-Dev.git

Branch:
main
```

Task IDをcommit messageへ含める。

---

# 18. Required Verification

最低限：

```text
python scripts/test_initialize_project.py
python scripts/create_handoff.py --test
git diff --check
git status
git remote -v
git log -1
```

可能なWindows環境ではPowerShell wrapper実行も確認。

---

# 19. Handoff

Planner提出物：

```text
受け渡し/DEV-TASK-0013_PLANNER_HANDOFF.zip
```

**1個のみ**。

500MB以内。

標準Generator使用。

Portable Verification PASS。

最低限：

```text
DEV-TASK-0013_PLANNER_HANDOFF.zip
├── REPORT.md
├── MANIFEST.md
└── files/
    ├── PROJECT_PROFILE.md
    ├── CURRENT_STATE.md
    ├── README.md
    ├── tasks/
    │   ├── TASK_REGISTER.md
    │   └── completed/
    │       └── DEV-TASK-0013.md
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

`docs/product/README.md`を変更・削除した場合は、
その事実をREPORTへ明記する。

---

# 20. REPORT Required Sections

最低限：

```text
## DEV-TASK-0012 Planner Independent Findings
## Actual PB-Dev Template Baseline
## Product Placeholder Resolution
## Unknown Product Content Protection
## PowerShell Thin Wrapper Verification
## Final Post-condition Verification
## Actual Template NEW_PRODUCT Test
## Actual Template EXISTING_PRODUCT Test
## No-Mutation Negative Tests
## Handoff Evidence Accuracy
## Final Acceptance Evidence
```

---

# 21. REPORT Concrete Evidence

実値で記載。

```text
Initializer tests:
- total:
- passed:
- failed:

Actual PB-Dev Template NEW_PRODUCT:
- result:
- origin:
- active recursive items:
- completed recursive items:
- Task Register history rows:
- Product SSOT files:
- unknown Product files:
- workflow phase:

Actual PB-Dev Template EXISTING_PRODUCT:
- result:
- origin:
- source hash mismatches:
- analysis template:
- workflow phase:

PowerShell:
- Native fallback exists: NO
- Business logic duplication: NO
- Python exit code propagation: PASS

Negative:
- unknown Product file: FAIL / no mutation
- unknown Product subdirectory: FAIL / no mutation

Handoff:
- actual ZIP entries:
- reported ZIP entries:
- backslash:
- absolute:
- traversal:
- evidence match:
```

---

# 22. Acceptance Criteria

以下をすべて満たせばCOMPLETE。

- [ ] DEV-TASK-0012 Planner指摘を新Taskで追跡
- [ ] 現在のPB-Dev TemplateからNEW_PRODUCT初期化できる
- [ ] 現在のPB-Dev TemplateからEXISTING_PRODUCT初期化できる
- [ ] `docs/product/README.md` placeholder問題が安全に解消
- [ ] unknown `docs/product` fileでNEW_PRODUCT FAIL
- [ ] unknown `docs/product` subdirectoryでNEW_PRODUCT FAIL
- [ ] 上記Negative CaseでNo Mutation
- [ ] Pythonが唯一のInitializer business logic
- [ ] PowerShellは真のthin wrapper
- [ ] PowerShell Native fallbackが存在しない
- [ ] Python unavailable時PowerShellはnon-zero
- [ ] Python failure時PowerShellは同等non-zero
- [ ] Final Post-conditionでPROJECT_PROFILE内容を再検証
- [ ] Final Post-conditionでTASK_REGISTER内容を再検証
- [ ] Final Post-conditionでCURRENT_STATE内容を再検証
- [ ] actual originを再検証
- [ ] Runtime recursive emptyを再検証
- [ ] NEW_PRODUCT Product SSOT filename setをexact確認
- [ ] EXISTING_PRODUCT Analysis Templateを確認
- [ ] CLIのProject identity入力が意図せずdefault成功しない
- [ ] Actual Template NEW_PRODUCT Integration Test PASS
- [ ] Actual Template EXISTING_PRODUCT Integration Test PASS
- [ ] Test countが実Test Runner結果と一致
- [ ] REPORT passed / failed件数が実結果と一致
- [ ] Handoff ZIP entry countがREPORTと一致
- [ ] Handoff Generator self-test PASS
- [ ] `git diff --check` PASS
- [ ] GitHub commit / push完了
- [ ] tracked working tree clean
- [ ] `受け渡し/` にDEV-TASK-0013 ZIP 1個のみ
- [ ] Handoff portable verification PASS
- [ ] Builder最終回答がZIP絶対パス案内で終了

---

# 23. Builder Final Response

最低限：

```text
Task: DEV-TASK-0013
Status: COMPLETE / BLOCKED

Final Template Acceptance:
- Actual Template NEW_PRODUCT: PASS / FAIL
- Actual Template EXISTING_PRODUCT: PASS / FAIL
- Unknown Product Content Protection: PASS / FAIL
- PowerShell Thin Wrapper: PASS / FAIL
- Final Post-condition Verification: PASS / FAIL
- Initializer Tests: <passed>/<total>

Handoff Evidence:
- Actual ZIP Entries: ...
- REPORT ZIP Entries: ...
- Evidence Match: PASS / FAIL

Git:
- Remote: https://github.com/h-shojaku/PB-Dev.git
- Branch: main
- Push: ...
- Working tree: ...

人間判断:
- 不要
または
- 必要: ...

これをPlannerに渡してください: <実際の絶対パス>\受け渡し\DEV-TASK-0013_PLANNER_HANDOFF.zip
```

**最後の1文より後には何も記載しないこと。**

---

# 24. Final Goal

本TaskではSynthetic fixtureだけを通して完了にしないでください。

最終的に証明すべきことは、

```text
現在のPB-Dev Repositoryそのもの
↓
Templateとして複製
↓
Project Initializer実行
↓
安全なProduct Repositoryへ初期化
↓
<PREFIX>-TASK-0001を開始可能
```

です。

DEV-TASK-0013がPlanner ReviewでACCEPTEDになれば、
PB-DevのPlanner / Builder AI Development Standard初期構築フェーズを完了とします。
