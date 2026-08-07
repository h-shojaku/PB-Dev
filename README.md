# Repository Root

当リポジトリは、製品ソースコードに加えて「Planner / Builder型 AI開発標準（AI Development Standard）」を備えた開発基盤です。

## AI Development System

本リポジトリでは、AIサービス依存を排除した **Planner / Builder 役割分離モデル** を採用しています。

- **Planner**: ブラウザ版AI（計画策定、仕様判断、Task作成、レビュー）
- **Builder**: VSCode + CLI型AI（リポジトリ直接操作、実装、テスト、報告）
- **AI Agnostic & Continuity**: 使用するAIサービス（ChatGPT / Claude / Gemini 等）の切り替えやセッション再起動時も、リポジトリから開発状態を完全復元可能

### 状況把握とルールの入口
初めてリポジトリを開いた人間および AI は、以下の順序で開発状況を把握できます。

1. 📍 [CURRENT_STATE.md](CURRENT_STATE.md) (現在の開発状態インデックス)
2. 📘 [Development System](docs/development/DEVELOPMENT_SYSTEM.md) (最上位SSOT)
3. 📋 [Task Register](tasks/TASK_REGISTER.md) (全タスク履歴)
4. ⚙️ [Session Rules](docs/development/SESSION_RULES.md) (セッション切替・復元ルール)

### バージョン管理・GitHub情報
- **Canonical Repository**: [https://github.com/h-shojaku/PB-Dev](https://github.com/h-shojaku/PB-Dev)
- **Standard Branch**: `main`
- **Git運用ルール**: [Git / GitHub Rules](docs/development/GIT_RULES.md)

### 成果物・タスク受渡場所
- **Planner向け成果物受け渡し**: `受け渡し/` （常に最新のPlanner Handoff ZIP 1個のみ。詳細: [HANDOFF_RULES.md](docs/development/HANDOFF_RULES.md)）
- **タスク管理**: [tasks/TASK_REGISTER.md](tasks/TASK_REGISTER.md) | [tasks/active/](tasks/active/) / [tasks/completed/](tasks/completed/)
