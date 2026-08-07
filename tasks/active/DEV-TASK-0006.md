# DEV-TASK-0006 — Task Lifecycle・Planner / Builder間運用標準化

## 0. Role

あなたはこのRepositoryの **Builder** です。

本Taskでは、これまで整備したAI Development Standardに、
PlannerからBuilderへTaskを渡してから、Builder実行、Plannerレビュー、
次Taskへ進むまでの**標準Task Lifecycle**を追加してください。

本Taskでは特定AIサービスや特定製品に依存しない、
再利用可能なTask運用を確立します。

人間判断が不要な限り、途中確認で停止せず、

```text
既存SSOT確認
→ Task運用設計
→ SSOT / Template実装
→ 現在Taskへの自己適用
→ 検証
→ commit / push
→ 標準Handoff生成・検証
→ 最終回答
```

まで自律的に完了してください。

---

# 1. Current Standard to Preserve

以下はすでに確立済みです。

## Roles

```text
Planner
= ブラウザ版AI
= 計画・仕様判断・Task作成・Builder成果物レビュー

Builder
= VSCode + CLI型AI
= Repositoryを直接操作する実行役
```

特定AIサービスには依存しません。

## Repository

```text
Repository = SSOT
Chat / AI Session = 一時的な作業場所
```

## GitHub

```text
Canonical Repository:
https://github.com/h-shojaku/PB-Dev.git

Remote:
origin

Branch:
main
```

## Planner Handoff

```text
受け渡し/
└── <LATEST-TASK-ID>_PLANNER_HANDOFF.zip
```

- 常に最新ZIP 1個のみ
- 500MB以内
- Git追跡対象外
- 標準Generatorを使用
- ZIP内部pathはPOSIX `/`
- 自動Verification必須
- Builder最終回答の最後に絶対パスを明示

これら既存SSOTを後退させないこと。

---

# 2. Objective

以下を標準化してください。

1. Task ID / filename規則
2. Task文書の標準構造
3. Taskは原則1件ずつ処理する
4. Plannerから受領したTaskをRepositoryへ正式登録する
5. `tasks/active/` と `tasks/completed/` の意味を固定する
6. TaskのInstructionを途中で勝手に書き換えない
7. Task受付から完了までのLifecycleを固定する
8. BLOCKED時の扱いを固定する
9. Planner Reviewの結果分類を固定する
10. 修正が必要な場合は過去Taskを書き換えず、新Taskを発行する
11. 次Task開始前に前TaskのPlanner Reviewを完了する
12. Task Registerに現在状態を残す
13. 新しいAI / Sessionでも現在TaskをRepositoryから判断できるようにする
14. 本Task自身を新Lifecycleへ可能な範囲で自己適用する

---

# 3. Files to Create / Update

最低限以下を整備してください。

```text
docs/development/
├── DEVELOPMENT_SYSTEM.md
├── BUILDER_RULES.md
├── TASK_RULES.md
└── REVIEW_RULES.md

tasks/
├── README.md
├── TASK_REGISTER.md
├── active/
└── completed/

templates/
└── TASK_TEMPLATE.md
```

必要に応じて、

```text
AGENTS.md
CLAUDE.md
GEMINI.md
README.md
docs/development/README.md
docs/development/GIT_RULES.md
docs/development/HANDOFF_RULES.md
```

を最小限更新してください。

詳細本文をAI Adapterへ重複コピーしないこと。

---

# 4. Task ID Standard

Task IDは以下を標準とします。

```text
<PREFIX>-TASK-XXXX
```

例：

```text
DEV-TASK-0006
APP-TASK-0001
E6-TASK-0034
SE-TASK-0140
```

---

## 4.1 Prefix

`<PREFIX>` はRepository / Productを識別する短い固定識別子とする。

本PB-Dev Repositoryでは：

```text
DEV
```

を使用する。

Templateから派生したProduct Repositoryでは、
Product初期化時にそのRepository固有Prefixを定義できるものとする。

Prefix定義の完全なProduct initializationは後続統合Taskへ残してよい。

---

## 4.2 Sequence

Task番号は原則4桁ゼロ埋め。

```text
0001
0002
0003
...
```

一度使用したTask IDを別目的で再利用しない。

過去Taskを削除して番号を再利用しない。

---

## 4.3 Filename

Task文書filenameはTask IDそのものを使用する。

```text
<TASK-ID>.md
```

例：

```text
DEV-TASK-0006.md
```

不要に長いfilenameへしない。

---

# 5. One Active Task Principle

標準運用では、Builderが同時に実行するTaskは原則 **1件のみ** とします。

通常状態：

```text
tasks/active/
└── DEV-TASK-0006.md
```

禁止する通常状態：

```text
tasks/active/
├── DEV-TASK-0006.md
├── DEV-TASK-0007.md
└── DEV-TASK-0008.md
```

理由：

- Planner / Builderの責任境界を明確にする
- AI Session切替時の「現在Task」を一意にする
- 未完了作業の混線を防ぐ
- Handoff / Review / Git履歴との対応を明確にする

---

## 5.1 Exception

複数Active Taskを許可するのは、
人間が明示的に並列開発を指示した場合のみ。

その場合でも各Taskの作業領域・Branch・Builder等の衝突回避設計が必要です。

本標準のdefaultは、

```text
One Builder / One Active Task
```

とする。

---

# 6. Task Document Is Immutable Instruction

Plannerから受領したTask文書は、
**そのTaskのInstruction Record** として扱います。

BuilderはTaskの目的・要件・Acceptance Criteriaを
自分の都合で書き換えてはいけません。

原則：

```text
Plannerが発行したTask
↓
tasks/active/<TASK-ID>.md
↓
Task完了後
tasks/completed/<TASK-ID>.md
```

内容はInstruction Recordとして保持する。

---

## 6.1 Builder Must Not Rewrite

Builderは以下の目的でTask本文を書き換えない。

- 実装しやすくするため要件を弱める
- Acceptance Criteriaを削除する
- Scopeを独断変更する
- 完了後に実装結果へ合わせてTask内容を修正する

Task中に判明した事実・実装結果は、

```text
REPORT.md
Repository変更
Git history
```

へ記録する。

---

## 6.2 Mechanical Metadata

Task TemplateにBuilder更新可能な明確なmetadata欄を設ける場合のみ、
Status等の機械的フィールド更新は許可してよい。

ただしTask instruction本文の意味を変更しない。

より単純な構造を選ぶなら、
Task本文を完全immutableとし、
状態は `TASK_REGISTER.md` だけで管理してもよい。

どちらを採用したかSSOTで明確にすること。

**Instructionの意味が不変であることを最優先**とする。

---

# 7. Standard Task Lifecycle

`docs/development/TASK_RULES.md` に、
以下を正式Lifecycleとして定義してください。

```text
Planner Task作成
↓
HumanがTaskをBuilderへ渡す
↓
Builder Task Intake
↓
tasks/active/ へ正式登録
↓
Task Register = ACTIVE
↓
Task実行
↓
検証
↓
BLOCKなし
↓
tasks/completed/ へ移動
↓
Task Register = COMPLETED
↓
Git commit / push
↓
最新Handoff ZIP生成
↓
Planner Review
↓
ACCEPTED
↓
次Task
```

---

# 8. Task Intake

BuilderがPlanner Taskを受領した直後、
実装開始前に以下を確認する。

1. Task IDが存在する
2. Filename / Task IDが一致する
3. Task IDが既使用IDと衝突していない
4. `tasks/active/` に別Taskが存在しない
5. Task内容がProduct / Development SSOTと重大矛盾していない
6. 人間判断なしで開始可能か
7. Repository / Git状態に異常がないか

---

## 8.1 Register Task

問題がなければTask文書を、

```text
tasks/active/<TASK-ID>.md
```

へ配置する。

Plannerから受け取ったTaskがRepository外の一時ファイルの場合も、
BuilderがRepository側へ正式登録する。

Taskがすでに正しい `tasks/active/` に存在する場合は重複コピーしない。

---

# 9. Task Intake Persistence

AI / Terminal / PC障害やSession切替があっても
現在Taskを失わないように、
Task Intake後はGitHubへ状態を残すことを標準とします。

原則としてTask受付時に、

```text
Task file
TASK_REGISTER update
```

をcommit / pushしてから本作業へ進む。

標準commit message例：

```text
DEV-TASK-0006: register task
```

### Important

これにより1 Taskが複数commitになることは正常とする。

Task IDを全関連commit messageに含めることで追跡可能にする。

人間判断不要なら、この受付commit / pushのために停止確認しない。

---

# 10. TASK_REGISTER.md

以下を作成してください。

```text
tasks/TASK_REGISTER.md
```

目的：

- 現在Taskを一目で把握
- 過去Taskの状態を把握
- Session / AI切替時の復帰点
- Task番号重複防止

過剰なDB化はしない。

Markdownで人間・AI双方が容易に読める形式とする。

---

## 10.1 Minimum Information

最低限、

```text
Task ID
Status
Location
Started
Completed
Summary
```

を追跡できること。

Statusは本Taskでは以下に統一する。

```text
ACTIVE
BLOCKED
COMPLETED
```

---

## 10.2 Current Task

Register上で現在Active Taskが明確に分かること。

例：

```markdown
## Current Task

| Task ID | Status | Location | Started | Summary |
|---|---|---|---|---|
| DEV-TASK-0006 | ACTIVE | tasks/active/DEV-TASK-0006.md | 2026-08-07 | Task lifecycle standardization |
```

---

## 10.3 History

Completed TaskはHistoryとして残す。

過去Entryを削除しない。

Task番号再利用防止に使えること。

---

# 11. Task Completion

TaskのAcceptance Criteriaを満たし、
必要検証が完了した場合：

```text
tasks/active/<TASK-ID>.md
```

を、

```text
tasks/completed/<TASK-ID>.md
```

へ移動する。

Task instructionの履歴はGitで残るため、
コピーして両方へ残さない。

最終状態：

```text
tasks/active/
(empty)

tasks/completed/
└── <TASK-ID>.md
```

---

## 11.1 Register Completion

`TASK_REGISTER.md` を、

```text
Status = COMPLETED
Location = tasks/completed/<TASK-ID>.md
Completed = <date>
```

へ更新する。

---

# 12. BLOCKED Lifecycle

人間判断が本当に必要でBuilderが停止する場合：

- Taskは `tasks/active/` に残す
- `TASK_REGISTER.md` を `BLOCKED` にする
- `tasks/completed/` へ移動しない
- 未完了なのにCOMPLETE Handoffとして扱わない
- 安全にcommit可能な作業はGitへ残す
- Planner向けHandoff ZIPは作成してよい
- REPORTでBlock理由を明確にする

Planner / Humanの判断後、
**同じTask scopeの継続であれば同じTask IDを再開**できる。

ただしTaskの目的や要求自体が変更される場合は、
新Taskとして発行する。

---

# 13. Planner Review Standard

`docs/development/REVIEW_RULES.md` を作成してください。

Builder Handoffを受け取ったPlannerは、
最低限以下を確認することを標準とする。

```text
1. REPORT.md
2. MANIFEST.md
3. 対象Task
4. Acceptance Criteria
5. 変更された主要成果物
6. Verification結果
7. Git / Commit状態
8. Human Decision欄
```

---

## 13.1 Planner Review Results

Planner Review結果は以下の3種類へ標準化する。

```text
ACCEPTED
CHANGES_REQUIRED
HUMAN_DECISION_REQUIRED
```

---

### ACCEPTED

TaskのAcceptance Criteriaを満たしている。

```text
Task lifecycle終了
↓
必要なら次Taskを発行
```

---

### CHANGES_REQUIRED

Builder成果物に不足・不具合・要件未達がある。

この場合、

**完了済みTask本文やGit履歴を書き換えて無かったことにしない。**

追加修正は新しいTask IDを発行する。

例：

```text
DEV-TASK-0006
↓ Planner Review
CHANGES_REQUIRED
↓
DEV-TASK-0007
```

新Task側で前Taskを参照し、
修正内容を明示する。

---

### HUMAN_DECISION_REQUIRED

仕様選択等、人間判断が必要。

Plannerは何を人間が決める必要があるか明示する。

判断確定後、

- 同じTaskを継続
- または新Task発行

をTask scopeに応じて決定する。

---

# 14. No Next Task Before Review

標準では、

**Builderは現在TaskのPlanner Reviewが完了する前に次Taskへ着手しない。**

禁止：

```text
Task A Handoff提出
↓
Planner未レビュー
↓
Builderが勝手にTask B開始
```

標準：

```text
Task A Handoff提出
↓
Builder停止
↓
Planner Review
↓
ACCEPTED / next Task
↓
Builder Task B開始
```

Builderの「人間判断不要なら自律進行」は、
**与えられたTaskの完了まで**を意味する。

未発行の次TaskをBuilder自身が作成して進行する意味ではない。

---

# 15. Planner Next-Task Behavior

Planner側の標準として以下を `REVIEW_RULES.md` に定義してください。

Planner Review結果が `ACCEPTED` で、
かつ次に実行すべきTaskが一意に決まっている場合：

```text
レビュー結果
+
次の単一Builder Task
+
全体進捗
```

を同じPlanner応答内で提示することを標準とする。

不要な「次へ進めますか？」確認で停止しない。

---

## 15.1 Progress Report

先のTask構成が決まっている場合、
Plannerが次Taskを発行する際には簡潔な進捗を付ける。

例：

```text
進捗: 6 / 8 Task完了

完了:
- DEV-TASK-0001 ...
- ...
現在:
- DEV-TASK-0007 ...
残り:
- DEV-TASK-0008 ...
```

詳細な長文進捗は不要。

---

# 16. Planner Task Output Format

PlannerがBuilderへTaskを渡す場合は、
原則として**1 Task = 1 Markdown file**とする。

```text
<TASK-ID>.md
```

Plannerが利用するブラウザAIがファイル生成機能を持つ場合は、
1クリックで取得可能な `.md` ファイルとして提供することを推奨標準とする。

AIサービスにファイル生成機能がない場合は、
Markdown本文として渡す代替を許可する。

特定AI製品機能を必須にしない。

---

# 17. TASK_TEMPLATE.md

`templates/TASK_TEMPLATE.md` を作成してください。

特定製品に依存しない標準Templateとする。

最低限以下を含める。

```text
# <TASK-ID> — <Task Name>

## 0. Role
## 1. Context
## 2. Objective
## 3. Required Changes
## 4. Constraints
## 5. Existing SSOT / Files to Read
## 6. Implementation Requirements
## 7. Verification
## 8. Git / GitHub
## 9. Handoff
## 10. Acceptance Criteria
## 11. Scope Boundary
```

---

## 17.1 Task Template Principles

Taskは、

- Builderが単独で実行可能な具体性
- Objectiveが明確
- Acceptance Criteriaが検証可能
- Human Decision境界が分かる
- Out of Scopeが必要に応じて明示される

状態にする。

---

# 18. Task Size Principle

Taskは大きすぎる作業単位にしない。

目安：

```text
Plannerが1回レビューできるまとまり
Builderが1つの目的として完結できるまとまり
```

巨大Taskを1つ発行するより、
依存関係に沿って複数Taskへ分割する。

ただし機械的に「必ず2件」「必ずNファイル」等へ固定しない。

Productや作業内容に応じた合理的な粒度とする。

---

# 19. Handoff ZIP Update

今後Handoff ZIPには、
PlannerがTaskと成果物を対応確認できるよう、
対象Task文書も含めることを標準としてください。

推奨：

```text
<TASK-ID>_PLANNER_HANDOFF.zip
├── REPORT.md
├── MANIFEST.md
└── files/
    ├── tasks/
    │   └── completed/
    │       └── <TASK-ID>.md
    └── ...
```

BLOCKEDの場合：

```text
files/tasks/active/<TASK-ID>.md
```

を含める。

`HANDOFF_RULES.md` と標準Generator運用を必要最小限更新する。

---

# 20. Git Workflow Integration

`GIT_RULES.md` をTask Lifecycleへ合わせて更新する。

標準TaskのGit履歴例：

```text
<TASK-ID>: register task
<TASK-ID>: <implementation summary>
```

Task規模によって中間commitが増えることは許可する。

全commitからTask IDを追跡できること。

---

# 21. Current Task Self-Application

本DEV-TASK-0006は、
Task Lifecycle標準を作成するTask自身です。

可能な範囲で本Taskから新運用を自己適用してください。

少なくとも：

1. `DEV-TASK-0006.md` を `tasks/active/` に登録
2. `TASK_REGISTER.md` にACTIVEとして登録
3. Task Intake commit / push
4. 実装・検証
5. Task完了時に `tasks/completed/DEV-TASK-0006.md` へ移動
6. RegisterをCOMPLETEDへ更新
7. Final commit / push
8. Handoff ZIP生成

を行う。

---

## 21.1 Bootstrap Exception

本Task開始時点ではTask Lifecycle自体がまだ存在しないため、
Task Intake commitが完全に新ルールどおりでなくても、
合理的に自己適用できる範囲で行えばよい。

REPORTに、

```text
Task Lifecycle Self-Application
```

として実施結果を明示する。

次Task以降は正式ルールとして完全適用する。

---

# 22. Historical Tasks

DEV-TASK-0001〜0005について、
過去TaskファイルがRepositoryに存在する場合は履歴を尊重する。

Task Registerへ履歴登録することは可。

ただし、

- 存在しないTask原文を推測で再生成しない
- 過去Taskの内容を書き換えない
- Git履歴を改ざんしない

こと。

過去Taskの情報が十分確認可能な範囲のみ登録する。

---

# 23. AI Adapter

AI Adapterは薄い入口を維持する。

必要なら、

```text
TASK_RULES.md
REVIEW_RULES.md
```

を参照先に追加する。

ルール本文をコピーしない。

Builder起動時に、

```text
現在Active Task
TASK_REGISTER
```

を確認する導線を追加してよい。

---

# 24. DEVELOPMENT_SYSTEM.md

Development Systemへ以下を簡潔に追加する。

- Task Management Principle
- One Active Task
- Task Register
- Planner Review Gate
- 詳細SSOTへのリンク

実装詳細を大量重複させない。

---

# 25. Review Evidence Timing

PlannerがBuilder Handoffをレビューする際、
**当該Handoff生成後の検証情報**をそのHandoffの評価材料として扱うことを標準とする。

Handoff提出より前に行われた人間側の実機検証・観察結果は、
新しいHandoffがその後に生成された場合、
自動的に新Handoffの評価へ持ち越さない。

例：

```text
人間が不具合報告
↓
Builderが修正
↓
新Handoff ZIP
↓
新Handoffに対する再検証が必要
```

ただし人間が明示的に、
過去の検証結果も評価へ含めるよう指示した場合は例外とする。

このルールを `REVIEW_RULES.md` に入れる。

---

# 26. Verification

最低限以下を確認する。

- [ ] `TASK_RULES.md` が存在
- [ ] `REVIEW_RULES.md` が存在
- [ ] `TASK_TEMPLATE.md` が存在
- [ ] `TASK_REGISTER.md` が存在
- [ ] One Active Task原則が定義されている
- [ ] Task ID / filename規則が定義されている
- [ ] Task Instructionの不変性が定義されている
- [ ] ACTIVE / BLOCKED / COMPLETEDが定義されている
- [ ] Task Intakeが定義されている
- [ ] Task Intake commit / pushが定義されている
- [ ] 完了時active→completed移動が定義されている
- [ ] Planner Review結果3分類が定義されている
- [ ] CHANGES_REQUIRED時は新Task IDを使う
- [ ] Review前に次Taskを開始しない
- [ ] Plannerが次Taskと進捗を同じ応答で提示する標準がある
- [ ] Review Evidence Timingが定義されている
- [ ] Handoff ZIPに対象Taskを含める標準がある
- [ ] Adapterにルール重複がない
- [ ] DEV-TASK-0006が可能な範囲で新Lifecycleを自己適用している
- [ ] `git diff --check` PASS
- [ ] origin/mainへpush済み
- [ ] tracked working tree clean

---

# 27. Handoff

本TaskのPlanner提出物は必ず、

```text
受け渡し/DEV-TASK-0006_PLANNER_HANDOFF.zip
```

1個のみ。

既存標準Generatorで生成・検証する。

500MB以内。

最低限以下を含める。

```text
DEV-TASK-0006_PLANNER_HANDOFF.zip
├── REPORT.md
├── MANIFEST.md
└── files/
    ├── tasks/
    │   ├── TASK_REGISTER.md
    │   └── completed/
    │       └── DEV-TASK-0006.md
    ├── templates/
    │   └── TASK_TEMPLATE.md
    └── docs/
        └── development/
            ├── DEVELOPMENT_SYSTEM.md
            ├── TASK_RULES.md
            ├── REVIEW_RULES.md
            ├── BUILDER_RULES.md
            ├── GIT_RULES.md
            └── HANDOFF_RULES.md
```

実際に変更した関連ファイルもPlanner Reviewに必要なら含める。

---

# 28. REPORT.md Additional Section

REPORTに以下を追加する。

```text
## Task Lifecycle Self-Application
```

最低限：

```text
Task intake:
Active registration:
Intake commit:
Execution:
Move to completed:
Register completion:
Final commit:
Push:
Handoff generation:
```

を記録する。

---

# 29. Git / GitHub

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

本Taskの関連commitには必ず、

```text
DEV-TASK-0006
```

を含める。

例：

```text
DEV-TASK-0006: register task
DEV-TASK-0006: standardize task lifecycle
```

---

# 30. Builder Final Response

既存標準に従う。

最低限：

```text
Task: DEV-TASK-0006
Status: COMPLETE / BLOCKED

実施内容:
- ...

Task Lifecycle:
- Active Task count: ...
- Register: ...
- Completed Task: ...
- Intake commit: ...
- Final commit: ...

検証:
- ...

Git:
- Remote: https://github.com/h-shojaku/PB-Dev.git
- Branch: main
- Push: ...
- Working tree: ...

人間判断:
- 不要
または
- 必要: ...

これをPlannerに渡してください: <実際の絶対パス>\受け渡し\DEV-TASK-0006_PLANNER_HANDOFF.zip
```

**最後の1文より後には何も記載しないこと。**

---

# 31. Acceptance Criteria

以下をすべて満たせばCOMPLETE。

- [ ] Task ID標準 `<PREFIX>-TASK-XXXX` がSSOT化されている
- [ ] 1 Task = 1 Markdown file
- [ ] One Active Taskがdefault
- [ ] Planner Task instructionの不変性が定義されている
- [ ] `tasks/active/` / `tasks/completed/` の役割が固定されている
- [ ] `TASK_REGISTER.md` が存在
- [ ] ACTIVE / BLOCKED / COMPLETEDが標準化されている
- [ ] Task Intake手順が存在
- [ ] Task受付状態をGitHubへ永続化するルールが存在
- [ ] Task完了時active→completed移動
- [ ] Planner Review Gateが存在
- [ ] ACCEPTED / CHANGES_REQUIRED / HUMAN_DECISION_REQUIREDが定義
- [ ] CHANGES_REQUIREDは新Taskとして修正
- [ ] BuilderはReview前に次Taskへ進まない
- [ ] Plannerは次Taskが一意なら同じ応答内で発行
- [ ] Plannerは既知の全体進捗を簡潔に提示
- [ ] Review Evidence Timingが定義されている
- [ ] `TASK_TEMPLATE.md` が存在
- [ ] Handoffに対象Task文書を含める
- [ ] DEV-TASK-0006が新Lifecycleを自己適用
- [ ] GitHub commit / push完了
- [ ] tracked working tree clean
- [ ] `受け渡し/` にDEV-TASK-0006 ZIP 1個のみ
- [ ] ZIP portable verification PASS
- [ ] Builder最終回答が絶対パス案内で終了

---

# 32. Scope Boundary

本TaskではTaskの流れとPlanner / Builder間のレビューゲートを標準化する。

以下は次Task以降へ残す。

- AI / Session切替の完全手順
- Session Handoff
- Context Recovery
- Definition of Done全体統合
- Product Repository初期化
- Template Repository最終検証
- CI/CD

今回の目的は、

**「PlannerがTaskを1つ渡せば、どのBuilder AIでも同じ方法でRepositoryへ登録し、実行し、完了し、Plannerレビューへ返せる」**

という開発体験を確立することです。
