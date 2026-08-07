# Project Initialization Rules

## 1. Purpose
本ドキュメント（`PROJECT_INITIALIZATION_RULES.md`）は、Template Repository（`PB-Dev`）を複製して新しいプロダクト開発（`NEW_PRODUCT`）を開始する際、または既存製品（`EXISTING_PRODUCT`）を取り込んで AI 開発標準を適用する際の初期化手続きおよびセーフティルールを定義します。

## 2. Template Duplication Principle (複製原則)
- `PB-Dev` から新しいリポジトリを作成・複製した直後は、**まだ通常のプロダクト機能開発タスクを開始してはなりません**。
- 必ず最初に「Project Initialization（プロジェクト初期化）」を実施し、プロダクトの識別情報、GitHub Remote、Task Prefix、およびランタイム状態を確定させます。

## 3. Remote Safety Check (誤Push防止ルール)
- 派生プロジェクトの初期化時、Builder は必ず `git remote -v` を確認します。
- **重要セーフティ規定**: 派生プロジェクトの `origin` Remote がテンプレート元である `https://github.com/h-shojaku/PB-Dev.git` を指したまま開発を進行し、誤って `PB-Dev` へプッシュしてはなりません。
- `PROJECT_PROFILE.md` の `Canonical Remote` と `git remote -v` の `origin` が一致しない場合、Builder は開発タスクを開始せず、Remote URL の修正または人間判断を要求します。

## 4. Project Identity & Task Prefix Initialization
- ルートの `PROJECT_PROFILE.md`（テンプレート: `templates/PROJECT_PROFILE_TEMPLATE.md`）を編集し、以下の識別情報を確定します。
  - **Project Name**: プロダクト名
  - **Project Mode**: `NEW_PRODUCT` または `EXISTING_PRODUCT`
  - **Task Prefix**: プロダクト固有のタスク接頭辞（例: `APP`, `SE`, `E6`）
  - **Canonical Remote**: プロダクト専用の GitHub Remote URL
- **循環依存の回避**: Prefix 確定前に投入される初期化タスクについては、予約識別子 `INIT`（例: `INIT.md`）または仮タスク名を利用し、「Prefix 決定前に Prefix 付き Task ID が必要」という循環依存を防止します。

## 5. Runtime State Reset (ランタイム状態の初期化)
- テンプレート元（`PB-Dev`）の開発標準構築タスク履歴（`DEV-TASK-0001`〜`0009`）は、派生プロジェクトのプロダクトタスク履歴としては引き継ぎません。
- **Git コミット履歴の保全**: Git のコミット履歴（`git log`）自体は削除・改ざんせずそのまま保持します。
- **タスクランタイム状態のクリア**: 以下のランタイム状態をプロジェクト用にリセットします。
  - `tasks/active/`: 空（ファイルなし）にクリア
  - `tasks/completed/`: クリア（`PB-Dev` 構築タスクを削除）
  - `tasks/TASK_REGISTER.md`: プロダクト用（`Current Active: なし`, `Task History: なし`）にリセット
  - `CURRENT_STATE.md`: `Workflow Phase = IDLE`, `Current Task = None` にリセット
  - `受け渡し/`: 古いローカル配送物があれば削除
- これにより、派生プロダクトはタスク番号 `<PREFIX>-TASK-0001` からクリーンに開始可能となります。

## 6. NEW_PRODUCT Initialization Flow (新規プロダクト開始フロー)
新規にゼロからプロダクトを開発する場合、以下の手順で初期化します。

```text
1. テンプレートからリポジトリ複製 / clone
2. `PROJECT_PROFILE.md` 作成 (Project Mode: NEW_PRODUCT, Prefix, Remote 確定)
3. Remote Safety Check (`git remote -v` 検証)
4. Runtime State Reset 実行
5. `docs/product/` 配下にプロダクト SSOT テンプレート (00〜05) を配置
6. `CURRENT_STATE.md` を Workflow Phase = IDLE に設定
7. Planner が最初のプロダクト計画タスク (<PREFIX>-TASK-0001) を作成・投入
8. 通常 Task Lifecycle 開始
```

### 6.1 Product SSOT Initial Structure
`docs/product/` 配下に以下の標準構造を作成します。
- `00_PRODUCT_OVERVIEW.md`: 製品概要・目的・ユーザー・価値
- `01_PRODUCT_PLAN.md`: 開発計画・ロードマップ・スコープ
- `02_REQUIREMENTS.md`: 機能要件・非機能要件・制約
- `03_UI_STRUCTURE.md`: 画面構造・UI・ナビゲーション
- `04_IMPLEMENTATION_SPEC.md`: 実装仕様・技術スタック・アーキテクチャ
- `05_OPERATION_RULES.md`: 運用・保守・リリースルール

## 7. EXISTING_PRODUCT Initialization Flow (既存プロダクト導入フロー)
すでに存在するコードベースに対して AI 開発標準を適用・更新する場合、既存ソースコードを破壊・改変しない安全な導入手順を踏みます。

```text
1. 既存コードベースへ PB-Dev の開発標準構成を追加導入
2. `PROJECT_PROFILE.md` 作成 (Project Mode: EXISTING_PRODUCT, Prefix, Remote 確定)
3. Remote Safety Check (`git remote -v` 検証)
4. 既存ソースコード保全確認 (コードの削除・大改修を行わない)
5. Runtime State Reset 実行
6. Planner が最初の Baseline Analysis Task (<PREFIX>-TASK-0001) を発行
7. Builder が既存コードの分析を実行し `reports/analysis/` に分析レポートを作成
8. 分析レポートに基づき Product SSOT (`docs/product/`) を漸進的に復元
9. 通常の Update / Feature Task Lifecycle へ移行
```

### 7.1 Existing Product Baseline Analysis Template
既存プロダクトの分析には `templates/product/EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md` を使用し、結果を `reports/analysis/` に保存します。分析時は「事実確認済み (Confirmed)」「目視観察 (Observed)」「推測 (Inferred)」「不明 (Unknown)」を厳密に区別します。
