# Development Documentation Area

このディレクトリは、リポジトリの開発標準・開発プロセス・運用ルール（Development SSOT）を管理する領域です。

## ドキュメント体系一覧

- [DEVELOPMENT_SYSTEM.md](./DEVELOPMENT_SYSTEM.md): AI開発標準（Planner/Builderモデル、SSOT原則、継続性原則、優先順位等）の最上位構造定義
- [BUILDER_RULES.md](./BUILDER_RULES.md): Builderの自律実行原則・Cold Startプロトコル・禁止事項・完了条件の定義
- [DECISION_RULES.md](./DECISION_RULES.md): 自律判断領域と人間判断のための停止境界の定義
- [TASK_RULES.md](./TASK_RULES.md): Task ID標準、Intake・登録・状態連動・ライフサイクル・不変性ルールの定義
- [REVIEW_RULES.md](./REVIEW_RULES.md): Planner Review Gate、エビデンス検証時期分類（Builder検証/人間検証）、判定3分類の定義
- [SESSION_RULES.md](./SESSION_RULES.md): AI/セッション切替、状態復元（Cold Start Recovery）、未永続化判断の取り扱い、機密情報非保存ルールの定義
- [GIT_RULES.md](./GIT_RULES.md): Git / GitHub バージョン管理・コミット・プッシュ・Remote安全性確認の定義
- [HANDOFF_RULES.md](./HANDOFF_RULES.md): Planner Handoff ZIP（`受け渡し/` ディレクトリにおける最新1 ZIP運用・Continuity Package）の構成・作成ルールの定義
- [DEFINITION_OF_DONE.md](./DEFINITION_OF_DONE.md): タスク完了時の共通最小品質条件（DoD）の定義
- [PROJECT_INITIALIZATION_RULES.md](./PROJECT_INITIALIZATION_RULES.md): テンプレート複製後のプロジェクト初期化（NEW_PRODUCT / EXISTING_PRODUCT）手続きの定義
