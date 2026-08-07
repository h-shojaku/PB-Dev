# DEV-TASK-0003 — Git / GitHub標準化・初回Repository同期・可搬性修正

## 0. Role

あなたはこのRepositoryの **Builder** です。

本Taskでは、これまで構築したPlanner / Builder型AI Development Standardを
正式にGitHubでバージョン管理できる状態へ移行してください。

今回から以下のGitHub Repositoryを本開発標準Repositoryの正式なRemoteとして使用します。

```text
https://github.com/h-shojaku/PB-Dev.git
```

人間判断が不要な限り、途中確認で停止せず、

```text
調査
→ Git標準整備
→ Portable link修正
→ Remote設定
→ Commit
→ Push
→ 検証
→ Planner Handoff ZIP生成
→ 最終報告
```

まで自律的に完了してください。

---

# 1. Current State

DEV-TASK-0002までで、少なくとも以下のDevelopment SSOTが存在します。

```text
docs/development/
├── DEVELOPMENT_SYSTEM.md
├── BUILDER_RULES.md
├── DECISION_RULES.md
└── HANDOFF_RULES.md
```

また、

```text
handoff/planner/
```

をPlannerへの唯一の標準提出先とし、

- 1 submission = 1 ZIP
- 500MB以内
- loose file提出禁止
- Builder最終回答の最後にZIP絶対パスを記載
- 最終文は「これをPlannerに渡してください: <absolute path>」

というルールが定義済みです。

これら既存SSOTを尊重してください。

---

# 2. Objective

本Taskの目的は以下です。

1. GitHub Repository `https://github.com/h-shojaku/PB-Dev.git` を正式Remoteとして設定する
2. RepositoryをGitHubで継続的にバージョン管理できる状態にする
3. Git運用の基本SSOTを作成する
4. 初回の正式commit / pushを完了する
5. 標準Branchを `main` に統一する
6. Handoff ZIPをGit追跡対象から除外する
7. 既存文書に含まれるローカルPC依存の絶対リンクを除去する
8. Windows / macOS / 別PC / Repository複製でも壊れない可搬性を確保する
9. Task完了時にworking tree cleanを確認する
10. 本Task自身を新しいGit/Handoffルールに従って提出する

---

# 3. Canonical GitHub Repository

本Repositoryの正式GitHub Remoteは以下で固定します。

```text
https://github.com/h-shojaku/PB-Dev.git
```

Git remote名は標準的に、

```text
origin
```

とします。

最終的に以下が成立していること。

```text
origin -> https://github.com/h-shojaku/PB-Dev.git
```

既存 `origin` が存在する場合は内容を確認してください。

### Existing origin handling

- 同じURLならそのまま利用
- 異なるURLなら、今回の人間明示指示を優先し上記URLへ修正
- Remote設定の履歴をREPORTへ記録

---

# 4. Default Branch

本開発標準Repositoryでは標準Branchを以下に統一します。

```text
main
```

現在のBranchが `master` の場合は、安全に `main` へ変更してください。

例：

```bash
git branch -M main
```

ただし既存Git履歴やRemoteに既存Branchがある場合は事前調査し、
破壊的な上書きをしないこと。

Remote Repositoryが空の場合は、
通常の初回pushとして `main` を作成してください。

---

# 5. Create GIT_RULES.md

以下を作成してください。

```text
docs/development/GIT_RULES.md
```

最低限、以下を定義します。

---

## 5.1 GitHub as Version Control Platform

正式Remote:

```text
https://github.com/h-shojaku/PB-Dev.git
```

Templateから派生した各Product Repositoryでは、
派生先RepositoryのURLへ置換できる設計にする。

`PB-Dev` 固有URLを「全Product共通のRemote」と誤解させないこと。

このRepository自体では上記URLがCanonical Remoteである。

---

## 5.2 Standard Remote

```text
origin
```

を正式Remote名とする。

---

## 5.3 Standard Branch

```text
main
```

を標準Branchとする。

---

## 5.4 Task Completion Git Principle

人間判断や技術的BLOCKがない通常Taskでは、
BuilderはTask提出前に原則以下まで完了する。

```text
変更
↓
検証
↓
git diff確認
↓
commit
↓
push origin main
↓
working tree clean確認
↓
Handoff ZIP生成
```

Handoff ZIPは、原則としてcommit / push完了後に作成し、
REPORT / MANIFESTへ確定Commit IDを記録する。

Definition of Done全体は後続Taskで詳細化するが、
Git部分については本Taskから適用する。

---

## 5.5 Commit Traceability

Taskに対応するcommitはTask IDを含める。

標準形式：

```text
<TASK-ID>: <summary>
```

例：

```text
DEV-TASK-0003: establish GitHub workflow
```

1 Task内で合理的な理由により複数commitとなることは許可するが、
Taskとの対応が追跡できること。

---

## 5.6 No Destructive Git Operations

人間の明示判断なしに以下を行わない。

- `git push --force`
- `git push --force-with-lease`
- 公開済み履歴のrebase / rewrite
- 既存Remote履歴の破壊
- `git reset --hard` による未退避作業破棄
- Branchの強制削除
- Tagの強制変更

---

## 5.7 Authentication / Identity

GitHub認証情報やSecretをRepositoryへ保存しない。

既存の安全なGit / GitHub認証環境を使用する。

Commitに必要な `user.name` / `user.email` が既に設定されている場合はそのまま使用する。

設定が存在せずcommitできない場合：

- 架空のidentityを作らない
- global Git configを勝手に変更しない
- 安全に完了できる範囲まで進める
- 必要な人間判断として報告する

---

# 6. Handoff ZIP and Git

Planner Handoff ZIPは配送物であり、
GitHubで永続管理する正式成果物ではありません。

以下をGit追跡対象外としてください。

```text
handoff/planner/*.zip
```

必要に応じて `.gitignore` を作成または更新します。

ただし、

```text
handoff/planner/
```

ディレクトリ自体の存在は維持できるよう `.gitkeep` 等を使用してよい。

既存 `.gitignore` を破壊しないこと。

---

# 7. Repository Portability Fix

DEV-TASK-0002成果物を確認すると、
Markdownリンクにローカル環境固有の絶対 `file:///...` URLが存在します。

例：

```text
file:///C:/Users/<user>/Documents/dev/PB-Dev/...
```

これはTemplate Repositoryとして不適切です。

本TaskでDevelopment Standard関連文書を調査し、
Repository内部の参照リンクを原則として**相対リンク**へ修正してください。

---

## 7.1 Forbidden for Internal Repository Links

Repository内ファイル同士の通常リンクで以下を使用しない。

```text
C:\Users\...
/Users/...
file:///C:/...
file:///Users/...
```

---

## 7.2 Preferred

例：

`docs/development/DEVELOPMENT_SYSTEM.md` から同階層なら、

```markdown
[Builder Rules](./BUILDER_RULES.md)
```

Repository rootの `README.md` からなら、

```markdown
[Development System](docs/development/DEVELOPMENT_SYSTEM.md)
```

AI Adapterからなら、

```markdown
[Development System](docs/development/DEVELOPMENT_SYSTEM.md)
```

など、GitHubでもローカルcloneでも解決可能な形式にする。

---

## 7.3 Absolute Paths Still Required for Handoff

注意：

Repository文書内の内部リンクは相対化するが、
Builder最終回答およびHandoff `MANIFEST.md` の

```text
Repository Root
Handoff ZIP path
```

については実行環境上の**絶対パス**を使用する。

つまり、

```text
SSOT document links = portable relative path
Builder delivery notification = actual absolute path
```

を明確に区別する。

---

# 8. ZIP Path Portability

Handoff ZIP内部のentry pathは、
可能な限りOS非依存になるよう `/` 区切りのRepository-relative pathとして格納してください。

推奨：

```text
files/docs/development/GIT_RULES.md
```

不要にWindows固有の `\` 区切りをZIP内部標準として固定しない。

Handoff ZIPの外側に表示する実ファイル絶対パスは、
実行OSの標準表記でよい。

---

# 9. DEVELOPMENT_SYSTEM.md Update

`docs/development/DEVELOPMENT_SYSTEM.md` を更新し、

```text
GIT_RULES.md
```

をGit詳細SSOTとしてリンクしてください。

Version Control Principleは少なくとも以下を明確にする。

- GitHubを正式なVersion Control Platformとする
- このRepositoryのCanonical Remoteは `https://github.com/h-shojaku/PB-Dev.git`
- 標準Branchは `main`
- 通常Taskではcommit / pushまでBuilderが自律実行する
- 詳細は `GIT_RULES.md`

Template派生RepositoryではRemote URLが派生先へ変更されることも明記する。

---

# 10. README Update

Repository root `README.md` にGitHub管理情報を簡潔に追加する。

最低限：

```text
Canonical Repository:
https://github.com/h-shojaku/PB-Dev
```

標準Branch：

```text
main
```

詳細Gitルール：

```text
docs/development/GIT_RULES.md
```

README内部リンクはportable relative linkにする。

---

# 11. AI Adapter Update

以下を確認する。

```text
AGENTS.md
CLAUDE.md
GEMINI.md
```

現在、ローカル `file:///...` リンクを使用している場合は相対リンクへ修正する。

詳細Gitルール本文をAdapterへ重複コピーしない。

必要なら、

```text
docs/development/GIT_RULES.md
```

を参照先として追加するだけにする。

---

# 12. Git Initialization / Initial Commit

現在Repositoryが、

- `git init` 済み
- 全ファイルuntracked
- commitなし
- Remote未設定

等の初期状態である可能性があります。

実際の状態をコマンドで調査してから処理してください。

通常ケースでは以下を完了する。

```text
1. Repository内容確認
2. .gitignore確認 / 更新
3. origin設定
4. main Branchへ統一
5. intentional filesをstage
6. commit
7. push -u origin main
8. remote / branch / commit / status確認
```

初回commitのsummaryはTask追跡可能にする。

推奨：

```text
DEV-TASK-0003: establish GitHub workflow
```

---

# 13. What to Commit

本Repositoryの開発標準として必要な、

- README
- AI Adapters
- docs/development/
- docs/product/の構造維持ファイル
- tasks/の構造維持ファイル
- reports/
- templates/
- handoffのREADME / .gitkeep
- Task文書等、現在Repositoryに存在し正式履歴として残すべき開発文書
- `.gitignore`

を調査して適切にcommitする。

以下はcommitしない。

- `handoff/planner/*.zip`
- credentials / secrets
- cache
- dependency directory
- OS一時ファイル
- 再生成可能な不要build artifact

何でも無差別に `git add .` して終わらせず、
stage対象を確認すること。

---

# 14. Remote Safety

Remote Repositoryに既存内容がある場合は、
必ずfetch / remote確認を行い、履歴を破壊しない。

Remoteが空であることを確認できた場合は、
通常の初回pushとして進めてよい。

Push時に認証が必要な場合は、
既存の認証環境を使用する。

認証失敗した場合も：

- local commitまで完了可能なら完了する
- remote設定を維持する
- 認証情報を要求・生成・保存しない
- REPORTでBLOCK理由と必要操作を明示する

---

# 15. Verification

最低限以下を実行・確認する。

```text
git remote -v
git branch --show-current
git status --short
git log -1 --oneline
git diff --check
```

可能であればRemoteも確認する。

```text
git ls-remote origin
```

Push後は以下を確認する。

- `origin` が `https://github.com/h-shojaku/PB-Dev.git`
- current branchが `main`
- upstreamが `origin/main`
- HEAD commitが存在
- push成功
- working tree clean
- Handoff ZIPだけがgitignore対象として存在してもcleanを維持できる

---

# 16. Search for Non-Portable Links

本Task完了前にDevelopment Standard対象ファイルを検索し、
ローカルユーザー環境依存リンクが残っていないことを確認する。

最低限以下を検索対象にする。

```text
file:///
C:\Users\
/Users/
PB-Dev/docs/
```

ただし `MANIFEST.md` やHandoff Reportに実行環境の絶対パスを記録する用途は除外する。

正式SSOT・README・AI Adapterの内部ナビゲーションに、
個人PC固定パスを残さないこと。

---

# 17. Handoff for This Task

本TaskのPlanner提出は必ず、

```text
handoff/planner/DEV-TASK-0003_PLANNER_HANDOFF.zip
```

の**1 ZIPのみ**とする。

500MB以内。

最低限以下を含める。

```text
DEV-TASK-0003_PLANNER_HANDOFF.zip
├── REPORT.md
├── MANIFEST.md
└── files/
    ├── README.md
    ├── .gitignore
    ├── AGENTS.md
    ├── CLAUDE.md
    ├── GEMINI.md
    └── docs/
        └── development/
            ├── DEVELOPMENT_SYSTEM.md
            └── GIT_RULES.md
```

実際に変更した他のDevelopment Standardファイルも、
Plannerレビューに必要なら `files/` 内へ追加する。

REPORTには最低限以下を明記。

```text
Remote
Branch
Commit ID
Push result
Working tree status
Portable link修正結果
Human Decision
```

---

# 18. Final Response Format

最終回答はDevelopment SSOTのHandoff規則に従う。

最低限：

```text
Task: DEV-TASK-0003
Status: COMPLETE / BLOCKED

実施内容:
- ...

検証:
- ...

Git:
- Repository root: <absolute path>
- Remote: https://github.com/h-shojaku/PB-Dev.git
- Branch: main
- Commit: <commit id>
- Push: <result>
- Working tree: <state>

人間判断:
- 不要
または
- 必要: <reason>

Planner Handoff:
- Filename: DEV-TASK-0003_PLANNER_HANDOFF.zip
- Size: <size>
- Absolute path: <absolute path>

これをPlannerに渡してください: <Handoff ZIPの絶対パス>
```

**最後の1文より後には何も記載しないこと。**

---

# 19. Acceptance Criteria

以下をすべて満たせばCOMPLETE。

- [ ] `origin` が `https://github.com/h-shojaku/PB-Dev.git` に設定されている
- [ ] 標準Branchが `main` になっている
- [ ] `docs/development/GIT_RULES.md` が存在する
- [ ] `DEVELOPMENT_SYSTEM.md` から `GIT_RULES.md` へ辿れる
- [ ] root READMEにCanonical GitHub Repositoryが明示されている
- [ ] `handoff/planner/*.zip` がGit追跡対象外になっている
- [ ] Development Standard文書の内部リンクがportable relative linkへ修正されている
- [ ] AI Adapterに個人PC固定 `file:///...` linkが残っていない
- [ ] ZIP内部entry pathが可能な限りOS非依存になっている
- [ ] intentional Repository filesがcommitされている
- [ ] commit messageからTask IDを追跡できる
- [ ] GitHub `origin/main` へpushされている
- [ ] upstreamが設定されている
- [ ] `git diff --check` が成功している
- [ ] working treeがcleanである
- [ ] `DEV-TASK-0003_PLANNER_HANDOFF.zip` が作成されている
- [ ] Handoff ZIPは500MB以内
- [ ] REPORTにRemote / Branch / Commit / Push結果がある
- [ ] 最終回答にHandoff ZIP絶対パスがある
- [ ] 最終文が「これをPlannerに渡してください: <absolute path>」である

---

# 20. If Push Cannot Complete

GitHub認証など人間しか解決できない理由でpushのみ失敗した場合は、
成功したように装わない。

その場合でも安全に可能な範囲として、

- Portable link修正
- GIT_RULES作成
- origin設定
- main化
- local commit
- Handoff作成

までは自律的に完了する。

Statusは必要に応じて `BLOCKED` とし、
人間が行う必要のある最小操作をREPORTに明記する。

認証問題以外の自己解決可能なGitエラーは、
途中確認せずBuilder自身で調査・修正する。

---

# 21. Scope Boundary

本TaskではGit/GitHub基盤を確立する。

以下は後続Taskへ残す。

- Task lifecycle完全版
- Planner Rules完全版
- Review lifecycle
- Session / AI切替完全版
- Definition of Done全体
- Product初期化フロー
- GitHub Actions
- CI/CD
- Pull Request必須化
- Release / Tag戦略

今回の目的は、

**「PB-Dev自体がGitHub上で正式に管理され、どのPC・どのAIからでも壊れず参照できる開発標準Repositoryになること」**

です。
