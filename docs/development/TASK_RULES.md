# Task Rules

## 1. Purpose
本ドキュメント（`TASK_RULES.md`）は、PlannerからBuilderへ投入されるTaskのID命名規則、受け入れ手続き（Task Intake）、ライフサイクル管理、および永続化に関する開発標準を定義します。

## 2. Task ID & Filename Standard
Taskの識別子（Task ID）およびファイル名は、以下の統一ルールに従います。

- **標準フォーマット**: `<PREFIX>-TASK-XXXX`
- **Prefix**: リポジトリまたは製品を特定する固定識別子（当 `PB-Dev` リポジトリでは `DEV` を使用。例: `DEV-TASK-0006`）。
- **Sequence**: 4桁ゼロ埋めの連番（`0001`, `0002`...）。一度使用したTask IDは別目的で再利用してはなりません。
- **Filename**: `<TASK-ID>.md` （例: `DEV-TASK-0006.md`）。不要な装飾や拡張文字列を付与してはなりません。

## 3. One Active Task Principle
- 当標準運用では、Builderが同時に着手・実行するTaskは原則 **1件のみ** とします。
- `tasks/active/` には常に現在実行中の1ファイルのみを配置します。複数タスクの並行着手は、人間による明示的な並列開発の指示がない限り禁止します。

## 4. Task Instruction Immutability (Instructionの不変性)
- Plannerから受領したTask文書は、そのTaskにおける「指示レコード（Instruction Record）」であり、**不可変（Immutable）** です。
- Builderは、実装を容易にするため、あるいは自己の都合により、Task本文の要件、目的、受入条件（Acceptance Criteria）を書き換えてはなりません。
- タスク実行中に判明した課題・結果・補足説明は、`REPORT.md` やコード、コミットメッセージに記録します。

## 5. Standard Task Lifecycle
Taskは以下の標準ステップに従って処理されます。

```text
Plannerが Task を作成 (1 Task = 1 Markdown file)
  ↓
人間が Task を Builder に提供
  ↓
Builder Task Intake (ID検証、重複・衝突チェック)
  ↓
`tasks/active/<TASK-ID>.md` へ正式登録
  ↓
`tasks/TASK_REGISTER.md` を ACTIVE に更新
  ↓
Task Intake Commit & Push (`<TASK-ID>: register task`)
  ↓
Task 実行 & 検証
  ↓
(完了時) `tasks/completed/<TASK-ID>.md` へ移動
  ↓
`tasks/TASK_REGISTER.md` を COMPLETED に更新
  ↓
Final Commit & Push (`<TASK-ID>: <summary>`)
  ↓
標準スクリプトによる Handoff ZIP (`受け渡し/<TASK-ID>_PLANNER_HANDOFF.zip`) 生成 & 自動検証
  ↓
Planner Review Gate (ACCEPTED / CHANGES_REQUIRED / HUMAN_DECISION_REQUIRED)
```

## 6. Task Intake Procedure & Persistence
1. **Intake チェック**: BuilderはTaskを受領した直後、Task IDの形式、重複の有無、`tasks/active/` に他タスクが存在しないかを確認します。
2. **正式登録**: Task文書を `tasks/active/<TASK-ID>.md` に配置し、`tasks/TASK_REGISTER.md` の Current Active Task 欄へ追加します。
3. **受付の永続化 (Commit & Push)**: セッション中断やPC障害等による状態喪失を防ぐため、実装開始前にタスク受付状態を GitHub へ `commit` & `push` します（メッセージ例: `<TASK-ID>: register task`）。

## 7. Task Completion & Register Update
- タスクの受入条件（Acceptance Criteria）を満たし、検証が完了した時点で、タスクファイルを `tasks/active/` から `tasks/completed/<TASK-ID>.md` へ移動します（Git履歴で追跡可能なため重複コピーは行いません）。
- `tasks/TASK_REGISTER.md` の状態を `COMPLETED` に更新し、完了日を記録します。

## 8. BLOCKED Lifecycle
- 人間判断や技術的障害により作業を一時停止（BLOCK）する場合、タスクファイルは `tasks/active/` に維持し、`tasks/completed/` へ移動してはなりません。
- `tasks/TASK_REGISTER.md` の状態を `BLOCKED` に更新し、`REPORT.md` に理由と選択肢を明記します。
- 同一スコープの継続であれば同じTask IDで再開可能です。仕様そのものが変更される場合は新Taskを発行します。
