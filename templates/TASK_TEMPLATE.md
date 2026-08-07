# <TASK-ID> — <Task Name>

## 0. Role
あなたはこのRepositoryの **Builder** です。

## 1. Context
本Taskの発行背景、前Task（<PREV-TASK-ID>）での成果・経緯、本Taskの位置付けを記述します。

## 2. Objective
本Taskで達成すべき主目的およびゴールを箇条書きで明記します。

## 3. Required Changes
作成・変更・削除すべき主なファイル群および変更概要を提示します。

## 4. Constraints
技術的制約、非依存ライブラリ、互換性維持ルール、パフォーマンス条件等を明記します。

## 5. Existing SSOT / Files to Read
作業開始前に確認すべきリポジトリ内の主要ドキュメント（SSOT）を明記します。

- [DEVELOPMENT_SYSTEM.md](docs/development/DEVELOPMENT_SYSTEM.md)
- [TASK_RULES.md](docs/development/TASK_RULES.md)

## 6. Implementation Requirements
具体的な実装要件、設計仕様、手順、詳細ルールを記述します。

## 7. Verification
Builderがタスク完了前に実施すべき具体的な検証手順（テスト実行、ビルド、自動スクリプト等）を記述します。

## 8. Git / GitHub
コミットメッセージ形式（`<TASK-ID>: <summary>`）および `origin main` へのプッシュ指示を記載します。

## 9. Handoff
標準 Generator（`scripts/create_handoff.ps1` または `.py`）による成果物生成および `受け渡し/<TASK-ID>_PLANNER_HANDOFF.zip` への配置指示を記載します。

## 10. Acceptance Criteria
本タスクの完了判定基準（チェックリスト形式）を明記します。

- [ ] 条件1
- [ ] 条件2

## 11. Scope Boundary
本タスクのスコープ外（後続タスクへ回す内容）を明記します。
