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
- **標準命名規則**: `<TASK-ID>_PLANNER_HANDOFF.zip` （例: `DEV-TASK-0006_PLANNER_HANDOFF.zip`）
- **禁止事項**:
  - `受け渡し/` 配下に過去タスクの旧ZIPを残すこと（複数ZIPの混在禁止）
  - `.gitkeep`, `.gitignore`, `README.md` 等のプレースホルダーファイルを置くこと
  - ZIP圧縮されていない個別ファイル（loose files）やサブディレクトリを置くこと

## 3. Cross-platform ZIP Format (クロスプラットフォームZIP仕様)
Handoff ZIPはWindows / macOS / Linux等、展開するOS環境に依存せず同一の論理構造として展開できなければなりません。

- **POSIXパス区切り規定**: ZIP内部のすべてのエントリ名（entry path）は、実行OSに関わらず **POSIX形式 `/` に統一** します。
- **バックスラッシュ禁止**: ZIPエントリ名に Windows ネイティブの `\` （バックスラッシュ）を含めることは厳禁とします。
- **絶対パス・親階層移動禁止**: ZIPエントリ名に絶対パス（ドライブ文字 `C:` や先頭 `/`）、親トラバーサル `..` を含めてはなりません。
- **無効なフォルダ構造防止**: OSネイティブの区切り文字をそのままZIPエントリ名に使用することで「バックスラッシュを含む単一ファイル名」として誤展開される不具合を防止します。

## 4. Standard Generator & Automated Verification
- Builderは手動ZIP作成やOS固有の圧縮コマンドではなく、リポジトリに配備された標準スクリプト（`scripts/create_handoff.py` または `scripts/create_handoff.ps1`）を使用してZIPを生成します。
- **自動検証必須**: ZIP生成後、以下の自動検証（Verification Metrics）がすべて合格（PASS）することがタスク完了の必須条件となります。
  1. ZIPファイルが存在し、500 MB 以内であること
  2. アーカイブの整合性（CRC・ヘッダー）に異常がないこと
  3. ルートに `REPORT.md` および `MANIFEST.md` が存在すること
  4. ZIPエントリ名に `\` が0件であること
  5. ZIPエントリ名に絶対パス、ドライブ文字、`..` が0件であること
  6. `.git` ディレクトリが含まれていないこと
  7. 実際に一時ディレクトリへ展開し、正常に解凍できること（Extraction Test PASS）
  8. `受け渡し/` 内が最新ZIP 1個のみ（通常ファイル数=1, ZIP数=1, サブディレクトリ数=0）であること

## 5. Cleanup Flow Before Handoff Generation
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
標準スクリプト (scripts/create_handoff.ps1 等) で最新 Handoff ZIP 生成
  ↓
アーカイブ自動検証・展開テスト実行
  ↓
`受け渡し/` 内が最新ZIP 1個のみであることを検証
  ↓
Builder最終回答出力
```

## 6. Git Tracking Exception (.gitignore)
- `受け渡し/` 配下は配送物領域であり、Gitの追跡対象外（`.gitignore` 設定）とします。
- `受け渡し/` 内には `.gitkeep` 等を配置しないため、リポジトリを `git clone` した直後の状態では `受け渡し/` ディレクトリが存在しないことが正常です。
- フォルダが存在しない環境では、標準スクリプトがHandoff ZIP作成時に自動作成します。

## 7. Maximum Size Limit
- Handoff ZIPのファイルサイズは **500 MB 以内** とします。
- 500 MB を超える場合は、ビルド成果物、依存パッケージ（`node_modules` 等）、キャッシュ、`.git` ディレクトリ、再生成可能な大容量ファイルを除外します。
- 不要ファイルを除外してもなお 500 MB を超える場合のみ、人間判断対象（BLOCK）とします。

## 8. Required ZIP Internal Structure
Handoff ZIP内部は、最低限以下の構造を持たなければなりません。

```text
<TASK-ID>_PLANNER_HANDOFF.zip
│
├── REPORT.md
├── MANIFEST.md
└── files/
    ├── tasks/
    │   ├── TASK_REGISTER.md
    │   └── completed/ (または active/)
    │       └── <TASK-ID>.md
    └── (Plannerがレビューするために必要な変更成果物)
```

- Plannerがタスク要求と成果物を直接対比レビューできるよう、**対象Task文書（`files/tasks/completed/<TASK-ID>.md` 等）および `files/tasks/TASK_REGISTER.md` をZIP内に含めることを必須**とします。
- ZIP内部のファイルパスは、POSIX `/` 区切りのリポジトリ相対構造（`files/docs/development/...`）を維持します。
- ZIP内部に `受け渡し/` ディレクトリ自体や過去の旧ZIPを含めてはなりません。

### 8.1 REPORT.md
PlannerがZIP解凍直後に確認する主報告書です（標準テンプレート: `templates/PLANNER_REPORT_TEMPLATE.md` を使用）。
`Task Lifecycle Self-Application` セクションおよび `ZIP Portability Verification` セクションを含め、検証結果を記録します。

### 8.2 MANIFEST.md
ZIP内部に含まれるコンテンツのインデックス情報です（Task ID, 作成日時, リポジトリ絶対パス, POSIX `/` 形式の含有ファイル一覧等）。

### 8.3 files/ ディレクトリ
対象 Task 文書および Planner がレビューするために必要な変更ファイル・文書をリポジトリ相対パス構造（POSIX `/` 形式）で格納します。

## 9. Output Rules in Final Response
Builderがタスクを完遂した際の最終回答は、**最後の1文**で新しいHandoff ZIPの絶対パスを明示しなければなりません。

```text
これをPlannerに渡してください: <Repository Root>\受け渡し\<TASK-ID>_PLANNER_HANDOFF.zip
```
