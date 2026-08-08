# AI Development Standard — System Definition

本ドキュメント（`DEVELOPMENT_SYSTEM.md`）は、当AI開発システム（AI Development Standard）全体の最上位構造・役割分担・運用原則を明確にする **Single Source of Truth (SSOT)** です。

---

## 1. Overall Concept (全体思想)

当開発システムは、ブラウザ環境で動作する **Planner AI** と、ローカルVSCode環境で動作する **Builder AI** が協調し、高品質かつ信頼性の高いソフトウェア開発を自動実行するためのAIペアプログラミング標準です。

### 1.1 Source-First & Outcome-Over-Procedure
- **Source-First Review**: レビューの一次真実は Builder のレポートではなく、Git HEAD コミットで追跡されている実際のソースコード（Tracked Repository Source）です。
- **Outcome-Over-Procedure**: タスク目的・受入条件・SSOT・安全制約を満たす限り、事前定義された手順やツールに過度に固執せず、最も確実な代替手段へ自律的に切り替える適応型ワークフロー（[ADAPTATION_RULES.md](ADAPTATION_RULES.md)）を適用します。

---

## 2. Core SSOT Registry (標準ルール構成)

各運用の詳細ルールは以下の個別 SSOT ドキュメントで管理されます。

1. **[ADAPTATION_RULES.md](ADAPTATION_RULES.md)**: 適応型ワークフロー規則・可変/不可変境界・同一失敗反復防止
2. **[BUILDER_RULES.md](BUILDER_RULES.md)**: Builder AI の基本行動規範・自律性・検証義務
3. **[DECISION_RULES.md](DECISION_RULES.md)**: 人間判断（Human Decision / BLOCK）の基準と運用手順
4. **[DEFINITION_OF_DONE.md](DEFINITION_OF_DONE.md)**: タスク完了定義（DoD）・品質基準
5. **[GIT_RULES.md](GIT_RULES.md)**: Git コミット・ブランチ・GitHub リモート同期規定
6. **[HANDOFF_RULES.md](HANDOFF_RULES.md)**: Handoff パッケージ構造（`repository/` Snapshot）・生成・自動検証
7. **[PROJECT_INITIALIZATION_RULES.md](PROJECT_INITIALIZATION_RULES.md)**: プロジェクト初期化（Initializer）の仕様と安全制約
8. **[REVIEW_RULES.md](REVIEW_RULES.md)**: Source-First Review 原則・Planner 独立検証手順
9. **[SESSION_RULES.md](SESSION_RULES.md)**: AI セッション切替・状態復元・コンティニュイティ標準
10. **[TASK_RULES.md](TASK_RULES.md)**: タスクライフサイクル（`active/` ➔ `completed/`）・管理標準

---

## 3. Core Role Definitions (役割の定義)

### 3.1 Planner AI (設計・指示・検証・承認)
- リポジトリ全域の設計・方針決定、タスク発行、および成果物の独立検証を担当します。
- レビュー時は Handoff ZIP 内の `repository/` スナップショットを直接検査し、必要に応じて同梱されたテストやスクリプトを再実行して検証します。

### 3.2 Builder AI (実装・検証・提出)
- 発行されたタスク指示書に基づき、ローカル環境でコード修正・テスト作成・動作検証を実行します。
- タスク完了時、変更を Git にコミット・プッシュした上で、`git archive HEAD` による Tracked Repository Snapshot を含んだ Handoff ZIP を生成して提出します。

---

## 4. Key Operational Workflow (運用フロー)

```text
Planner タスク発行 (tasks/active/<TASK-ID>.md)
  ↓
Builder タスク受入・実装・ローカル検証
  ↓
Builder テスト実行・Git コミット & プッシュ (origin main)
  ↓
Builder 標準 Generator で Handoff ZIP 生成 (repository/ スナップショット同梱)
  ↓
Builder 最終回答出力 (「これをPlannerに渡してください: ...」)
  ↓
Planner 解凍・Source-First レビュー・独立検証
  ↓
Planner 承認 (COMPLETED) または 修正指示 (CHANGES_REQUIRED)
```
