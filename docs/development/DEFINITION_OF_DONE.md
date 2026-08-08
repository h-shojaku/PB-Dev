# Definition of Done (DoD — タスク完了定義)

当AI開発システムにおいて、タスクを COMPLETE と判定するための必須完了条件（Definition of Done）です。

---

## 1. Quality & Verification Criteria (品質・検証基準)

1. **Objective & Acceptance Criteria Met**:
   - タスク指示書（`tasks/active/<TASK-ID>.md`）に記載されたすべての受入条件を満たしていること。
2. **Empirical Verification Passed**:
   - 変更に関連する単体テスト、統合テスト、ビルドスクリプトを実行し、すべて正常合格（PASS）していること。
3. **No Known-Bad Retries & Adaptive Principle Compliance**:
   - 失敗した旧手順を繰り返さず、適応型ワークフロー（[ADAPTATION_RULES.md](ADAPTATION_RULES.md)）に従ってより確実な方法が選択されていること。

---

## 2. Source-First Handoff Criteria (ソースファーストHandoff基準)

1. **Tracked Repository Snapshot (`repository/`)**:
   - Handoff ZIP 内の `repository/` サブディレクトリに Git HEAD コミット追跡ファイルが 100% 格納されていること（`Missing Tracked Files = 0`）。
2. **Git Commit Binding**:
   - `REPORT.md` / `MANIFEST.md` に記載された Commit ハッシュと Git HEAD コミットハッシュが完全一致していること。
3. **Automated MANIFEST**:
   - `MANIFEST.md` が Generator によって実際の `repository/` スナップショットから自動生成されていること。
4. **POSIX Entries & Integrity**:
   - ZIP エントリー名がすべて POSIX `/` 形式であり、バックスラッシュ `\`、絶対パス、`..` が 0 件であること。
   - 解凍・オープンテスト（Extraction Test）に成功すること。
5. **Latest One ZIP Rule**:
   - `受け渡し/` ディレクトリ直下に最新の Handoff ZIP 1 個のみが配置されていること。

---

## 3. Git & Registry Sync Criteria (Git・レジスタ同期基準)

1. **Clean Working Tree**:
   - 必要なすべての変更が Git にコミットされ、Working tree が Clean 状態であること（`git status --porcelain` が空）。
2. **Remote Push Completed**:
   - 最新コミットが Canonical Remote (`https://github.com/h-shojaku/PB-Dev.git` `origin/main`) へ正常に Push されていること。
3. **SSOT & Registry Updated**:
   - `CURRENT_STATE.md` (`AWAITING_PLANNER_REVIEW`), `tasks/TASK_REGISTER.md` (`COMPLETED`), および `tasks/completed/<TASK-ID>.md` が正しく更新・移動されていること。
