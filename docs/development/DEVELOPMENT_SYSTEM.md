# Development System

## Purpose
本ドキュメント（`DEVELOPMENT_SYSTEM.md`）は、当リポジトリにおけるAIを活用した開発標準（Planner / Builder AI Development Standard）の最上位構造および基本原則を定義する「Development SSOT（Single Source of Truth）」の共通入口です。
製品開発、既存機能の分析・改修、AIサービスやセッションの切り替えが発生しても、再現可能で整合性の取れた開発運用を成立させることを目的とします。

## Source of Truth
1. 会話履歴（Chat Log）やAI内部の記憶は正式な仕様・履歴とはみなしません。
2. リポジトリにコミットされたファイルおよび構造のみを「SSOT（Single Source of Truth）」と定義します。
   - Chat / AI Session: 一時的な作業場所
   - Repository: 永続的な記憶・仕様・履歴の管理場所

## Roles
開発プロセスにおけるAIおよび人間の役割は、以下の抽象化された役割名に固定します。特定AIサービス名（ChatGPT, Claude, Gemini, Codex等）には依存しません。

### Planner
- **形態**: ブラウザ版AI（または対話型計画AI）
- **役割**: 全体計画の策定、仕様判断、Taskの作成・発行、Builder成果物のレビュー・承認を担当します。

### Builder
- **形態**: VSCode + CLI型AI（コード・リポジトリ直接操作AI）
- **役割**: リポジトリ構造を直接参照・操作し、コードの調査・実装・テスト検証・ドキュメント更新および成果物の提出（Handoff）を担当します。
- **詳細ルール**: [BUILDER_RULES.md](./BUILDER_RULES.md)

## AI Service Independence
- 共通開発ルールは特定AI固有の指示ファイルに重複記載せず、本ドキュメントおよび `docs/development/` 以下を正（SSOT）とします。
- リポジトリ直下のAI固有ファイル（`AGENTS.md`, `CLAUDE.md`, `GEMINI.md` 等）は、本共通SSOTへアクセスするための「薄いAdapter」として配置・運用します。

## Autonomous Execution Principle
- Builderは、人間の明示的な判断を必要としない作業（調査、実装、テスト実行、ドキュメント更新、検証等の定義されたプロセス）について、途中確認で停止せず自律的に実行・完結します。
- 自律進行範囲および人間判断のための停止境界の詳細は [DECISION_RULES.md](./DECISION_RULES.md) に定義します。

## Repository Areas
本リポジトリは以下の標準構造により関心の分離を実現します。

- `/`: リポジトリルート（概要ドキュメントおよびAI Adapterファイル）
- `受け渡し/`: BuilderからPlannerへの成果物受け渡し領域（Git追跡対象外）
- `docs/`: 正式ドキュメント領域（SSOT）
  - `docs/development/`: 開発標準・運用ルール（Development SSOT）
    - [DEVELOPMENT_SYSTEM.md](./DEVELOPMENT_SYSTEM.md)
    - [BUILDER_RULES.md](./BUILDER_RULES.md)
    - [DECISION_RULES.md](./DECISION_RULES.md)
    - [HANDOFF_RULES.md](./HANDOFF_RULES.md)
    - [GIT_RULES.md](./GIT_RULES.md)
  - `docs/product/`: 製品仕様・アーキテクチャ（Product SSOT）
- `tasks/`: Task管理領域（PlannerからBuilderへのタスク投入・管理）
  - `tasks/active/`: 進行中タスク
  - `tasks/completed/`: 完了済みタスク
- `reports/`: 分析・調査結果の永続レポート配置領域
- `templates/`: 標準テンプレート配置領域（Task, Handoff等）

## Handoff Principle
- BuilderからPlannerへの成果物受け渡しは、リポジトリルート直下の `受け渡し/` を唯一の標準配置場所とします。
- **`受け渡し/` には常に現在Plannerへ渡すべき最新のHandoff ZIP（`<TASK-ID>_PLANNER_HANDOFF.zip`、上限500MB）1個のみを配置します。**
- Handoff ZIPはOS非依存のポータブルアーカイブとし、ZIP内部パスは常に POSIX 形式 `/` とします。標準スクリプトによる生成・自動検証を必須とします。
- `受け渡し/` は配送物領域であり Git 追跡対象外とします。`git clone` 直後に存在しない場合は Builder が自動作成します。
- 詳細は [HANDOFF_RULES.md](./HANDOFF_RULES.md) に定義します。

## Version Control Principle
- 本リポジトリのすべての変更履歴および状態管理は GitHub (Git) を正式なバージョン管理・同期基盤として運用します。
- 本開発標準リポジトリの Canonical Remote は `https://github.com/h-shojaku/PB-Dev.git` 、標準ブランチは `main` とします（Templateから派生した各製品リポジトリでは、派生先リポジトリのURLがRemoteとして設定されます）。
- 通常タスクでは、検証完了後の `commit` および `push`（`origin main`）までBuilderが自律的に完了させ、その後に `受け渡し/` に最新 ZIP を作成・検証します。
- 詳細は [GIT_RULES.md](./GIT_RULES.md) に定義します。

## Rule Precedence
ルール内容に矛盾や競合が発生した場合の標準的な優先順位は以下の通りとします。

1. **明示された最新の人間判断**
2. **Product SSOT** (`docs/product/`)
3. **Development SSOT** (`docs/development/`)
4. **Active Task** (`tasks/active/`)
5. **AI固有Adapter** (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md` 等)
6. **AIサービス既定の慣習**

## Future Standardization Areas
以下の領域については本基盤設定以降の後続タスクにて段階的に詳細標準化を推進します。
- Task Lifecycle および 命名・移動規則
- AI / Session 切替手順・Session Handoff
- Product SSOT / 各種テンプレートの標準フォーマット
