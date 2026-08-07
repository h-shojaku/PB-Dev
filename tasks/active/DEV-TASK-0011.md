# DEV-TASK-0011 — Initializer Fail-Closed化・実Git Integration Test・最終受入補正

## 0. Role

あなたはこのRepositoryの **Builder** です。

本Taskは、DEV-TASK-0010のPlanner独立検証で発見された残課題を修正する
**AI Development Standard初期構築フェーズの最終補正Task**です。

DEV-TASK-0010ではProject Initializerの主要機能は改善されましたが、
Builder側テストがRemote Safetyの核心部分を `allow mismatch` で迂回しており、
Plannerが実際のTemporary Git Repositoryで追加検証したところ、
まだ「失敗すべき状態を成功扱いする」ケースが残っていました。

本TaskではProject Initializerを **Fail Closed** にし、
「処理がexit 0した」ではなく
**実Git状態・実ファイルシステム状態・REPORT Evidenceまで一致すること**
を自動テストしてください。

本TaskがPlanner ReviewでACCEPTEDになれば、
PB-Devの初期構築フェーズを完了とします。

---

# 1. Previous Task

Previous Task:

```text
DEV-TASK-0010
```

Planner Review:

```text
CHANGES_REQUIRED
```

DEV-TASK-0010のCompleted Instruction Recordはimmutableです。

修正内容を過去Taskへ追記・改変せず、
DEV-TASK-0011として追跡してください。

---

# 2. What Passed in DEV-TASK-0010

Planner独立検証で以下はPASSしています。

```text
Handoff ZIP展開: PASS
ZIP entry count: 45
Backslash entries: 0
Absolute entries: 0
Parent traversal entries: 0
Archive integrity: PASS
create_handoff.py --test: PASS
test_initialize_project.py: 4 tests PASS
```

また以下の主要改善も確認できています。

```text
tasks/active reset
tasks/completed reset
受け渡し reset
TASK_REGISTER reset
CURRENT_STATE reset
NEW_PRODUCT Product SSOT 00〜05配置
EXISTING_PRODUCT source preservation
placeholder remote validation
prefix validation
project name validation
```

これらを後退させないこと。

---

# 3. Planner Independent Verification Findings

PlannerはDEV-TASK-0010 HandoffをLinux環境へ展開し、
Builderのテストに加えて独自のTemporary Repository検証を行いました。

以下は実際に再現した問題です。

---

## 3.1 Finding A — Wrong `origin` Can Still Succeed

Temporary Git Repository：

```text
actual origin:
https://github.com/other/Wrong.git

requested Canonical Remote:
https://github.com/myorg/TestApp.git
```

でInitializerを実行しました。

結果：

```text
Initializer returned: SUCCESS
actual origin after initialization:
https://github.com/other/Wrong.git
```

つまり、

```text
PROJECT_PROFILE Canonical Remote
!=
actual git origin
```

の状態を成功扱いできます。

これはDefinition of DoneおよびProject Initialization Rulesに違反します。

---

## 3.2 Finding B — Non-Git Directory Can Succeed

`.git` が存在しないTemporary DirectoryでInitializerを実行しました。

結果：

```text
Initializer returned: SUCCESS
```

実Project Initializationでは、
Git Repositoryでない状態を成功扱いしてはいけません。

---

## 3.3 Finding C — Missing Product Template Can Succeed

NEW_PRODUCT fixtureから、

```text
templates/product/05_OPERATION_RULES.md
```

を削除してInitializerを実行しました。

結果：

```text
Initializer returned: SUCCESS
docs/product file count: 5
```

Product SSOT 00〜05が揃っていないのにsuccessになっています。

---

## 3.4 Finding D — Existing Product SSOT Is Silently Overwritten

NEW_PRODUCT fixtureの、

```text
docs/product/00_PRODUCT_OVERVIEW.md
```

へ既存内容を入れてからInitializerを実行しました。

結果：

```text
Initializer returned: SUCCESS
既存内容はTemplate内容で上書き
```

これはTemplate初期化時の安全性要件に反します。

NEW_PRODUCTだからといって、
既存Product SSOTを確認なく破壊してはいけません。

---

## 3.5 Finding E — Current Integration Tests Bypass Remote Safety

現在のPython Integration Testでは概ね、

```python
allow_mismatch=True
```

を使用しています。

PowerShell Testでも、

```text
-AllowRemoteMismatch
```

を使用しています。

さらにfixture自体が実Git Repositoryではありません。

したがって現在の、

```text
NEW_PRODUCT Integration Test: PASS
EXISTING_PRODUCT Integration Test: PASS
Remote Safety: PASS
```

は、Remote Safetyの実動作を証明していません。

---

## 3.6 Finding F — REPORT Evidence Is Not Exact

DEV-TASK-0010 `REPORT.md` では、

```text
Entry count: 41
```

と報告されていますが、
Plannerが実ZIPを直接確認した結果は、

```text
Entry count: 45
```

でした。

Handoff自体は正常ですが、
**REPORT Evidenceと実成果物が一致していません。**

Definition of Doneの、

```text
失敗・事実を正しく記録する
Evidenceを正しくREPORTへ記録する
```

という原則に反します。

---

# 4. Objective

以下を完了してください。

1. Project Initializerを実Git Repository前提のFail-Closed設計にする
2. `PROJECT_PROFILE Canonical Remote == actual origin` を成功条件にする
3. 指定RemoteをInitializer自身が安全にoriginへ反映する
4. `.git` がない実InitializationをFAILにする
5. 必須Product Template不足をFAILにする
6. NEW_PRODUCTで既存Product SSOTを無断上書きしない
7. Remote Safety bypassを通常Integration Testから排除する
8. Temporary Git Repositoryを使う実Integration Testへ変更する
9. Git remote状態までassertする
10. filesystem最終状態までassertする
11. 初期化処理終了前のFinal Verificationを実装する
12. REPORTの数値を実成果物から自動取得または正確に生成する
13. Python / PowerShellの入口を同一ロジックへ統一する
14. DEV-TASK-0011を通常Lifecycleで完了
15. GitHub commit / push
16. 最新Handoff ZIP 1個を生成
17. Plannerが再実行可能なTest Evidenceを同梱する

---

# 5. Canonical Initializer Architecture

本Taskでは、

```text
scripts/initialize_project.py
```

を**唯一のCanonical implementation**としてください。

PowerShell版：

```text
scripts/initialize_project.ps1
```

はPython版を呼び出す**薄いwrapper**へ変更することを原則とします。

理由：

- Python / PowerShellのロジック二重管理を廃止
- Windows / macOS / Linuxで同一ロジック
- 将来の修正漏れ防止
- Test対象を1つに固定
- Development SSOTのAI Agnostic思想と一致

PowerShellネイティブ実装を残す合理的理由がある場合は、
Planner Reviewで同一動作を証明できる自動テストが必要です。

特別な理由がなければPython Canonical + thin PowerShell wrapperを採用してください。

---

# 6. Remove Production Safety Bypass

現在の、

```text
--allow-remote-mismatch
-AllowRemoteMismatch
```

は本番利用時に安全規則を無効化できるため、
通常のProject Initialization interfaceから削除することを推奨します。

最低条件：

- Production initializationでは使用不可
- Integration Testもこのflagを使わない
- Remote Safety Testを迂回しない

内部Unit Test専用helperとして残す場合でも、
CLIの通常ユーザーが誤使用できない設計にしてください。

---

# 7. Git Repository Requirement

`NEW_PRODUCT` / `EXISTING_PRODUCT` の実Initializationは、

```text
.git
```

を持つ有効なGit Repositoryであることを必須とします。

最低限、Initializer内部で以下に相当する確認を行う。

```text
git rev-parse --is-inside-work-tree
```

期待：

```text
true
```

それ以外：

```text
Initialization FAILED
```

---

## 7.1 Dry Run

Dry RunでもGit Repository Safety Checkを実行する。

Dry Runは「変更しない」だけであり、
危険状態を成功扱いするモードではありません。

---

# 8. Canonical Remote Application

ユーザーが明示的に、

```text
--remote <Canonical Remote>
```

を指定しているため、
Initializerはその値を派生Projectの正式originへ反映してください。

標準動作：

## origin exists

```text
git remote set-url origin <Canonical Remote>
```

## origin does not exist

```text
git remote add origin <Canonical Remote>
```

---

## 8.1 Post-condition

Initialization成功前に必ず、

```text
git remote get-url origin
```

を取得し、

```text
actual origin == requested Canonical Remote
```

を確認する。

一致しない場合：

```text
Initialization FAILED
```

---

## 8.2 PB-Dev Template Remote

派生Projectで現在originが、

```text
https://github.com/h-shojaku/PB-Dev.git
```

でも、
ユーザーが新しいCanonical Remoteを明示指定している場合は、
**指定Remoteへ安全に切り替える**。

これによりTemplate cloneからの初期化をスムーズにする。

ただし、

```text
--remote
```

未指定時に勝手なRemoteを生成しない。

---

# 9. Remote URL Comparison

単純なsubstring比較ではなく、
少なくともactual origin全体を取得して比較する。

以下を誤って同一としない。

```text
https://github.com/org/App.git
https://github.com/org/App2.git
```

必要なら末尾 `/` 等の安全なNormalizationのみ行う。

異なるRepositoryを同一視してはいけません。

---

# 10. Product Template Preflight

NEW_PRODUCT Initializationで必要なTemplate：

```text
templates/product/
├── 00_PRODUCT_OVERVIEW.md
├── 01_PRODUCT_PLAN.md
├── 02_REQUIREMENTS.md
├── 03_UI_STRUCTURE.md
├── 04_IMPLEMENTATION_SPEC.md
└── 05_OPERATION_RULES.md
```

Initializerは**変更開始前**に6ファイルすべて存在するか確認する。

1つでも欠ける場合：

```text
Initialization FAILED
```

Runtime resetやProfile書換えを始める前にFailすること。

---

# 11. NEW_PRODUCT Existing SSOT Safety

NEW_PRODUCTで、

```text
docs/product/
```

に既存内容がある場合、
確認なくTemplateでoverwriteしてはいけません。

---

## 11.1 Safe Empty State

以下なら自動初期化可能。

```text
docs/product/ が存在しない
```

または、

```text
docs/product/ が空
```

または、
明確にTemplate placeholderだけであることを
安全かつ機械的に判定できる場合。

---

## 11.2 Non-empty / Unknown Existing State

既存Product SSOTがある場合：

```text
Initialization FAILED
```

とし、

```text
Existing Product SSOT detected.
Use EXISTING_PRODUCT or resolve existing docs before NEW_PRODUCT initialization.
```

等を明示する。

---

## 11.3 No Force-overwrite Flag

本Taskでは、

```text
--force
```

のような破壊回避を無効化するflagを追加しない。

必要なら人間が先に状態を整理する。

---

# 12. Preflight Before Mutation

Initializerは、
可能なValidationを**ファイル変更前にすべて実行**する。

推奨順：

```text
1. Input validation
2. Git repository validation
3. Remote input validation
4. Product template existence validation
5. Product SSOT safety validation
6. Existing source / required structure validation
7. Planned remote operation validation
8. Mutation開始
```

Validation failure後に、

```text
PROJECT_PROFILEだけ書き換わった
Task historyだけ消えた
```

等の半端状態を残さない。

---

# 13. Final Verification Before Success

Mutation後、
successを表示する直前に最終状態を機械検証する。

共通：

```text
PROJECT_PROFILE exists
PROJECT_PROFILE inputs match
actual origin == Canonical Remote
tasks/active files = 0
tasks/completed files = 0
TASK_REGISTER task history = 0
CURRENT_STATE Workflow Phase = IDLE
CURRENT_STATE Current Task = None
受け渡し delivery artifacts = 0
```

NEW_PRODUCT：

```text
docs/product 00〜05 = exactly present
```

EXISTING_PRODUCT：

```text
required analysis template available
existing source preservation verified by Integration Test
```

どれかFAIL：

```text
Initialization FAILED
```

成功文言を出さない。

---

# 14. Transaction / Partial Failure Safety

Remote変更後にfilesystem操作が失敗する可能性も考慮する。

過剰なTransaction systemは不要ですが、
少なくとも以下を満たすこと。

- Preflightで可能な失敗を先に検出
- file copy missing等はMutation前に検出
- final verification失敗をsuccess扱いしない
- エラー理由を明示

可能なら、
書き換え対象の小さなstate filesは
temporary file → atomic replace等を利用してよい。

---

# 15. Rebuild Integration Tests with Real Git Repositories

現在のTest fixtureはRemote Safetyを迂回しています。

本TaskではTemporary Directoryごとに実際に、

```text
git init
git remote add origin ...
```

を実行してください。

Integration Testで、

```text
allow mismatch
```

を使用してはいけません。

---

# 16. NEW_PRODUCT Integration Test

Temporary Git Repository fixture：

```text
.git/
origin = https://github.com/h-shojaku/PB-Dev.git

tasks/active/OLD.md
tasks/completed/DEV-TASK-0010.md
TASK_REGISTER = DEV history
CURRENT_STATE = PB-Dev state
受け渡し/OLD_HANDOFF.zip

templates/product/00〜05
docs/product/ = empty
```

実行：

```text
Mode: NEW_PRODUCT
Name: TestApp
Prefix: TST
Remote: https://github.com/test-org/TestApp.git
```

assert：

```text
exit / result: SUCCESS
origin == https://github.com/test-org/TestApp.git
PROJECT_PROFILE Canonical Remote == same
tasks/active count == 0
tasks/completed count == 0
Task Register history count == 0
CURRENT_STATE == IDLE
Latest Completed Task == None
old Handoff count == 0
docs/product required files == 6
Next Action contains TST-TASK-0001
```

---

# 17. EXISTING_PRODUCT Integration Test

Temporary Git Repository fixture：

```text
origin = PB-Dev or another source remote
src/app.txt
config/example.json
```

initial file hashesを取得。

実行：

```text
Mode: EXISTING_PRODUCT
Name: LegacyApp
Prefix: LEG
Remote: https://github.com/test-org/LegacyApp.git
```

assert：

```text
SUCCESS
origin == requested remote
Profile remote == requested remote
runtime task state reset
CURRENT_STATE == IDLE
Next Action = LEG-TASK-0001 Baseline Analysis
analysis template exists
src/app.txt hash unchanged
config/example.json hash unchanged
```

---

# 18. Required Negative Tests

最低限以下を実装。

## 18.1 Not a Git Repository

```text
Expected: FAIL
No state mutation
```

---

## 18.2 Missing Remote

```text
Expected: FAIL
No state mutation
```

---

## 18.3 Placeholder Remote

```text
Expected: FAIL
No state mutation
```

---

## 18.4 Invalid Prefix

```text
Expected: FAIL
No state mutation
```

---

## 18.5 Invalid Project Name

```text
Expected: FAIL
No state mutation
```

---

## 18.6 Missing Product Template

6ファイルのうち1つを削除。

```text
Expected: FAIL
docs/product not partially populated
runtime state not reset
```

---

## 18.7 Existing Product SSOT in NEW_PRODUCT

```text
docs/product/00_PRODUCT_OVERVIEW.md
= important existing content
```

Expected：

```text
FAIL
existing file content unchanged
runtime state unchanged
```

---

## 18.8 Wrong Origin Post-condition

Test helper等でremote update failureを再現可能なら、

```text
actual origin != requested remote
```

の状態では成功しないことを確認。

少なくともIntegration Testで、
Initializer実行後の実originをassertする。

---

# 19. Dry Run Integration Test

実Git Repository上で実行。

Dry Run前後で、

```text
git remote get-url origin
filesystem snapshot
```

が変わらないことを確認。

ただしValidationは通常通り実施。

Dry Run出力には最低限：

```text
Current origin
Requested Canonical Remote
Planned origin action
Runtime files to reset
Product SSOT action
Final expected state
```

を表示する。

---

# 20. PowerShell Wrapper Test

PowerShell wrapperはCanonical Python implementationを呼ぶだけの薄い入口とする。

Windows環境では最低限：

```text
PowerShell wrapper
→ Python initializer
→ NEW_PRODUCT Integration behavior
```

を確認する。

PowerShell専用のInitialization business logicを重複させない。

---

# 21. Test Suite Result Requirements

Python test実行例：

```text
python scripts/test_initialize_project.py
```

最低限、Test名単位で以下が見えること。

```text
NEW_PRODUCT real git integration
EXISTING_PRODUCT real git integration
not-git rejection
missing remote rejection
placeholder rejection
invalid prefix rejection
invalid name rejection
missing template rejection
existing Product SSOT rejection
dry-run no mutation
remote post-condition
```

「4 tests PASS」だけで内部複数条件をまとめすぎず、
失敗箇所を容易に特定できる構造にする。

---

# 22. Evidence Must Be Generated from Reality

REPORTへ以下の数値を手入力で推測しない。

特に：

```text
ZIP entry count
Test count
Delivery file count
Product SSOT file count
Git commit
```

は実際のコマンド / Script結果から取得する。

Handoff Generatorが既にVerification結果を返せるなら、
その実値をREPORTへ反映する。

---

# 23. Handoff REPORT Accuracy Check

Handoff生成後、
REPORTに記録された主要数値と実ZIPを照合する。

最低限：

```text
Reported ZIP entry count == actual ZIP entry count
Reported backslash count == actual
Reported absolute path count == actual
Reported parent traversal count == actual
Reported delivery ZIP count == actual
```

不一致なら提出しない。

---

# 24. Documentation Alignment

実装修正後、必要な場合のみ以下を更新。

```text
docs/development/PROJECT_INITIALIZATION_RULES.md
docs/development/DEFINITION_OF_DONE.md
docs/development/GIT_RULES.md
scripts/README.md
README.md
```

以下をSSOTへ明記。

- Initialization requires Git Repository
- explicit Canonical Remote required
- Initializer sets / verifies origin
- NEW_PRODUCT does not overwrite unknown existing Product SSOT
- missing Product Template is fatal
- successful initialization requires final state verification

Documentation要件を弱めてScriptへ合わせてはいけません。

---

# 25. Task Lifecycle

DEV-TASK-0011も正式Lifecycleを適用。

```text
Task Intake
↓
tasks/active/DEV-TASK-0011.md
↓
TASK_REGISTER = ACTIVE
↓
CURRENT_STATE = ACTIVE
↓
Intake commit / push
↓
実装修正
↓
Real Git Integration Tests
↓
Negative Tests
↓
Task completion
↓
tasks/completed/DEV-TASK-0011.md
↓
TASK_REGISTER = COMPLETED
↓
CURRENT_STATE = AWAITING_PLANNER_REVIEW
↓
Final commit / push
↓
Handoff生成
↓
REPORT Accuracy Verification
```

---

# 26. Git / GitHub

PB-Dev本体：

```text
Canonical Remote:
https://github.com/h-shojaku/PB-Dev.git

Branch:
main
```

Task IDを含むcommitを作成。

例：

```text
DEV-TASK-0011: register task
DEV-TASK-0011: make project initialization fail closed
```

origin/mainへpush。

---

# 27. Required Verification

最低限以下を実行。

```text
python scripts/test_initialize_project.py
python scripts/create_handoff.py --test
git diff --check
git status
git log -1
git remote -v
```

Windows環境ではPowerShell wrapperも検証。

---

# 28. Planner Handoff

Planner提出物は必ず、

```text
受け渡し/DEV-TASK-0011_PLANNER_HANDOFF.zip
```

**1個のみ**。

500MB以内。

標準Generator使用。

Portable Verification PASS。

最低限以下を含める。

```text
DEV-TASK-0011_PLANNER_HANDOFF.zip
├── REPORT.md
├── MANIFEST.md
└── files/
    ├── PROJECT_PROFILE.md
    ├── CURRENT_STATE.md
    ├── tasks/
    │   ├── TASK_REGISTER.md
    │   └── completed/
    │       └── DEV-TASK-0011.md
    ├── scripts/
    │   ├── initialize_project.py
    │   ├── initialize_project.ps1
    │   ├── test_initialize_project.py
    │   ├── create_handoff.py
    │   └── README.md
    └── docs/
        └── development/
            ├── PROJECT_INITIALIZATION_RULES.md
            ├── DEFINITION_OF_DONE.md
            └── GIT_RULES.md
```

実際に変更した関連ファイルも含める。

---

# 29. REPORT Required Sections

通常項目に加えて以下を含める。

```text
## DEV-TASK-0010 Planner Independent Findings

## Canonical Initializer Architecture

## Real Git NEW_PRODUCT Integration Test

## Real Git EXISTING_PRODUCT Integration Test

## Remote Post-condition Verification

## Git Repository Requirement Verification

## Product Template Preflight Verification

## Existing Product SSOT Protection Verification

## Negative Test Matrix

## Dry Run No-Mutation Verification

## Handoff Evidence Accuracy Verification

## Final Template Acceptance Evidence
```

---

# 30. REPORT Required Concrete Evidence

最低限以下を実値で記録。

```text
Initializer test count:
Initializer tests passed:
Initializer tests failed:

NEW_PRODUCT:
- origin before:
- requested remote:
- origin after:
- active files after:
- completed files after:
- Task Register history rows:
- Product SSOT files:
- old Handoff files:

EXISTING_PRODUCT:
- origin after:
- source files verified:
- source hash mismatches:
- runtime reset:

Negative:
- not git:
- missing remote:
- placeholder:
- invalid prefix:
- invalid name:
- missing template:
- existing Product SSOT:
- dry run mutation count:

Handoff:
- actual ZIP entry count:
- reported ZIP entry count:
- backslash entries:
- absolute entries:
- parent traversal entries:
```

---

# 31. Acceptance Criteria

以下をすべて満たせばCOMPLETE。

- [ ] DEV-TASK-0010 Planner Review指摘を新Taskで追跡
- [ ] Python InitializerがCanonical implementation
- [ ] PowerShellはthin wrapperまたは同等性を証明
- [ ] Production safety bypassがない
- [ ] NEW_PRODUCT / EXISTING_PRODUCTはGit Repository必須
- [ ] `.git` なしでsuccessにならない
- [ ] Canonical Remote指定必須
- [ ] placeholder Remoteでsuccessにならない
- [ ] Initializerがactual originを指定Canonical Remoteへ設定
- [ ] Initialization後 actual origin == Project Profile Remote
- [ ] 任意のwrong originを残したままsuccessにならない
- [ ] PB-Dev originを派生Project Remoteとして残さない
- [ ] Product Template 00〜05不足時にFAIL
- [ ] Template不足でpartial mutationしない
- [ ] NEW_PRODUCTで既存Product SSOTを無断overwriteしない
- [ ] Existing Product SSOT検出時はFAILまたは非破壊安全処理
- [ ] ValidationをMutation前に実施
- [ ] Final state verification後のみsuccess
- [ ] Runtime State Resetが維持されている
- [ ] NEW_PRODUCT Product SSOT 6ファイル配置
- [ ] EXISTING_PRODUCT source preservation
- [ ] Integration Testsが実Temporary Git Repositoryを使用
- [ ] Integration TestsでRemote bypassを使用しない
- [ ] Integration Testsがactual originをassert
- [ ] NEW_PRODUCT real git integration PASS
- [ ] EXISTING_PRODUCT real git integration PASS
- [ ] not-git negative test PASS
- [ ] missing remote negative test PASS
- [ ] placeholder negative test PASS
- [ ] invalid prefix negative test PASS
- [ ] invalid name negative test PASS
- [ ] missing Product Template negative test PASS
- [ ] existing Product SSOT protection test PASS
- [ ] Dry Run no-mutation test PASS
- [ ] Handoff Generator self-test PASS
- [ ] REPORT数値と実Handoffが一致
- [ ] ZIP actual entry countとREPORT entry countが一致
- [ ] `git diff --check` PASS
- [ ] GitHub commit / push完了
- [ ] tracked working tree clean
- [ ] `受け渡し/` にDEV-TASK-0011 ZIP 1個のみ
- [ ] Handoff portable verification PASS
- [ ] Builder最終回答がZIP絶対パス案内で終了

---

# 32. Builder Final Response

最低限：

```text
Task: DEV-TASK-0011
Status: COMPLETE / BLOCKED

実施内容:
- ...

Initializer Final Verification:
- Real Git NEW_PRODUCT: PASS / FAIL
- Real Git EXISTING_PRODUCT: PASS / FAIL
- Actual Remote Match: PASS / FAIL
- Non-Git Rejection: PASS / FAIL
- Missing Template Rejection: PASS / FAIL
- Existing Product SSOT Protection: PASS / FAIL
- Dry Run No-Mutation: PASS / FAIL
- Test Count: <actual>

Handoff Evidence:
- Actual ZIP Entries: <actual>
- REPORT ZIP Entries: <reported>
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

これをPlannerに渡してください: <実際の絶対パス>\受け渡し\DEV-TASK-0011_PLANNER_HANDOFF.zip
```

**最後の1文より後には何も記載しないこと。**

---

# 33. Final Goal

本Taskの目的は「テストを増やすこと」ではありません。

最終的に、

```text
PB-Dev Template
↓
実Git Repositoryとして派生
↓
Project Initializer
↓
正しいProduct Remote
↓
クリーンなTask Runtime
↓
安全なProduct SSOT
↓
<PREFIX>-TASK-0001
```

が、文書上だけでなく**実動作として再現されること**を保証してください。

DEV-TASK-0011がPlanner ReviewでACCEPTEDになれば、
Planner / Builder AI Development Standardの初期構築フェーズを完了とします。
