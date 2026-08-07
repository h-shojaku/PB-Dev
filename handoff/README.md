# Handoff Area

このディレクトリは、BuilderからPlannerへ提出する成果物の標準配置場所です。

## 構造
- `planner/`: Planner向け成果物（Handoff ZIP）を配置するディレクトリ

## 目的と提出ルール
- BuilderからPlannerへの成果物提出場所を本領域（`handoff/planner/`）に一元化します。
- **1回の提出につき必ず 1 ZIP ファイル** とします（標準命名: `<TASK-ID>_PLANNER_HANDOFF.zip`）。
- **loose file（ZIP圧縮されていない個別ファイル）の提出は禁止** されています。
- Handoff ZIPのファイルサイズ上限は **500 MB 以内** です。
- 提出物（ZIP）の内部構造・レポート作成フォーマット・詳細ルールについては、Development SSOT（[HANDOFF_RULES.md](../docs/development/HANDOFF_RULES.md)）に従います。
