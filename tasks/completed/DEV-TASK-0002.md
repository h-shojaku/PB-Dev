# DEV-TASK-0002 — Builder運用・Planner Handoff標準化

## 0. Role

あなたはこのRepositoryの **Builder** です。

本Taskでは、DEV-TASK-0001で作成したAI Development Standard基盤を拡張し、

- Builderの自律実行ルール
- 人間判断が必要な場合の停止境界
- Plannerへの報告方法
- `handoff/planner/` による1 ZIP受け渡し
- Builder最終回答フォーマット
- 成果物の絶対パス明示

を正式なDevelopment SSOTとして定義してください。

本Task自身のPlanner提出から、新しいHandoffルールを適用してください。

---

# 1. Current SSOT

作業開始前に最低限以下を確認してください。

- `docs/development/DEVELOPMENT_SYSTEM.md`
- `README.md`
- `AGENTS.md`
- 使用中CLI AIに対応するAdapter
- 現在のGit状態
- Repository rootの絶対パス

現在のDevelopment Systemではすでに、

- Planner / Builderの役割分離
- Repository is SSOT
- AI Service Independence
- Autonomous Execution Principle
- `handoff/planner/`
- 1 Taskにつき1 ZIP、上限500MBというHandoff Principle
- GitHubを基盤とするVersion Control Principle

が基礎原則として存在します。

これらと矛盾しないよう詳細化してください。

---

# 2. Objective

今後どのBuilder AIを使用しても、Task完了時の動作が同じになるよう標準化する。

特に次を必須化します。

1. 人間判断が不要ならBuilderは途中確認せず自律的に完了まで進める
2. Plannerへの提出物は1回の提出につき必ず1 ZIP
3. ZIPはRepository TOPの `handoff/planner/` に配置する
4. ZIPサイズは500MB以内
5. `handoff/planner/` にPlanner確認用の loose file を提出しない
6. Builder最終回答にTask結果・Git状態・人間判断有無を明示する
7. Builder最終回答の**最後の1文**でHandoff ZIPの**絶対パス**を明示する
8. 最後の1文には必ず **「これをPlannerに渡してください」** という案内を含める
9. 本Task自身もこのルールに従ってPlanner Handoff ZIPを作成する

---

# 3. Files to Create / Update

以下を基本としてください。

```text
docs/development/
├── DEVELOPMENT_SYSTEM.md
├── BUILDER_RULES.md
├── DECISION_RULES.md
└── HANDOFF_RULES.md

templates/
└── PLANNER_REPORT_TEMPLATE.md

handoff/
├── README.md
└── planner/
```

必要に応じて既存READMEやAI Adapterも最小限更新してください。

重複SSOTを作らないこと。

---

# 4. BUILDER_RULES.md

`docs/development/BUILDER_RULES.md` を作成してください。

最低限、以下を定義してください。

## 4.1 Builder Identity

Builderは、

- VSCode + CLI型AI
- Repositoryを直接参照・操作する実行役
- 特定AIサービス名に依存しない

とする。

---

## 4.2 Autonomous by Default

Builderは、人間判断を必要としない限り、途中確認を行わず以下を連続して進める。

```text
Task確認
↓
Repository調査
↓
実装 / 文書更新
↓
検証
↓
必要な自己修正
↓
Git状態確認
↓
Planner Handoff作成
↓
最終回答
```

単なる不明点、軽微な実装選択、一般的な技術判断を理由に停止しない。

Repository、Product SSOT、Development SSOT、Active Taskから合理的に決定できる場合は自律的に決定する。

---

## 4.3 Builder Must Not

以下をBuilderが独断で行わないこと。

- Product仕様そのものの重大変更
- 人間が明示した要件の撤回・置換
- 本番公開
- 外部送信
- 課金発生
- 秘密情報・認証情報に関する危険な操作
- 復元困難な破壊的操作
- Product SSOTとDevelopment SSOTの重大な矛盾を推測で解消
- Taskの目的そのものを別目的へ変更

---

## 4.4 No Premature Completion

以下だけではTask完了としない。

- コードを書いた
- 文書を作った
- テストを一部実施した
- 「対応しました」と回答した

Taskで要求された検証、Handoff、Git状態確認、最終報告まで完了して初めて提出可能とする。

Definition of Doneの詳細は後続Taskでさらに標準化する。

---

# 5. DECISION_RULES.md

`docs/development/DECISION_RULES.md` を作成してください。

人間判断が必要なケースと、Builderが自律判断すべきケースを明確に分ける。

最低限以下を含めてください。

## Human Decision Required

- Product要求が複数解釈でき、どれを採用するかでユーザー体験が大きく変わる
- SSOT同士に重大な矛盾があり、優先順位ルールだけでは解決できない
- 本番公開・配布・課金・外部公開
- 復元困難または不可逆な操作
- 人間しか提供できない資格情報や契約判断が必要
- 法務・契約・権利等について製品方針の決定が必要
- Task scopeを大きく変更する必要がある

## Builder Decision

原則として以下では停止しない。

- ファイル構成の軽微な選択
- 関数名・変数名
- 内部実装方式
- テスト方法
- 一般的なエラー修正
- Task達成のための小規模リファクタリング
- ドキュメント整形
- 明白なtypo修正
- 既存パターンに沿った実装判断

## Blocking Behavior

人間判断が本当に必要な場合のみ、

- 何が決められないか
- 選択肢
- 各選択肢の影響
- Builderが推奨する案（合理的に提示可能な場合）
- 現在安全に完了できている範囲

を明示して停止する。

---

# 6. HANDOFF_RULES.md

`docs/development/HANDOFF_RULES.md` を作成してください。

今回から以下を**必須ルール**として定義します。

---

## 6.1 Standard Location

Plannerへの提出物はRepository TOP配下の、

```text
handoff/planner/
```

へ配置する。

---

## 6.2 Exactly One ZIP Per Submission

Plannerへの**1回の提出につき、提出物は必ず1 ZIP**とする。

標準命名：

```text
<TASK-ID>_PLANNER_HANDOFF.zip
```

例：

```text
DEV-TASK-0002_PLANNER_HANDOFF.zip
```

Plannerに個別のMarkdown、画像、ログ、patch等をバラバラに渡さない。

必要なものはすべてZIP内部へ含める。

---

## 6.3 Maximum Size

Handoff ZIPは、

```text
500 MB以内
```

とする。

500MBを超える場合は無条件に巨大ファイルを詰め込まず、

- 不要なbuild成果物
- dependency
- cache
- `.git`
- 再生成可能な巨大ファイル

を除外する。

それでも500MBを超える場合のみ人間判断対象とする。

---

## 6.4 ZIP Is Delivery Artifact

Handoff ZIPはPlannerへの配送物であり、Product SSOTそのものではない。

正式な仕様・コード・履歴はRepository側を正とする。

Handoff ZIPをGitで恒久管理するかどうかの詳細は、Git標準化Taskで確定する。

現時点で既存 `.gitignore` やRepositoryルールがある場合はそれを尊重する。

---

# 7. Required ZIP Contents

このTask以降、Handoff ZIPには最低限以下を含める。

```text
<TASK-ID>_PLANNER_HANDOFF.zip
│
├── REPORT.md
├── MANIFEST.md
└── files/
    └── Plannerがレビューするために必要な成果物
```

必要に応じて以下を追加可能。

```text
evidence/
logs/
screenshots/
diff/
```

ただし、不要なファイルを大量に詰め込まない。

---

## 7.1 REPORT.md

PlannerがZIPを開いた直後に読む主報告書。

最低限以下を含める。

```text
# Builder Report

## Task
## Status
## Summary
## Changes
## Verification
## Acceptance Criteria
## Human Decision
## Git State
## Known Issues
## Planner Review Guide
```

`Planner Review Guide` では、

- 何を確認すべきか
- どのファイルを見るべきか
- 実機確認が必要か

を簡潔に示す。

---

## 7.2 MANIFEST.md

ZIP内容の索引。

最低限以下を記載。

- Task ID
- Handoff ZIP filename
- 作成日時
- Repository root
- 含有ファイル一覧
- ZIPサイズ
- 対応するGit commit（存在する場合）
- Branch（存在する場合）

---

## 7.3 files/

Plannerレビューに必要な変更ファイル・文書を、
可能な限りRepository-relative構造が分かる形で格納する。

例：

```text
files/
└── docs/
    └── development/
        ├── BUILDER_RULES.md
        ├── DECISION_RULES.md
        └── HANDOFF_RULES.md
```

PlannerがRepositoryへ直接アクセスできない前提でも、
Handoff ZIPだけで変更内容をレビューできるようにする。

---

# 8. PLANNER_REPORT_TEMPLATE.md

`templates/PLANNER_REPORT_TEMPLATE.md` を作成し、
`REPORT.md` の標準テンプレートとして利用できる形にする。

特定製品固有の内容を入れない。

---

# 9. handoff/README.md

既存の `handoff/README.md` を更新し、

- Plannerへの標準提出先
- 1 submission = 1 ZIP
- 500MB以内
- loose file提出禁止
- ZIP内部の正式仕様は `HANDOFF_RULES.md`

を明示する。

---

# 10. DEVELOPMENT_SYSTEM.md Update

`docs/development/DEVELOPMENT_SYSTEM.md` を更新し、

- `BUILDER_RULES.md`
- `DECISION_RULES.md`
- `HANDOFF_RULES.md`

が詳細SSOTとして存在することをリンクする。

Handoff Principleの表現は、

「1 Taskにつき1 ZIPを想定」

ではなく、

**「Plannerへの1回の提出につき1 ZIPを必須とする」**

という正式ルールへ更新する。

---

# 11. AI Adapter Update

必要に応じて、

- `AGENTS.md`
- `CLAUDE.md`
- `GEMINI.md`

を最小限更新する。

各Adapterには詳細ルールをコピーせず、

Builderが作業開始時に最低限、

- `DEVELOPMENT_SYSTEM.md`
- `BUILDER_RULES.md`
- `DECISION_RULES.md`
- `HANDOFF_RULES.md`

を参照するようにする。

---

# 12. Absolute Path Requirement

Builderの最終回答では、Repository-relative pathだけでは不十分です。

**実行環境上のRepository rootを実際に取得し、Handoff ZIPの絶対パスを出力してください。**

Windows例：

```text
C:\Users\example\Documents\dev\ProductRepo\handoff\planner\DEV-TASK-0002_PLANNER_HANDOFF.zip
```

macOS例：

```text
/Users/example/dev/ProductRepo/handoff/planner/DEV-TASK-0002_PLANNER_HANDOFF.zip
```

テンプレート内に特定ユーザーの固定パスをハードコードしないこと。

Builderが実行時に現在のRepository rootから解決すること。

---

# 13. Mandatory Final Sentence

Builder最終回答の**最後の1文**は、必ず以下の形式にする。

```text
これをPlannerに渡してください: <Handoff ZIPの絶対パス>
```

例：

```text
これをPlannerに渡してください: C:\Users\example\Documents\dev\ProductRepo\handoff\planner\DEV-TASK-0002_PLANNER_HANDOFF.zip
```

この文より後に、

- 補足
- 提案
- 注意書き
- 質問
- 次Task案

等を追加してはいけない。

**文字通りこの案内文を最終行とすること。**

---

# 14. Builder Final Response Format

最終回答全体は最低限以下とする。

```text
Task: DEV-TASK-0002
Status: COMPLETE / BLOCKED

実施内容:
- ...

検証:
- ...

Git:
- Repository: ...
- Branch: ...
- Commit: ...
- Push: ...
- Working tree: ...

人間判断:
- 不要
または
- 必要: ...

Planner Handoff:
- Filename: DEV-TASK-0002_PLANNER_HANDOFF.zip
- Size: ...
- Absolute path: ...

これをPlannerに渡してください: <Handoff ZIPの絶対パス>
```

Git remote等がまだ設定されておらずpush不能な場合は、
成功したように装わず事実を明記する。

ただし、それだけを理由に本Taskで実行可能な作業まで停止しない。

---

# 15. This Task Must Use the New Handoff Rule

本Taskの成果物提出も、今回定義したルールに従う。

必ず、

```text
handoff/planner/DEV-TASK-0002_PLANNER_HANDOFF.zip
```

を作成すること。

Planner向けに別々のファイルを提出しない。

ZIPには少なくとも、

```text
REPORT.md
MANIFEST.md
files/docs/development/BUILDER_RULES.md
files/docs/development/DECISION_RULES.md
files/docs/development/HANDOFF_RULES.md
files/docs/development/DEVELOPMENT_SYSTEM.md
files/templates/PLANNER_REPORT_TEMPLATE.md
```

を含める。

READMEやAdapterを変更した場合は、それらも `files/` 以下へ含める。

---

# 16. Git Safety

現在のGit状態を調査すること。

特に初期Repositoryでは、

- `git init` 済みだが未commit
- remote未設定
- 全ファイルuntracked

等の状態もあり得る。

以下を守る。

- Git履歴を偽装しない
- remoteが存在しないのにpush成功と報告しない
- 既存履歴を破壊しない
- `git reset --hard` 等の破壊的操作を不用意に行わない
- GitHub remote作成や認証が必要な場合は、勝手に外部設定を作らない
- Gitに関して実行可能な安全な範囲は自律的に進める
- 未解決事項はREPORTと最終回答に明記する

Git/GitHub詳細標準は後続Taskで正式化する。

---

# 17. Verification

最低限以下を確認する。

- [ ] `BUILDER_RULES.md` が存在する
- [ ] `DECISION_RULES.md` が存在する
- [ ] `HANDOFF_RULES.md` が存在する
- [ ] `PLANNER_REPORT_TEMPLATE.md` が存在する
- [ ] `DEVELOPMENT_SYSTEM.md` から詳細ルールへ辿れる
- [ ] AI Adapterにルール本文が大量重複していない
- [ ] `handoff/planner/DEV-TASK-0002_PLANNER_HANDOFF.zip` が存在する
- [ ] ZIPが500MB以内
- [ ] ZIP内に `REPORT.md` がある
- [ ] ZIP内に `MANIFEST.md` がある
- [ ] ZIPだけでPlannerが主要変更をレビューできる
- [ ] ZIP内に `.git`、dependency、cache等の不要物がない
- [ ] 最終回答でZIPの絶対パスが明示されている
- [ ] 最終行が「これをPlannerに渡してください: <absolute path>」になっている

---

# 18. Do Not Over-Implement

本Taskでは以下をまだ詳細実装しない。

- Planner詳細運用
- Task lifecycle完全版
- Task Template完全版
- Session Handoff完全版
- AI切替完全手順
- Branch戦略
- Commit message完全規則
- Definition of Done完全版
- CI/CD
- GitHub Actions
- Handoff自動生成システムの高度化

必要最低限の補助処理は可とするが、
後続Taskの設計領域を先回りして複雑化しない。

---

# 19. Acceptance Criteria

以下をすべて満たせば完了。

- [ ] Builderの自律実行原則が詳細化されている
- [ ] 人間判断が必要な境界が明文化されている
- [ ] Planner Handoffが1 submission = 1 ZIPとして必須化されている
- [ ] Handoff ZIPは500MB以内と定義されている
- [ ] Planner向けloose file提出禁止が定義されている
- [ ] REPORT / MANIFEST / filesの基本構造が定義されている
- [ ] Planner Report Templateが存在する
- [ ] 本Task自身のHandoff ZIPが作成されている
- [ ] Builder最終回答形式が標準化されている
- [ ] Handoff ZIPの絶対パスが最終回答に含まれる
- [ ] 最終行が「これをPlannerに渡してください: <absolute path>」である
- [ ] 人間判断不要な処理を途中確認なしで完了している
