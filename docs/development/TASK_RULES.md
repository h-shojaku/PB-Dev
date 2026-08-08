# Task Rules (タスク運用規定)

## 1. Task Standard Location
すべての Task 定義書はリポジトリの以下の標準ディレクトリで管理されます。

- **実行中 Active Task**: `tasks/active/<TASK-ID>.md` (常に最大 1 個)
- **完了完了 Completed Task**: `tasks/completed/<TASK-ID>.md`

---

## 2. Task Identification & Lifecycle
- **Task ID 命名規則**: `<PREFIX>-TASK-XXXX` （例: `DEV-TASK-0015`）
- **Lifecycle Flow**:
  1. **Intake**: Planner から受領したタスクファイルを `tasks/active/<TASK-ID>.md` に配置し、`CURRENT_STATE.md` および `tasks/TASK_REGISTER.md` を `ACTIVE` に更新して Commit & Push。
  2. **Execution**: 指示に従い実装・ローカル検証を実行。適応型ワークフロー（[ADAPTATION_RULES.md](ADAPTATION_RULES.md)）に基づき、目的に最適な手法を自律選択。
  3. **Completion**: タスクファイルを `tasks/completed/<TASK-ID>.md` に移動し、`CURRENT_STATE.md` (`AWAITING_PLANNER_REVIEW`) および `TASK_REGISTER.md` (`COMPLETED`) を更新して Commit & Push。
  4. **Handoff Generation**: `git archive HEAD` による Tracked Repository Snapshot（`repository/`）を含む Handoff ZIP を生成。

---

## 3. Adaptive Procedure Authority (適応的手順変更権限)
- Builder はタスクの目的・受入条件・SSOT・セーフティ制約を満たす範囲内において、指示書に記載された内部手順や使用ユーティリティを、より確実で堅牢な代替手法へ自律的に切り替える権限を持ちます。
- 手順の切り替えにあたり、人間や Planner への確認要求は不要です（Scope 変更を伴う場合を除く）。
