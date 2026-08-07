# DEV-TASK-0004 — 受け渡しフォルダ簡素化・最新1 ZIP運用への移行

## 0. Role

あなたはこのRepositoryの **Builder** です。

本Taskでは、これまでのPlanner Handoff運用をさらに簡素化し、
人間が迷わず「最新成果物だけ」を取得できる状態へ変更してください。

今回の人間判断により、従来の

```text
handoff/planner/
```

は廃止します。

今後のPlanner向け受け渡し場所は、Repository TOP直下の

```text
受け渡し/
```

のみとします。

また、このフォルダには **常に最新のHandoff ZIP 1個だけ** が存在する状態を標準とします。

本Task自身の成果物から、この新ルールを適用してください。

---

# 1. Human Decision / Highest Priority Change

以下は今回明示された最新の人間判断であり、
既存Development SSOTより優先します。

## New Canonical Handoff Location

```text
<REPOSITORY_ROOT>/受け渡し/
```

## New Directory Content Rule

Task完了後の `受け渡し/` の内容は、

```text
受け渡し/
└── <LATEST-TASK-ID>_PLANNER_HANDOFF.zip
```

のみとする。

つまり、

- 最新ZIP 1個のみ
- 古いZIPを残さない
- `.gitkeep` を置かない
- `README.md` を置かない
- loose fileを置かない
- subdirectoryを置かない

を必須ルールとする。

---

# 2. Objective

以下を完了してください。

1. `handoff/planner/` 運用を廃止する
2. Repository root直下に `受け渡し/` を標準Handoff領域として採用する
3. 既存の古いHandoff ZIPを削除する
4. `handoff/` 配下の旧Handoff構造を撤去する
5. Development SSOT内の参照をすべて新パスへ更新する
6. `.gitignore` を新パスへ対応させる
7. 最新のHandoff ZIPだけを残すcleanupルールを正式化する
8. 本TaskのHandoff ZIPを `受け渡し/` に生成する
9. Task完了時、`受け渡し/` 内が本Task ZIP 1個だけであることを検証する
10. Builder最終回答の最後に新しいZIP絶対パスを記載する

---

# 3. Required Final Repository Shape

Handoffに関して最終的に以下の状態へ移行してください。

```text
/
├── README.md
├── AGENTS.md
├── CLAUDE.md
├── GEMINI.md
├── 受け渡し/
│   └── DEV-TASK-0004_PLANNER_HANDOFF.zip
├── docs/
├── tasks/
├── reports/
├── templates/
└── ...
```

### Important

`受け渡し/` は **配送物専用フォルダ** です。

Gitでディレクトリ構造を維持するための `.gitkeep` 等も置かないでください。

Gitは空ディレクトリを管理しないため、
`受け渡し/` が存在しない環境ではBuilderがHandoff生成時に自動作成します。

---

# 4. Remove Legacy Handoff Structure

現在の旧構造：

```text
handoff/
├── README.md
└── planner/
    ├── .gitkeep
    ├── DEV-TASK-0002_PLANNER_HANDOFF.zip
    └── DEV-TASK-0003_PLANNER_HANDOFF.zip
```

等が存在する可能性があります。

これを調査し、旧Handoff用途として使用されているものは撤去してください。

最低限：

- `handoff/planner/.gitkeep` を削除
- `handoff/README.md` を削除
- `handoff/planner/` 内の古いHandoff ZIPを削除
- 旧 `handoff/` ディレクトリをHandoff用途から完全廃止
- SSOT・README・Adapter等に残る `handoff/planner/` 参照を除去

ただし、`handoff/` という文字列を別用途で使用しているコード等が存在する場合は、
無差別削除せず用途を確認すること。

本AI Development StandardのPlanner Handoff用途については、
`受け渡し/` へ完全移行する。

---

# 5. Latest One ZIP Rule

`docs/development/HANDOFF_RULES.md` を更新し、
以下を正式な必須ルールとして定義してください。

## 5.1 Exactly One Current Artifact

`受け渡し/` には、
**現在Plannerへ渡すべき最新のHandoff ZIPを1個だけ置く。**

Task完了時に以下は禁止。

```text
受け渡し/
├── OLD-TASK_PLANNER_HANDOFF.zip
└── NEW-TASK_PLANNER_HANDOFF.zip
```

必ず以下にする。

```text
受け渡し/
└── NEW-TASK_PLANNER_HANDOFF.zip
```

---

## 5.2 Cleanup Before New Handoff

新しいHandoff ZIPを作成する直前に、

```text
受け渡し/
```

の既存内容を確認する。

既存のPlanner配送物がある場合は削除してから、
新しいZIPを生成する。

標準フロー：

```text
Task実装完了
↓
検証
↓
commit
↓
push
↓
受け渡し/ を作成（存在しない場合）
↓
受け渡し/ の旧配送物を削除
↓
新しいHandoff ZIPを生成
↓
ZIP検証
↓
受け渡し/ 内がZIP 1個のみであることを確認
↓
Builder最終回答
```

---

## 5.3 What May Exist in `受け渡し/`

許可：

```text
<LATEST-TASK-ID>_PLANNER_HANDOFF.zip
```

のみ。

禁止：

- `.gitkeep`
- `.gitignore`
- `README.md`
- Markdown
- screenshot
- log
- directory
- 複数ZIP
- 前TaskのZIP
- temporary ZIP
- backup ZIP

ZIP生成の一時ファイルが必要な場合は、
別のtemporary locationで作成してから最終ZIPだけを `受け渡し/` に配置すること。

---

# 6. Git Tracking Rule

Handoff ZIPはDelivery ArtifactでありGit管理対象外とします。

`.gitignore` を更新してください。

旧：

```gitignore
handoff/planner/*.zip
```

新：

```gitignore
/受け渡し/
```

または同等に、
`受け渡し/` 配下を配送物としてGit追跡対象外にする安全な設定とする。

### Important

`受け渡し/` 配下にはGit管理用ファイルを置かない。

そのため、clone直後にフォルダが存在しないことは正常とする。

BuilderがPlanner Handoff生成時に必要に応じて作成する。

---

# 7. Development SSOT Updates

少なくとも以下を確認・更新してください。

```text
docs/development/DEVELOPMENT_SYSTEM.md
docs/development/HANDOFF_RULES.md
docs/development/GIT_RULES.md
docs/development/BUILDER_RULES.md
docs/development/README.md
README.md
AGENTS.md
CLAUDE.md
GEMINI.md
```

ただしAI Adapterに詳細ルールをコピーしない。

---

# 8. DEVELOPMENT_SYSTEM.md

Repository AreasおよびHandoff Principleを更新する。

旧：

```text
handoff/
└── planner/
```

新：

```text
受け渡し/
```

Handoff Principleとして最低限以下を明記する。

- Repository TOP直下の `受け渡し/` が唯一のPlanner提出場所
- 最新ZIP 1個だけを保持
- 1 submission = 1 ZIP
- ZIP上限500MB
- 新Handoff作成前に旧配送物を削除
- `受け渡し/` はGit追跡対象外
- clone直後に存在しなくても正常
- Builderが必要時に作成する

---

# 9. HANDOFF_RULES.md

既存ルールを新構造へ全面更新する。

標準Location：

```text
受け渡し/
```

標準filename：

```text
<TASK-ID>_PLANNER_HANDOFF.zip
```

本Task：

```text
DEV-TASK-0004_PLANNER_HANDOFF.zip
```

ZIP内部構造は既存標準を維持してよい。

最低限：

```text
DEV-TASK-0004_PLANNER_HANDOFF.zip
├── REPORT.md
├── MANIFEST.md
└── files/
```

500MB上限も維持する。

---

# 10. GIT_RULES.md

Git Task Completion Workflowを更新する。

旧：

```text
commit
↓
push
↓
working tree clean
↓
handoff/planner/ にZIP生成
```

新：

```text
commit
↓
push
↓
working tree clean
↓
受け渡し/ を準備
↓
旧Handoffを削除
↓
最新ZIP生成
↓
受け渡し/ が最新ZIP 1個のみであることを確認
```

配送物がgitignoreされているため、
Handoff生成後もRepository tracked stateがcleanであることを確認する。

---

# 11. README.md

Repository root READMEのHandoff案内を簡潔に更新する。

Planner向け成果物：

```text
受け渡し/
```

ルール：

```text
常に最新のPlanner Handoff ZIP 1個のみ
```

詳細：

```text
docs/development/HANDOFF_RULES.md
```

Portable relative linkの原則を維持する。

---

# 12. Adapter Review

以下を検索する。

```text
AGENTS.md
CLAUDE.md
GEMINI.md
```

Adapterに旧パス、

```text
handoff/
handoff/planner/
```

が残っている場合は修正する。

AdapterはSSOTへの薄い入口に留める。

---

# 13. Repository-wide Legacy Reference Search

Repository全体を検索し、
Planner Handoff用途の旧参照が残っていないことを確認してください。

検索例：

```text
handoff/planner
handoff/
PLANNER_HANDOFF
.gitkeep
```

### Important

`PLANNER_HANDOFF` はZIP命名として今後も使用するため、
単純に文字列を削除するのではなく用途を確認する。

Task履歴として `tasks/completed/DEV-TASK-0002.md` 等に
当時のパスが記録されている場合、
過去Taskの原文を改変して履歴を書き換える必要はありません。

正式な現行SSOT・README・Adapter・テンプレートに
旧ルールが残っていないことを重視する。

---

# 14. Existing ZIP Cleanup

ユーザー環境では少なくとも古いHandoff ZIPが残る運用になっています。

本Task実行時には、

- DEV-TASK-0002の旧ZIP
- DEV-TASK-0003の旧ZIP
- その他既存のPlanner Handoff ZIP

を確認してください。

旧配送物はGit管理対象外の一時成果物なので、
現在の最新人間判断に基づき削除して構いません。

最終的にPlannerが見るべきZIPは、

```text
受け渡し/DEV-TASK-0004_PLANNER_HANDOFF.zip
```

1個のみとする。

---

# 15. No Placeholder Files in Delivery Directory

特に重要です。

以下のようにしてはいけません。

```text
受け渡し/
├── .gitkeep
└── DEV-TASK-0004_PLANNER_HANDOFF.zip
```

これは「最新1 ZIPのみ」という人間要件に違反します。

必ず：

```text
受け渡し/
└── DEV-TASK-0004_PLANNER_HANDOFF.zip
```

とする。

---

# 16. Handoff ZIP Internal Paths

ZIP内部のパスは引き続きRepository-relative構造が理解できる形にする。

例：

```text
files/
├── README.md
├── .gitignore
└── docs/
    └── development/
        ├── DEVELOPMENT_SYSTEM.md
        ├── HANDOFF_RULES.md
        └── GIT_RULES.md
```

ZIP内部には `受け渡し/` 自身を含めない。

古いHandoff ZIPも含めない。

---

# 17. This Task Handoff

本TaskのPlanner提出物は、

```text
受け渡し/DEV-TASK-0004_PLANNER_HANDOFF.zip
```

のみ。

ZIPを作る前に `受け渡し/` の既存内容を削除する。

生成後に以下を機械的に確認してください。

### Directory count

```text
受け渡し/ 配下の通常ファイル数 = 1
```

### ZIP count

```text
受け渡し/ 配下の *.zip 数 = 1
```

### Directory count

```text
受け渡し/ 配下のサブディレクトリ数 = 0
```

### Filename

```text
DEV-TASK-0004_PLANNER_HANDOFF.zip
```

### Size

```text
<= 500 MB
```

---

# 18. Required ZIP Contents

最低限以下を含める。

```text
DEV-TASK-0004_PLANNER_HANDOFF.zip
├── REPORT.md
├── MANIFEST.md
└── files/
    ├── README.md
    ├── .gitignore
    └── docs/
        └── development/
            ├── DEVELOPMENT_SYSTEM.md
            ├── HANDOFF_RULES.md
            ├── GIT_RULES.md
            └── BUILDER_RULES.md
```

実際に変更したAdapterやDevelopment README等も、
Plannerレビューに必要なら含める。

---

# 19. REPORT.md Requirements

REPORTには最低限以下を記載する。

```text
Task
Status
Summary
Changes
Verification
Acceptance Criteria
Human Decision
Git State
Known Issues
Planner Review Guide
```

さらに本Taskでは、

```text
Handoff Directory Migration
```

を追加し、以下を明記する。

- 旧Path: `handoff/planner/`
- 新Path: `受け渡し/`
- 古いZIP削除結果
- 旧handoff構造撤去結果
- `受け渡し/` 内の最終ファイル一覧
- 最新ZIP 1個のみであることの検証結果

---

# 20. MANIFEST.md Requirements

最低限：

- Task ID
- Handoff ZIP filename
- Created At
- Repository Root absolute path
- Handoff Directory absolute path
- Handoff ZIP absolute path
- Branch
- Commit
- ZIP size
- Included files

を記載する。

---

# 21. Git / GitHub

Canonical Repositoryは引き続き以下。

```text
https://github.com/h-shojaku/PB-Dev.git
```

Remote：

```text
origin
```

Branch：

```text
main
```

本Taskの変更をcommit / pushする。

推奨commit message：

```text
DEV-TASK-0004: simplify Planner handoff
```

ただし、Handoff ZIP自体はGit追跡対象外。

---

# 22. Verification

最低限以下を確認してください。

- [ ] `docs/development/HANDOFF_RULES.md` が新ルールへ更新されている
- [ ] `docs/development/DEVELOPMENT_SYSTEM.md` が新ルールへ更新されている
- [ ] `docs/development/GIT_RULES.md` が新ルールへ更新されている
- [ ] root READMEが `受け渡し/` を案内している
- [ ] 現行SSOTに `handoff/planner/` が残っていない
- [ ] `.gitignore` が `受け渡し/` を配送物として除外している
- [ ] 旧 `handoff/` Handoff構造が撤去されている
- [ ] 旧Handoff ZIPが削除されている
- [ ] `受け渡し/` に `.gitkeep` が存在しない
- [ ] `受け渡し/` にREADMEが存在しない
- [ ] `受け渡し/` にsubdirectoryが存在しない
- [ ] `受け渡し/` に通常ファイルが1個だけ存在する
- [ ] その1個が `DEV-TASK-0004_PLANNER_HANDOFF.zip`
- [ ] ZIPが500MB以内
- [ ] ZIP内にREPORT.md / MANIFEST.mdが存在する
- [ ] Git commitがTask IDと追跡可能
- [ ] `origin/main` へpush成功
- [ ] tracked working treeがclean
- [ ] 最終回答にZIP絶対パスがある

---

# 23. Builder Final Response

最終回答は最低限以下とする。

```text
Task: DEV-TASK-0004
Status: COMPLETE / BLOCKED

実施内容:
- ...

受け渡し:
- Directory: <absolute path>\受け渡し
- Files: 1
- ZIP: DEV-TASK-0004_PLANNER_HANDOFF.zip
- Size: ...

Git:
- Remote: https://github.com/h-shojaku/PB-Dev.git
- Branch: main
- Commit: ...
- Push: ...
- Working tree: ...

人間判断:
- 不要
または
- 必要: ...

これをPlannerに渡してください: <Repository Root>\受け渡し\DEV-TASK-0004_PLANNER_HANDOFF.zip
```

実際のOS上の絶対パスを使用すること。

**最後の1文より後には何も記載しないこと。**

---

# 24. Acceptance Criteria

以下をすべて満たせばCOMPLETE。

- [ ] Planner Handoffの唯一の標準場所がRepository TOPの `受け渡し/` になっている
- [ ] `handoff/planner/` は現行運用から廃止されている
- [ ] `受け渡し/` には最新ZIP 1個だけを残すルールがSSOT化されている
- [ ] 新Handoff作成時に旧配送物を削除するルールがSSOT化されている
- [ ] `.gitkeep` 等のplaceholderを `受け渡し/` に置かないルールがある
- [ ] clone後にフォルダがなければBuilderが生成するルールがある
- [ ] `.gitignore` が新Handoff領域に対応している
- [ ] 旧Handoff ZIPがローカルから削除されている
- [ ] 本TaskのHandoff ZIPが `受け渡し/` にある
- [ ] `受け渡し/` の内容が本TaskZIP 1個のみ
- [ ] 500MB以内
- [ ] GitHubへcommit / pushされている
- [ ] Builder最終回答の最後が新Handoff ZIP絶対パス案内で終わる

---

# 25. Scope Boundary

本TaskはHandoff運用の修正に集中する。

以下は後続Taskへ残す。

- Task lifecycle完全版
- Planner Rules完全版
- Review lifecycle
- AI / Session切替完全版
- Definition of Done全体
- Product初期化フロー
- CI/CD

今回の目的は、

**「人間がRepository TOPの `受け渡し/` を開けば、そこにPlannerへ渡すべき最新ZIPが必ず1個だけある」**

という開発体験を確立することです。
