# Git / GitHub Rules

## 1. GitHub as Version Control Platform
本プロジェクトおよび開発標準は、GitHubを正式なバージョン管理・同期基盤として利用します。

- **Canonical Repository**: [PROJECT_PROFILE.md](../../PROJECT_PROFILE.md) の `Canonical Remote` を正とします（`PB-Dev` 本体では `https://github.com/h-shojaku/PB-Dev.git`）。
- **Template派生プロジェクト**: 本リポジトリをテンプレートとして複製・作成された各製品リポジトリでは、`PROJECT_PROFILE.md` に設定された派生先リポジトリの GitHub URL を正式 Remote とします。

## 2. Standard Remote Name
- 正式 Remote 名は一律 `origin` とします。

## 3. Standard Branch
- 標準ブランチ名は `main` とします。

## 4. Remote Safety Check (派生リポジトリの誤Push防止)
- テンプレートから派生したプロダクトリポジトリの初期化時およびタスク実行時、Builder は `git remote -v` の `origin` URL が `PROJECT_PROFILE.md` の `Canonical Remote` と一致していることを確認します。
- 派生プロダクトが `PB-Dev.git` へ誤ってプッシュすることを防止するため、URL 不一致時はプッシュを停止します。

## 5. Task Completion Git Workflow
通常タスク（人間判断や技術的BLOCKがないタスク）において、Builderはタスク提出前に原則として以下のフローを自律的に完遂します。

```text
コード/ドキュメント変更
  ↓
検証 (Builder Verification & git diff --check)
  ↓
git commit (Intake コミットおよび最終コミット)
  ↓
git push origin main
  ↓
working tree clean 確認
  ↓
`受け渡し/` ディレクトリ準備 & 旧配送物削除
  ↓
標準スクリプト (scripts/create_handoff.ps1 / .py) で最新 1 ZIP 生成
  ↓
アーカイブ自動検証・展開テスト合格確認
  ↓
`受け渡し/` 内が最新 ZIP 1個のみであることを検証
```

- Handoff ZIPは原則として `commit` および `push` 完了後に生成し、`REPORT.md` および `MANIFEST.md` に確定した Git Commit ID および Branch 情報を記録します。

## 6. Commit Traceability & Message Format
各コミットは、対応するタスクとの相互追跡を可能にするためコミットメッセージに Task ID を含めます。

- **標準メッセージフォーマット**: `<TASK-ID>: <summary>`
- **例**: `DEV-TASK-0009: finalize reusable development template`

1タスク内で合理的な理由（機能単位の分離、Intake 永続化等）により複数コミットに分割することは認められますが、すべてタスクIDが含まれる必要があります。

## 7. Prohibited Destructive Operations
人間の明示的な承認なしに以下の破壊的・不可逆な Git 操作を行うことは禁止します。

- `git push --force` および `git push --force-with-lease`
- 公開済み・共有済みコミット履歴の `rebase` / 改ざん
- `git reset --hard` による未退避作業の破壊
- Remoteブランチの強制削除
- Tagの強制書き換え

## 8. Authentication & Credentials Safety
- GitHubの認証情報、アクセストークン、シークレットをリポジトリ内にコミット・保存してはなりません。
- 実行環境上に設定されている安全な Git / GitHub 認証（SSH Key, GitHub CLI, Credential Manager 等）を使用します。

## 9. Git Tracking Exceptions (.gitignore)
- 配送物領域である `受け渡し/` 配下は Git 追跡対象外とします（`.gitignore` に `受け渡し/` を設定）。
- `受け渡し/` 内には `.gitkeep` 等を保持させないため、Git追跡対象のフォルダ構造としては管理されません。
