# DEV-TASK-0016 — Source-First Handoff安定化・Offline Planner Reproduction・Evidence単一化

## 0. Role

あなたはこのRepositoryの **Builder** です。

本TaskはDEV-TASK-0015のSource-First Reviewによって判明した、
Handoff生成・Evidence・Planner再現性の構造的問題をまとめて解消する
**Stabilization Task**です。

今回は細かなCorrectionを1件ずつ行うのではなく、
Handoff生成系のRoot Causeを一度に整理してください。

重要：

> 本Task中に自己テスト・Fresh Extraction Test・Planner相当テストで問題を発見した場合、
> その時点でHandoff提出してはいけません。
>
> Objective / Acceptance Criteria / Safetyを変更しない範囲で、
> `ADAPTATION_RULES.md` に従ってBuilder自身が方法を修正し、
> すべてのFinal GateがPASSするまで同一Task内で反復してください。

Plannerへ既知Failureを渡して次Correction Taskを作らせる運用を標準にしないこと。

---

# 1. Previous Task

Previous Task:

```text
DEV-TASK-0015
```

Planner Review:

```text
CHANGES_REQUIRED
```

ただしDEV-TASK-0015で導入した以下の方針自体は **ACCEPTED** とします。

```text
Source-First Review
Tracked Repository Snapshot
Adaptive Workflow Principle
Outcome-over-Procedure
Planner / Builder Adaptive Authority
Initializer explicit identity CLI
```

今回修正するのは主に、

```text
Handoff Generator
Offline Planner Reproduction
Evidence generation
```

です。

過去Completed Task本文はimmutableです。

---

# 2. Planner Source-First Independent Findings

Plannerは提出された、

```text
DEV-TASK-0015_PLANNER_HANDOFF.zip
```

をREPORTではなく実Archive / `repository/` Sourceから直接検証しました。

---

## 2.1 Final ZIP Structure — PASS

Actual ZIP：

```text
Total entries: 62
repository/ files: 60
Backslash entries: 0
Absolute entries: 0
Parent traversal entries: 0
Archive integrity: PASS
```

Source-first Snapshot自体は今回は正常に展開できています。

---

## 2.2 MANIFEST — Mostly Correct

Actual MANIFEST：

```text
Tracked File Count: 60
Snapshot File Count: 60
Missing Tracked Files: 0
Unexpected Snapshot Files: 0
ZIP Entry Count: 62
```

Actual Archiveと一致しています。

---

## 2.3 REPORT Evidence Is Stale

REPORT：

```text
Git Tracked Files = 29
Snapshot Files = 29

Initializer Tests:
Ran 19 tests
```

Planner actual：

```text
Snapshot Files = 60

python scripts/test_initialize_project.py
Ran 24 tests
24 PASS
```

つまり、

```text
REPORT derived metrics
!=
actual Source / Test result
```

です。

---

## 2.4 create_handoff.py --test Fails in Planner Snapshot

PlannerがHandoffを普通に展開した、

```text
repository/
```

内で、

```text
python scripts/create_handoff.py --test
```

を実行しました。

結果：

```text
FAIL

RuntimeError:
Empty Review Package Rejection:
0 files found under 'repository/'.
```

理由：

Handoffの`repository/`はGit tracked source snapshotであり、

```text
.git/
```

を含みません。

しかし現在の`create_handoff.py --test`は、
実行元Repository自体にGit metadataが存在することへ依存しています。

---

## 2.5 Same Source Passes After Temporary Git Init

Plannerが同じSnapshotをTemporary Git Repositoryとして、

```text
git init
git add .
git commit
```

した後に、

```text
python scripts/create_handoff.py --test
```

を実行すると、

```text
ALL SELF-TESTS PASSED
```

でした。

つまりGenerator logicの中心は動作しますが、

**Self-testがPlanner Handoff環境でself-containedではありません。**

---

## 2.6 create_handoff.ps1 Is NOT a Thin Wrapper

Source直接検査の結果、

```text
scripts/create_handoff.ps1
```

にはPython呼び出し後、

```text
Native PowerShell Tracked Repository Snapshot Generator
```

が丸ごと残っています。

具体的に以下のbusiness logicを再実装しています。

```text
git archive
staging population
MANIFEST generation
System.IO.Compression ZIP generation
archive verification
delivery cleanup
```

したがって、

```text
Python = Canonical
PowerShell = Thin Wrapper
```

というSSOT / Task Acceptance Criteriaと一致していません。

---

## 2.7 Python Generator Has Fail-open Git Fallbacks

`create_handoff.py`のSourceでは、
Git metadata取得失敗時に概ね以下のfallbackがあります。

```text
Commit -> "UNKNOWN"
Branch -> "main"
Remote -> PB-Dev URL
Tracked Files -> []
```

またSnapshot export失敗時に、

```text
git archive
↓ fail
git show
↓ fail
working tree copy
```

へfallback可能です。

Source-first Snapshotは、

```text
declared Git HEAD
```

そのものが真実である必要があります。

Git metadata取得に失敗したのに、

```text
UNKNOWN
main
default remote
working tree
```

を使って成功してはいけません。

---

## 2.8 Internal ZIP SHA256 Is Structurally Self-referential

現在のPython Generator Sourceでは、

```text
1. First ZIP生成
2. ZIP SHA256計算
3. そのSHA256をMANIFEST.mdへ記載
4. MANIFESTを含めてFinal ZIPを再生成
```

しています。

Plannerが同Generatorで作成したTest ZIPを確認すると、

```text
MANIFEST SHA256
!=
Final ZIP SHA256
```

となりました。

これは実装Bugというより構造問題です。

Final ZIP自身の中に、

```text
Final ZIP自身のSHA256
```

を埋め込むと、
MANIFESTを書き換えた時点でZIP内容が変わるため、
一般的な方法では自己一致しません。

`ADAPTATION_RULES.md` に従い、
この要件は方法自体を変更してください。

---

# 3. Adaptive Decision for This Task

今回以下のMethod Changeを正式採用します。

## Previous

```text
Final ZIP SHA / Sizeを内部MANIFESTへ記録
PlannerはGit metadataがないSnapshotでGit-dependent self-test
PowerShell fallbackでもHandoff生成可能
REPORTへDerived Metricsを重複手入力
```

## New

```text
Snapshot content integrityを機械検証
Self-testはTemporary Git fixtureを自分で生成
PowerShellはPythonのみを呼ぶtrue thin wrapper
Git metadata失敗はFail Closed
Derived Metricsはmachine-generated ownerを1つにする
```

---

# 4. Objective

以下を同一Task内で完了してください。

1. `create_handoff.py`を完全Fail-Closed Git Snapshot Generatorにする
2. `create_handoff.ps1`をtrue thin wrapperにする
3. Native PowerShell Handoff logicを完全撤去
4. `create_handoff.py --test`をGit metadataなしのPlanner Snapshotでもself-containedにする
5. Self-test自身がTemporary Git Repository fixtureを作る
6. Working-tree fallbackを撤去
7. Fake Git metadata fallbackを撤去
8. Snapshot setだけでなくcontent integrityも検証する
9. Final ZIP自己SHA256を内部MANIFESTへ記録する要件を廃止
10. Snapshot Content Digestへ置換
11. Derived MetricsのSSOTをmachine-generated artifactへ集約
12. REPORTで同じ数値を手入力重複しない
13. PlannerがFresh ExtractionだけでSource / Testを再検証可能にする
14. Builder自身がPlanner相当Fresh Extraction Testを実行する
15. DEV-TASK-0016をSource-first Handoffで提出
16. すべてのFinal GateがPASSするまで同一Task内で自律修正する

---

# 5. Handoff Root Structure

今後の標準を以下とします。

```text
<TASK-ID>_PLANNER_HANDOFF.zip
├── REPORT.md
├── MANIFEST.md
├── SOURCE_INDEX.json
└── repository/
    └── Git HEAD tracked source snapshot
```

---

# 6. SOURCE_INDEX.json

新規にmachine-readableな、

```text
SOURCE_INDEX.json
```

をGeneratorが自動生成してください。

Builderが手入力してはいけません。

最低限以下を含める。

```json
{
  "task_id": "...",
  "repository_url": "...",
  "branch": "...",
  "commit": "...",
  "snapshot_method": "git archive <commit>",
  "files": [
    {
      "path": "README.md",
      "sha256": "..."
    }
  ],
  "file_count": 0,
  "snapshot_digest": "..."
}
```

JSON構造は合理的に調整可。

---

# 7. Snapshot Digest

Final ZIP自身のSHA256ではなく、

**Git HEAD Source Snapshot内容のdeterministic digest**

を使用する。

推奨アルゴリズム：

```text
for each file sorted by POSIX path:
    path
    SHA256(file bytes)

これらをcanonical形式で連結
↓
SHA256
```

これを、

```text
Snapshot Digest
```

とする。

---

## 7.1 Why

Snapshot Digestは、

```text
ZIP圧縮方式
ZIP timestamp
MANIFEST更新
```

に影響されず、
Plannerが展開後Sourceから再計算できます。

---

# 8. Remove Internal Final-ZIP SHA Requirement

以下を現行SSOTから削除 / 修正する。

```text
MANIFEST must contain final ZIP SHA256
```

Final ZIPのSHA256が必要なら、
**ZIP外での配送チャネルmetadata**として利用可能だが、
1 ZIP運用の内部必須値にはしない。

---

## 8.1 ZIP Size

Final ZIP Sizeも内部MANIFESTの必須値から外してよい。

理由：

内部metadata更新による再生成ループを避けるため。

Builder最終回答では実ファイルサイズを報告可能。

MANIFESTのSource Snapshot metricsを優先する。

---

# 9. Git Metadata Must Fail Closed

`get_git_commit_info()` 等は、
以下のいずれかが失敗したらHandoff生成をFAILする。

```text
git rev-parse HEAD
git rev-parse --abbrev-ref HEAD
git remote get-url origin
git ls-files
```

以下を使用しない。

```text
UNKNOWN
assumed main
hardcoded PB-Dev remote
empty tracked list
```

---

# 10. Snapshot Export Must Fail Closed

Primary：

```text
git archive <declared commit>
```

これが失敗した場合、
勝手にWorking Treeへfallbackしない。

Alternativeを使用する場合も、

```text
git show <commit>:<path>
```

のように**同じcommitからのみ**取得する。

それも失敗：

```text
FAIL
```

---

## 10.1 Forbidden

```text
shutil.copy(repo_root / tracked_file)
```

等でCurrent Working TreeをCommit Snapshot代替にしない。

---

# 11. Snapshot Set Verification

Generation中：

```text
Git HEAD tracked set
==
Snapshot file set
```

を確認。

期待：

```text
Missing = 0
Unexpected = 0
```

---

# 12. Snapshot Content Verification

さらに各fileについて、

```text
Source Index SHA256
==
Snapshot file SHA256
```

を確認。

Plannerも展開後に同じ検証が可能であること。

---

# 13. Offline Snapshot Verifier

以下のいずれかを実装してください。

## Preferred

```text
scripts/verify_source_snapshot.py
```

使用例：

```text
python repository/scripts/verify_source_snapshot.py \
  --snapshot-root repository \
  --index SOURCE_INDEX.json
```

## Alternative

`create_handoff.py`へ、

```text
--verify-snapshot
```

modeを追加。

---

## 13.1 Critical Requirement

この検証は、

```text
.git/
Git executable
Remote access
```

を必要としない。

Handoff ZIPを展開しただけのPlanner環境で動作する。

---

# 14. create_handoff.py --test Must Be Self-contained

現在のSelf-testは、

```text
current repository must already be a Git repo
```

へ依存しています。

これを廃止。

Self-test内部でTemporary Directoryを作り、

```text
git init
git config local user
fixture files作成
git add
git commit
```

して、
そのTemporary Git fixtureに対してGeneratorを検証する。

---

## 14.1 Required Self-tests

最低限：

```text
test_git_fixture_snapshot_generation
test_snapshot_file_set_match
test_snapshot_content_hash_match
test_posix_zip_paths
test_git_metadata_failure_is_fatal
test_working_tree_fallback_does_not_exist
test_powershell_is_true_thin_wrapper
test_offline_snapshot_verifier
test_final_zip_reopen
```

Test名から失敗内容を特定可能にする。

---

# 15. PowerShell Handoff Must Be True Thin Wrapper

`create_handoff.ps1`を、

```text
1. Parameters
2. Python executable discovery
3. create_handoff.py path
4. argument forwarding
5. Python invocation
6. stdout / stderr passthrough
7. exit code propagation
```

だけにする。

---

# 16. Remove All Native PowerShell Handoff Logic

以下を完全削除。

```text
git archive implementation
System.IO.Compression
ZipArchive
CreateEntry
Native MANIFEST generation
Native staging
Native verification
Native delivery cleanup
Python failure fallback
```

---

## 16.1 Python Missing

```text
clear error
non-zero exit
```

---

## 16.2 Python Generator Failure

```text
same non-zero exit
```

PowerShell側で救済生成しない。

---

# 17. PowerShell Thinness Regression Test

Python Self-testから、
`create_handoff.ps1`をStatic Inspectする。

最低限、以下が存在しないこと。

```text
Compress-Archive
System.IO.Compression
ZipArchive
CreateEntry
git archive
```

さらに、

```text
create_handoff.py
```

へのdelegateが存在すること。

---

# 18. Derived Metrics Single Ownership

同じDerived Metricを、

```text
REPORT
MANIFEST
Console
```

へ人手で重複記載しない。

---

## 18.1 MANIFEST Owns Snapshot Metrics

以下はMANIFEST / SOURCE_INDEXのmachine-generated値を正とする。

```text
Tracked File Count
Snapshot File Count
Missing
Unexpected
Commit
Snapshot Digest
```

REPORTは、

```text
Snapshot verification: PASS
See MANIFEST / SOURCE_INDEX
```

程度に留めてよい。

---

## 18.2 Test Result Counts

Test countをREPORTへ記載する場合は、
実Test Runner outputからprogrammatically取得する。

困難なら、

```text
Initializer tests: PASS
```

だけにし、
件数を手入力しない。

---

# 19. REPORT Role Simplification

REPORTはNarrative Summaryに集中する。

推奨：

```text
Task
Status
Summary
Major Changes
Verification PASS/FAIL
Human Decision
Known Issues
Planner Review Guide
```

Derived numerical factsを大量に複製しない。

---

# 20. MANIFEST Redesign

最低限：

```text
Task ID
Repository URL
Branch
Commit
Snapshot Method
Tracked File Count
Snapshot File Count
Missing
Unexpected
Snapshot Digest
ZIP Entry Count
Included Root Artifacts
```

ZIP Entry Countは、

```text
SOURCE_INDEX.json
REPORT.md
MANIFEST.md
repository/*
```

の構成からfinal archive作成後に実測し、
必要ならGenerator console / final responseで報告する。

MANIFEST内部に持つ場合は、
final passで値が安定する設計を証明する。

不要ならMANIFEST必須値から外してよい。

Adaptive Workflowに従い、
循環依存を生まない単純設計を優先する。

---

# 21. Fresh Extraction Planner Reproduction Gate

BuilderがPlannerへHandoffを提出する前に、
必ず**生成した最終ZIPそのもの**をTemporary Directoryへ展開する。

重要：

```text
そのTemporary Directoryには.gitが存在しない
```

こと。

---

# 22. Planner-equivalent Test

Fresh Extractionで最低限以下を実行。

```text
python repository/scripts/test_initialize_project.py
python repository/scripts/create_handoff.py --test
python repository/scripts/verify_source_snapshot.py \
  --snapshot-root repository \
  --index SOURCE_INDEX.json
```

実装したCLIに合わせて調整可。

---

## 22.1 Required Result

すべて：

```text
PASS
```

しなければHandoff提出禁止。

---

# 23. Why create_handoff --test Must Work Without .git

通常のGenerator実行はGit Repositoryを必要とする。

しかし、

```text
--test
```

はGenerator自身のロジックを検証するSelf-testなので、
自身でTemporary Git fixtureを構築すればよい。

Planner Snapshotに`.git`を含める必要はない。

---

# 24. Do Not Add .git to Handoff

この問題を解決するために、

```text
repository/.git/
```

をSnapshotへ含めない。

Source-first Handoffは引き続きTracked Source Snapshotとする。

---

# 25. Optional Commit Verification

Handoffだけで、

```text
declared remote commit本体
```

を暗号学的に完全証明することまでは本Taskの必須にしない。

Builder生成時点ではGit Repository上で、

```text
Commit
Tracked set
Snapshot content
```

を検証する。

Plannerは、

```text
SOURCE_INDEX
Snapshot Digest
Source
```

をoffline検証できればよい。

必要に応じてPublic GitHub commitとの外部照合も可能。

---

# 26. Initializer Regression

DEV-TASK-0015 Source上でInitializer Python TestはPlanner環境で、

```text
24 / 24 PASS
```

しています。

本TaskではInitializer coreを再設計しない。

Regressionのみ確認。

---

# 27. Adaptive Workflow Integration

今回の修正自体を、
`ADAPTATION_RULES.md` の正式なExampleとして追加してよい。

例：

```text
Final ZIP SHA self-reference discovered
↓
same implementationをretryしない
↓
Snapshot Digestへmethod change
```

---

# 28. No Known-bad Retry

以下を再導入しない。

```text
PowerShell Native fallback
Working-tree source fallback
Fake Git defaults
Final ZIP internal self-SHA
Manual derived metric duplication
Git-dependent self-test in extracted snapshot
```

---

# 29. Development SSOT Update

最低限確認・更新：

```text
docs/development/
├── ADAPTATION_RULES.md
├── HANDOFF_RULES.md
├── REVIEW_RULES.md
├── BUILDER_RULES.md
└── DEFINITION_OF_DONE.md
```

必要な場合：

```text
DEVELOPMENT_SYSTEM.md
scripts/README.md
```

---

# 30. Handoff Rules Final Model

Handoffの目的：

```text
Actual Source Delivery
+
Offline Integrity Verification
+
Planner Independent Reproduction
```

であることを明確化。

---

# 31. Builder Final Gate

本Taskでは以下のFinal Gateをすべて満たすまで提出しない。

```text
GATE 1: Builder unit / integration tests PASS
GATE 2: Handoff Generator self-tests PASS
GATE 3: Git HEAD snapshot set/content verification PASS
GATE 4: Final ZIP path/integrity verification PASS
GATE 5: Fresh Extraction Offline Snapshot Verification PASS
GATE 6: Fresh Extraction Initializer Tests PASS
GATE 7: Fresh Extraction create_handoff.py --test PASS
GATE 8: REPORT has no stale derived metrics
GATE 9: tracked working tree clean
GATE 10: origin/main push completed
```

---

# 32. Adaptive Self-correction Within Same Task

上記GateのどれかがFAILした場合：

```text
Do NOT prepare final Handoff
Do NOT report COMPLETE
Do NOT ask Planner to find the next correction
```

Builder自身で、

```text
Root Cause
↓
Local Fix / Method Change
↓
rerun all affected Gates
```

を実施。

Task Objective / AC / Safetyが変わらない限り、
人間確認不要。

---

# 33. Task Lifecycle

DEV-TASK-0016を正式Lifecycleで処理。

```text
Intake
↓
ACTIVE
↓
Intake commit / push
↓
Stabilization implementation
↓
Builder tests
↓
Fresh Extraction Planner-equivalent test
↓
COMPLETED
↓
Final commit / push
↓
HEAD Source Snapshot Handoff
↓
Final Gate再確認
```

---

# 34. Git / GitHub

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
DEV-TASK-0016: register task
DEV-TASK-0016: stabilize source-first handoff verification
```

---

# 35. Final Handoff

提出物：

```text
受け渡し/DEV-TASK-0016_PLANNER_HANDOFF.zip
```

1個のみ。

構造：

```text
DEV-TASK-0016_PLANNER_HANDOFF.zip
├── REPORT.md
├── MANIFEST.md
├── SOURCE_INDEX.json
└── repository/
    └── Git HEAD tracked source snapshot
```

500MB以内。

---

# 36. Planner Reproduction README

Plannerが迷わないよう、
REPORTのPlanner Review Guideに、
今回最低限以下を記載。

```text
1. ZIPを展開
2. SOURCE_INDEX offline verification
3. Initializer tests
4. Handoff self-tests
```

実コマンドも記載。

---

# 37. Required Verification

Builder実環境で最低限：

```text
python scripts/test_initialize_project.py
python scripts/create_handoff.py --test
git diff --check
git status
git remote -v
git log -1
```

および最終ZIPのFresh Extraction環境で：

```text
python repository/scripts/test_initialize_project.py
python repository/scripts/create_handoff.py --test
python repository/scripts/verify_source_snapshot.py --snapshot-root repository --index SOURCE_INDEX.json
```

---

# 38. REPORT Required Sections

```text
## DEV-TASK-0015 Planner Findings
## Root Cause Consolidation
## Method Changes
## Git Fail-Closed Changes
## PowerShell Thin Wrapper
## Self-contained Self-tests
## Snapshot Digest / SOURCE_INDEX
## Derived Evidence Ownership
## Fresh Extraction Planner Reproduction
## Final Gate Results
## Planner Review Guide
```

---

# 39. REPORT Metrics Rule

REPORTに数値を書く場合：

```text
programmatically generated actual value only
```

それが保証できない値は書かない。

例えば：

```text
Snapshot: PASS — see MANIFEST.md / SOURCE_INDEX.json
```

で十分。

---

# 40. Acceptance Criteria

以下をすべて満たせばCOMPLETE。

## Git Snapshot Fail Closed

- [ ] Git metadata失敗でHandoff FAIL
- [ ] Commit `"UNKNOWN"` fallbackなし
- [ ] Branch `"main"` fake fallbackなし
- [ ] Hardcoded Remote fallbackなし
- [ ] Tracked Files empty fallbackなし
- [ ] Working Tree copy fallbackなし
- [ ] Snapshotはdeclared commitからのみ生成

## PowerShell

- [ ] `create_handoff.ps1` true thin wrapper
- [ ] Native Git archive logicなし
- [ ] Native ZIP logicなし
- [ ] Native MANIFEST logicなし
- [ ] Native verificationなし
- [ ] Python failure fallbackなし
- [ ] Python unavailable時non-zero
- [ ] Python exit code propagation

## Self-test

- [ ] `create_handoff.py --test`が外部`.git`に依存しない
- [ ] Self-testがTemporary Git fixtureを自動生成
- [ ] Fresh extracted Handoffでself-test PASS
- [ ] Failure Test名が識別可能

## Source Integrity

- [ ] SOURCE_INDEX.json auto-generated
- [ ] 全Snapshot file pathを記録
- [ ] 全Snapshot file content SHA256を記録
- [ ] deterministic Snapshot Digestあり
- [ ] Missing tracked files = 0
- [ ] Unexpected snapshot files = 0
- [ ] Content mismatches = 0
- [ ] Offline verifier PASS

## Archive

- [ ] Final ZIP backslash = 0
- [ ] absolute path = 0
- [ ] traversal = 0
- [ ] integrity PASS
- [ ] extraction PASS
- [ ] repository/ snapshot present
- [ ] REPORT / MANIFEST / SOURCE_INDEX present

## Evidence

- [ ] Internal final-ZIP SHA self-reference要件を撤廃
- [ ] Snapshot Digestへ置換
- [ ] REPORTにstale manual derived metricsなし
- [ ] Snapshot metricsのmachine ownerが明確
- [ ] Test countを記載するならactual resultから生成
- [ ] REPORT / MANIFESTで矛盾するDerived Metricなし

## Planner-equivalent Reproduction

- [ ] Builderが最終ZIPをFresh Directoryへ展開
- [ ] Fresh directoryに`.git`なし
- [ ] Initializer tests PASS
- [ ] Handoff self-tests PASS
- [ ] Offline Snapshot verifier PASS
- [ ] Plannerが同手順を再現可能

## Adaptive Workflow

- [ ] 今回のMethod ChangeがADAPTATION_RULESと整合
- [ ] Known-bad methodを再利用していない
- [ ] Final Gate FAIL時に同Task内で自律修正
- [ ] 既知FAILをPlannerへ提出しない

## Git / Delivery

- [ ] `git diff --check` PASS
- [ ] GitHub commit / push完了
- [ ] tracked working tree clean
- [ ] `受け渡し/` に最新ZIP 1個のみ
- [ ] ZIP <= 500MB
- [ ] Builder最終回答が絶対パス案内で終了

---

# 41. Builder Final Response

最低限：

```text
Task: DEV-TASK-0016
Status: COMPLETE / BLOCKED

Source-First Stabilization:
- Git Fail-Closed: PASS / FAIL
- PowerShell Thin Wrapper: PASS / FAIL
- SOURCE_INDEX: PASS / FAIL
- Snapshot Content Verification: PASS / FAIL
- Offline Verification: PASS / FAIL

Fresh Extraction Planner Reproduction:
- .git present: NO
- Initializer Tests: PASS / FAIL
- Handoff Self-tests: PASS / FAIL
- Snapshot Verifier: PASS / FAIL

Adaptive Final Gates:
- Passed: <all / not all>
- Known Failure Submitted: NO

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

これをPlannerに渡してください: <実際の絶対パス>\受け渡し\DEV-TASK-0016_PLANNER_HANDOFF.zip
```

最後の1文より後には何も記載しないこと。

---

# 42. Final Goal

本Taskの目的は、
Handoff GeneratorのBugを1個直すことではありません。

最終的に、

```text
Builder
↓
Git HEAD Source Snapshotを機械生成
↓
Source integrityを機械検証
↓
Final ZIPをFresh環境へ展開
↓
Plannerと同じ条件で再テスト
↓
全Gate PASS
↓
Plannerへ提出
```

というループを確立してください。

これにより、

```text
Builder環境ではPASS
↓
Plannerへ渡す
↓
初めて不具合発見
```

を例外ケースにし、

**BuilderがPlanner相当の検証条件まで自律的に再現してから提出する**
運用へ切り替えます。
