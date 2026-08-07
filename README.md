# Repository Root

当リポジトリは、製品ソースコードに加えて「Planner / Builder型 AI開発標準（AI Development Standard）」を備えた開発基盤です。

## AI Development System

本リポジトリでは、AIサービス依存を排除した **Planner / Builder 役割分離モデル** を採用しています。

- **Planner**: ブラウザ版AI（計画策定、仕様判断、Task作成、レビュー）
- **Builder**: VSCode + CLI型AI（リポジトリ直接操作、実装、テスト、報告）
- **AI Agnostic**: 使用するAIサービス（ChatGPT / Claude / Gemini 等）は自由に変更可能

### 共通ルールの入口
共通開発ルールおよび運用の最上位SSOTは以下に定義されています。

- 📘 [Development System](docs/development/DEVELOPMENT_SYSTEM.md)
- 📋 [Task Rules](docs/development/TASK_RULES.md) | [Review Rules](docs/development/REVIEW_RULES.md)

### バージョン管理・GitHub情報
- **Canonical Repository**: [https://github.com/h-shojaku/PB-Dev](https://github.com/h-shojaku/PB-Dev)
- **Standard Branch**: `main`
- **Git運用ルール**: [Git / GitHub Rules](docs/development/GIT_RULES.md)

### 成果物・タスク受渡場所
- **Planner向け成果物受け渡し**: `受け渡し/` （常に最新のPlanner Handoff ZIP 1個のみ。詳細: [HANDOFF_RULES.md](docs/development/HANDOFF_RULES.md)）
- **タスク管理**: [tasks/TASK_REGISTER.md](tasks/TASK_REGISTER.md) | [tasks/active/](tasks/active/) / [tasks/completed/](tasks/completed/)
