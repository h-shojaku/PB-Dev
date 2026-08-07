# Session Rules

## 1. Purpose & AI Service Independence
本ドキュメント（`SESSION_RULES.md`）は、Planner / Builder の AI サービス変更、セッション切替、CLI 再起動、PC変更、作業中断等が発生した場合に、チャット履歴や AI 内部記憶に依存せず、リポジトリのみから開発状態を完全復元（Continuity & Recovery）するための開発標準を定義します。

本規定は特定の AI サービス（ChatGPT, Claude, Gemini, Codex等）に依存せず、将来の未知の AI モデルやツールに対しても統一して適用されます。

## 2. Builder Cold Start Protocol (Cold Start 順序)
新しい Builder AI または新しい CLI セッションがリポジトリを初めて開いた場合、以下の標準順序で情報を取得し、開発状況を把握します。

```text
1. リポジトリルートの存在確認
2. AI Adapter (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md` 等) の確認
3. `README.md` の確認
4. `docs/development/DEVELOPMENT_SYSTEM.md` の確認
5. `CURRENT_STATE.md` (Current State Index) の確認
6. `tasks/TASK_REGISTER.md` の確認
7. `tasks/active/` の確認
8. Active Task が存在する場合はそのタスク定義書 (`<TASK-ID>.md`) の確認
9. 関連する Product SSOT および Development SSOT の確認
10. Git 状態 (`git status`, `git log -n 5`) の確認
11. 復元判定 (Recovery State)
12. 作業再開 または 待機 (IDLE / AWAITING_PLANNER_REVIEW)
```

## 3. Fallback Entry Point for Unknown / Future AI
リポジトリ内に専用の AI Adapter（`CLAUDE.md` 等）が存在しない新しい AI モデルや汎用 CLI の場合は、以下の汎用エントリポイントに従って状態を復元します。

```text
README.md -> AGENTS.md -> docs/development/DEVELOPMENT_SYSTEM.md -> CURRENT_STATE.md
```

## 4. Intentional Builder Session Switch Protocol (意図的なセッション切替)
CLIの切り替えやセッション更新等、意図的に Builder セッションを変更する場合は、変更前に以下のチェックポイントを作成します。

1. 作業ツリーの状態 (`git status`) を確認する。
2. 構文エラーやビルド破壊、機密情報の混入がないか検証する。
3. 実施済み作業および残作業を `CURRENT_STATE.md` に簡潔に更新する。
4. 安全にコミット可能な状態である場合、Task ID を含むチェックポイントコミット（例: `<TASK-ID>: checkpoint before session switch`）を作成し、`origin main` へプッシュする。
5. ビルドエラー等により安全にコミットできない場合は、破壊的なコミットを避け、`CURRENT_STATE.md` に未コミットの作業ツリー状態を記録してローカル作業ツリーを保持する。

## 5. Unexpected Interruption Recovery (予期せぬ中断からの復旧)
AI クラッシュ、ターミナル強制終了、PC再起動等により事前チェックポイントなしで中断された場合、新セッションは推測で作業を再作成せず、以下の順序で状態を復元します。

```text
CURRENT_STATE.md -> TASK_REGISTER.md -> tasks/active/ -> git status -> git diff -> git log
```

- 未コミットの変更が存在する場合は、`git diff` を確認して直前の作業内容を特定し、タスク要件と対比して再開します。

## 6. Active Task Recovery Rule
- `tasks/active/` にタスクファイルが存在する場合、新 Builder は原則としてそのタスクを唯一の「現在タスク」として扱います。
- タスク定義書、`TASK_REGISTER.md`、`CURRENT_STATE.md`、および Git 履歴の間に矛盾がある場合は、[DEVELOPMENT_SYSTEM.md](./DEVELOPMENT_SYSTEM.md) の優先順位規定に従います。

## 7. BLOCKED Recovery Rule
- 現在タスクの状態が `BLOCKED` の場合、新 Builder は人間による意思決定（Human Decision）を独自に推測して勝手にブロックを解除してはなりません。
- 人間判断の入力または Planner からの明示的な指示が得られるまで、停止状態を維持します。

## 8. No Active Task Behavior Rule
- `tasks/active/` が空であり、`CURRENT_STATE.md` の Workflow Phase が `IDLE` または `AWAITING_PLANNER_REVIEW` の場合、Builder は未発行の次タスクを独断で捏造・作成・開始してはなりません。
- Planner からの次タスク投入を待機します。

## 9. Planner Session Switch & Recovery Protocol
Planner はブラウザ版 AI でありリポジトリを直接操作しないことを標準ケースとします。新しい Planner セッションへ切り替える場合は、以下の優先順位で開発状態を復元します。

1. **最新の Builder Handoff ZIP** (`受け渡し/<TASK-ID>_PLANNER_HANDOFF.zip`)
2. `CURRENT_STATE.md` (Handoff ZIP 内またはリポジトリ)
3. `REPORT.md` (Handoff ZIP 内)
4. `tasks/TASK_REGISTER.md`
5. 対象タスク定義書 (`files/tasks/completed/<TASK-ID>.md`)
6. Product SSOT / Development SSOT
7. Planner Session Handoff (`templates/PLANNER_SESSION_HANDOFF_TEMPLATE.md` を使用した一時引継ぎ文書)

## 10. Planner Unpersisted Decisions (未永続化判断の取り扱い)
- Planner のブラウザセッション内で決定された仕様判断・レビュー結果・次タスク方針であっても、Builder に渡されて `tasks/active/` へ登録・コミットされるまでは **リポジトリ未永続化状態** です。
- 未永続化の判断が存在する状態で Planner セッションを切り替える場合は、[PLANNER_SESSION_HANDOFF_TEMPLATE.md](../../templates/PLANNER_SESSION_HANDOFF_TEMPLATE.md) に従って一時引継ぎ文書を作成します。
- この文書は正式な SSOT ではなく参考 Context であり、Builder が Task Intake を行って Git コミットした時点で正式に永続化されます。

## 11. Context Minimization Rule (コンテキスト最小化)
引き継ぎ文書や Handoff において、コンテキストの肥大化を防ぐため以下を徹底します。

- リポジトリ全文や過去チャットログ全文、大量のローログを不要にコピーしない。
- 代わりに「結果」「決定事項」「現在状態」「未完了事項」「参照パス」を記録する。

## 12. Chain-of-Thought & Secret Non-Persistence Rules
- **思考過程の非永続化**: AI の内部推論（private chain-of-thought, scratchpad）をリポジトリや引き継ぎ文書に保存してはなりません。記録するのは「決定事項」「理由（最小限）」「結果」「エビデンス」のみとします。
- **機密情報の非保存**: パスワード、APIキー、アクセストークン、秘密鍵等の認証情報を引き継ぎ文書やリポジトリにコミットしてはなりません。

## 13. Recovery Verification Protocol
AI / セッション切替後の復元が正常であるか検証するため、新セッションは作業開始前に「リポジトリ識別」「現在のWorkflow Phase」「現在タスク」「人間判断の有無」「Git状態」「次にとるべきアクション」が一意に特定できることを確認します。
