# Review Rules (Planner レビュー規定)

## 1. Source-First Review Principle (ソースファースト・レビュー原則)

Planner Review における一次真実（Source of Truth）は、Builder の作成したレポート（`REPORT.md`）ではなく、**Handoff ZIP 内の `repository/` スナップショットに格納された実際のソースコード（Tracked Repository Source）**です。

---

## 2. Review Evidence Hierarchy (レビュー根拠の優先順位)

1. **Actual Tracked Source at declared Git commit**（`repository/` 配下のソースコード正本）
2. **Planner Independent Verification Result**（Planner 自身によるソースコード直接検査・独立テスト実行結果）
3. **Builder Verification Evidence**（Builder 実行ログ・テスト結果）
4. **REPORT / MANIFEST Summary**（レポート・サマリー文書）

REPORT は重要な説明文書ですが、実際のソースコードや独立検証結果を超える真実ではありません。

---

## 3. Planner Review Standard Procedure (標準レビュー手順)

Planner は以下の手順に従ってレビューを実施します。

1. **Commit & Task Verification**:
   - `REPORT.md` / `MANIFEST.md` から Task ID, 対象 Git Commit ハッシュ, Branch, リモートURLを確認します。
2. **Source Direct Inspection**:
   - `repository/` サブディレクトリを展開し、タスクの受入条件（Acceptance Criteria）および関連 SSOT（`docs/product/`, `docs/development/`）と照合してコード・文書を直接検査します。
3. **Independent Verification Execution**:
   - 可能な場合、Planner 実行環境において同梱されているテストスクリプト（例: `python scripts/test_initialize_project.py`, `python scripts/create_handoff.py --test`, `npm test` 等）を直接再実行し、動作を独立検証します。
4. **Evidence Comparison**:
   - Planner の独立検証結果と Builder レポートの記載内容を比較検証します。
5. **Review Decision**:
   - 基準を満たしていれば `COMPLETED` として承認し、不足や不一致がある場合は具体的な指摘とともに `CHANGES_REQUIRED` を発行します。
