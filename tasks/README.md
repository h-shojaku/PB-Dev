# Tasks Area

このディレクトリは、PlannerからBuilderへ渡すTask（作業指示）およびタスク状態を管理する領域です。

## ディレクトリおよびファイル構造
- `TASK_REGISTER.md`: 全タスクの現在状態（Current Active Task）および過去履歴（Task History）を一元管理するレジスタ
- `active/`: 進行中（実行中）のTaskファイル（原則1件のみ）を配置する場所
- `completed/`: 完了したTaskファイルを保存する場所

## 運用ルール
- Task ID は `<PREFIX>-TASK-XXXX` （当リポジトリでは `DEV-TASK-XXXX`）を標準とします。
- 詳細なタスク登録・ライフサイクル・不変性ルールについては [TASK_RULES.md](../docs/development/TASK_RULES.md) を参照してください。
- Planner Review ゲートおよび評価後の対応については [REVIEW_RULES.md](../docs/development/REVIEW_RULES.md) を参照してください。
