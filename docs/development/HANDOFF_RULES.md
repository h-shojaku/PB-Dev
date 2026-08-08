# Handoff Rules (成果物提出・検証規定)

## 1. Standard Location
BuilderからPlannerへの成果物受け渡しは、リポジトリルート直下の以下のディレクトリを唯一の標準配置場所とします。

```text
受け渡し/
```

- `受け渡し/` はPlannerへ提出する配送物（Delivery Artifacts）専用の領域です。

---

## 2. Latest One ZIP Rule (最新1 ZIP必須ルール)
- Plannerへの提出物は、`受け渡し/` 直下に **常に現在Plannerへ渡すべき最新のHandoff ZIP 1個のみ** を配置します。
- **標準命名規則**: `<TASK-ID>_PLANNER_HANDOFF.zip` （例: `DEV-TASK-0015_PLANNER_HANDOFF.zip`）
- **禁止事項**:
  - `受け渡し/` 配下に過去タスクの旧ZIPを残すこと（複数ZIPの混在禁止）
  - `.gitkeep`, `.gitignore`, `README.md` 等のプレースホルダーファイルを置くこと
  - ZIP圧縮されていない個別ファイル（loose files）やサブディレクトリを置くこと

---

## 3. Required ZIP Internal Structure: Tracked Repository Snapshot
Handoff ZIP内部は、Builderが手動選択した一部ファイルではなく、**Git HEAD コミットにおける追跡対象ソースコード全域（Tracked Repository Snapshot）**を含まなければなりません。

```text
<TASK-ID>_PLANNER_HANDOFF.zip
├── REPORT.md
├── MANIFEST.md
└── repository/
    ├── README.md
    ├── PROJECT_PROFILE.md
    ├── CURRENT_STATE.md
    ├── AGENTS.md
    ├── CLAUDE.md
    ├── GEMINI.md
    ├── docs/
    ├── scripts/
    ├── tasks/
    ├── templates/
    └── ... (Git HEAD で追跡されているすべてのファイル)
```

- `repository/` 配下は `git archive HEAD` により機械抽出され、作業ツリーの未追跡ファイルや未コミットの差分は一切混入しません。
- **Commit Binding**: `REPORT.md` / `MANIFEST.md` に記載される Git コミットハッシュと `repository/` スナップショットの元コミットは 100% 一致（Git HEAD）しなければなりません。

---

## 4. Automated Manifest Generation
- `MANIFEST.md` の記述は Builder の手入力ではなく、Handoff Generator（`scripts/create_handoff.py`）により実際の `repository/` スナップショットおよび Git コミット情報から全自動生成されます。
- `MANIFEST.md` には、Task ID, コミットハッシュ, リモートURL, ブランチ, ファイル数実測値, ZIPサイズ, SHA256ハッシュ, および `repository/` 配下の全 POSIX パスリストが自動記録されます。

---

## 5. Cross-platform ZIP Format & Verification
- **POSIXパス区切り規定**: ZIP内部のすべてのエントリ名（entry path）は、実行OSに関わらず **POSIX形式 `/` に統一** します。
- **バックスラッシュ禁止**: ZIPエントリ名に Windows ネイティブの `\` を含めることは厳禁です。
- **絶対パス・親階層移動禁止**: ZIPエントリ名に絶対パス（`C:` や先頭 `/`）、親トラバーサル `..` を含めてはなりません。
- **自動検証項目**:
  1. ZIPファイルが存在し、500 MB 以内であること
  2. アーカイブの CRC・ヘッダー整合性に異常がないこと
  3. ルートに `REPORT.md` および `MANIFEST.md` が存在すること
  4. `repository/` 配下に Git HEAD 追跡ファイルが 100% 漏れなく存在すること（`Missing Tracked Files = 0`, `Unexpected Snapshot Files = 0`）
  5. エントリ名に `\` が 0 件であること
  6. エントリ名に絶対パス、ドライブ文字、`..` が 0 件であること
  7. 実際に一時ディレクトリへ展開し、正常に解凍できること（Extraction Test PASS）
  8. `受け渡し/` 内が最新ZIP 1個のみであること

---

## 6. Canonical Implementation & Pure Thin Wrapper
- **Canonical Implementation**: `scripts/create_handoff.py` が Handoff ZIP 生成および検証の唯一の正本ロジックです。
- **Thin Wrapper**: `scripts/create_handoff.ps1` は PowerShell 環境における完全な Thin Wrapper であり、ネイティブ ZIP 生成（`Compress-Archive` 等）やフォールバック処理を行わず、100% `create_handoff.py` へ処理を移送します。Python 実行環境が無効な場合は FAIL します。

---

## 7. Output Rules in Final Response
Builderがタスクを完遂した際の最終回答は、**最後の1文**で新しいHandoff ZIPの絶対パスを明示しなければなりません。

```text
これをPlannerに渡してください: <Repository Root>\受け渡し\<TASK-ID>_PLANNER_HANDOFF.zip
```
