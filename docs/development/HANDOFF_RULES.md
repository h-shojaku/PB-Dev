# Handoff Rules

## 1. Standard Location
BuilderからPlannerへの提出物は、リポジトリルート配下の以下のディレクトリを唯一の標準配置場所とします。

```text
handoff/planner/
```

- `handoff/planner/` 配下に直接 loose file（ZIP圧縮されていない個別ファイル）を提出してはいけません。

## 2. Exactly One ZIP Per Submission
- Plannerへの **1回の提出につき、提出物は必ず 1 ZIP ファイル** とします。
- **標準命名規則**: `<TASK-ID>_PLANNER_HANDOFF.zip` （例: `DEV-TASK-0002_PLANNER_HANDOFF.zip`）
- Plannerへ個別のMarkdown、画像、ログ、patch等をバラバラに渡すことは禁止します。すべての関連成果物はZIP内部に格納します。

## 3. Maximum Size Limit
- Handoff ZIPのファイルサイズは **500 MB 以内** とします。
- 500 MB を超える場合は、ビルド成果物、依存パッケージ（`node_modules` 等）、キャッシュ、`.git` ディレクトリ、再生成可能な大容量ファイルを除外します。
- 不要ファイルを除外してもなお 500 MB を超える場合のみ、人間判断対象（BLOCK）とします。

## 4. Delivery Artifact Concept
- Handoff ZIPはPlannerへの「配送物（Delivery Artifact）」であり、リポジトリのProduct SSOTそのものではありません。
- 正式な仕様・コード・変更履歴はリポジトリ（Git）を正とします。

## 5. Required ZIP Internal Structure
Handoff ZIP内部は、最低限以下の構造を持たなければなりません。

```text
<TASK-ID>_PLANNER_HANDOFF.zip
│
├── REPORT.md
├── MANIFEST.md
└── files/
    └── (Plannerがレビューするために必要な成果物)
```

必要に応じて以下のディレクトリを併設できます（不要な大量ファイルの混入は避けること）。

```text
├── evidence/
├── logs/
├── screenshots/
└── diff/
```

### 5.1 REPORT.md
PlannerがZIP解凍直後に確認する主報告書です（標準テンプレート: `templates/PLANNER_REPORT_TEMPLATE.md` を使用）。
最低限以下のセクションを含みます。

```markdown
# Builder Report

## Task
## Status
## Summary
## Changes
## Verification
## Acceptance Criteria
## Human Decision
## Git State
## Known Issues
## Planner Review Guide
```

`Planner Review Guide` では、Plannerがどのファイルを確認すべきか、何に注意すべきかを明確に記載します。

### 5.2 MANIFEST.md
ZIP内部に含まれるコンテンツのインデックス情報です。以下を記載します。

- Task ID
- Handoff ZIP filename
- 作成日時（ISO 8601等）
- Repository root Absolute Path
- 含有ファイル一覧（パスと説明）
- ZIPファイルサイズ
- Git commit ID / Branch名（存在する場合）

### 5.3 files/ ディレクトリ
Plannerがレビューするために必要な変更ファイル・文書を、リポジトリ相対構造（`Repository-relative path`）を維持した形で格納します。

```text
files/
└── docs/
    └── development/
        ├── BUILDER_RULES.md
        ├── DECISION_RULES.md
        └── HANDOFF_RULES.md
```

## 6. Output & Notification Rules in Final Response
Builderがタスクを完遂し、Plannerへ引き渡す際の最終回答は、開発標準で定められたフォーマットに従い、**最後の1文**でHandoff ZIPの絶対パスを提示しなければなりません。

```text
これをPlannerに渡してください: <Handoff ZIPの絶対パス>
```
