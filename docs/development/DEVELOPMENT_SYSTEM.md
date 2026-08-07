# Development System

## Purpose
本ドキュメント（`DEVELOPMENT_SYSTEM.md`）は、当リポジトリにおけるAIを活用した開発標準（Planner / Builder AI Development Standard）の最上位構造および基本原則を定義する「Development SSOT（Single Source of Truth）」の共通入口です。
製品開発、既存機能の分析・改修、AIサービスやセッションの切り替えが発生しても、再現可能で整合性の取れた開発運用を成立させることを目的とします。

## Source of Truth
1. 会話履歴（Chat Log）やAI内部の記憶は正式な仕様・履歴とはみなしません。
2. リポジトリにコミットされたファイルおよび構造のみを「SSOT（Single Source of Truth）」と定義します。
   - Chat / AI Session: 一時的な作業場所
   - Repository: 永続的な記憶・仕様・履歴の管理場所

## Roles & Identity
開発プロセスにおけるAIおよび人間の役割は、以下の抽象化された役割名に固定します。特定AIサービス名（ChatGPT, Claude, Gemini, Codex等）には依存しません。プロダクト固有の識別子・Remote情報・Prefixは [PROJECT_PROFILE.md](../../PROJECT_PROFILE.md) を正とします。

### Planner
- **形態**: ブラウザ版AI（または対話型計画AI）
- **役割**: 全体計画の策定、仕様判断、Taskの作成・発行、Builder成果物のレビュー・承認を担当します。

### Builder
- **形態**: VSCode + CLI型AI（コード・リポジトリ直接操作AI）
- **役割**: リポジトリ構造を直接参照・操作し、コードの調査・実装・テスト検証・ドキュメント更新および成果物の提出（Handoff）を担当します。
- **詳細ルール**: [BUILDER_RULES.md](./BUILDER_RULES.md)

## AI Service Independence & Continuity Principle
- AIサービスやセッションの切替・CLI再起動・PC変更は正常な運用イベントとして扱います。
- チャット履歴や AI 内部記憶（chain-of-thought等）には一切依存せず、リポジトリ上の設定およびドキュメントのみから開発状態を完全復元します。
- リポジトリルートの [CURRENT_STATE.md](../../CURRENT_STATE.md) を開発状態のインデックス（Current State Index）として運用します。
- 共通開発ルールは特定AI固有の指示ファイルに重複記載せず、本ドキュメントおよび `docs/development/` 以下を正（SSOT）とします。AI固有ファイル（`AGENTS.md` 等）は薄い Adapter として運用します。
- 詳細は [SESSION_RULES.md](./SESSION_RULES.md) に定義します。

## Autonomous Execution Principle
- Builderは、人間の明示的な判断を必要としない作業（調査、実装、テスト実行、ドキュメント更新、検証等の定義されたプロセス）について、途中確認で停止せず自律的に実行・完結します。
- 自律進行範囲および人間判断のための停止境界の詳細は [DECISION_RULES.md](./DECISION_RULES.md) に定義します。

## Task Management Principle & Lifecycle
- **Task ID 標準**: `<PREFIX>-TASK-XXXX` （`<PREFIX>` は `PROJECT_PROFILE.md` で定義。例: `DEV-TASK-0009`）を識別子およびファイル名（`<TASK-ID>.md`）とします。
- **One Active Task**: 原則として同時に着手するActive Taskは `tasks/active/` に配置される 1 件のみとします。
- **Task Instruction Immutability**: Plannerから発行されたTask文書は指示レコードであり不可変です。Builderが要件や受入条件を書き換えてはなりません。
- **Task Register**: `tasks/TASK_REGISTER.md` にて全タスクの現在状態（ACTIVE / BLOCKED / COMPLETED）および過去履歴を一元管理します。
- **Task Intake Persistence**: タスク受領直後、`tasks/active/<TASK-ID>.md` への正式登録、`TASK_REGISTER.md` および `CURRENT_STATE.md` の更新内容を GitHub へコミット・プッシュして受付状態を永続化します。
- 詳細は [TASK_RULES.md](./TASK_RULES.md) に定義します。

## Planner Review Gate & Evidence Rules
- **Review Gate**: タスク完遂後、Builderが提出した Handoff ZIP を Planner がレビューします。
- **Evidence 区分**:
  - **Builder技術検証**: タスク最終コミットを対象とした自動テスト・ビルド・`git diff --check` 等は、Handoff ZIP 生成前に実施されていても正式エビデンスとして有効です。
  - **人間・外部検証**: 人間による実機・目視確認等は Handoff 世代境界に紐付き、新 Handoff 生成時に過去の人間検証は自動継承されません（明示的指定がない限り再検証を要求）。
- **3分類の判定結果**:
  1. `ACCEPTED`: 承認。タスク終了・次タスクへ。
  2. `CHANGES_REQUIRED`: 修正要求。過去タスクやGit履歴を上書きせず、修正用の新 Task IDを発行して対処します。
  3. `HUMAN_DECISION_REQUIRED`: 人間判断要求。人間による意思決定を整理提示します。
- **No Next Task Before Review**: BuilderはPlannerのレビューが完了する前に未発行の次タスクへ着手してはなりません。
- 詳細は [REVIEW_RULES.md](./REVIEW_RULES.md) に定義します。

## Definition of Done (DoD) Principle
- すべてのタスクは、タスク固有の受入条件（Acceptance Criteria）に加え、共通の最小品質条件を満たして初めて `COMPLETE` と判定されます。
- Git コミット・プッシュ・Remote 安全性チェック、`受け渡し/` ディレクトリへのポータブル Handoff ZIP 生成・自動検証の全合格が必須条件です。
- 詳細は [DEFINITION_OF_DONE.md](./DEFINITION_OF_DONE.md) に定義します。

## Project Initialization & Template Duplication
- テンプレートリポジトリからの複製後、`NEW_PRODUCT`（新規開発）または `EXISTING_PRODUCT`（既存製品分析・改善）モードに応じた初期化を実施します。
- `PROJECT_PROFILE.md` の確定、Remote 安全性チェック (`git remote -v` の誤 push 防止確認)、ランタイムタスク状態のリセット、および Product SSOT (`docs/product/`) の初期構築を行います。
- 詳細は [PROJECT_INITIALIZATION_RULES.md](./PROJECT_INITIALIZATION_RULES.md) に定義します。

## Repository Areas
本リポジトリは以下の標準構造により関心の分離を実現します。

- `/`: リポジトリルート（概要ドキュメント、`PROJECT_PROFILE.md`, `CURRENT_STATE.md` および AI Adapter）
- `受け渡し/`: BuilderからPlannerへの成果物受け渡し領域（Git追跡対象外）
- `docs/`: 正式ドキュメント領域（SSOT）
  - `docs/development/`: 開発標準・運用ルール（Development SSOT）
    - [DEVELOPMENT_SYSTEM.md](./DEVELOPMENT_SYSTEM.md)
    - [BUILDER_RULES.md](./BUILDER_RULES.md)
    - [DECISION_RULES.md](./DECISION_RULES.md)
    - [HANDOFF_RULES.md](./HANDOFF_RULES.md)
    - [GIT_RULES.md](./GIT_RULES.md)
    - [TASK_RULES.md](./TASK_RULES.md)
    - [REVIEW_RULES.md](./REVIEW_RULES.md)
    - [SESSION_RULES.md](./SESSION_RULES.md)
    - [DEFINITION_OF_DONE.md](./DEFINITION_OF_DONE.md)
    - [PROJECT_INITIALIZATION_RULES.md](./PROJECT_INITIALIZATION_RULES.md)
  - `docs/product/`: 製品仕様・アーキテクチャ（Product SSOT）
- `tasks/`: Task管理領域（PlannerからBuilderへのタスク投入・管理）
  - [TASK_REGISTER.md](../../tasks/TASK_REGISTER.md)
  - `tasks/active/`: 進行中タスク
  - `tasks/completed/`: 完了済みタスク
- `reports/`: 分析・調査結果の永続レポート配置領域 (`reports/analysis/` 等)
- `templates/`: 標準テンプレート配置領域（Task, Session Handoff, Product SSOT等）

## Handoff Principle
- BuilderからPlannerへの成果物受け渡しは、リポジトリルート直下の `受け渡し/` を唯一の標準配置場所とします。
- **`受け渡し/` には常に現在Plannerへ渡すべき最新のHandoff ZIP（`<TASK-ID>_PLANNER_HANDOFF.zip`、上限500MB）1個のみを配置します。**
- Handoff ZIPには Planner Continuity Package として `files/CURRENT_STATE.md`、`files/tasks/TASK_REGISTER.md`、および対象タスク文書（`files/tasks/completed/<TASK-ID>.md` 等）を必須で含めます。
- Handoff ZIPはOS非依存のポータブルアーカイブとし、ZIP内部パスは常に POSIX 形式 `/` とします。標準スクリプトによる生成・自動検証を必須とします。
- `受け渡し/` は配送物領域であり Git 追跡対象外とします。`git clone` 直後に存在しない場合は Builder が自動作成します。
- 詳細は [HANDOFF_RULES.md](./HANDOFF_RULES.md) に定義します。

## Version Control Principle
- 本リポジトリのすべての変更履歴および状態管理は GitHub (Git) を正式なバージョン管理・同期基盤として運用します。
- Canonical Remote は [PROJECT_PROFILE.md](../../PROJECT_PROFILE.md) を正とします（`PB-Dev` 本体では `https://github.com/h-shojaku/PB-Dev.git` 、標準ブランチ `main`）。
- 通常タスクでは、Intake コミット (`<TASK-ID>: register task`) および実装完了コミット (`<TASK-ID>: <summary>`) を行い、プッシュ後に `受け渡し/` に最新 ZIP を作成・検証します。
- 詳細は [GIT_RULES.md](./GIT_RULES.md) に定義します。

## Rule Precedence
ルール内容に矛盾や競合が発生した場合の標準的な優先順位は以下の通りとします。

1. **明示された最新の人間判断**
2. **Product SSOT** (`docs/product/`)
3. **Development SSOT** (`docs/development/`)
4. **Active Task** (`tasks/active/`)
5. **AI固有Adapter** (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md` 等)
6. **AIサービス既定の慣習**
