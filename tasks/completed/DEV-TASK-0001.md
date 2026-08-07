# DEV-TASK-0001 — AI Development Standard 基盤整備

## 0. Role

あなたはこのRepositoryの **Builder** です。

このTaskでは、今後複数の製品開発・既存製品アップデートで再利用できる
「Planner / Builder型 AI開発標準」のRepository基盤を整備してください。

Plannerはブラウザ版AI、BuilderはVSCode + CLI型AIを利用します。
ただし、ChatGPT / Codex / Claude / Gemini等の**特定AIサービスへ依存しない構造**にしてください。

本Taskは「開発標準の土台を作るTask」です。
Planner / Builderの詳細権限、Handoff ZIPの詳細仕様、Git運用詳細などは後続Taskで定義します。
このTaskで先回りして詳細仕様を大量に確定しないでください。

---

# 1. Objective

今後このRepositoryをTemplate Repositoryとして複製し、

- 新規製品開発
- 既存製品の分析
- 既存製品のアップデート
- Planner AIの変更
- Builder AIの変更
- Planner / Builderのセッション切替

が発生しても、同じ開発体験を再現できる基盤を作る。

特に以下を成立させること。

1. Repositoryが開発状態・ルールのSSOTとなる
2. チャット履歴に依存しない
3. Planner / Builderという役割名を固定する
4. AIサービス固有ファイルと共通ルールを分離する
5. 後続Taskでルールを段階的に追加できる
6. Repository TOPにPlannerとの受け渡し領域を確保する
7. GitHubによるバージョン管理を前提とする

---

# 2. Core Principles

今回、以下の原則をRepository上に明文化してください。

## 2.1 Repository is SSOT

会話履歴やAIの内部記憶を正式な仕様・履歴として扱わない。

正式な情報はRepository内のSSOTへ反映する。

概念上は以下とする。

- Chat / AI session = 作業場所
- Repository = 記憶・仕様・履歴

---

## 2.2 Role Separation

役割名は以下で固定する。

### Planner

- ブラウザ版AI
- 計画・仕様判断・Task作成・Builder成果物レビューを担当
- 特定AIサービス名を意味しない

### Builder

- VSCode + CLI型AI
- Repositoryを直接扱い、調査・実装・検証・文書更新等を担当
- 特定AIサービス名を意味しない

今後AIサービスが変更されても、役割名は変更しない。

---

## 2.3 AI Agnostic

共通の開発ルールを、

- AGENTS.md
- CLAUDE.md
- GEMINI.md
- その他AI固有ファイル

へ重複記載しない。

AI固有ファイルは共通SSOTへの入口・Adapterとして扱う。

共通ルールは `docs/development/` 以下を正とする。

---

## 2.4 Autonomous by Default

Builderは、人間判断が不要な作業については自律的に進行する。

ただし、この原則の詳細な停止条件・判断境界は後続Taskで正式定義する。

本Taskでは原則のみ明文化する。

---

# 3. Required Repository Structure

既存Repositoryの構成を確認したうえで、既存資産を壊さず、以下を基本構造として整備してください。

```text
/
├── README.md
├── AGENTS.md
├── CLAUDE.md
├── GEMINI.md
│
├── handoff/
│   ├── README.md
│   └── planner/
│       └── .gitkeep
│
├── docs/
│   ├── development/
│   │   ├── DEVELOPMENT_SYSTEM.md
│   │   └── README.md
│   │
│   └── product/
│       └── README.md
│
├── tasks/
│   ├── active/
│   │   └── .gitkeep
│   ├── completed/
│   │   └── .gitkeep
│   └── README.md
│
├── reports/
│   └── README.md
│
└── templates/
    └── README.md
```

### Important

既存Repositoryにすでに同等のディレクトリ・文書・命名規則が存在する場合は、
無条件に重複作成しないこと。

既存構造を調査し、今回の標準構造へ安全に統合すること。

既存ソースコード・製品仕様・テスト・設定ファイル等を削除・移動しないこと。
大規模なRepository再編は本Taskの対象外。

---

# 4. DEVELOPMENT_SYSTEM.md

`docs/development/DEVELOPMENT_SYSTEM.md` を、この開発標準の最上位入口として作成してください。

本Taskでは詳細ルールを書き切らず、最低限以下を定義してください。

## Required Sections

```text
# Development System

## Purpose
## Source of Truth
## Roles
### Planner
### Builder
## AI Service Independence
## Autonomous Execution Principle
## Repository Areas
## Handoff Principle
## Version Control Principle
## Rule Precedence
## Future Standardization Areas
```

---

# 5. Rule Precedence

ルール競合時の基本優先順位を `DEVELOPMENT_SYSTEM.md` に定義してください。

暫定的に以下の考え方とします。

1. 明示された最新の人間判断
2. Product SSOT
3. Development SSOT
4. Active Task
5. AI固有Adapter
6. AIサービス既定の慣習

ただし、既存Repositoryにこれより強い明示ルールがある場合は、
勝手に破壊・上書きせず、矛盾として報告してください。

---

# 6. AI Adapter Files

以下を作成または整理してください。

- `AGENTS.md`
- `CLAUDE.md`
- `GEMINI.md`

各ファイルは薄いAdapterとすること。

共通ルールをコピーして大量記載してはいけません。

最低限、

- 自分はBuilderとして動作すること
- `docs/development/DEVELOPMENT_SYSTEM.md` を最初に読むこと
- Repository SSOTをAIサービス固有慣習より優先すること
- Active Taskを確認して作業すること
- 人間判断不要なら自律的に進行すること

を記載してください。

AIによってサポートされていない固有仕様がある場合でも、
架空の機能・設定を記載しないこと。

---

# 7. Handoff Directory

Repository TOPに以下を設置してください。

```text
handoff/
└── planner/
```

この領域は、BuilderからPlannerへ渡す成果物の標準配置場所とします。

最終的にはPlannerへの報告を原則1 ZIPに統一する予定です。

想定：

```text
handoff/planner/<TASK-ID>_PLANNER_HANDOFF.zip
```

最大サイズ：

```text
500 MB
```

ただし、ZIP詳細構造・生成条件・Git追跡方針・SHA256・Archive Log等は
**後続Taskで正式定義するため、本Taskでは実装しすぎないこと。**

`handoff/README.md` には、この領域の目的と
「詳細仕様はDevelopment SSOTに従う」旨だけ記載してください。

---

# 8. Git / GitHub Principle

GitHubをRepositoryのバージョン管理基盤として利用する前提を明文化してください。

本Taskでは以下までとします。

- 変更はGitで追跡可能であること
- Repositoryの正式状態はcommitされた内容を基準とすること
- GitHubへのpushを標準運用とすること
- Taskと変更履歴を追跡可能にする方針であること

Branch戦略、Commit形式、push条件、clean state、
`git diff --check`、Definition of Doneなどの詳細は後続Taskで定義します。

---

# 9. README.md

Repository TOPの `README.md` に、
このRepositoryが何であるかを短く明示してください。

少なくとも以下が分かる状態にします。

- このRepositoryは製品コードだけでなくAI開発標準を含む
- Planner = Browser AI
- Builder = VSCode + CLI AI
- AIサービスは交換可能
- 共通ルールの入口は `docs/development/DEVELOPMENT_SYSTEM.md`
- Plannerへの成果物は `handoff/planner/`
- GitHubで履歴管理する

既存READMEに製品説明がある場合は破壊せず、
「Development System」セクション等として追記してください。

---

# 10. Product / Task / Report / Template Areas

以下は本Taskでは「器」だけ整備してください。

## `docs/product/`

製品固有のSSOT領域。

詳細構造は後続Taskまたは各製品初期化Taskで定義する。

## `tasks/`

PlannerがBuilderへ渡すTaskの管理領域。

- `active/`
- `completed/`

を用意する。

Task lifecycleや命名規則の詳細は後続Task。

## `reports/`

分析・調査等の永続Report配置候補。

Handoff ZIPとは目的が異なることをREADMEで簡潔に区別する。

## `templates/`

Task、Handoff、Session Handoff等の標準テンプレート配置領域。

テンプレート本体は後続Taskで整備する。

---

# 11. Do Not Over-Implement

本Taskでは以下を詳細実装しないこと。

- Planner詳細ルール
- Builder詳細ルール
- 人間判断の詳細境界
- Task Template本体
- Task lifecycle詳細
- Planner Handoff ZIPの詳細構造
- ZIP自動生成Script
- Session Handoff詳細
- AI / Session切替手順詳細
- Review Rules詳細
- Git運用詳細
- Commit message規則詳細
- Definition of Done詳細
- Product SSOTの具体的テンプレート
- CI/CD
- GitHub Actions

後続Taskで順番に標準化する。

---

# 12. Existing Repository Safety

作業開始時に必ずRepository全体を調査してください。

以下を守ること。

- 既存ファイルを不用意に削除しない
- 既存仕様を推測で上書きしない
- 既存AI指示ファイルがある場合は内容を確認する
- 重複SSOTを作らない
- 既存ルールと今回Taskが衝突した場合は、安全側で処理する
- 人間判断が必要な重大な矛盾がなければ、自律的に統合する

---

# 13. Verification

最低限以下を確認してください。

1. 指定した基盤ディレクトリが存在する
2. `DEVELOPMENT_SYSTEM.md` が共通入口として機能する
3. AI Adapterに共通ルールの大量重複がない
4. READMEからDevelopment SSOTへ辿れる
5. `handoff/planner/` がRepository TOP配下に存在する
6. 既存製品資産を破壊していない
7. Git差分に意図しないファイルが含まれていない

利用可能であれば既存Repositoryの通常検証も実施すること。
ただし本Taskと無関係な既存不具合を勝手に大規模修正しないこと。

---

# 14. Completion Behavior

人間判断が不要な場合、途中確認で停止せず、
調査 → 実装 → 検証 → 必要な修正 → Repository反映まで自律的に進めてください。

ただし、このRepositoryにすでに確立済みのcommit / pushルールがある場合はそれに従うこと。

まだGit運用ルールが未定義であり、安全に判断できない場合でも、
少なくとも作業内容とRepository状態を明確に報告してください。

---

# 15. Builder Final Response

Builderの最終回答には最低限以下を含めてください。

```text
Task:
Status:

実施内容:
- ...

検証:
- ...

変更した主要ファイル:
- ...

Git状態:
- ...

人間判断:
- 不要
または
- 必要: <内容>

成果物 / Planner確認場所:
- <Repository-relative path>
```

**回答の最後は必ず「成果物 / Planner確認場所」で終えてください。**

本TaskでPlanner向けZIP生成まで安全に実装されていない場合、
無理にZIPを作らず、Plannerが確認すべきRepository内ファイルまたは作業結果の場所を明示してください。

---

# 16. Acceptance Criteria

以下をすべて満たせば本Task完了とします。

- [ ] Planner / Builder型の開発標準基盤がRepositoryに存在する
- [ ] `docs/development/DEVELOPMENT_SYSTEM.md` が作成されている
- [ ] Planner / Builderが特定AIサービス名と結び付いていない
- [ ] AGENTS / CLAUDE / GEMINIが薄いAdapterとして整理されている
- [ ] Repository TOPに `handoff/planner/` が存在する
- [ ] GitHubによるバージョン管理方針が明文化されている
- [ ] `tasks/active/` と `tasks/completed/` が存在する
- [ ] `docs/product/`, `reports/`, `templates/` の役割が明確になっている
- [ ] 既存Repository資産を破壊していない
- [ ] 後続Taskで詳細標準化できる構造になっている
- [ ] Builder最終回答でPlanner確認場所が明示されている

---

# 17. Scope Reminder

今回の目的は、

**「詳細ルールを全部作ること」ではなく、
今後すべての詳細ルールを安定して載せられる開発標準の骨格を作ること。**

過剰実装せず、本TaskのAcceptance Criteriaを満たした時点で完了してください。
