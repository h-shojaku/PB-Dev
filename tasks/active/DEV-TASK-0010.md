# DEV-TASK-0010 — Project Initializer実動作修正・Template最終受入

## 0. Role

あなたはこのRepositoryの **Builder** です。

本Taskは、DEV-TASK-0009のPlanner Review結果 `CHANGES_REQUIRED` を受けた最終修正Taskです。

DEV-TASK-0009でDevelopment Standard、Definition of Done、Project Profile、
NEW_PRODUCT / EXISTING_PRODUCT初期化ルール等の文書設計は概ね完成しました。

しかしPlannerがHandoff ZIP内の初期化スクリプトを別環境で実際に実行したところ、
**SSOTに定義した初期化動作と実装が一致していない**ことを確認しました。

本TaskではProject Initializerを実際にTemplateとして安全に使える状態へ修正し、
自動テストでその動作を証明してください。

本Task完了後にPB-Devの最終完成判定を行います。

---

# 1. Previous Task

Previous Task:

```text
DEV-TASK-0009
```

Planner Review:

```text
CHANGES_REQUIRED
```

DEV-TASK-0009のCompleted Instruction Recordを改変しないこと。

修正はDEV-TASK-0010として追跡する。

---

# 2. Planner Independent Verification Findings

Planner側で `DEV-TASK-0009_PLANNER_HANDOFF.zip` をLinux環境へ展開し、
同梱スクリプトを実行して確認しました。

## 2.1 Handoff ZIP

以下はPASSしています。

```text
ZIP展開: PASS
Backslash entry: 0
Absolute entry: 0
Parent traversal: 0
create_handoff.py --test: PASS
```

Handoff Generatorは今回の修正対象ではありません。

---

## 2.2 initialize_project.py 実行結果

Plannerは展開したRepository copyに対し概ね以下を実行しました。

```text
python scripts/initialize_project.py \
  --mode NEW_PRODUCT \
  --name TestApp \
  --prefix TST \
  --remote https://github.com/example/TestApp.git
```

Scriptは、

```text
Project initialization completed successfully.
```

と終了しました。

しかし実際の状態は以下でした。

### Problem A — completed Task history is not reset

実行前：

```text
tasks/completed/DEV-TASK-0009.md
```

実行後も：

```text
tasks/completed/DEV-TASK-0009.md
```

が残りました。

これは `PROJECT_INITIALIZATION_RULES.md` の、

```text
派生ProductではPB-DevのDEV Task履歴をProduct Task Register / runtime stateへ持ち込まない
tasks/completed/ をresetする
```

という規則と不一致です。

---

### Problem B — Product SSOT is not initialized

NEW_PRODUCT実行後も、

```text
docs/product/
```

へ以下が配置されませんでした。

```text
00_PRODUCT_OVERVIEW.md
01_PRODUCT_PLAN.md
02_REQUIREMENTS.md
03_UI_STRUCTURE.md
04_IMPLEMENTATION_SPEC.md
05_OPERATION_RULES.md
```

これはNEW_PRODUCT Initialization Flowと不一致です。

---

### Problem C — Remote Safety is warning-only

Python版はRemoteがPB-Devを向いている可能性があっても
警告を表示するだけで処理を成功扱いにできます。

PowerShell版についても、
Canonical Remoteとの一致を強制する十分なRemote Safety処理がありません。

派生Projectで、

```text
origin -> PB-Dev
```

のまま通常開発へ進める可能性を残してはいけません。

---

### Problem D — Placeholder Remote can become successful state

`--remote` 未指定時に、

```text
https://github.com/example/<name>.git
```

のようなplaceholderをCanonical Remoteとして書き込み、
Initialization成功扱いにする実装があります。

架空Remoteを正式なProject Profileへ保存してはいけません。

---

### Problem E — Runtime reset is incomplete

現在Scriptは主に、

```text
tasks/active/
TASK_REGISTER.md
CURRENT_STATE.md
```

を更新しますが、

```text
tasks/completed/
受け渡し/
Product SSOT initialization
```

など、SSOT上のRuntime Reset / Initialization要件を完全には実行していません。

---

### Problem F — Initialization test is too weak

DEV-TASK-0009ではDry RunがPASSと報告されていますが、

```text
Script process exited successfully
```

だけでは、

```text
Runtime state actually reset
Product SSOT actually created
Remote actually safe
Existing source actually preserved
```

ことを証明できません。

今後は**結果のファイルシステム状態までassertするテスト**が必要です。

---

# 3. Objective

以下を完了してください。

1. Project Initializer実装を `PROJECT_INITIALIZATION_RULES.md` と一致させる
2. NEW_PRODUCT初期化を実際に完遂できるようにする
3. EXISTING_PRODUCT初期化を安全に実行できるようにする
4. PB-Dev DEV Task runtime historyを派生Productから確実に除去する
5. `受け渡し/` の旧配送物を初期化する
6. NEW_PRODUCTではProduct SSOT 00〜05を実際に配置する
7. Canonical Remoteをplaceholderで確定しない
8. Remote Safety違反時は成功扱いにしない
9. Python / PowerShellの動作差をなくす
10. 実際の結果をassertするcross-platform self-testを追加する
11. NEW_PRODUCT / EXISTING_PRODUCT双方のIntegration TestをPASSさせる
12. DEV-TASK-0010自身を通常Lifecycleで完了
13. GitHub commit / push
14. Planner Handoff ZIP生成
15. PB-Dev Templateの最終受入に必要なEvidenceをREPORTへ含める

---

# 4. Source of Truth

作業前に最低限以下を読むこと。

```text
PROJECT_PROFILE.md
CURRENT_STATE.md

docs/development/
├── DEVELOPMENT_SYSTEM.md
├── PROJECT_INITIALIZATION_RULES.md
├── DEFINITION_OF_DONE.md
├── BUILDER_RULES.md
├── TASK_RULES.md
├── GIT_RULES.md
├── HANDOFF_RULES.md
└── SESSION_RULES.md

scripts/
├── initialize_project.py
├── initialize_project.ps1
├── create_handoff.py
└── create_handoff.ps1

templates/
├── PROJECT_PROFILE_TEMPLATE.md
└── product/
    ├── 00_PRODUCT_OVERVIEW.md
    ├── 01_PRODUCT_PLAN.md
    ├── 02_REQUIREMENTS.md
    ├── 03_UI_STRUCTURE.md
    ├── 04_IMPLEMENTATION_SPEC.md
    ├── 05_OPERATION_RULES.md
    └── EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md
```

---

# 5. Project Initializer Architecture

Python版をCanonical implementationとすることを推奨します。

```text
scripts/initialize_project.py
```

PowerShell版：

```text
scripts/initialize_project.ps1
```

は可能ならPython版を呼び出す薄いwrapperにし、
Python / PowerShellでInitialization logicを二重実装しないでください。

目的：

- Windows / macOS / Linuxで同じ動作
- 修正漏れ防止
- SSOTとの不整合防止

別設計を採用する場合は、
両実装の同等性を自動テストで証明してください。

---

# 6. Required Inputs

派生Productを正式初期化する場合、
最低限以下を必要入力とする。

```text
Mode
Project Name
Task Prefix
Canonical Remote
```

Mode:

```text
NEW_PRODUCT
EXISTING_PRODUCT
```

PB-Dev自身を再初期化する通常用途として
`TEMPLATE` を安易に使用しない。

---

## 6.1 Remote Is Required

`NEW_PRODUCT` / `EXISTING_PRODUCT` の実初期化では、

```text
Canonical Remote
```

を必須とする。

未指定の場合：

```text
Initialization FAILED
```

とする。

以下のplaceholderを自動生成して成功扱いにしない。

```text
https://github.com/example/...
example.com
TODO
TBD
```

Dry Runであっても、
Remote Validationを行える設計にする。

---

# 7. Remote Safety

派生Productでは、
実Git `origin` と指定Canonical Remoteの安全性を検証する。

---

## 7.1 PB-Dev Remote Guard

Modeが、

```text
NEW_PRODUCT
EXISTING_PRODUCT
```

の場合、

```text
origin = https://github.com/h-shojaku/PB-Dev.git
```

のまま成功終了してはいけない。

---

## 7.2 Expected Behavior

状況に応じて安全に以下のどちらかとする。

### Option A — Explicitly update origin

指定されたCanonical Remoteへ、

```text
git remote set-url origin <Canonical Remote>
```

を安全に実施し、
実際に一致したことを検証する。

### Option B — Fail closed

Remote変更をScript責務外とするなら、

```text
Remote mismatch
```

でInitializationを失敗させ、

```text
originをCanonical Remoteへ修正後に再実行してください
```

とする。

どちらでもよいが、

**警告だけ出してsuccessは禁止。**

---

## 7.3 No Git Repository

Template内容のDry RunやUnit Test用Temporary Directoryなど、
`.git` が存在しないケースは明確に区別する。

実Initialization：

```text
Git Repositoryでない
```

なら原則FAILED。

Self-test fixtureではGit Repositoryをtemporaryに作成して検証する。

---

# 8. Runtime State Reset

派生Product初期化時に、
PB-Dev runtime stateを確実にresetする。

対象：

```text
tasks/active/
tasks/completed/
tasks/TASK_REGISTER.md
CURRENT_STATE.md
受け渡し/
```

---

## 8.1 tasks/active/

空にする。

---

## 8.2 tasks/completed/

PB-Dev由来のCompleted Task filesを
派生Product runtimeから除去する。

Template clone側で削除するだけであり、
PB-Dev元RepositoryやGit historyを破壊する操作ではありません。

Git history自体は保持する。

---

## 8.3 TASK_REGISTER

以下のProduct初期状態へreset。

```text
Current Active Task:
none

Task History:
none
```

DEV-TASK-0001〜0010等をProduct runtime historyへ残さない。

---

## 8.4 CURRENT_STATE

最低限：

```text
Project Name: <new project>
Project Mode: NEW_PRODUCT / EXISTING_PRODUCT
Task Prefix: <prefix>
Canonical Remote: <remote>
Workflow Phase: IDLE
Current Task: None
Latest Completed Task: None
Human Decision: None
```

NEW_PRODUCT / EXISTING_PRODUCTで
Next Expected Actionを適切に変える。

---

## 8.5 受け渡し/

存在する古い配送物を削除する。

初期化後は空またはdirectory自体なしでよい。

Git追跡対象外という既存原則を維持する。

---

# 9. NEW_PRODUCT Initialization

NEW_PRODUCTではRuntime Resetに加えて、

```text
templates/product/
```

からProduct SSOTを、

```text
docs/product/
```

へ実際に配置する。

最終構造：

```text
docs/product/
├── 00_PRODUCT_OVERVIEW.md
├── 01_PRODUCT_PLAN.md
├── 02_REQUIREMENTS.md
├── 03_UI_STRUCTURE.md
├── 04_IMPLEMENTATION_SPEC.md
└── 05_OPERATION_RULES.md
```

---

## 9.1 Existing docs/product content

初期化対象に既存Product SSOTが存在する場合、
無条件overwriteしない。

NEW_PRODUCTとして本当に空のTemplate cloneかを確認する。

既存内容がある場合は、

```text
安全に一意判断できる
```

場合のみ処理し、
そうでなければFAILED / Human Decisionとする。

---

# 10. EXISTING_PRODUCT Initialization

EXISTING_PRODUCTでは、
既存source codeを削除・移動・上書きしない。

Runtime stateだけをresetし、
Product SSOTについては既存内容を保全する。

---

## 10.1 Baseline Analysis

`EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md` を利用可能な状態にする。

Initialization Scriptが分析そのものを実行する必要はない。

CURRENT_STATEのNext Expected Actionを、

```text
Planner issues <PREFIX>-TASK-0001 Baseline Analysis Task
```

等にする。

---

## 10.2 Existing source preservation

Integration Test fixtureにdummy sourceを作り、

```text
src/app.txt
```

等がInitialization後もbyte-for-byte残ることをassertする。

---

# 11. Initialization Timestamp

以下のような固定日時をScriptへハードコードしない。

```text
2026-08-08T00:00:00+09:00
```

実行時刻から生成する。

タイムゾーン付きISO 8601形式を推奨。

Testでは日時そのものを固定比較せず、
形式・存在を検証する。

---

# 12. Prefix Validation

Task Prefixを最低限Validationする。

推奨：

```text
A-Z
0-9
hyphen
```

等の安全な短い識別子。

空文字やPath separator、
Markdownを壊す文字列を受け入れない。

過剰に狭いルールへ固定しない。

---

# 13. Project Name Validation

Project Nameが、

- 空
- Path traversal
- 制御文字

等を含む危険な入力でないことを確認する。

Display Nameとして合理的な範囲を許可する。

---

# 14. Dry Run Semantics

`--dry-run` / `-DryRun` は、

```text
何も変更しない
```

だけでは不十分。

最低限以下を表示する。

```text
Mode
Project Name
Prefix
Canonical Remote
Current origin
Remote action / validation result
Files that would be reset
Product SSOT action
Final expected state
```

Dry RunでValidation failureがある場合は
成功コードでごまかさない。

---

# 15. Initialization Result Verification

実Initialization終了前に、
Script自身で最終状態を検証する。

最低限：

```text
PROJECT_PROFILE matches inputs
TASK_REGISTER reset
tasks/active empty
tasks/completed empty
CURRENT_STATE matches profile and IDLE
old Handoff removed
origin == Canonical Remote
```

NEW_PRODUCT：

```text
Product SSOT 00〜05 exists
```

EXISTING_PRODUCT：

```text
existing source preserved
```

Verificationに失敗した場合は、
successを表示しない。

---

# 16. Add Automated Integration Tests

標準ライブラリのみで、
結果状態まで検証する自動テストを追加してください。

推奨：

```text
scripts/test_initialize_project.py
```

または `initialize_project.py --test`。

Temporary Directory / Temporary Git Repositoryを使い、
PB-Dev本体を破壊しない。

---

# 17. Required Test — NEW_PRODUCT

Temporary fixtureを作成。

初期状態例：

```text
PROJECT_PROFILE = PB-Dev
tasks/completed/DEV-TASK-0009.md
tasks/active/OLD.md
tasks/TASK_REGISTER.md = DEV historyあり
CURRENT_STATE = PB-Dev
受け渡し/OLD_HANDOFF.zip
templates/product/00〜05
.git/
origin = PB-Dev
```

実行：

```text
NEW_PRODUCT
Name = TestApp
Prefix = TST
Canonical Remote = test product remote
```

期待値をassert：

```text
PASS: PROJECT_PROFILE = TestApp
PASS: Mode = NEW_PRODUCT
PASS: Prefix = TST
PASS: Canonical Remote = test remote
PASS: origin = test remote
PASS: tasks/active empty
PASS: tasks/completed empty
PASS: TASK_REGISTER history empty
PASS: CURRENT_STATE = IDLE
PASS: Latest Completed = None
PASS: old Handoff absent
PASS: docs/product/00〜05 exist
PASS: no PB-Dev runtime task remains
```

---

# 18. Required Test — EXISTING_PRODUCT

Temporary fixtureにdummy sourceを追加。

例：

```text
src/app.txt
config/example.json
```

実行前hashを取得。

Initialization後：

```text
PASS: source files exist
PASS: hashes unchanged
PASS: Runtime state reset
PASS: Profile updated
PASS: origin safe
PASS: CURRENT_STATE next action = Baseline Analysis
```

---

# 19. Required Negative Tests

最低限：

### Remote omitted

```text
Expected: FAIL
```

### origin still PB-Dev and cannot / should not be changed

```text
Expected: FAIL
```

または安全に指定Remoteへ変更して一致確認。

### invalid Prefix

```text
Expected: FAIL
```

### unsafe Project Name

```text
Expected: FAIL
```

### NEW_PRODUCT with non-empty Product SSOT that would be overwritten

```text
Expected: FAIL / explicit safe handling
```

---

# 20. PowerShell Wrapper Test

Windows Builder環境では、

```text
scripts/initialize_project.ps1
```

経由でもCanonical Python implementationと
同じ結果になることを確認する。

PowerShell wrapperは、
argumentをPython版へ安全に渡す薄い入口とすることを推奨。

Pythonが使用不能なら、
成功を装わず明確に失敗する。

---

# 21. Documentation Alignment

修正後の実装に合わせて、
必要な場合のみ以下を更新する。

```text
docs/development/PROJECT_INITIALIZATION_RULES.md
docs/development/DEFINITION_OF_DONE.md
docs/development/GIT_RULES.md
scripts/README.md
README.md
```

重要：

**DocumentationをScriptの不具合へ合わせて要件弱体化してはいけません。**

DEV-TASK-0009で意図した安全なInitializationを
Script側が満たすことを基本とする。

---

# 22. No Scope Expansion

本Taskでは以下を行わない。

- 新しいDevelopment役割追加
- Task Lifecycle再設計
- Handoff Generator再設計
- Product SSOT内容の詳細設計
- Git Branch戦略追加
- CI/CD追加
- Application code開発

Project Initializerの実動作整合と最終受入に集中する。

---

# 23. Task Lifecycle

本Taskも正式Lifecycleを適用。

```text
DEV-TASK-0010 Intake
↓
tasks/active/DEV-TASK-0010.md
↓
TASK_REGISTER = ACTIVE
↓
CURRENT_STATE = ACTIVE
↓
Intake commit / push
↓
修正
↓
Integration Test
↓
tasks/completed/DEV-TASK-0010.md
↓
TASK_REGISTER = COMPLETED
↓
CURRENT_STATE = AWAITING_PLANNER_REVIEW
↓
Final commit / push
↓
Handoff ZIP
```

---

# 24. Git / GitHub

PB-Dev：

```text
Canonical Remote:
https://github.com/h-shojaku/PB-Dev.git

Branch:
main
```

最低限Task IDを含むcommitを作成。

例：

```text
DEV-TASK-0010: register task
DEV-TASK-0010: make project initializer production-ready
```

origin/mainへpush。

---

# 25. Verification

最低限以下をすべて実施。

## Existing Standard

```text
git diff --check
create_handoff self-test
Handoff archive verification
```

## Initializer

```text
Python syntax check
Python integration tests
NEW_PRODUCT integration test
EXISTING_PRODUCT integration test
Negative tests
PowerShell wrapper test（Windows環境）
```

---

# 26. REPORT.md Required Sections

通常項目に加えて以下を含める。

```text
## DEV-TASK-0009 Review Correction

## Project Initializer Architecture

## NEW_PRODUCT Integration Test

## EXISTING_PRODUCT Integration Test

## Negative Tests

## Remote Safety Verification

## Runtime Reset Verification

## Product SSOT Initialization Verification

## PowerShell Wrapper Verification

## Final Template Acceptance Evidence
```

---

# 27. REPORT — Required Evidence

NEW_PRODUCTについて最低限数値・結果を記録。

例：

```text
Active Task files after init: 0
Completed Task files after init: 0
Task Register history rows after init: 0
Old Handoff files after init: 0
Product SSOT files created: 6
origin matches Canonical Remote: PASS
```

EXISTING_PRODUCT：

```text
Existing source files before:
Existing source files after:
Hash comparison:
Runtime reset:
origin:
Baseline Analysis next action:
```

---

# 28. Final Template Acceptance Test

本Taskの修正後、
Temporary Repositoryを使って最終的に次を証明する。

## NEW_PRODUCT

```text
PB-Dev Template
↓
initialize
↓
Product-specific clean runtime
↓
Product SSOT ready
↓
correct origin
↓
<PREFIX>-TASK-0001を受けられる
```

PASS。

## EXISTING_PRODUCT

```text
Existing source
+
PB-Dev Development Standard
↓
initialize
↓
source preserved
↓
clean task runtime
↓
correct origin
↓
Baseline Analysis Taskを受けられる
```

PASS。

---

# 29. Final Cold Start Verification

DEV-TASK-0010完了後のPB-Dev本体では、

```text
Project Mode = TEMPLATE
Workflow Phase = AWAITING_PLANNER_REVIEW
Current Task = None
Latest Completed Task = DEV-TASK-0010
Human Decision = None
Next Action = Planner Review
```

をRepositoryから一意に判断可能であること。

---

# 30. Handoff

Planner提出物は、

```text
受け渡し/DEV-TASK-0010_PLANNER_HANDOFF.zip
```

**1個のみ**。

500MB以内。

標準Generator使用。

ZIP Verification PASS。

最低限含める。

```text
DEV-TASK-0010_PLANNER_HANDOFF.zip
├── REPORT.md
├── MANIFEST.md
└── files/
    ├── CURRENT_STATE.md
    ├── PROJECT_PROFILE.md
    ├── tasks/
    │   ├── TASK_REGISTER.md
    │   └── completed/
    │       └── DEV-TASK-0010.md
    ├── scripts/
    │   ├── initialize_project.py
    │   ├── initialize_project.ps1
    │   ├── test_initialize_project.py
    │   └── README.md
    └── docs/
        └── development/
            ├── PROJECT_INITIALIZATION_RULES.md
            ├── DEFINITION_OF_DONE.md
            └── GIT_RULES.md
```

Test file名は実装に応じて変更可。

実際に変更した関連ファイルも含める。

---

# 31. Acceptance Criteria

以下をすべて満たせばCOMPLETE。

- [ ] DEV-TASK-0009のPlanner Review指摘を新Taskで追跡
- [ ] initialize_project.pyとSSOTの動作が一致
- [ ] PowerShell入口とPython Canonical implementationの動作が一致
- [ ] NEW_PRODUCTでtasks/activeが空になる
- [ ] NEW_PRODUCTでtasks/completedが空になる
- [ ] Product Task Registerが空へresetされる
- [ ] CURRENT_STATEが新Project Profileと一致
- [ ] 古い受け渡し成果物が除去される
- [ ] NEW_PRODUCTでProduct SSOT 00〜05が実際に配置される
- [ ] EXISTING_PRODUCTで既存sourceが変更されない
- [ ] EXISTING_PRODUCTでBaseline Analysis開始状態になる
- [ ] Canonical Remote未指定をsuccessにしない
- [ ] placeholder Remoteを生成してsuccessにしない
- [ ] PB-Dev originのまま派生Project初期化successにしない
- [ ] 実originとProject Profile Canonical Remoteが一致
- [ ] 固定Initialization timestampを使用しない
- [ ] unsafe Prefixを拒否
- [ ] unsafe Project Nameを拒否
- [ ] Dry RunがValidationを実施
- [ ] NEW_PRODUCT Integration Test PASS
- [ ] EXISTING_PRODUCT Integration Test PASS
- [ ] Negative Tests PASS
- [ ] Testがprocess exitだけでなくfilesystem結果をassert
- [ ] Handoff Generator self-test PASS
- [ ] `git diff --check` PASS
- [ ] GitHub commit / push完了
- [ ] tracked working tree clean
- [ ] `受け渡し/` にDEV-TASK-0010 ZIP 1個のみ
- [ ] Handoff portable verification PASS
- [ ] Builder最終回答がZIP絶対パス案内で終了

---

# 32. Builder Final Response

最低限：

```text
Task: DEV-TASK-0010
Status: COMPLETE / BLOCKED

実施内容:
- ...

Initializer Verification:
- NEW_PRODUCT: PASS / FAIL
- EXISTING_PRODUCT: PASS / FAIL
- Remote Safety: PASS / FAIL
- Runtime Reset: PASS / FAIL
- Product SSOT Initialization: PASS / FAIL
- Existing Source Preservation: PASS / FAIL
- Negative Tests: PASS / FAIL
- PowerShell Wrapper: PASS / FAIL

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

これをPlannerに渡してください: <実際の絶対パス>\受け渡し\DEV-TASK-0010_PLANNER_HANDOFF.zip
```

**最後の1文より後には何も記載しないこと。**

---

# 33. Final Goal

今回の目的は単にTestを通すことではありません。

**PB-DevをTemplateとして複製しProject Initializerを実行したとき、
文書に書かれた標準どおりの状態が実際に作られること**を保証してください。

DEV-TASK-0010がACCEPTEDになれば、
Planner / Builder AI Development Standardの初期構築フェーズは完了です。
