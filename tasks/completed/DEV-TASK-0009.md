# DEV-TASK-0009 — Definition of Done・Project初期化・Template Repository最終統合

## 0. Role

あなたはこのRepositoryの **Builder** です。

本Taskは、これまでDEV-TASK-0001〜0008で構築してきた
Planner / Builder型 AI Development Standard の**最終統合Task**です。

目的は、PB-Devを単なる開発途中のRepositoryではなく、

- 新規製品開発
- 既存製品の分析・アップデート
- Planner AI変更
- Builder AI変更
- Session変更
- PC変更

に再利用できる**標準Template Repository**として完成させることです。

人間判断が不要な限り、

```text
Task Intake
→ 全SSOT監査
→ Definition of Done整備
→ Project Identity / 初期化設計
→ 新規 / 既存Product開始標準
→ Template向け整理
→ Cross-document contradiction audit
→ Cold Start / Initialization test
→ Task完了処理
→ commit / push
→ Handoff生成・検証
→ 最終報告
```

まで自律的に完了してください。

---

# 1. Current Standard to Preserve

これまで確立済みの以下を後退させないこと。

## Roles

```text
Planner
= Browser AI
= 計画・仕様判断・Task作成・Builder成果物レビュー

Builder
= VSCode + CLI AI
= Repositoryを直接操作する実行役
```

特定AIサービス名には依存しない。

---

## Repository is SSOT

```text
Chat / AI Session
= 一時的な作業場所

Repository
= 永続的な記憶・仕様・履歴
```

---

## Autonomous Builder

人間判断が不要なTask内作業では、
Builderは途中確認せず完了まで進める。

---

## Task Lifecycle

```text
Planner Task
↓
Builder Intake
↓
tasks/active/
↓
TASK_REGISTER = ACTIVE
↓
実装 / Verification
↓
tasks/completed/
↓
TASK_REGISTER = COMPLETED
↓
commit / push
↓
受け渡し/
↓
Planner Review
```

原則One Active Task。

---

## Review Gate

Planner Review結果：

```text
ACCEPTED
CHANGES_REQUIRED
HUMAN_DECISION_REQUIRED
```

BuilderはReview前に未発行の次Taskへ進まない。

---

## Review Evidence

- Builder Verificationは最終成果物に対して行われていればHandoff前でも有効
- Human / External ValidationはHandoff Generation Boundary単位
- 古い人間検証は新Handoffへ自動持ち越ししない
- 人間の明示指示がある場合のみCarry-over可能

---

## GitHub

現在PB-Dev自体のCanonical Repository：

```text
https://github.com/h-shojaku/PB-Dev.git
```

Remote：

```text
origin
```

Branch：

```text
main
```

---

## Handoff

```text
受け渡し/
└── 最新の <TASK-ID>_PLANNER_HANDOFF.zip 1個のみ
```

- 500MB以内
- Git追跡対象外
- portable ZIP
- 標準Generator使用
- Verification必須
- Planner Continuity Packageとして機能
- Builder最終回答最後に絶対パスを表示

---

## Continuity

```text
CURRENT_STATE.md
tasks/TASK_REGISTER.md
SESSION_RULES.md
最新Handoff ZIP
```

から状態復元する。

AI内部記憶や過去チャットへの依存は禁止。

---

# 2. Objective

以下を完成させる。

1. 標準Definition of DoneをSSOT化
2. PB-Dev固有情報とTemplate共通ルールを分離
3. Project identityを1箇所に集約
4. Template複製後のProject初期化手順を定義
5. `NEW_PRODUCT` 開始フローを定義
6. `EXISTING_PRODUCT` 分析・Update開始フローを定義
7. ProductごとのTask Prefixを初期化可能にする
8. 派生RepositoryでPB-Devへ誤pushしない仕組み・確認を定義
9. Product SSOTの標準初期構造を用意
10. 既存製品Baseline Analysisの標準入口を用意
11. CURRENT_STATEのGit情報表現を自己矛盾しない形へ整理
12. Development SSOT全体の矛盾・重複・壊れたリンクを監査
13. AI Adapterを薄い入口として最終確認
14. Template複製後を想定したInitialization Dry Runを実施
15. 新Builder Cold Startを再検証
16. 新Planner Recoveryを再検証
17. 本Task完了後、PB-Devを再利用可能なTemplate基盤として完成状態にする

---

# 3. Files to Create / Update

最低限以下を整備してください。

```text
PROJECT_PROFILE.md

docs/development/
├── DEVELOPMENT_SYSTEM.md
├── DEFINITION_OF_DONE.md
└── PROJECT_INITIALIZATION_RULES.md

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

必要に応じて以下も最小限更新する。

```text
README.md
CURRENT_STATE.md
AGENTS.md
CLAUDE.md
GEMINI.md
.gitignore

docs/development/
├── README.md
├── BUILDER_RULES.md
├── DECISION_RULES.md
├── TASK_RULES.md
├── REVIEW_RULES.md
├── SESSION_RULES.md
├── GIT_RULES.md
└── HANDOFF_RULES.md

tasks/
├── README.md
└── TASK_REGISTER.md

templates/
├── README.md
├── TASK_TEMPLATE.md
├── PLANNER_REPORT_TEMPLATE.md
├── SESSION_HANDOFF_TEMPLATE.md
└── PLANNER_SESSION_HANDOFF_TEMPLATE.md

scripts/
├── create_handoff.py
├── create_handoff.ps1
└── README.md
```

過剰な重複SSOTを作らない。

---

# 4. PROJECT_PROFILE.md

Repository rootに以下を作成する。

```text
PROJECT_PROFILE.md
```

目的：

**Product / Repository固有のidentityを1箇所に集約する。**

Development Standard本文へ、

```text
PB-Dev
DEV
https://github.com/h-shojaku/PB-Dev.git
```

等を大量にハードコードし続けない。

---

## 4.1 PB-Dev Profile

PB-Dev自身では最低限以下を定義する。

```text
Project Name: PB-Dev
Project Mode: TEMPLATE
Task Prefix: DEV
Canonical Remote: https://github.com/h-shojaku/PB-Dev.git
Default Branch: main
Development Standard: Planner / Builder AI Development Standard
```

---

## 4.2 Project Mode

標準Project Modeは最低限以下。

```text
TEMPLATE
NEW_PRODUCT
EXISTING_PRODUCT
```

### TEMPLATE

PB-Dev本体など、
再利用元となる開発標準Repository。

### NEW_PRODUCT

新規製品をゼロから開始するRepository。

### EXISTING_PRODUCT

既存製品を取り込み、
現状分析・仕様復元・改善・Updateを行うRepository。

---

## 4.3 Task Prefix

Projectごとに、

```text
Task Prefix
```

をProfileで定義する。

例：

```text
SE
E6
APP
```

Task IDは既存標準どおり、

```text
<PREFIX>-TASK-XXXX
```

とする。

Development Standard本文側では、
PB-Devの `DEV` を例として扱うことは可。

ただし共通ルールとして固定しない。

---

# 5. PROJECT_PROFILE_TEMPLATE.md

以下を作成。

```text
templates/PROJECT_PROFILE_TEMPLATE.md
```

最低限：

```text
# Project Profile

## Project Identity
- Project Name:
- Project Mode:
- Task Prefix:

## Repository
- Canonical Remote:
- Default Branch:

## Product
- Product SSOT Root: docs/product/

## Development Standard
- Source Template: PB-Dev
- Planner Role: Browser AI
- Builder Role: VSCode + CLI AI

## Initialization
- Initialized At:
- Initialized By Task:
```

---

# 6. Generic Development SSOT

Development SSOT内のProject固有値は、
可能な限り `PROJECT_PROFILE.md` 参照へ置換する。

例えば `GIT_RULES.md` では、

誤：

```text
Canonical Remoteは常に
https://github.com/h-shojaku/PB-Dev.git
```

正：

```text
Canonical RemoteはPROJECT_PROFILE.mdを正とする。
PB-Dev本体では https://github.com/h-shojaku/PB-Dev.git。
```

同様にTask PrefixもProfileを参照する。

---

# 7. Important Git Safety for Derived Repositories

Templateを複製してProduct Repositoryを作る際、
誤ってPB-Devへpushしないことを最重要Safety Ruleとする。

派生Repository初期化時には必ず、

```text
git remote -v
```

を確認する。

期待値：

```text
origin = PROJECT_PROFILE.md の Canonical Remote
```

不一致の場合は、
通常開発Task開始前に修正またはHuman Decisionを要求する。

---

## 7.1 Never Assume PB-Dev Remote in Product Repositories

`NEW_PRODUCT` / `EXISTING_PRODUCT` では、

```text
https://github.com/h-shojaku/PB-Dev.git
```

をoriginとして開発を続行してはいけない。

PB-DevはTemplate sourceであり、
派生Productの正式Remoteではない。

---

# 8. PROJECT_INITIALIZATION_RULES.md

以下を作成。

```text
docs/development/PROJECT_INITIALIZATION_RULES.md
```

最低限以下を定義する。

```text
## Purpose
## Preconditions
## Project Identity Initialization
## Remote Safety Check
## Task Prefix Initialization
## Runtime State Reset
## NEW_PRODUCT Initialization
## EXISTING_PRODUCT Initialization
## Product SSOT Initialization
## First Planner Task
## First Builder Intake
## Initialization Verification
```

---

# 9. Template Duplication Principle

PB-Devを複製した直後は、
**まだProduct開発を開始しない**。

最初にProject Initializationを実施する。

概念：

```text
PB-Dev Template
↓
新Repository作成 / clone
↓
Project Initialization
↓
PROJECT_PROFILE確定
↓
Remote確認
↓
Task Prefix確定
↓
Runtime State初期化
↓
Product mode固有初期化
↓
最初のPlanner Task
↓
通常Task Lifecycle開始
```

---

# 10. Runtime State Reset

Templateから派生したProjectでは、
PB-Dev自身の構築Task履歴を
ProductのTask履歴として扱わない。

初期化時に以下のRuntime stateを
Project用へ初期化するルールを定義する。

```text
CURRENT_STATE.md
tasks/TASK_REGISTER.md
tasks/active/
tasks/completed/
受け渡し/
```

---

## 10.1 Important History Principle

Git historyそのものを破壊してはいけない。

PB-Dev由来のファイル履歴がGitに存在することは問題ない。

ただしProductのRuntime Task Registerへ、

```text
DEV-TASK-0001
...
DEV-TASK-0009
```

をProduct Taskとして残さない。

派生ProjectではTask番号を、

```text
<PREFIX>-TASK-0001
```

から開始できる状態にする。

---

# 11. `受け渡し/` at Initialization

`受け渡し/` はGit追跡対象外であるため、
clone / template生成直後に存在しなくても正常。

Project Initialization時に古いローカル配送物がある場合は削除。

通常Task Handoff時にBuilderが必要に応じて作成する。

---

# 12. NEW_PRODUCT Initialization

Project Mode：

```text
NEW_PRODUCT
```

では最低限以下を行う。

1. `PROJECT_PROFILE.md` 確定
2. Product Task Prefix確定
3. Canonical Remote確認
4. Runtime state reset
5. `docs/product/` を初期化
6. Product SSOTテンプレートを配置
7. `CURRENT_STATE = IDLE`
8. Plannerが最初のProduct Planning Taskを作成
9. BuilderはTask受領まで勝手に製品仕様を決めない

---

# 13. Product SSOT Standard Structure

NEW_PRODUCTの標準初期構造：

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

## 13.1 Meaning

### 00_PRODUCT_OVERVIEW.md

製品の概要・目的・対象ユーザー・価値。

### 01_PRODUCT_PLAN.md

Product計画・Scope・Roadmap等。

### 02_REQUIREMENTS.md

機能要件・非機能要件・制約。

### 03_UI_STRUCTURE.md

画面構造・UI・状態・ナビゲーション。

UIを持たないProductでは適用範囲を明示して簡略化可。

### 04_IMPLEMENTATION_SPEC.md

Builderが実装時に参照する技術・実装仕様SSOT。

### 05_OPERATION_RULES.md

運用・保守・Release後のProduct固有ルール。

---

## 13.2 Template Content

各Templateは、
特定Productの仕様を勝手に埋めない。

Section structureと記入ガイドのみ提供する。

---

# 14. EXISTING_PRODUCT Initialization

Project Mode：

```text
EXISTING_PRODUCT
```

では、
既存コードをいきなり大規模変更しない。

標準開始フロー：

```text
既存Product取り込み / clone
↓
Development Standard導入
↓
PROJECT_PROFILE確定
↓
Remote / Branch確認
↓
既存コード保全
↓
Baseline Analysis Task
↓
現状仕様・Architecture・Issue把握
↓
Product SSOT初期化 / 復元
↓
Planner Review
↓
改善 / Update Task
```

---

# 15. Existing Product Safety

初期分析前にBuilderが勝手に、

- 大規模refactor
- Dependency総入替
- Architecture全面変更
- UI全面刷新
- Product仕様変更

を行ってはいけない。

まず分析し、PlannerがUpdate方針を決める。

---

# 16. EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md

以下を作成する。

```text
templates/product/EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md
```

最低限：

```text
# Existing Product Baseline Analysis

## Repository Overview
## Product Purpose
## Current User-facing Behavior
## Architecture
## Main Components
## Data / Persistence
## External Dependencies
## Build / Test Status
## Known Issues
## Documentation Gaps
## Security / Secret Risks
## Product SSOT Recovery Status
## Recommended Planner Decisions
## Recommended Next Task
```

分析結果の標準配置候補：

```text
reports/analysis/
```

必要に応じてDirectory structureを整備する。

---

# 17. Existing Product Product SSOT Recovery

既存製品では、
既存READMEやコードから推測した内容を
直ちに正式Product SSOTと断定しない。

区別：

```text
Observed
Inferred
Confirmed
Unknown
```

を分析時に利用できるようにする。

Planner / 人間が確認した内容を、
後続Taskで正式Product SSOTへ反映する。

---

# 18. Definition of Done

以下を作成。

```text
docs/development/DEFINITION_OF_DONE.md
```

Task完了の共通最小条件を定義する。

Task固有Acceptance Criteriaを置き換えず、
**すべてのTaskに共通する最低条件**とする。

---

# 19. Standard Task Definition of Done

人間判断による例外またはBLOCKがない通常Taskは、
最低限以下をすべて満たして初めて `COMPLETE` とする。

## Instruction / Scope

- [ ] 正しいActive Taskを実行した
- [ ] Task Instructionを独断で変更していない
- [ ] Task scope外の重大変更を行っていない

## Implementation

- [ ] Objectiveを満たした
- [ ] Acceptance Criteriaを満たした
- [ ] 必要なSSOTを更新した
- [ ] 意図しない変更を残していない

## Verification

- [ ] Taskに必要なtest / build / lint / checkを実行
- [ ] 失敗を成功扱いにしていない
- [ ] `git diff --check` PASS
- [ ] 必要なBuilder Verification EvidenceをREPORTへ記録

## Task State

- [ ] `tasks/active/` からTaskを完了処理
- [ ] `tasks/completed/<TASK-ID>.md` が存在
- [ ] `TASK_REGISTER.md = COMPLETED`
- [ ] `CURRENT_STATE.md = AWAITING_PLANNER_REVIEW`

## Git

- [ ] Task関連変更をcommit
- [ ] commit messageからTask IDを追跡可能
- [ ] `origin` とProject Profileが一致
- [ ] 標準Branchへpush済み
- [ ] tracked working tree clean

## Handoff

- [ ] `受け渡し/` に最新ZIP 1個のみ
- [ ] 500MB以内
- [ ] 標準Generator使用
- [ ] archive verification PASS
- [ ] portable path verification PASS
- [ ] REPORT / MANIFEST / Continuity filesを含む

## Final Response

- [ ] Statusを明示
- [ ] Git状態を明示
- [ ] Human Decision有無を明示
- [ ] Handoff ZIPの絶対パスを明示
- [ ] 最終行が
      `これをPlannerに渡してください: <absolute path>`
      で終了

---

# 20. BLOCKED Definition

人間判断が必要でTaskを完了できない場合は、
無理にDoDを満たしたことにしない。

Status：

```text
BLOCKED
```

とし、

- 完了済み範囲
- 未完了範囲
- Human Decision
- Git状態
- Handoff

を明示する。

DoD未達を隠して `COMPLETE` と報告しない。

---

# 21. DoD Precedence

優先関係：

```text
Task-specific Acceptance Criteria
+
Development Standard Definition of Done
```

両方を満たす必要がある。

矛盾する場合はRule Precedenceに従う。

---

# 22. CURRENT_STATE Git Information Cleanup

DEV-TASK-0008で `CURRENT_STATE.md` に

```text
## Current Branch / Commit
```

というSectionがある一方、
Snapshot自身がcommit内容に含まれるため
「常に自身の最終commit hashを埋め込む」設計は自己参照問題を起こす。

この点を最終整理してください。

推奨：

```text
## Git State
- Branch: main
- Working Tree at Last Update: Clean
- Current commit: resolve live with `git rev-parse HEAD`
```

または同等の、
**stale hashをSSOTとして固定しない設計**とする。

正確なHEADはCold Start時にGitから取得する。

REPORT / MANIFESTには生成時点の確定commit hashを記録してよい。

---

# 23. Final Development SSOT Audit

以下をRepository-wideに監査する。

## 23.1 Hardcoded Project Identity

検索：

```text
PB-Dev
DEV-TASK
https://github.com/h-shojaku/PB-Dev.git
```

共通Development Standard本文で、
PB-Dev固有値が不要に固定されていないか確認。

例示・PB-Dev Profileとして必要な箇所は可。

---

## 23.2 Legacy Handoff Paths

検索：

```text
handoff/planner
handoff/
```

過去Completed Task Instruction Record以外の
現行SSOT / Templateに旧運用が残っていないこと。

---

## 23.3 Non-portable Links

検索：

```text
file:///
C:\Users\
/Users/
```

現行SSOT・Adapter・Templateの内部リンクに
ローカル絶対pathが残っていないこと。

REPORT / MANIFEST等の実行時絶対パスは除外。

---

## 23.4 Rule Contradictions

最低限以下の整合を確認。

```text
DEVELOPMENT_SYSTEM
BUILDER_RULES
DECISION_RULES
TASK_RULES
REVIEW_RULES
SESSION_RULES
GIT_RULES
HANDOFF_RULES
DEFINITION_OF_DONE
PROJECT_INITIALIZATION_RULES
```

特に：

- 自律進行 vs Review Gate
- Task Completed timing vs Handoff timing
- Git commit / push timing
- CURRENT_STATE timing
- Human Decision / BLOCKED
- Handoff Generation
- Planner Review
- Session Recovery
- Project Profile / Remote

を確認。

---

# 24. AI Adapter Final Audit

以下は薄いAdapterのままにする。

```text
AGENTS.md
CLAUDE.md
GEMINI.md
```

必要な入口：

```text
DEVELOPMENT_SYSTEM.md
PROJECT_PROFILE.md
CURRENT_STATE.md
TASK_REGISTER.md
```

へ辿れるようにする。

共通ルール本文を大量コピーしない。

---

# 25. README Finalization

Repository root READMEは、
初見の人間にもAIにも以下が分かる状態にする。

1. PB-Devが何か
2. Planner / Builderとは何か
3. どこがSSOTか
4. Current Stateはどこか
5. Taskはどこか
6. Handoffはどこか
7. Templateから新Projectを始める入口
8. GitHub管理方針

README自体を巨大な運用SSOTにしない。

詳細文書へリンクする。

---

# 26. Template Repository Usage Guide

READMEまたは
`PROJECT_INITIALIZATION_RULES.md` に、
Template利用時の人間側操作を簡潔に記載する。

例：

```text
1. PB-Devを新Repositoryへ複製
2. RepositoryをVSCodeで開く
3. Builder AIを起動
4. Project初期化Taskを渡す
5. PROJECT_PROFILEを確定
6. Remote安全確認
7. NEW_PRODUCT / EXISTING_PRODUCT初期化
8. Plannerが最初のProduct Taskを発行
```

特定AIサービス名に依存しない。

---

# 27. Initialization Task Pattern

Template複製後に最初にPlannerがBuilderへ渡すTaskの
標準目的を文書化する。

例：

```text
<PREFIX>-TASK-0001
Project Initialization
```

ただし、
Prefix未確定の段階では一時的なInitialization Task名を使う必要があるため、
その扱いはBuilderが矛盾なく設計してください。

よりシンプルなら、
Project初期化だけは `INIT.md` 等のReserved Bootstrap Taskとして定義してもよい。

### Requirement

「Prefixを決める前にPrefix付きTask IDが必要」
という循環依存を残さないこと。

---

# 28. Initialization Script

Project初期化を安全に簡略化できる場合、
以下のような標準Scriptを追加してよい。

```text
scripts/initialize_project.py
```

ただし必須条件：

- Python標準ライブラリ中心
- Product固有値をハードコードしない
- destructive operation前に対象を検証
- `.git` historyを削除しない
- source codeを削除しない
- PB-Dev originへ誤pushしない
- dry-runまたは同等の安全確認が可能
- NEW_PRODUCT / EXISTING_PRODUCTを区別可能
- Task runtime stateだけを安全にreset

実装が過剰になる場合は、
本Taskでは手順SSOTとTemplateだけでも可。

**開発体験の標準化に明確な価値がある場合のみ実装する。**

---

# 29. Initialization Dry Run

本Taskでは、
実Repositoryを壊さずTemporary Directory等を使い、

```text
PB-DevをTemplateとして複製した直後
```

を想定したDry Run / Simulationを行ってください。

最低限2ケース。

---

## 29.1 NEW_PRODUCT Test

確認：

```text
Project Mode = NEW_PRODUCT
Task Prefixを設定可能
Canonical RemoteをProduct用に変更可能
Runtime Task historyをProduct用にreset可能
Product SSOT初期構造を作成可能
CURRENT_STATE = IDLE
PB-Devへ誤pushする状態でない
```

---

## 29.2 EXISTING_PRODUCT Test

確認：

```text
Project Mode = EXISTING_PRODUCT
既存sourceを削除しない
Baseline Analysis開始導線がある
Product SSOTを未確認推測で確定しない
CURRENT_STATE = IDLE または初期分析待ち
PB-Devへ誤pushする状態でない
```

---

# 30. Cold Start Final Test

最終Repository状態について、
過去チャットを知らないBuilderを想定する。

以下から現在状態を一意に復元できること。

```text
README.md
PROJECT_PROFILE.md
AGENTS.md
docs/development/DEVELOPMENT_SYSTEM.md
CURRENT_STATE.md
tasks/TASK_REGISTER.md
Git state
```

本Task完了後の期待：

```text
Project Mode = TEMPLATE
Workflow Phase = AWAITING_PLANNER_REVIEW
Current Task = None
Latest Completed Task = DEV-TASK-0009
Human Decision = None
Next Action = Planner Review
```

---

# 31. Planner Recovery Final Test

最終Handoff ZIPだけを新Plannerへ渡した状態で、
最低限以下が分かること。

```text
PB-Devの目的
今回Task
最終統合内容
Review対象
Git状態
Human Decision有無
現在9 Taskまで完了したこと
次のActionがPlanner Reviewであること
```

---

# 32. PB-Dev Task History

PB-Dev自身のDEV-TASK-0001〜0009履歴は、
PB-Devの開発標準構築履歴として保持してよい。

ただし派生Product初期化時は、
Product Task Registerへ引き継がない標準とする。

過去Task Instruction Recordを改変しない。

---

# 33. GitHub Template Readiness

本TaskではRepository内容を、
GitHubのTemplate Repositoryとして利用しても破綻しない状態へする。

確認事項：

- Project固有値の集約
- 派生Remote Safety
- Runtime State Reset手順
- Product Prefix初期化
- Product SSOT初期化
- AI Adapter portability
- Handoff portability
- Session portability

GitHub側の「Template repository」設定自体を変更する操作は、
既存認証・権限があり、安全かつ明確に実行可能な場合のみ行ってよい。

実行した場合はREPORTに明記する。

認証や権限がない場合、
Repository内容のTemplate Readinessを完成させるだけでよい。
それをBLOCK理由にしない。

---

# 34. Final Documentation Index

`docs/development/README.md` を最終目次として整理する。

最低限以下へ辿れること。

```text
DEVELOPMENT_SYSTEM.md
BUILDER_RULES.md
DECISION_RULES.md
TASK_RULES.md
REVIEW_RULES.md
SESSION_RULES.md
GIT_RULES.md
HANDOFF_RULES.md
DEFINITION_OF_DONE.md
PROJECT_INITIALIZATION_RULES.md
```

各文書の役割を1〜2行で記載。

---

# 35. Final Repository Shape

最終的に概ね以下となること。

```text
/
├── README.md
├── PROJECT_PROFILE.md
├── CURRENT_STATE.md
├── AGENTS.md
├── CLAUDE.md
├── GEMINI.md
├── .gitignore
│
├── docs/
│   ├── development/
│   │   ├── README.md
│   │   ├── DEVELOPMENT_SYSTEM.md
│   │   ├── BUILDER_RULES.md
│   │   ├── DECISION_RULES.md
│   │   ├── TASK_RULES.md
│   │   ├── REVIEW_RULES.md
│   │   ├── SESSION_RULES.md
│   │   ├── GIT_RULES.md
│   │   ├── HANDOFF_RULES.md
│   │   ├── DEFINITION_OF_DONE.md
│   │   └── PROJECT_INITIALIZATION_RULES.md
│   │
│   └── product/
│
├── tasks/
│   ├── README.md
│   ├── TASK_REGISTER.md
│   ├── active/
│   └── completed/
│
├── reports/
│   └── analysis/
│
├── templates/
│   ├── README.md
│   ├── PROJECT_PROFILE_TEMPLATE.md
│   ├── TASK_TEMPLATE.md
│   ├── PLANNER_REPORT_TEMPLATE.md
│   ├── SESSION_HANDOFF_TEMPLATE.md
│   ├── PLANNER_SESSION_HANDOFF_TEMPLATE.md
│   └── product/
│       ├── 00_PRODUCT_OVERVIEW.md
│       ├── 01_PRODUCT_PLAN.md
│       ├── 02_REQUIREMENTS.md
│       ├── 03_UI_STRUCTURE.md
│       ├── 04_IMPLEMENTATION_SPEC.md
│       ├── 05_OPERATION_RULES.md
│       └── EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md
│
├── scripts/
│   ├── README.md
│   ├── create_handoff.py
│   └── create_handoff.ps1
│
└── 受け渡し/
    └── DEV-TASK-0009_PLANNER_HANDOFF.zip
```

`受け渡し/` はGit追跡対象外なので、
GitHub上で空Directoryとして存在する必要はない。

---

# 36. Task Lifecycle

DEV-TASK-0009も正式Lifecycleに従う。

```text
Task Intake
↓
tasks/active/DEV-TASK-0009.md
↓
TASK_REGISTER = ACTIVE
↓
CURRENT_STATE = ACTIVE
↓
Intake commit / push
↓
実装 / Audit / Test
↓
tasks/completed/DEV-TASK-0009.md
↓
TASK_REGISTER = COMPLETED
↓
CURRENT_STATE = AWAITING_PLANNER_REVIEW
↓
Final commit / push
↓
Handoff Generator
↓
Final Verification
```

---

# 37. Git / GitHub

PB-Dev本体：

```text
Canonical Repository:
https://github.com/h-shojaku/PB-Dev.git

Remote:
origin

Branch:
main
```

Task関連commitには `DEV-TASK-0009` を含める。

例：

```text
DEV-TASK-0009: register task
DEV-TASK-0009: finalize reusable development template
```

---

# 38. Verification

最低限以下を確認する。

## Definition of Done

- [ ] `DEFINITION_OF_DONE.md` が存在
- [ ] Task固有Acceptance Criteriaとの関係が明確
- [ ] COMPLETE / BLOCKEDの違いが明確
- [ ] Git / Handoff / Final ResponseまでDoDに含まれる

## Project Identity

- [ ] `PROJECT_PROFILE.md` が存在
- [ ] PB-Dev固有identityがそこへ集約されている
- [ ] Project Modeが定義されている
- [ ] Task PrefixがProjectごとに設定可能
- [ ] Canonical RemoteがProfileで確認可能

## Initialization

- [ ] `PROJECT_INITIALIZATION_RULES.md` が存在
- [ ] NEW_PRODUCTフローがある
- [ ] EXISTING_PRODUCTフローがある
- [ ] Prefix確定前Taskの循環依存が解決されている
- [ ] Product runtime state reset方法がある
- [ ] PB-DevのDEV Task履歴をProduct Registerへ持ち込まない
- [ ] Remote Safety Checkがある
- [ ] NEW_PRODUCT Dry Run PASS
- [ ] EXISTING_PRODUCT Dry Run PASS

## Product SSOT

- [ ] Product SSOT Template 00〜05が存在
- [ ] 特定Product仕様がハードコードされていない
- [ ] Existing Product Analysis Templateが存在
- [ ] Observed / Inferred / Confirmed / Unknownの扱いがある

## Portability

- [ ] 現行SSOTに旧 `handoff/planner` がない
- [ ] 現行SSOT内部リンクに`file:///`がない
- [ ] 個人PC絶対pathが現行Templateにない
- [ ] AI Adapterがthin
- [ ] Handoff Generator self-test PASS
- [ ] Handoff portable verification PASS

## Consistency

- [ ] Development SSOT間に重大矛盾なし
- [ ] Current State / Task Register / Git workflowが整合
- [ ] Review Gate / Autonomous Builderが整合
- [ ] Session Recovery / BLOCKEDが整合
- [ ] Project Profile / Git Remote規則が整合
- [ ] CURRENT_STATEのcommit表現が自己参照矛盾を起こさない

## Git

- [ ] `git diff --check` PASS
- [ ] originがPB-Dev Profileと一致
- [ ] branch = main
- [ ] Final commit / push成功
- [ ] tracked working tree clean

## Recovery

- [ ] Final Builder Cold Start Test PASS
- [ ] Final Planner Recovery Test PASS

---

# 39. Handoff

Planner提出物は必ず、

```text
受け渡し/DEV-TASK-0009_PLANNER_HANDOFF.zip
```

1個のみ。

500MB以内。

標準Generatorを使用し、
すべてのarchive verificationをPASSさせる。

最低限以下を含める。

```text
DEV-TASK-0009_PLANNER_HANDOFF.zip
├── REPORT.md
├── MANIFEST.md
└── files/
    ├── README.md
    ├── PROJECT_PROFILE.md
    ├── CURRENT_STATE.md
    ├── tasks/
    │   ├── TASK_REGISTER.md
    │   └── completed/
    │       └── DEV-TASK-0009.md
    ├── docs/
    │   └── development/
    │       ├── README.md
    │       ├── DEVELOPMENT_SYSTEM.md
    │       ├── DEFINITION_OF_DONE.md
    │       ├── PROJECT_INITIALIZATION_RULES.md
    │       ├── BUILDER_RULES.md
    │       ├── DECISION_RULES.md
    │       ├── TASK_RULES.md
    │       ├── REVIEW_RULES.md
    │       ├── SESSION_RULES.md
    │       ├── GIT_RULES.md
    │       └── HANDOFF_RULES.md
    └── templates/
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

実際に追加・変更したscript等もPlanner Reviewに必要なら含める。

---

# 40. REPORT.md Additional Sections

REPORTには最低限以下を追加する。

```text
## Final Standardization Summary
## Definition of Done
## Project Identity / Template Portability
## NEW_PRODUCT Initialization Test
## EXISTING_PRODUCT Initialization Test
## Development SSOT Consistency Audit
## Final Builder Cold Start Test
## Final Planner Recovery Test
## GitHub Template Readiness
```

---

# 41. Development SSOT Consistency Audit Report

REPORTに、
各SSOTについて最低限、

```text
File
Role
Contradiction found
Action
Result
```

が分かる簡潔なAudit結果を含める。

対象：

```text
DEVELOPMENT_SYSTEM.md
BUILDER_RULES.md
DECISION_RULES.md
TASK_RULES.md
REVIEW_RULES.md
SESSION_RULES.md
GIT_RULES.md
HANDOFF_RULES.md
DEFINITION_OF_DONE.md
PROJECT_INITIALIZATION_RULES.md
```

---

# 42. Builder Final Response

既存標準に従う。

最低限：

```text
Task: DEV-TASK-0009
Status: COMPLETE / BLOCKED

実施内容:
- ...

Final Standard:
- Definition of Done: ...
- Project Profile: ...
- NEW_PRODUCT test: PASS / FAIL
- EXISTING_PRODUCT test: PASS / FAIL
- SSOT consistency audit: PASS / FAIL
- Builder Cold Start: PASS / FAIL
- Planner Recovery: PASS / FAIL

Task Lifecycle:
- Intake commit: ...
- Final commit: ...
- Register: ...
- Workflow Phase: ...

Git:
- Remote: ...
- Branch: ...
- Push: ...
- Working tree: ...

人間判断:
- 不要
または
- 必要: ...

これをPlannerに渡してください: <実際の絶対パス>\受け渡し\DEV-TASK-0009_PLANNER_HANDOFF.zip
```

**最後の1文より後には何も記載しないこと。**

---

# 43. Acceptance Criteria

以下をすべて満たせばCOMPLETE。

- [ ] Planner / Builder AI Development Standardの最終構造が完成
- [ ] `DEFINITION_OF_DONE.md` が正式SSOTとして存在
- [ ] `PROJECT_PROFILE.md` が存在
- [ ] Project固有値がDevelopment共通ルールから適切に分離
- [ ] TEMPLATE / NEW_PRODUCT / EXISTING_PRODUCTが定義
- [ ] ProjectごとにTask Prefixを設定可能
- [ ] ProductごとのCanonical Remoteを安全に管理可能
- [ ] PB-Dev誤push防止ルールが存在
- [ ] Template複製後のRuntime State Resetが定義
- [ ] PB-DevのDEV Task履歴をProduct Task Registerへ持ち込まない
- [ ] NEW_PRODUCT初期化フローが完成
- [ ] EXISTING_PRODUCT分析・Update開始フローが完成
- [ ] Product SSOT 00〜05 Templateが存在
- [ ] Existing Product Baseline Analysis Templateが存在
- [ ] Prefix決定前Initializationの循環依存が解消
- [ ] CURRENT_STATEのGit表現が自己矛盾しない
- [ ] 全Development SSOTの整合監査PASS
- [ ] AI Adapter thinness確認
- [ ] 現行SSOTに旧Handoff pathなし
- [ ] 現行内部リンクにローカル依存なし
- [ ] NEW_PRODUCT Initialization Test PASS
- [ ] EXISTING_PRODUCT Initialization Test PASS
- [ ] Final Builder Cold Start Test PASS
- [ ] Final Planner Recovery Test PASS
- [ ] Handoff Generator self-test PASS
- [ ] GitHub commit / push完了
- [ ] tracked working tree clean
- [ ] `受け渡し/` にDEV-TASK-0009 ZIP 1個のみ
- [ ] Handoff portable verification PASS
- [ ] Builder最終回答がZIP絶対パス案内で終了

---

# 44. Final Goal

本Task完了後のPB-Devは、

**「どの製品でも、どのPlanner AIでも、どのBuilder CLI AIでも、
同じTask・Git・Handoff・Review・Session Recovery体験で開発を開始できる再利用可能な標準Repository」**

であること。

このTaskでは新しいProductを実際に開発しない。

AI Development StandardとTemplateとしての完成に集中してください。
