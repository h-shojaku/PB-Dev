# DEV-TASK-0014 — Handoff完全性保証・Manifest整合・DEV-TASK-0013最終再提出

## 0. Role

あなたはこのRepositoryの **Builder** です。

本TaskはDEV-TASK-0013のPlanner Reviewで発見された、
**Planner Handoff ZIPそのものの重大な完全性不具合**を修正するTaskです。

DEV-TASK-0013のREPORTではInitializer改善・19 Test PASS等が報告されていますが、
Plannerが実際の提出ZIPを展開したところ、ZIP内部には次の2ファイルしか存在しませんでした。

```text
REPORT.md
MANIFEST.md
```

一方、MANIFEST.mdには多数の`files/...`が含まれると記載されています。

つまり、

```text
MANIFESTが示す内容
!=
実際のZIP内容
```

です。

PlannerはRepositoryへ直接アクセスできない場合でもHandoff ZIPだけでレビュー可能であることが
既存Development Standardの必須要件です。

この状態ではDEV-TASK-0013の実装内容を正式レビューできないため、
DEV-TASK-0013は `CHANGES_REQUIRED` とします。

本Taskでは、

1. Handoff Generator / staging運用を修正
2. MANIFESTと実ZIPの内容一致を自動検証
3. 必須Review Files欠落時はFail-Closed
4. DEV-TASK-0013で実装したInitializer成果物を含む完全Handoffを再提出
5. PlannerがHandoff ZIPだけで最終受入検証できる状態にする

ことへ集中してください。

---

# 1. Previous Task

Previous Task:

```text
DEV-TASK-0013
```

Planner Review:

```text
CHANGES_REQUIRED
```

過去Task Instruction Recordはimmutableです。

DEV-TASK-0013本文を修正せず、
本修正はDEV-TASK-0014として追跡してください。

---

# 2. Planner Independent Finding

Plannerが提出された、

```text
DEV-TASK-0013_PLANNER_HANDOFF.zip
```

を直接検査した実結果：

```text
Actual ZIP entry count: 2

Entries:
- MANIFEST.md
- REPORT.md

Archive integrity: PASS
Backslash entries: 0
Absolute entries: 0
Parent traversal entries: 0
```

しかしMANIFEST.mdでは少なくとも以下を含むと記載されています。

```text
files/CURRENT_STATE.md
files/PROJECT_PROFILE.md
files/README.md
files/AGENTS.md
files/CLAUDE.md
files/GEMINI.md
files/docs/development/...
files/scripts/initialize_project.py
files/scripts/initialize_project.ps1
files/scripts/test_initialize_project.py
files/tasks/TASK_REGISTER.md
files/tasks/completed/DEV-TASK-0013.md
files/templates/product/...
```

これは重大なHandoff Completeness Failureです。

---

# 3. Important Review Principle

今回の問題について、

```text
GitHubにファイルがあるからPlannerが直接見ればよい
```

とは扱いません。

既存標準では、

```text
Handoff ZIP
= PlannerがRepositoryへ直接アクセスできない場合でも
  Taskの主要成果物をレビューできるDelivery / Continuity Package
```

です。

したがってHandoff ZIPの欠落は、
Task Completionを妨げる正式な不具合です。

---

# 4. Objective

以下を完了してください。

1. なぜDEV-TASK-0013 Handoffが2 entriesだけになったかRoot Causeを特定
2. Handoff Generatorまたはstaging手順を修正
3. Manifest-listed filesが実ZIPに存在することを自動検証
4. Required Review Files欠落時はHandoff生成をFAIL
5. REPORT / MANIFESTと実ZIPのentry数を一致させる
6. DEV-TASK-0013の主要実装成果物を本Task Handoffへ含める
7. PlannerがInitializerをHandoff内だけで再テスト可能にする
8. Handoff completeness regression testを追加
9. DEV-TASK-0014を正式Lifecycleで完了
10. GitHub commit / push
11. `受け渡し/` にDEV-TASK-0014 ZIP 1個だけを残す

---

# 5. Root Cause Analysis

REPORTへ、

```text
## DEV-TASK-0013 Handoff Completeness Root Cause
```

を追加してください。

最低限：

```text
Expected staging contents:
Actual staging contents:
Generator behavior:
Why only REPORT.md / MANIFEST.md entered ZIP:
Why existing self-test did not catch it:
Corrective action:
```

を記録する。

単に「再生成しました」で終わらせず、
再発防止まで行う。

---

# 6. Handoff Generator Completeness Model

現在のportable path / security validationは維持する。

追加で、

```text
Archive Safety
+
Archive Completeness
```

の両方を検証する。

---

# 7. Required Review Files

Handoff生成時には、
TaskごとにPlanner Reviewに必要なファイルを明示する。

実装方法は以下のどちらでもよい。

## Option A — Required file list argument

例：

```text
--require files/scripts/initialize_project.py
--require files/CURRENT_STATE.md
```

## Option B — Required manifest file

例：

```text
handoff_required_files.txt
```

BuilderがTask用staging作成時にrequired listを生成し、
Generatorが確認する。

---

## 7.1 Requirement

どの設計でも、

```text
required path
not in final ZIP
```

なら、

```text
FAIL
```

とする。

ZIP生成成功を表示しない。

---

# 8. MANIFEST Integrity Rule

今後MANIFEST.mdのIncluded Filesと
最終ZIP entryを機械比較する。

最低限：

```text
Manifest-declared file
→ actual ZIPに存在
```

を全件確認。

---

## 8.1 No Phantom Entries

MANIFESTに、

```text
files/scripts/initialize_project.py
```

と書かれているのに、
ZIPに存在しない状態は禁止。

---

## 8.2 Actual Undeclared Files

REPORT / MANIFEST以外のReview fileが
ZIPへ含まれている場合も、
可能な範囲でMANIFESTへ記録する。

少なくとも、

```text
MANIFEST declared count
Actual relevant file count
Missing declared entries
```

を検証する。

---

# 9. Entry Count Accuracy

Handoff Generatorが最終ZIPを閉じた後に、

```text
actual ZIP entry count
```

を実測する。

REPORT / MANIFESTのentry countは
その実値を利用する。

ZIP生成前のstaging file数を、
最終ZIP entry countとして報告しない。

---

# 10. Required Structural Validation

最終ZIPに最低限以下が存在すること。

```text
REPORT.md
MANIFEST.md
files/
```

`files/`配下にReview Fileが1件以上存在することを標準とする。

通常のCompleted Taskで、

```text
REPORT.md
MANIFEST.md
```

だけのZIPはFAIL。

---

# 11. Task-specific Required Content — DEV-TASK-0014

本TaskのHandoffには、
DEV-TASK-0013でPlannerがレビューできなかった成果物も含めてください。

最低限：

```text
DEV-TASK-0014_PLANNER_HANDOFF.zip
├── REPORT.md
├── MANIFEST.md
└── files/
    ├── README.md
    ├── PROJECT_PROFILE.md
    ├── CURRENT_STATE.md
    ├── AGENTS.md
    ├── CLAUDE.md
    ├── GEMINI.md
    │
    ├── tasks/
    │   ├── TASK_REGISTER.md
    │   └── completed/
    │       ├── DEV-TASK-0013.md
    │       └── DEV-TASK-0014.md
    │
    ├── scripts/
    │   ├── initialize_project.py
    │   ├── initialize_project.ps1
    │   ├── test_initialize_project.py
    │   ├── test_initialize_project.ps1
    │   ├── create_handoff.py
    │   ├── create_handoff.ps1
    │   └── README.md
    │
    ├── docs/
    │   └── development/
    │       ├── DEVELOPMENT_SYSTEM.md
    │       ├── PROJECT_INITIALIZATION_RULES.md
    │       ├── DEFINITION_OF_DONE.md
    │       ├── HANDOFF_RULES.md
    │       ├── BUILDER_RULES.md
    │       ├── GIT_RULES.md
    │       └── REVIEW_RULES.md
    │
    └── templates/
        └── product/
            ├── 00_PRODUCT_OVERVIEW.md
            ├── 01_PRODUCT_PLAN.md
            ├── 02_REQUIREMENTS.md
            ├── 03_UI_STRUCTURE.md
            ├── 04_IMPLEMENTATION_SPEC.md
            ├── 05_OPERATION_RULES.md
            └── EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md
```

DEV-TASK-0013で実際に変更した追加ファイルも
Reviewに必要なら含める。

---

# 12. Initializer Re-verification

本TaskはInitializerの新機能追加Taskではありません。

ただしPlannerが0013を正式レビューできなかったため、
本Task Handoff生成前に0013のAcceptance Testを再実行する。

最低限：

```text
python scripts/test_initialize_project.py
```

および、

```text
actual template NEW_PRODUCT
actual template EXISTING_PRODUCT
```

のTestがTest Suite内でPASSすること。

---

# 13. PowerShell Thin Wrapper Verification

Handoffへ実ファイルを含め、
Plannerが直接確認できるようにする。

最低限Builder側でも、

```text
initialize_project.ps1
```

にNative Initialization business logicが再導入されていないことをTestする。

---

# 14. Handoff Regression Tests

`scripts/create_handoff.py` のself-testまたは
別Testへ以下を追加する。

---

## 14.1 Complete Package Success

Staging：

```text
REPORT.md
MANIFEST.md
files/a.txt
files/docs/b.md
```

MANIFEST：

```text
files/a.txt
files/docs/b.md
```

Expected：

```text
PASS
```

---

## 14.2 Manifest Phantom Entry Failure

MANIFEST：

```text
files/a.txt
files/missing.txt
```

Actual：

```text
files/a.txt
```

Expected：

```text
FAIL
```

---

## 14.3 Required Review File Missing

Required：

```text
files/scripts/initialize_project.py
```

Actual absent。

Expected：

```text
FAIL
```

---

## 14.4 Empty Review Package Failure

Actual：

```text
REPORT.md
MANIFEST.md
```

only.

Expected：

```text
FAIL
```

---

## 14.5 Entry Count Match

Expected：

```text
reported entry count == zipfile.namelist() actual count
```

---

# 15. Update HANDOFF_RULES.md

以下を正式SSOTへ追加する。

```text
Handoff Completeness
Manifest Integrity
Required Review Files
Empty Review Package Rejection
Evidence Accuracy
```

最低限：

- REPORT + MANIFESTだけではCompleted Task Handoffとして不十分
- Planner review filesを必ず含める
- MANIFESTに記載したfileは実ZIPに存在
- required file欠落時はFAIL
- actual ZIPを閉じた後に実測してEvidence化
- HandoffはPlannerがRepositoryなしでレビュー可能

---

# 16. Update DEFINITION_OF_DONE.md

Handoff DoDに最低限追加：

```text
- Manifest-listed review files actually exist in ZIP
- Required review files present
- Handoff completeness verification PASS
- REPORT / MANIFEST evidence matches actual archive
```

---

# 17. Builder Rules

Builderは、

```text
Handoff ZIP生成
```

だけでは完了扱いにしない。

標準：

```text
staging作成
↓
required review files確認
↓
ZIP生成
↓
archive safety verification
↓
manifest integrity verification
↓
completeness verification
↓
REPORT evidence verification
↓
Final response
```

---

# 18. No Manual ZIP Repair

BuilderがGenerator失敗時に、

```text
Explorer等で手動ZIPを作って提出
```

してCompleteness Verificationを迂回しない。

標準Generatorで同一検証を通すこと。

---

# 19. Task Lifecycle

DEV-TASK-0014を通常Lifecycleで処理する。

```text
Task Intake
↓
ACTIVE
↓
Intake commit / push
↓
Handoff completeness修正
↓
Regression Test
↓
0013 Initializer Acceptance Test再実行
↓
COMPLETED
↓
Final commit / push
↓
Complete Handoff ZIP生成
```

---

# 20. Git / GitHub

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
DEV-TASK-0014: register task
DEV-TASK-0014: enforce handoff package completeness
```

origin/mainへpush。

---

# 21. Required Verification

最低限：

```text
python scripts/test_initialize_project.py
python scripts/create_handoff.py --test
git diff --check
git status
git remote -v
git log -1
```

加えて最終HandoffについてPython等で直接、

```text
zipfile.namelist()
```

を取得し、

```text
actual entry count
manifest missing count
required missing count
```

を確認する。

---

# 22. REPORT Required Sections

最低限：

```text
## DEV-TASK-0013 Planner Finding
## Root Cause
## Handoff Generator Correction
## Manifest Integrity Verification
## Required Review Files Verification
## Handoff Regression Tests
## DEV-TASK-0013 Initializer Re-verification
## Final Archive Evidence
```

---

# 23. REPORT Concrete Evidence

推測値ではなく実値。

```text
Initializer tests:
- total:
- passed:
- failed:

Handoff generator tests:
- total:
- passed:
- failed:

Final ZIP:
- actual entry count:
- manifest declared review files:
- manifest missing files:
- required review files:
- required missing files:
- backslash entries:
- absolute entries:
- parent traversal entries:
- archive integrity:
- delivery directory files:
```

期待：

```text
manifest missing files: 0
required missing files: 0
archive integrity: PASS
delivery directory files: 1
```

---

# 24. MANIFEST Required Data

MANIFESTには最低限：

```text
Task ID
ZIP filename
Created At
Repository Root
Handoff ZIP Absolute Path
Branch
Commit
ZIP Size
Actual ZIP Entry Count
Included Files
```

を記録する。

Included Filesは実ZIP内容から生成することを推奨。

---

# 25. Final Self-check

Builder最終回答前に、
**生成された最終ZIPファイルそのものを再オープンして**検証する。

Staging directoryを確認しただけで完了しない。

---

# 26. Acceptance Criteria

以下をすべて満たせばCOMPLETE。

- [ ] DEV-TASK-0013 Handoff欠落問題を新Taskで追跡
- [ ] Handoff欠落のRoot Causeが特定されている
- [ ] Complete Review Packageを生成できる
- [ ] REPORT + MANIFESTのみのCompleted HandoffをReject
- [ ] MANIFEST記載fileと実ZIPを照合
- [ ] Phantom Manifest EntryをReject
- [ ] Required Review File欠落をReject
- [ ] Final ZIPを再オープンして検証
- [ ] Actual entry countを最終ZIPから取得
- [ ] REPORT entry countとActual entry count一致
- [ ] MANIFEST missing files = 0
- [ ] Required missing files = 0
- [ ] Handoff ZIPだけでInitializer成果物をレビュー可能
- [ ] initialize_project.pyをHandoffに含む
- [ ] initialize_project.ps1をHandoffに含む
- [ ] test_initialize_project.pyをHandoffに含む
- [ ] create_handoff.pyをHandoffに含む
- [ ] DEV-TASK-0013.mdをHandoffに含む
- [ ] DEV-TASK-0014.mdをHandoffに含む
- [ ] PROJECT_INITIALIZATION_RULES.mdをHandoffに含む
- [ ] DEFINITION_OF_DONE.mdをHandoffに含む
- [ ] Product template 00〜05をHandoffに含む
- [ ] Existing Product Analysis TemplateをHandoffに含む
- [ ] Initializer Test Suite PASS
- [ ] Actual Template NEW_PRODUCT Test PASS
- [ ] Actual Template EXISTING_PRODUCT Test PASS
- [ ] Handoff regression tests PASS
- [ ] ZIP portable verification PASS
- [ ] `git diff --check` PASS
- [ ] GitHub commit / push完了
- [ ] tracked working tree clean
- [ ] `受け渡し/` にDEV-TASK-0014 ZIP 1個のみ
- [ ] Builder最終回答がZIP絶対パス案内で終了

---

# 27. Builder Final Response

最低限：

```text
Task: DEV-TASK-0014
Status: COMPLETE / BLOCKED

Handoff Completeness:
- Root Cause: ...
- Actual ZIP Entries: ...
- Manifest Missing Files: 0
- Required Missing Files: 0
- Empty Package Rejection: PASS
- Manifest Integrity: PASS

DEV-TASK-0013 Re-verification:
- Initializer Tests: <passed>/<total>
- Actual Template NEW_PRODUCT: PASS / FAIL
- Actual Template EXISTING_PRODUCT: PASS / FAIL

Git:
- Remote: https://github.com/h-shojaku/PB-Dev.git
- Branch: main
- Push: ...
- Working tree: ...

人間判断:
- 不要
または
- 必要: ...

これをPlannerに渡してください: <実際の絶対パス>\受け渡し\DEV-TASK-0014_PLANNER_HANDOFF.zip
```

**最後の1文より後には何も記載しないこと。**

---

# 28. Final Goal

今回の目的は、

```text
Builderが「成功」と報告したZIP
```

と、

```text
Plannerが実際に受け取ったZIP
```

が完全に同じ内容・Evidenceを持つことを保証することです。

DEV-TASK-0014がPlanner ReviewでACCEPTEDになった時点で、
DEV-TASK-0013のInitializer成果物もあわせて最終受入し、
PB-DevのAI Development Standard初期構築フェーズを完了判定します。
