# Handoff Rules

## 1. Standard Location
BuilderからPlannerへの成果物受け渡しは、リポジトリルート直下の以下のディレクトリを唯一の標準配置場所とします。

```text
受け渡し/
```

- `受け渡し/` はPlannerへ提出する配送物（Delivery Artifacts）専用の領域です。
- 旧 `handoff/planner/` 領域は全廃されました。

## 2. Latest One ZIP Rule (最新1 ZIP必須ルール)
- Plannerへの提出物は、`受け渡し/` 直下に **常に現在Plannerへ渡すべき最新のHandoff ZIP 1個のみ** を配置します。
- **標準命名規則**: `<TASK-ID>_PLANNER_HANDOFF.zip` （例: `DEV-TASK-0004_PLANNER_HANDOFF.zip`）
- **禁止事項**:
  - `受け渡し/` 配下に過去タスクの旧ZIPを残すこと（複数ZIPの混在禁止）
  - `.gitkeep`, `.gitignore`, `README.md` 等のプレースホルダーファイルを置くこと
  - ZIP圧縮されていない個別ファイル（loose files）やサブディレクトリを置くこと

## 3. Cleanup Flow Before Handoff Generation
Builderが新しいHandoff ZIPを生成する際は、事前に以下のクリーンアップ・生成手順を自律的に実行します。

```text
タスク実装・検証完了
  ↓
Git コミット & プッシュ完了
  ↓
`受け渡し/` ディレクトリの存在確認（存在しなければ作成）
  ↓
`受け渡し/` 内の既存ファイルをすべて削除（旧ZIP等）
  ↓
最新の Handoff ZIP を生成して配置
  ↓
`受け渡し/` 内が最新ZIP 1個のみであることを検証
  ↓
Builder最終回答出力
```

## 4. Git Tracking Exception (.gitignore)
- `受け渡し/` 配下は配送物領域であり、Gitの追跡対象外（`.gitignore` 設定）とします。
- `受け渡し/` 内には `.gitkeep` 等を配置しないため、リポジトリを `git clone` した直後の状態では `受け渡し/` ディレクトリが存在しないことが正常です。
- フォルダが存在しない環境では、BuilderがHandoff ZIP作成時に必要に応じて自動作成します。

## 5. Maximum Size Limit
- Handoff ZIPのファイルサイズは **500 MB 以内** とします。
- 500 MB を超える場合は、ビルド成果物、依存パッケージ（`node_modules` 等）、キャッシュ、`.git` ディレクトリ、再生成可能な大容量ファイルを除外します。
- 不要ファイルを除外してもなお 500 MB を超える場合のみ、人間判断対象（BLOCK）とします。

## 6. Required ZIP Internal Structure
Handoff ZIP内部は、最低限以下の構造を持たなければなりません。

```text
<TASK-ID>_PLANNER_HANDOFF.zip
│
├── REPORT.md
├── MANIFEST.md
└── files/
    └── (Plannerがレビューするために必要な成果物)
```

- ZIP内部のファイルパスは、リポジトリ相対構造（`files/...`）を維持します。
- ZIP内部に `受け渡し/` ディレクトリ自体や過去の旧ZIPを含めてはなりません。

### 6.1 REPORT.md
PlannerがZIP解凍直後に確認する主報告書です（標準テンプレート: `templates/PLANNER_REPORT_TEMPLATE.md` を使用）。

### 6.2 MANIFEST.md
ZIP内部に含まれるコンテンツのインデックス情報です（Task ID, 作成日時, リポジトリ絶対パス, 含有ファイル一覧等）。

### 6.3 files/ ディレクトリ
Plannerがレビューするために必要な変更ファイル・文書をリポジトリ相対パス構造で格納します。

## 7. Output Rules in Final Response
Builderがタスクを完遂した際の最終回答は、**最後の1文**で新しいHandoff ZIPの絶対パスを明示しなければなりません。

```text
これをPlannerに渡してください: <Repository Root>\受け渡し\<TASK-ID>_PLANNER_HANDOFF.zip
```
