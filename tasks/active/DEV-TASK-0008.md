# DEV-TASK-0008 — AI / Session切替・状態復元・Continuity標準化

## 0. Role

あなたはこのRepositoryの **Builder** です。

本Taskでは、Planner / BuilderのAIサービス変更、セッション切替、CLI再起動、
PC変更、作業中断などが発生しても、過去チャットやAI内部記憶に依存せず
Repositoryから安全に開発状態を復元できる **Continuity / Recovery標準** を整備してください。

対象は特定AIサービスに限定しません。

```text
Planner
= Browser AI

Builder
= VSCode + CLI AI
```

という役割は維持しつつ、

```text
ChatGPT
Claude
Gemini
Codex
その他将来のAI
```

へ切り替えても運用を継続できることを目標とします。

人間判断が不要な限り、途中確認で停止せず、

```text
Task Intake
→ 現行SSOT調査
→ Continuity設計
→ Repository実装
→ Recovery検証
→ Task完了処理
→ commit / push
→ Handoff生成・検証
→ 最終回答
```

まで自律的に進めてください。

---

# 1. Current Standard to Preserve

以下はすでに確立済みです。

## Repository is SSOT

```text
Chat / AI Session
= 一時的な作業場所

Repository
= 永続的な記憶・仕様・履歴
```

## Roles

```text
Planner
= Browser AI
= 計画・仕様判断・Task作成・Builder成果物レビュー

Builder
= VSCode + CLI AI
= Repositoryを直接操作する実行役
```

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
実行
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

## One Active Task

通常はBuilderが同時に扱うTaskは1件のみ。

## GitHub

```text
Canonical Repository:
https://github.com/h-shojaku/PB-Dev.git

Remote:
origin

Branch:
main
```

## Handoff

```text
受け渡し/
└── 最新の <TASK-ID>_PLANNER_HANDOFF.zip 1個のみ
```

- 500MB以内
- Git追跡対象外
- portable ZIP
- 標準Generator使用
- 自動Verification必須

## Review Evidence

- Builder Verificationは最終成果物に対して行われていればHandoff前でも有効
- Human / External ValidationはHandoff世代単位
- 古い人間検証は新Handoffへ自動持ち越ししない

これらを後退させないこと。

---

# 2. Objective

本Taskでは以下を標準化してください。

1. 新しいBuilder AI / CLI SessionがRepositoryから現在状態を復元する方法
2. 新しいPlanner AI / Browser Sessionへ引き継ぐ方法
3. AIサービス変更時もPlanner / Builderの役割を維持するルール
4. Repository内の「現在状態」を1箇所から確認できる仕組み
5. 意図的なBuilder Session切替前のCheckpoint方法
6. 予期しないSession切断・PC再起動後のRecovery方法
7. Active Task途中から安全に再開する方法
8. BLOCKED Taskを勝手に再開しないルール
9. Active Taskがない状態でBuilderが勝手に次Taskを作らないルール
10. Planner Session切替時に必要な最小Context Package
11. Plannerで未永続化の判断をRepository SSOTと混同しないルール
12. Handoff ZIPにContinuity情報を含める標準
13. AI内部記憶・チャット履歴への依存禁止
14. secrets / credentials / private chain-of-thoughtを引き継ぎ文書へ保存しない
15. Cold Start / Recovery Testを実施する

---

# 3. Files to Create / Update

最低限以下を整備してください。

```text
CURRENT_STATE.md

docs/development/
├── DEVELOPMENT_SYSTEM.md
└── SESSION_RULES.md

templates/
├── SESSION_HANDOFF_TEMPLATE.md
└── PLANNER_SESSION_HANDOFF_TEMPLATE.md
```

必要に応じて以下を最小限更新してください。

```text
README.md
AGENTS.md
CLAUDE.md
GEMINI.md

docs/development/
├── BUILDER_RULES.md
├── TASK_RULES.md
├── REVIEW_RULES.md
├── HANDOFF_RULES.md
├── GIT_RULES.md
└── README.md

tasks/
├── README.md
└── TASK_REGISTER.md

templates/
├── README.md
├── TASK_TEMPLATE.md
└── PLANNER_REPORT_TEMPLATE.md

scripts/create_handoff.py
scripts/create_handoff.ps1
```

AI Adapterへルール本文を大量コピーしないこと。

---

# 4. CURRENT_STATE.md

Repository rootに以下を作成してください。

```text
CURRENT_STATE.md
```

これは製品仕様SSOTではなく、
**現在の開発運用状態を短時間で把握するためのCurrent State Index** とします。

---

## 4.1 Purpose

新しいAI / SessionがRepositoryを開いた際、

```text
「今どこまで進んでいるか」
「現在Taskは何か」
「次に何を読むべきか」
「人間判断待ちはあるか」
```

を最初の数分で把握できること。

---

## 4.2 Do Not Duplicate Product SSOT

`CURRENT_STATE.md` に製品仕様を大量コピーしない。

正：

```text
Current Task:
DEV-TASK-0008

Product SSOT:
docs/product/...

Relevant Development SSOT:
docs/development/SESSION_RULES.md
```

誤：

```text
Product Requirements全文をCURRENT_STATEへ複製
```

Current Stateは **Index / State Snapshot** とする。

---

## 4.3 Required Sections

最低限以下を含める。

```text
# Current State

## Repository
## Workflow Phase
## Current Task
## Latest Completed Task
## Current Branch / Commit
## Human Decision Status
## Known Blocking Issues
## Relevant SSOT
## Recovery Entry Point
## Last Updated
```

必要に応じて以下も可。

```text
## Latest Planner Handoff
## Next Expected Action
```

---

# 5. Workflow Phase

`CURRENT_STATE.md` 内のWorkflow Phaseは、
Task Statusと混同しない簡潔な運用状態として扱います。

最低限以下を利用可能とする。

```text
IDLE
ACTIVE
BLOCKED
AWAITING_PLANNER_REVIEW
```

意味：

### IDLE

```text
Active Taskなし
Plannerから次Task待ち
```

### ACTIVE

```text
Builderが現在Taskを実行中
```

### BLOCKED

```text
人間判断等でTask停止中
```

### AWAITING_PLANNER_REVIEW

```text
Builder実装・Handoff提出済み
Planner Review待ち
```

---

# 6. CURRENT_STATE Update Timing

CURRENT_STATEは最低限以下のタイミングでBuilderが更新する。

## Task Intake

```text
Workflow Phase = ACTIVE
Current Task = <TASK-ID>
Human Decision = None
```

## BLOCKED

```text
Workflow Phase = BLOCKED
Current Task = <TASK-ID>
Human Decision = Required
```

## Builder Completion / Handoff

```text
Workflow Phase = AWAITING_PLANNER_REVIEW
Current Task = None
Latest Completed Task = <TASK-ID>
Latest Planner Handoff = <TASK-ID>_PLANNER_HANDOFF.zip
```

---

# 7. Important Planner Review Limitation

PlannerはBrowser AIでありRepositoryを直接書き換えないことを前提とします。

したがって、

```text
PlannerがTaskをACCEPTED
```

した直後に、
Planner自身が `CURRENT_STATE.md` を直接更新することは標準としません。

次のBuilder Task Intake時に、
前TaskのPlanner Review結果を新Task Contextから確認し、
Repository状態へ反映します。

---

## 7.1 No False Persistence

Planner Browser Session内で決めただけで、
まだBuilderへ渡されておらずRepositoryへcommitされていない判断を、

```text
Repository SSOTに保存済み
```

と扱ってはいけません。

Repositoryへ永続化されるのは、
原則としてBuilderがTaskとしてIntakeしcommitした時点以降です。

---

# 8. SESSION_RULES.md

以下を作成してください。

```text
docs/development/SESSION_RULES.md
```

最低限以下を定義する。

```text
## Purpose
## AI Service Independence
## Builder Cold Start Protocol
## Builder Session Switch Protocol
## Unexpected Interruption Recovery
## Active Task Recovery
## BLOCKED Recovery
## No Active Task Behavior
## Planner Session Switch Protocol
## Planner Unpersisted Decisions
## Context Minimization
## Sensitive Information Rules
## Recovery Verification
```

---

# 9. Builder Cold Start Protocol

新しいBuilder AI / CLI SessionがRepositoryを初めて開いた場合、
以下の順序を標準としてください。

```text
1. Repository root確認
2. AI Adapter確認
3. README.md
4. docs/development/DEVELOPMENT_SYSTEM.md
5. CURRENT_STATE.md
6. tasks/TASK_REGISTER.md
7. tasks/active/ の確認
8. Active TaskがあればTask文書を読む
9. 関連Product / Development SSOTを読む
10. Git状態確認
11. Recovery判定
12. 作業再開または待機
```

---

# 10. AI Adapter

Builder AIごとの入口：

```text
AGENTS.md
CLAUDE.md
GEMINI.md
```

等は薄いAdapterを維持する。

Sessionルール追加後は、
必要に応じて以下への参照を追加する。

```text
CURRENT_STATE.md
docs/development/SESSION_RULES.md
tasks/TASK_REGISTER.md
```

詳細本文をAdapterへコピーしない。

---

# 11. Unknown / Future Builder AI

Repositoryに専用Adapterがない将来AIを使用する場合の
Fallback Entry Pointを定義してください。

推奨：

```text
README.md
↓
AGENTS.md
↓
docs/development/DEVELOPMENT_SYSTEM.md
↓
CURRENT_STATE.md
```

特定サービス専用機能なしでも再開可能であること。

---

# 12. Builder Session Switch Protocol

Builderを、

```text
Codex CLI → Claude Code
Gemini CLI → Codex
Session A → Session B
```

等へ意図的に変更する場合、
現在Builderは可能な範囲で安全なCheckpointを作る。

---

## 12.1 Intentional Checkpoint

Active Task途中で意図的にSession / AIを切り替える場合、
最低限：

```text
1. 現在の変更状態を確認
2. 破損した中間状態でないことを確認
3. 実施済み内容をCURRENT_STATEへ簡潔に反映
4. 残作業をCURRENT_STATEへ記録
5. Human Decision有無を記録
6. 可能ならTask ID付きcheckpoint commit
7. push
8. 新Sessionへ切替
```

---

## 12.2 Checkpoint Commit

安全にcommit可能な状態なら、
Task IDを含むcheckpoint commitを許可する。

例：

```text
DEV-TASK-0012: checkpoint before session switch
```

WIPという曖昧なcommit名だけにせずTask IDを含める。

---

## 12.3 Do Not Commit Broken State

単にSessionを切り替えるためだけに、

```text
build不能
syntax error
secret混入
明らかな破損状態
```

を無理にcommitしない。

安全にcommitできない場合は、

- CURRENT_STATEに状況を記録
- Git working treeを保持
- 新Sessionが `git status` から復旧

できるようにする。

ただしPC変更を伴う場合、
uncommitted local stateは引き継げないため、
安全なcheckpoint作成を優先する。

---

# 13. Unexpected Interruption Recovery

AI crash、Terminal終了、PC再起動など、
事前Checkpointなしで中断する場合も想定する。

新Sessionは推測で作業をやり直さず、
最低限以下を確認する。

```text
CURRENT_STATE.md
TASK_REGISTER.md
tasks/active/
git status
git diff
git log
git branch
```

必要に応じて、

```text
git diff --staged
```

等も確認する。

---

# 14. Active Task Recovery

`tasks/active/` にTaskが1件ある場合、
新Builderは原則そのTaskを現在Taskとして扱う。

確認順：

```text
Task Instruction
↓
TASK_REGISTER
↓
CURRENT_STATE
↓
Git history
↓
working tree
```

矛盾がある場合はRule Precedenceに従う。

自己解決可能なら修正して継続する。

---

# 15. BLOCKED Recovery

Current TaskがBLOCKEDの場合：

```text
新Builderが独断でHuman Decisionを推測して解除しない
```

確認：

```text
TASK_REGISTER = BLOCKED
CURRENT_STATE = BLOCKED
Human Decision Status
```

人間判断がまだ存在しない場合は停止状態を維持する。

---

# 16. No Active Task Behavior

以下の状態：

```text
tasks/active/ = empty
CURRENT_STATE = IDLE
または AWAITING_PLANNER_REVIEW
```

では、
Builderは未発行の次Taskを勝手に作成・開始しない。

標準：

```text
Planner Task待ち
```

とする。

---

# 17. Planner Session Switch Protocol

PlannerはBrowser AIであり、
Repositoryを直接操作できない場合を標準ケースとして扱う。

新しいPlanner Sessionへ切り替える場合、
以下をContinuity sourceとする。

優先順位：

```text
1. 最新Builder Handoff ZIP
2. CURRENT_STATE.md（Handoff内またはRepository参照）
3. REPORT.md
4. TASK_REGISTER.md
5. 最新Task文書
6. Product / Development SSOT
7. Planner Session Handoff（未永続化判断がある場合のみ）
```

---

# 18. Latest Builder Handoff as Planner Recovery Package

Planner Handoff ZIPは、
単なる差分提出だけでなく、
新しいPlanner Sessionが最低限の状態を復元できる
Continuity Packageとしても機能させます。

今後のHandoff ZIPには最低限、

```text
CURRENT_STATE.md
tasks/TASK_REGISTER.md
対象Task文書
REPORT.md
MANIFEST.md
```

を必須で含める。

さらに、
Taskレビューに必要な関連SSOTを `files/` 以下へ含める。

---

# 19. Planner Unpersisted Decisions

Planner Session内で、

```text
新しい要求
仕様判断
次Task方針
Review結果
```

が決まったが、
まだBuilderへ渡されていない場合、
それはRepository未永続化状態です。

---

## 19.1 Intentional Planner Session Switch

この状態でPlanner Sessionを切り替える場合、
`PLANNER_SESSION_HANDOFF` を作ることを標準化してください。

ブラウザAIにファイル生成機能がある場合：

```text
PLANNER_SESSION_HANDOFF.md
```

として1クリック取得可能なMarkdownを推奨。

ファイル生成機能がないAIではMarkdown本文でも可。

---

# 20. PLANNER_SESSION_HANDOFF_TEMPLATE.md

以下を作成してください。

```text
templates/PLANNER_SESSION_HANDOFF_TEMPLATE.md
```

最低限：

```text
# Planner Session Handoff

## Repository / Product
## Latest Reviewed Handoff
## Latest Planner Review Result
## Decisions Made in This Session
## Decisions Not Yet Persisted to Repository
## Current User Requests
## Next Builder Task Status
## Human Decisions Pending
## Important Constraints
## Files / Handoffs to Give the New Planner
## Recommended Next Action
```

---

## 20.1 Important

Planner Session Handoffは、
Repositoryへcommitされるまでは
**正式SSOTではない一時的な引き継ぎ資料** と明記する。

新Plannerはこれを参考Contextとして使用し、
次Builder Taskへ必要情報を組み込む。

BuilderがTask IntakeしてRepositoryへcommitした時点で、
必要判断が正式に永続化される。

---

# 21. Generic SESSION_HANDOFF_TEMPLATE.md

以下も作成してください。

```text
templates/SESSION_HANDOFF_TEMPLATE.md
```

Builder側・将来の別役割でも利用可能な汎用Template。

最低限：

```text
# Session Handoff

## Role
## Repository
## Current Task
## Current Status
## Completed Work
## Remaining Work
## Relevant Files
## Verification Status
## Git State
## Human Decisions
## Known Issues
## Next Action
```

---

# 22. Context Minimization

Session Handoffへ何でもコピーしない。

特に以下を避ける。

- Repository全文
- 過去チャット全文
- 不要なログ全文
- 既にSSOTにある仕様全文
- AIの内部思考過程

代わりに、

```text
結果
決定
現在状態
未完了事項
参照先
```

を記録する。

---

# 23. No Chain-of-Thought Persistence

AIの内部推論、private chain-of-thought、scratchpad等を
RepositoryやSession Handoffに保存する標準にしてはいけません。

記録するのは、

```text
Decision
Reason（必要最小限の説明）
Result
Evidence
```

までとする。

---

# 24. Sensitive Information Rules

Session / Handoff文書へ以下を保存しない。

```text
password
API key
access token
private key
secret
個人認証情報
```

秘密情報が必要な場合は、
安全な外部認証環境・secret managementを使用し、
Repositoryには存在場所や必要性のみ記録する。

---

# 25. Update HANDOFF_RULES.md

Handoff ZIP必須内容に、

```text
files/CURRENT_STATE.md
files/tasks/TASK_REGISTER.md
```

を追加する。

Completed Taskの場合：

```text
files/tasks/completed/<TASK-ID>.md
```

BLOCKEDの場合：

```text
files/tasks/active/<TASK-ID>.md
```

を維持する。

---

# 26. Update Handoff Generator

`scripts/create_handoff.py` / PowerShell wrapperを確認し、
今回の必須Continuity filesを無理なく含められるようにする。

実装方式はBuilder判断。

ただしGeneratorへProduct固有情報をハードコードしない。

---

# 27. Update TASK_RULES.md

Task Intake / Completion時のCURRENT_STATE更新を
Lifecycleへ統合する。

概念：

```text
Task Intake
↓
CURRENT_STATE = ACTIVE
↓
Intake commit / push

Task Completion
↓
TASK_REGISTER = COMPLETED
↓
CURRENT_STATE = AWAITING_PLANNER_REVIEW
↓
Final commit / push
↓
Handoff
```

---

# 28. Update BUILDER_RULES.md

Builder開始時に、
新しいSessionかどうかに関係なく最低限、

```text
CURRENT_STATE
TASK_REGISTER
Active Task
Git State
```

を確認する規則を追加する。

---

# 29. Update DEVELOPMENT_SYSTEM.md

以下を簡潔に追加する。

```text
Continuity Principle
```

内容：

- AI / Session変更は正常イベントとして扱う
- Repositoryから状態復元する
- CURRENT_STATEをCurrent State Indexとする
- Chat履歴・AI内部記憶へ依存しない
- 詳細はSESSION_RULES

実装詳細はSESSION_RULESへ委譲する。

---

# 30. Update README.md

Repository初見の人間 / AIが、

```text
「どこから読めばいいか」
```

を理解できるようにする。

推奨入口：

```text
Development System
CURRENT_STATE
Task Register
```

過剰に長くしない。

---

# 31. Cold Start Recovery Test

本Taskでは実際に
**「過去会話を知らない新Builder」** を想定したRecovery Testを行ってください。

テストでは、
以下だけから状態を復元可能か確認する。

```text
README.md
AGENTS.md
docs/development/DEVELOPMENT_SYSTEM.md
docs/development/SESSION_RULES.md
CURRENT_STATE.md
tasks/TASK_REGISTER.md
tasks/active/
Git state
```

確認事項：

```text
Repository identity
Canonical remote
Current branch
Current Task
Current workflow phase
Human Decision有無
次に読むべきTask / SSOT
次に取るべきAction
```

---

# 32. Post-Completion Recovery State

本Task完了後は、

```text
tasks/active/
= empty

TASK_REGISTER:
DEV-TASK-0008 = COMPLETED

CURRENT_STATE:
Workflow Phase = AWAITING_PLANNER_REVIEW
Current Task = None
Latest Completed Task = DEV-TASK-0008
Human Decision Status = None
Next Expected Action = Planner reviews latest Handoff
```

となること。

Cold Start時にこれが一意に分かること。

---

# 33. Planner Recovery Test

Handoff ZIPだけを新Plannerへ渡した場合を想定し、
最低限以下から状態を把握できることを確認する。

```text
REPORT.md
MANIFEST.md
files/CURRENT_STATE.md
files/tasks/TASK_REGISTER.md
files/tasks/completed/DEV-TASK-0008.md
```

新Plannerが少なくとも、

```text
何のRepositoryか
何Taskまで完了したか
今回何をレビューすべきか
人間判断が必要か
次がPlanner Reviewであること
```

を理解できること。

---

# 34. Task Lifecycle

本DEV-TASK-0008も正式Lifecycleに従う。

```text
Task Intake
↓
tasks/active/DEV-TASK-0008.md
↓
TASK_REGISTER = ACTIVE
↓
CURRENT_STATE = ACTIVE
↓
Intake commit / push
↓
実装
↓
検証
↓
tasks/completed/DEV-TASK-0008.md
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

# 35. Git / GitHub

Canonical Repository：

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

最低限：

```text
DEV-TASK-0008: register task
DEV-TASK-0008: standardize session continuity
```

等、Task IDを追跡可能なcommitを行う。

---

# 36. Verification

最低限以下を確認する。

- [ ] `CURRENT_STATE.md` がRepository rootに存在
- [ ] CURRENT_STATEがProduct SSOTを大量複製していない
- [ ] Workflow Phaseが定義されている
- [ ] `SESSION_RULES.md` が存在
- [ ] Builder Cold Start Protocolがある
- [ ] Intentional Session Switchが定義されている
- [ ] Unexpected Interruption Recoveryが定義されている
- [ ] Active Task Recoveryが定義されている
- [ ] BLOCKEDを勝手に解除しない
- [ ] No Active Task時に勝手に次Taskを開始しない
- [ ] Planner Session Switch Protocolがある
- [ ] Planner未永続化判断の扱いが明確
- [ ] `PLANNER_SESSION_HANDOFF_TEMPLATE.md` が存在
- [ ] `SESSION_HANDOFF_TEMPLATE.md` が存在
- [ ] chain-of-thoughtを保存しない
- [ ] secretsを保存しない
- [ ] Handoff ZIPにCURRENT_STATEが含まれる
- [ ] Handoff ZIPにTASK_REGISTERが含まれる
- [ ] Cold Start Recovery Test PASS
- [ ] Planner Recovery Test PASS
- [ ] DEV-TASK-0008が正式Lifecycleを使用
- [ ] `git diff --check` PASS
- [ ] origin/mainへpush済み
- [ ] tracked working tree clean

---

# 37. Handoff

Planner提出物は必ず、

```text
受け渡し/DEV-TASK-0008_PLANNER_HANDOFF.zip
```

1個のみ。

標準Generatorで作成し、
Portable ZIP VerificationをPASSさせる。

500MB以内。

最低限以下を含める。

```text
DEV-TASK-0008_PLANNER_HANDOFF.zip
├── REPORT.md
├── MANIFEST.md
└── files/
    ├── CURRENT_STATE.md
    ├── README.md
    ├── tasks/
    │   ├── TASK_REGISTER.md
    │   └── completed/
    │       └── DEV-TASK-0008.md
    ├── templates/
    │   ├── SESSION_HANDOFF_TEMPLATE.md
    │   └── PLANNER_SESSION_HANDOFF_TEMPLATE.md
    └── docs/
        └── development/
            ├── DEVELOPMENT_SYSTEM.md
            ├── SESSION_RULES.md
            ├── BUILDER_RULES.md
            ├── TASK_RULES.md
            └── HANDOFF_RULES.md
```

実際に変更した関連ファイルも必要なら含める。

---

# 38. REPORT.md Additional Sections

REPORTに最低限以下を追加する。

```text
## Continuity Standard
## Builder Cold Start Test
## Planner Recovery Test
```

### Builder Cold Start Test

最低限：

```text
Repository identified:
Current workflow phase identified:
Current task identified:
Human decision state identified:
Git state identified:
Next action identified:
Result:
```

### Planner Recovery Test

最低限：

```text
Latest completed task identified:
Review target identified:
Human decision state identified:
Next Planner action identified:
Result:
```

---

# 39. Builder Final Response

既存標準に従う。

最低限：

```text
Task: DEV-TASK-0008
Status: COMPLETE / BLOCKED

実施内容:
- ...

Continuity:
- CURRENT_STATE: ...
- Builder Cold Start Test: PASS / FAIL
- Planner Recovery Test: PASS / FAIL
- AI / Session Independence: ...

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

これをPlannerに渡してください: <実際の絶対パス>\受け渡し\DEV-TASK-0008_PLANNER_HANDOFF.zip
```

**最後の1文より後には何も記載しないこと。**

---

# 40. Acceptance Criteria

以下をすべて満たせばCOMPLETE。

- [ ] AI / Session切替を正常な開発イベントとして標準化
- [ ] Repositoryから状態復元できる
- [ ] `CURRENT_STATE.md` がCurrent State Indexとして存在
- [ ] Workflow Phaseが一意に把握できる
- [ ] 新BuilderのCold Start順序が標準化
- [ ] Builder AI変更手順がある
- [ ] 意図的Session切替前のCheckpoint規則がある
- [ ] unexpected interruptionからRecoveryできる
- [ ] Active Task途中から再開できる
- [ ] BLOCKED Taskを独断解除しない
- [ ] Active TaskなしでBuilderが次Taskを捏造しない
- [ ] 新Planner SessionのRecovery sourceが定義されている
- [ ] Planner未永続化判断がRepository SSOTと区別されている
- [ ] Planner Session Handoff Templateが存在
- [ ] Generic Session Handoff Templateが存在
- [ ] Handoff ZIPがPlanner Continuity Packageとして機能
- [ ] HandoffにCURRENT_STATE / TASK_REGISTERを必須化
- [ ] AI内部記憶に依存しない
- [ ] chain-of-thoughtを永続化しない
- [ ] secretをRepositoryへ保存しない
- [ ] Builder Cold Start Recovery Test PASS
- [ ] Planner Recovery Test PASS
- [ ] GitHub commit / push完了
- [ ] tracked working tree clean
- [ ] `受け渡し/` にDEV-TASK-0008 ZIP 1個のみ
- [ ] Handoff portable verification PASS
- [ ] 最終回答最後がZIP絶対パス案内

---

# 41. Scope Boundary

本TaskではAI / Session Continuityと状態復元を標準化する。

以下は次Taskへ残す。

- Definition of Done全体統合
- Development Standard全体の矛盾監査
- Template Repositoryとしての最終構造整理
- 新規Product開始フロー
- 既存Product取込 / Analysis開始フロー
- Template複製後の初期化手順
- 最終テンプレート検証
- 不要なBootstrap residueの整理

今回の目的は、

**「Planner / BuilderのAIやセッションが変わっても、Repositoryと最新Handoffだけから安全に現在地を復元し、同じ開発体験を継続できる」**

ことです。
