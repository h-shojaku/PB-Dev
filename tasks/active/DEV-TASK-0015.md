# DEV-TASK-0015 — Source-First Review・Tracked Repository Snapshot・Adaptive Workflow標準化

## 0. Role

あなたはこのRepositoryの **Builder** です。

本Taskは、これまでのPlanner Reviewで繰り返し発生した、

```text
Builder ReportではPASS
↓
Plannerが実成果物を独立検証
↓
Reportと実態の差異を発見
↓
Correction Task
```

という非効率を解消し、
Planner / Builder AI Development Standardそのものを
**結果重視・Source-first・状況適応型の運用**へ進化させるTaskです。

本Taskでは、従来の

```text
Builderがレビュー対象ファイルを選んでHandoff ZIPへ格納
```

という方式を廃止し、

```text
Task完了時点のGit HEADに含まれるTracked Repository Snapshot
```

をPlannerへ渡す方式へ切り替えてください。

さらに今回のように、
既存手順が繰り返し問題を生む・非効率になる・前提が崩れる場合、
Planner / Builderが人間確認なしに
**より確実な方法へ自律的に切り替えられるAdaptive Workflow Principle**
をDevelopment Standardへ追加してください。

本Task完了後の基本思想は、

```text
Procedure is replaceable.
Objective / SSOT / Acceptance Criteria / Safety are not.
```

です。

---

# 1. Previous State

これまでHandoffは、

```text
REPORT.md
MANIFEST.md
files/
```

へBuilderがTaskごとのReview対象を選択して格納する方式でした。

この方式では、

- ManifestとActual ZIPの差異
- 必要ファイルの入れ忘れ
- Builder Reportと実Sourceの不一致
- PowerShell / Pythonの生成経路差
- Plannerが実Sourceを再検証できない
- Review対象選択そのものの漏れ

が繰り返し発生しました。

このため人間判断により、
今後のPlanner Reviewは **Source-first Review** を標準とします。

---

# 2. Human Decision — Source-First Review

今後のPlanner Handoffは、
Builderが選んだ一部ファイルではなく、

**Task完了時点のGit HEAD commitに含まれるTracked Repository Sourceを基準にする。**

Plannerは、

```text
REPORTを信頼してSourceを確認する
```

のではなく、

```text
Sourceを直接確認・実行
↓
REPORTと照合する
```

ことを標準とします。

---

# 3. Core Principle

正式なReview evidence hierarchyを以下とします。

```text
1. Actual tracked source at declared Git commit
2. Planner independent verification result
3. Builder verification evidence
4. REPORT / MANIFEST summary
```

REPORTは重要ですが、
**実Sourceより上位の真実ではありません。**

---

# 4. Objective

本Taskでは以下を完成させてください。

1. HandoffをTracked Repository Snapshot方式へ変更
2. SnapshotをGit HEADから機械生成
3. BuilderによるReview file選択を原則廃止
4. PlannerがHandoffだけでRepository Sourceを直接確認可能にする
5. Plannerが同じtest / scriptを再実行可能にする
6. Snapshot CommitとREPORT Commitを一致させる
7. Handoff ZIPのManifestをActual Snapshotから自動生成
8. Windows / macOS / Linuxで同じSnapshot構造にする
9. PowerShell Handoff生成をPython Canonical implementationのthin wrapperへ統一
10. Initializer CLIのidentity default問題も既存Task方針どおり修正
11. Adaptive Workflow PrincipleをDevelopment SSOTへ追加
12. Planner / Builder双方のAdaptive behaviorを標準化
13. 手段変更とScope変更の境界を明確化
14. 「同じ失敗を同じ方法で繰り返す」ことを防止
15. Task / Review方式を状況に応じて自律改善可能にする
16. 本Task自身をSource-first Handoffで提出する

---

# 5. New Handoff Structure

標準Handoffを以下へ変更します。

```text
<TASK-ID>_PLANNER_HANDOFF.zip
├── REPORT.md
├── MANIFEST.md
└── repository/
    └── <Git HEAD tracked files snapshot>
```

例：

```text
DEV-TASK-0015_PLANNER_HANDOFF.zip
├── REPORT.md
├── MANIFEST.md
└── repository/
    ├── README.md
    ├── PROJECT_PROFILE.md
    ├── CURRENT_STATE.md
    ├── AGENTS.md
    ├── CLAUDE.md
    ├── GEMINI.md
    ├── docs/
    ├── scripts/
    ├── tasks/
    ├── templates/
    ├── src/
    ├── tests/
    └── ...
```

---

# 6. Snapshot Definition

`repository/` は、

```text
git HEAD
```

で追跡されているファイルから生成します。

原則として以下のどちらかを利用してください。

## Preferred

```text
git archive HEAD
```

を基準にする。

## Alternative

```text
git ls-files
```

からTracked Filesを列挙し、
HEAD内容を機械的にSnapshotする。

---

# 7. Snapshot Must Represent HEAD

重要です。

Working treeのファイルを単純コピーしてはいけません。

Snapshotは、

```text
REPORTに記載されたCommit
==
repository/ SnapshotのSource Commit
```

である必要があります。

---

## 7.1 Reason

以下を防止します。

```text
commit後にlocal fileを変更
↓
Snapshotはworking tree
↓
REPORTは古いcommit
```

この状態は禁止です。

---

# 8. Git Commit Binding

REPORT / MANIFESTに最低限以下を記録します。

```text
Repository
Branch
Commit
Snapshot Source
```

例：

```text
Repository:
https://github.com/h-shojaku/PB-Dev.git

Branch:
main

Commit:
abc123...

Snapshot Source:
git archive abc123...
```

---

# 9. Handoff Generation Timing

標準Task完了順：

```text
Implementation
↓
Builder Verification
↓
Task Completion state update
↓
git diff --check
↓
commit
↓
push
↓
working tree clean確認
↓
HEAD commit取得
↓
HEAD tracked source snapshot生成
↓
REPORT / MANIFEST生成
↓
Handoff ZIP生成
↓
Final archive verification
↓
Builder final response
```

---

# 10. What Is Excluded

SnapshotはGit HEAD tracked sourceなので、
通常以下は自動的に除外されます。

```text
.git/
node_modules/
build/
dist/
cache/
受け渡し/
untracked temporary files
local secrets
```

---

## 10.1 Git-tracked Large / Generated Files

Git管理されているものは原則Snapshotへ含めます。

ただし500MB上限を超える場合は、
Handoff Generatorが勝手にファイルを間引いて成功扱いしてはいけません。

```text
Handoff > 500MB
```

の場合：

```text
BLOCKED or alternate strategy required
```

とし、Adaptive Workflow Ruleに従って
安全な代替方法を選択する。

---

# 11. Source Snapshot Completeness

Planner Handoffの`repository/`は、

```text
HEAD tracked file set
```

と完全一致すること。

以下を機械検証する。

```text
Git HEAD tracked file count
Snapshot file count
Missing tracked files
Unexpected snapshot files
```

期待：

```text
Missing tracked files = 0
Unexpected snapshot files = 0
```

---

# 12. Manifest Redesign

MANIFESTのIncluded Filesを
Builderが手作業で列挙する方式を廃止する。

GeneratorがActual Snapshotから自動生成してください。

最低限：

```text
Task ID
ZIP filename
Created At
Repository URL
Branch
Commit
Snapshot Method
Tracked File Count
Snapshot File Count
Missing Tracked Files
Unexpected Snapshot Files
ZIP Entry Count
ZIP Size
SHA256
```

---

# 13. Manifest File List

ファイル一覧が必要な場合は、
Actual Snapshotから自動生成する。

人間 / Builderが手入力でManifest file listを保守しない。

---

# 14. REPORT Role

REPORTはSummary / Verification Reportとして維持する。

REPORTはSourceの代替ではありません。

標準：

```text
Source = actual truth
REPORT = explanation / verification summary
```

---

# 15. Planner Review Standard — Source First

`docs/development/REVIEW_RULES.md` を更新してください。

Planner Reviewの標準順序：

```text
1. REPORT / MANIFESTからTask / Commitを確認
2. repository/ Snapshotを確認
3. Task Acceptance Criteriaを確認
4. 主要Source / SSOTを直接確認
5. 可能なら同梱testをPlanner環境で再実行
6. Builder VerificationとPlanner Verificationを比較
7. Review Result決定
```

---

# 16. Planner Independent Verification

Plannerが実行可能なtest / validationは、
必要に応じてPlanner自身が再実行する。

例：

```text
python scripts/test_initialize_project.py
python scripts/create_handoff.py --test
```

Product codeであれば：

```text
unit tests
build
lint
static checks
```

など。

Plannerが実行環境を持たない場合は、
Source Inspection + Builder EvidenceでReviewする。

---

# 17. Handoff Generator Canonical Implementation

引き続き、

```text
scripts/create_handoff.py
```

を唯一のHandoff business logicとする。

---

# 18. PowerShell Handoff Wrapper

```text
scripts/create_handoff.ps1
```

は完全thin wrapperにする。

役割：

```text
Parameters
Python discovery
Python script invocation
argument forwarding
stdout / stderr forwarding
exit-code propagation
```

---

# 19. Remove Native PowerShell Handoff Generation

以下を完全撤去。

```text
Compress-Archive
Native ZipFile generation
Native staging logic
Native manifest logic
Native verification
Python failure fallback
```

Python unavailable：

```text
FAIL
```

Python Generator failure：

```text
FAIL
```

---

# 20. Cross-platform Archive Rules

最終ZIP内pathは常にPOSIX `/`。

期待：

```text
repository/scripts/create_handoff.py
repository/docs/development/REVIEW_RULES.md
```

禁止：

```text
repository\scripts\create_handoff.py
```

---

# 21. Final ZIP Verification

最終ZIPを再オープンし、

```text
entry count
backslash count
absolute path count
parent traversal count
CRC / integrity
repository file count
```

を確認する。

---

# 22. Snapshot vs Git Verification

最終ZIPの`repository/`からfile setを取得し、
Git HEADと比較する。

最低限：

```text
git tracked files
snapshot files
missing
unexpected
```

を検証。

---

# 23. Snapshot Content Verification

可能なら一部だけでなく、
各Tracked Fileのcontent hashも比較する。

推奨：

```text
Git HEAD blob content
vs
Snapshot file content
```

全ファイルのSHA256等を比較してもよい。

過剰に遅くならない範囲で、
SnapshotがHEADそのものだと証明する。

---

# 24. Handoff Self-test

最低限以下を追加する。

```text
test_snapshot_matches_git_head
test_snapshot_missing_file_fails
test_snapshot_unexpected_file_fails
test_snapshot_content_mismatch_fails
test_zip_paths_are_posix
test_powershell_is_thin_wrapper
test_final_zip_reopen_verification
```

---

# 25. Initializer CLI Residual Fix

前Taskから残っている以下も本Taskで完了する。

現在：

```text
--mode   default=NEW_PRODUCT
--name   default=MyNewProduct
--prefix default=APP
```

等の仮値が存在する場合は撤去する。

---

## 25.1 Required CLI Identity

通常CLIでは、

```text
--mode
--name
--prefix
```

を明示必須。

NEW_PRODUCT / EXISTING_PRODUCTでは、

```text
--remote
```

も必須。

---

## 25.2 No Default Product Identity

以下の仮defaultで正式Project初期化できないこと。

```text
MyNewProduct
APP
NEW_PRODUCT
```

---

# 26. Initializer CLI Tests

最低限：

```text
test_cli_missing_mode_fails
test_cli_missing_name_fails
test_cli_missing_prefix_fails
test_cli_remote_only_fails
```

既存Initializer core testsを後退させない。

---

# 27. Adaptive Workflow Principle

今回の運用改善を一般化し、

```text
docs/development/ADAPTATION_RULES.md
```

を新規作成してください。

目的：

**既存手順が目的達成に不適切になった場合、
Planner / Builderが安全範囲内で方法を自律変更できるようにする。**

---

# 28. Stable vs Replaceable

`ADAPTATION_RULES.md` で、
以下を明確に分ける。

## Stable — 自律変更してはいけない

```text
Human explicit decisions
Product requirements
Product SSOT
Development safety constraints
Task Objective
Acceptance Criteria
Data / security constraints
External publication / payment / production boundaries
```

---

## Replaceable — 自律変更可能

```text
implementation technique
testing technique
review technique
tool choice
script language
temporary directory strategy
file discovery method
Handoff packaging implementation
investigation approach
debugging approach
internal workflow detail
```

---

# 29. Outcome-over-Procedure Principle

正式原則：

> Taskの目的・Acceptance Criteria・SSOT・Safetyを満たす限り、
> Planner / Builderは既存手順そのものに固執する必要はない。

---

# 30. Adaptive Trigger

以下が発生した場合、
既存方法の継続ではなく、
**方法自体の見直しを自律的に検討する。**

例：

```text
同種のFailureが再発
同じCorrectionが繰り返される
Manual workaroundが増える
Evidenceと実態のズレが発生
特定OS / AI / Tool依存が発覚
既存方法ではAcceptance Criteriaを安定して検証できない
作業手順自体が主要なFailure sourceになっている
```

---

# 31. Do Not Repeat Known-bad Method

明示的にルール化する。

> 同一または本質的に同じ原因によるFailureが再発した場合、
> 原因となった方法をそのまま繰り返すことを標準対応にしない。

まず、

```text
Failure原因
方法自体の問題か
局所Bugか
```

を判断する。

方法自体が原因なら、
より単純・直接・検証可能な方式へ変更する。

---

# 32. Escalation Ladder

問題が発生した場合の標準順：

```text
1. Local Fix
2. Root Cause Fix
3. Method Change
4. Workflow / Standard Change
5. Human Decision
```

---

## 32.1 Local Fix

単純Bugであり手法自体は適切。

---

## 32.2 Root Cause Fix

同種Bugを生む共通原因を修正。

---

## 32.3 Method Change

現在の方法自体が問題なら別方式へ切替。

今回の例：

```text
selected-files Handoff
↓
Tracked Repository Snapshot
```

---

## 32.4 Workflow / Standard Change

複数Task / Productへ影響する場合、
Development Standard自体を更新。

---

## 32.5 Human Decision

変更が、

```text
Product scope
major UX
legal
cost
production
external publication
irreversible operation
```

等へ影響する場合のみ人間判断。

---

# 33. Builder Adaptive Authority

BuilderはTask Objective / ACを変えない範囲で、
以下を自律変更してよい。

```text
implementation method
tool
script
test strategy
debug strategy
internal file processing
verification method
```

例：

```text
PowerShell実装がクロスプラットフォーム問題を起こす
↓
Python canonical + wrapperへ変更
```

この変更のために人間確認で停止しない。

---

# 34. Builder Must Not Adapt Scope

Adaptive Authorityは、
「何でも変更してよい」という意味ではありません。

Builderは以下を勝手に変更しない。

```text
Product requirement
Task Objective
Acceptance Criteriaの意味
Human decision
external behavior not required by Task
paid service
production deployment
destructive external operation
```

---

# 35. Planner Adaptive Authority

PlannerもReview / Task設計方法を固定しない。

以下の場合、
PlannerはReview方法や次Taskのアプローチを自律変更できる。

```text
Builder Report中心Reviewで見逃しが続く
↓
Source-first Reviewへ変更

巨大Taskで問題が追跡不能
↓
Taskを小さく分割

多数のCorrection Task
↓
局所修正ではなくworkflow root cause修正Task
```

---

# 36. Planner Must Prefer Structural Fix

同種問題が繰り返された場合、
Plannerは単発Bug修正Taskを出し続ける前に、

```text
「なぜ同じ種類の問題が再発するのか」
```

を評価する。

再発原因がWorkflow / Tooling / Review Processなら、
Product codeではなく標準運用を修正するTaskへ切り替える。

---

# 37. Adaptive Decision Record

方法を大きく変更した場合、
private chain-of-thoughtは保存せず、
最低限以下だけをREPORT / SSOTに記録する。

```text
Previous Method
Observed Problem
New Method
Why It Is Safer / More Reliable
Scope Impact
```

長い思考過程は不要。

---

# 38. Adaptation Does Not Require a New Human Decision

以下をすべて満たす場合、
方法変更は人間確認不要。

```text
Objective unchanged
Acceptance Criteria unchanged
Product behavior unchanged
Safety maintained or improved
External side effects unchanged
Cost / publication / production impactなし
```

---

# 39. When Human Decision Is Required

方法変更が以下へ影響する場合のみ停止。

```text
Product scope
User-visible requirement
Architecture with major irreversible consequence
external API / paid service
data migration
production
legal / licensing
security policy weakening
```

---

# 40. Update DEVELOPMENT_SYSTEM.md

以下を追加。

```text
## Adaptive Workflow Principle
```

簡潔に：

- Procedureは目的ではない
- Outcome / SSOT / Safetyを優先
- 方法がFailure sourceなら自律変更
- 詳細はADAPTATION_RULES.md

---

# 41. Update BUILDER_RULES.md

Builderへ以下を追加。

```text
Do not repeatedly retry a method shown to be structurally unreliable.
```

自己解決可能な方法変更は、
確認なしで実施。

---

# 42. Update REVIEW_RULES.md

Planner ReviewをSource-firstへ更新。

また、

```text
Repeated Review Failure
```

時にはReview方式自体を変更することを定義。

---

# 43. Update TASK_RULES.md

TaskのImplementation Requirementsに書かれた具体的手段について、
Taskが明示的に、

```text
mandatory
```

としていない限り、
Objective / ACを満たすための推奨手段として扱える設計にする。

ただし人間明示指示は必須。

---

# 44. Update DEFINITION_OF_DONE.md

Handoff DoDをSource-firstへ変更。

最低限：

```text
HEAD tracked snapshot generated
snapshot commit matches REPORT
snapshot file set matches Git HEAD
snapshot verification PASS
portable ZIP verification PASS
Planner can inspect source from Handoff alone
```

---

# 45. Source-first Handoff 500MB Rule

500MB以内を維持する。

Snapshot生成前に概算可能ならサイズ確認。

超過時：

```text
勝手にファイルを削除して成功
```

は禁止。

Adaptive Workflowにより、
安全な代替を選択する。

例：

```text
Git bundle / split evidence / source-only with referenced large assets
```

ただしProduct-specificな最適方式はその時点で判断する。

---

# 46. This Task Handoff

本Task自身からSource-first方式を使用する。

```text
受け渡し/DEV-TASK-0015_PLANNER_HANDOFF.zip
```

構造：

```text
DEV-TASK-0015_PLANNER_HANDOFF.zip
├── REPORT.md
├── MANIFEST.md
└── repository/
    └── HEAD tracked repository snapshot
```

---

# 47. Source Snapshot Exclusion

`repository/`内に、

```text
受け渡し/
```

は存在しないこと。

理由：

Handoff ZIPはgitignore対象で、
HEAD tracked sourceではないため。

---

# 48. Final Source-first Verification

最終ZIPに対して以下を確認。

```text
REPORT Commit
==
MANIFEST Commit
==
Git HEAD used for snapshot

Git HEAD tracked files
==
repository/ snapshot files

Missing = 0
Unexpected = 0
```

---

# 49. Planner Reproduction

Handoffの`repository/`だけを別Directoryへ展開し、
最低限以下を実行可能であること。

```text
python scripts/test_initialize_project.py
python scripts/create_handoff.py --test
```

Git metadataを必要とするTestについては、
Snapshot-onlyで実行不能な場合はその理由をREPORTへ明示し、
Temporary Git init等によるreproduction方法を記載。

---

# 50. Git / GitHub

PB-Dev：

```text
Canonical Remote:
https://github.com/h-shojaku/PB-Dev.git

Branch:
main
```

Task ID付きcommit。

例：

```text
DEV-TASK-0015: register task
DEV-TASK-0015: adopt source-first adaptive review workflow
```

push完了。

---

# 51. Required Verification

最低限：

```text
python scripts/test_initialize_project.py
python scripts/create_handoff.py --test
git diff --check
git status
git remote -v
git log -1
```

加えて：

```text
Tracked Snapshot Verification
PowerShell thin wrapper static test
PowerShell Handoff entrypoint test on Windows
Initializer CLI required-identity tests
Final ZIP reopen verification
Planner reproduction test
```

---

# 52. REPORT Required Sections

```text
## Source-First Review Migration
## Previous Handoff Failure Pattern
## Tracked Snapshot Architecture
## Snapshot vs Git HEAD Verification
## PowerShell Thin Wrapper
## Initializer CLI Safety
## Adaptive Workflow Standard
## Method Change Record
## Test Results
## Final Handoff Evidence
```

---

# 53. Method Change Record

今回最低限：

```text
Previous Method:
Selected review files + manual/staged manifest

Observed Problem:
Repeated mismatch between REPORT/MANIFEST and actual deliverable

New Method:
Git HEAD tracked repository snapshot

Why:
Planner can independently verify actual source and rerun tests

Scope Impact:
Review/Handoff method only; Product requirements unchanged
```

---

# 54. REPORT Concrete Evidence

実値：

```text
Git:
- HEAD:
- Branch:
- Remote:

Snapshot:
- Git tracked file count:
- Snapshot file count:
- Missing tracked files:
- Unexpected snapshot files:
- Content mismatches:

Initializer tests:
- total:
- passed:
- failed:

Handoff generator tests:
- total:
- passed:
- failed:

Final ZIP:
- entry count:
- repository file count:
- backslash:
- absolute:
- traversal:
- integrity:
- extraction:
- size:
```

---

# 55. Acceptance Criteria

以下をすべて満たせばCOMPLETE。

## Source-first Handoff

- [ ] Handoff標準がTracked Repository Snapshot方式へ変更
- [ ] `repository/` はGit HEAD tracked sourceから生成
- [ ] Working tree直接コピーではない
- [ ] REPORT / MANIFEST / Snapshot Commitが一致
- [ ] Git tracked file set == Snapshot file set
- [ ] Missing tracked files = 0
- [ ] Unexpected snapshot files = 0
- [ ] PlannerがHandoffだけで実Sourceを確認可能
- [ ] Plannerが同梱testを再実行可能

## Handoff Generator

- [ ] `create_handoff.py` がCanonical implementation
- [ ] `create_handoff.ps1` がtrue thin wrapper
- [ ] Native PowerShell ZIP fallbackなし
- [ ] Windows PowerShell入口でもPOSIX ZIP path
- [ ] Backslash entry = 0
- [ ] Absolute entry = 0
- [ ] Traversal entry = 0
- [ ] Final ZIP reopen verification PASS

## Manifest / Evidence

- [ ] MANIFESTはActual Snapshotから自動生成
- [ ] 手入力file list依存を廃止
- [ ] Snapshot file countsは実値
- [ ] REPORT entry countは実値
- [ ] REPORT / MANIFEST / Actual ZIP metrics一致

## Initializer CLI

- [ ] `--mode`明示必須
- [ ] `--name`明示必須
- [ ] `--prefix`明示必須
- [ ] NEW_PRODUCT / EXISTING_PRODUCTで`--remote`必須
- [ ] 仮default identityで正式初期化不可
- [ ] Existing Initializer regression tests全PASS

## Adaptive Workflow

- [ ] `ADAPTATION_RULES.md` が存在
- [ ] Stable / Replaceableが定義
- [ ] Outcome-over-Procedure Principleが定義
- [ ] Adaptive Triggerが定義
- [ ] Repeated known-bad method禁止
- [ ] Escalation Ladderが定義
- [ ] Builder Adaptive Authorityが定義
- [ ] Planner Adaptive Authorityが定義
- [ ] Scope変更との境界が明確
- [ ] 方法変更のみなら不要な人間確認をしない
- [ ] Structural failureではworkflow自体を改善可能

## Standard Integration

- [ ] DEVELOPMENT_SYSTEM更新
- [ ] BUILDER_RULES更新
- [ ] REVIEW_RULES Source-first化
- [ ] TASK_RULES Adaptive method対応
- [ ] DEFINITION_OF_DONE Source-first対応
- [ ] AI Adapterに重複ルールを大量追加していない

## Git / Delivery

- [ ] `git diff --check` PASS
- [ ] GitHub commit / push完了
- [ ] tracked working tree clean
- [ ] `受け渡し/` に最新ZIP 1個のみ
- [ ] ZIP <= 500MB
- [ ] Builder最終回答が絶対パス案内で終了

---

# 56. Builder Final Response

最低限：

```text
Task: DEV-TASK-0015
Status: COMPLETE / BLOCKED

Source-First Handoff:
- HEAD: ...
- Git Tracked Files: ...
- Snapshot Files: ...
- Missing: 0
- Unexpected: 0
- Snapshot Verification: PASS / FAIL

Adaptive Workflow:
- ADAPTATION_RULES: ...
- Method Switching Principle: ...
- Repeated Failure Handling: ...

Initializer CLI:
- Explicit Mode: PASS / FAIL
- Explicit Name: PASS / FAIL
- Explicit Prefix: PASS / FAIL
- Regression Tests: <passed>/<total>

Handoff:
- PowerShell Thin Wrapper: PASS / FAIL
- ZIP Entries: ...
- Backslash: 0
- Integrity: PASS
- Planner Reproduction: PASS / FAIL

Git:
- Remote: https://github.com/h-shojaku/PB-Dev.git
- Branch: main
- Commit: ...
- Push: ...
- Working tree: ...

人間判断:
- 不要
または
- 必要: ...

これをPlannerに渡してください: <実際の絶対パス>\受け渡し\DEV-TASK-0015_PLANNER_HANDOFF.zip
```

最後の1文より後には何も記載しないこと。

---

# 57. Final Goal

今回の最終目的は、
Handoff ZIP形式そのものを綺麗にすることではありません。

開発標準を、

```text
Builderが報告する
↓
Plannerが信頼する
```

から、

```text
Builderが実Sourceを渡す
↓
Plannerが直接検証する
↓
REPORTと照合する
```

へ変更することです。

さらに、

```text
一度決めたProcedureを守り続ける開発
```

ではなく、

```text
Objective / SSOT / Safetyを守りながら
状況に応じて最も確実なProcedureへ自律的に切り替える開発
```

を標準化してください。

これにより、
特定AI・特定OS・特定Tool・過去の手順に開発全体が縛られず、
失敗からWorkflow自体を改善できるAI Development Standardを完成させます。
