# Definition of Done (DoD)

## 1. Purpose
本ドキュメント（`DEFINITION_OF_DONE.md`）は、当開発システムにおけるタスク完了の「標準最小品質条件（Definition of Done）」を定義します。
個別のタスク定義書に記載される「タスク固有の受入条件（Task-specific Acceptance Criteria）」を置き換えるものではなく、**すべてのタスクにおいて共通して満たすべき基本条件**として適用されます。

## 2. Standard Task Definition of Done Checklist
人間判断による例外指示または作業一時停止（BLOCKED）がない通常のタスクは、以下の全項目を満たして初めて `COMPLETE` と判定されます。

### 2.1 Instruction & Scope DoD
- [ ] **対象タスクの合致**: `tasks/active/` に配置された正しい Active Task を実行している。
- [ ] **指示の不変性維持**: タスク定義書（Instruction Record）の本文・要件・受入条件を独断で改変していない。
- [ ] **スコープ境界の遵守**: タスク指示のスコープ外である不必要な大改修や無関係な変更を行っていない。

### 2.2 Implementation & Quality DoD
- [ ] **目的達成**: タスクの Objective および要件を満たす実装・ドキュメント更新を行っている。
- [ ] **受入条件達成**: タスク固有の Acceptance Criteria をすべて満たしている。
- [ ] **SSOT 同期**: 変更に対応する Product SSOT および Development SSOT を整合的に更新している。
- [ ] **無関係な変更の排除**: 意図しない一時ファイルやデバッグコードを残していない。

### 2.3 Verification DoD
- [ ] **技術検証の実行**: タスク完了に必要なユニットテスト、ビルド、リンターチェック、型チェック等の技術検証（Builder Verification）を実行している。
- [ ] **失敗の非隠蔽**: エラーやテスト失敗、例外を握り潰したり誤魔化したりせず、正常通過（PASS）している。
- [ ] **Git Diff チェック**: `git diff --check` を実行し、末尾空白やコンフリクトマーカー等の構文エラーがないことを確認している（PASS）。
- [ ] **エビデンス記録**: 実施した検証内容と結果を `REPORT.md` に正しく記録している。

### 2.4 Task State & Registry DoD
- [ ] **ファイル移動**: 完了したタスク定義書を `tasks/active/` から `tasks/completed/<TASK-ID>.md` へ移動している。
- [ ] **タスクレジスタ更新**: `tasks/TASK_REGISTER.md` のタスク状態を `COMPLETED` に更新し、完了日を記録している。
- [ ] **カレントステート更新**: ルートの `CURRENT_STATE.md` の Workflow Phase を `AWAITING_PLANNER_REVIEW`、Current Task を `None` に更新している。

### 2.5 Version Control (Git) DoD
- [ ] **コミット作成**: タスクに関連するすべての変更を Git コミットに含めている。
- [ ] **追跡可能コミットメッセージ**: コミットメッセージにタスク ID（例: `<TASK-ID>: <summary>`）を含めている。
- [ ] **Remote 安全性**: Git の `origin` Remote URL が `PROJECT_PROFILE.md` の Canonical Remote と一致している。
- [ ] **GitHub 同期**: コミットを正式ブランチ（`main`）の `origin` へ正常に `git push` 完了している。
- [ ] **作業ツリーのクリーン化**: コミットおよびプッシュ後、追跡対象の作業ツリー（`git status`）が clean である。

### 2.6 Handoff Package DoD
- [ ] **最新1 ZIP 運用**: `受け渡し/` ディレクトリ直下に最新の Handoff ZIP (`<TASK-ID>_PLANNER_HANDOFF.zip`) 1個のみが存在する。
- [ ] **サイズ制限**: Handoff ZIP のファイルサイズが 500 MB 以内である。
- [ ] **標準スクリプト使用**: リポジトリ配備の標準スクリプト（`scripts/create_handoff.ps1` または `.py`）を使用して生成している。
- [ ] **アーカイブ整合性検証**: 自動検証（Integrity test, Security test）をすべて PASS している。
- [ ] **ポータブルパス検証**: ZIP 内部エントリパスがすべて POSIX 形式 `/` に統一され、バックスラッシュ `\` や絶対パスが含まれていない（PASS）。
- [ ] **解凍テスト**: 自動解凍テスト（Extraction test）が合格（PASS）している。
- [ ] **必須コンテンツ同梱**: ルートに `REPORT.md`, `MANIFEST.md` を、`files/` 配下に `CURRENT_STATE.md`, `TASK_REGISTER.md`, 対象タスク定義書、および変更成果物・SSOT を同梱している。

### 2.7 Final Response DoD
- [ ] **ステータス明示**: タスクのステータス（COMPLETE）を明確に宣言している。
- [ ] **Git 状態明示**: Remote, Branch, Commit, Push, Working tree の状態を提示している。
- [ ] **人間判断明示**: 人間判断の要否（不要または必要事項）を明示している。
- [ ] **最終行の案内**: 最終回答の**最後の1文**が、生成された Handoff ZIP の実際の絶対パス案内で厳密に終了している。
  `これをPlannerに渡してください: <Repository Root>\受け渡し\<TASK-ID>_PLANNER_HANDOFF.zip`

## 3. BLOCKED Definition & DoD Exemption
- 人間判断が必要な場合や技術的障害によりタスクを完遂できない場合、無理に DoD を満たした振りをせず、ステータスを **`BLOCKED`** として扱います。
- `BLOCKED` 時は、タスクファイルを `tasks/active/` に維持し、`TASK_REGISTER.md` および `CURRENT_STATE.md` を `BLOCKED` に更新した上で、完了範囲・未完了範囲・ブロック理由・選択肢を `REPORT.md` および最終回答に記載します。
- 虚偽の `COMPLETE` 報告を行ってはなりません。

## 4. Precedence Rule
- タスク完了の評価においては、**「タスク固有の Acceptance Criteria」＋「標準 Definition of Done」** の両方を満たす必要があります。
- 競合が発生した場合は、[DEVELOPMENT_SYSTEM.md](./DEVELOPMENT_SYSTEM.md) の優先順位規定に従います。
