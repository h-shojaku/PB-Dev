# DEV-TASK-0005 — Handoff ZIPクロスプラットフォーム化・生成検証標準化

## 0. Role

あなたはこのRepositoryの **Builder** です。

本Taskでは、DEV-TASK-0004で確立した

- Repository TOP直下の `受け渡し/`
- 最新Handoff ZIP 1個のみ
- 1 submission = 1 ZIP
- 500MB以内
- Git追跡対象外
- 最終回答でZIP絶対パスを案内

という運用を維持したまま、
**Handoff ZIPそのものをWindows / macOS / Linuxで同じ構造として展開できる形式へ修正**してください。

本Task自身のHandoff ZIPから新ルールを適用します。

---

# 1. Planner Review Finding

DEV-TASK-0004のPlanner Handoff ZIPを別OS環境で検証したところ、
ZIP内部entry nameが以下のようなWindows形式になっていました。

```text
files\docs\development\HANDOFF_RULES.md
files\docs\development\GIT_RULES.md
files\README.md
```

ZIP内部の階層区切りとして `\` が使われています。

この形式はWindowsでは自然に見える場合がありますが、
macOS / Linux等では `\` がディレクトリ区切りとして解釈されず、
以下のように「バックスラッシュを含む1つのファイル名」として展開される可能性があります。

したがって、AI Development Standardの

```text
AI / OS / PC / Session Independence
```

に反します。

---

# 2. Human Decision

今後のHandoff ZIP内部パスは、
実行OSに関係なく **POSIX形式 `/` を標準** とします。

正：

```text
files/docs/development/HANDOFF_RULES.md
files/docs/development/GIT_RULES.md
files/README.md
REPORT.md
MANIFEST.md
```

禁止：

```text
files\docs\development\HANDOFF_RULES.md
files\docs\development\GIT_RULES.md
```

このルールはZIP内部entry nameに適用します。

### Important Distinction

以下を混同しないこと。

```text
Repository内Markdownリンク
    = portable relative path

ZIP内部entry path
    = `/` 区切りのportable relative path

Builder最終回答のHandoff ZIP path
    = 実行OS上の実際の絶対パス
```

Windows上のBuilder最終回答で、

```text
C:\Users\...\PB-Dev\受け渡し\DEV-TASK-0005_PLANNER_HANDOFF.zip
```

と表示すること自体は正しい。

問題は**ZIP内部entry name**である。

---

# 3. Objective

以下を完了してください。

1. ZIP内部entry pathをOS非依存の `/` 区切りへ統一
2. Handoff Rulesへ正式ルールとして追加
3. Builderが毎回同じ形式でZIPを作れる標準生成方法を用意
4. ZIP生成後に内部entry pathを自動検証できるようにする
5. `\` を含むZIP entryが1件でもあればTaskをCOMPLETEにしない
6. Windows / macOS / Linuxで論理的に同じ階層として展開可能にする
7. DEV-TASK-0005のHandoff ZIP自身を新形式で作成
8. GitHubへcommit / push
9. `受け渡し/` にはDEV-TASK-0005のZIP 1個だけを残す

---

# 4. Current Rules to Preserve

本Taskで以下を変更・後退させてはいけません。

```text
受け渡し/
└── <LATEST-TASK-ID>_PLANNER_HANDOFF.zip
```

必須：

- Repository TOP直下
- 最新ZIP 1個のみ
- 古いZIP削除
- loose file禁止
- subdirectory禁止
- `.gitkeep` 禁止
- README禁止
- 500MB以内
- `/受け渡し/` はGit追跡対象外
- Handoff前にcommit / push
- 最終回答最後の1文で絶対パスを案内

---

# 5. Create Standard Handoff ZIP Generator

AIやOSごとにZIP生成方法が変わって再発しないよう、
Repositoryに**標準Handoff ZIP生成スクリプト**を用意してください。

推奨：

```text
scripts/create_handoff.py
```

Python 3標準ライブラリのみで実装することを推奨します。

理由：

- Windows / macOS / Linuxで利用可能
- ZIP entry nameを明示的に制御可能
- 外部dependency不要
- AI CLIサービスを変更しても利用可能

別方式を採用する場合は、
同等以上のクロスプラットフォーム性と再現性を説明してください。

---

# 6. create_handoff.py Requirements

最低限、以下を満たしてください。

## 6.1 Inputs

Task IDとHandoff用staging sourceを受け取れること。

実装方法はBuilder判断でよいですが、
特定Task専用にハードコードしないこと。

概念例：

```text
python scripts/create_handoff.py \
  --task DEV-TASK-0005 \
  --source <staging-directory>
```

Windows PowerShellからも合理的に実行できること。

---

## 6.2 Output

Repository rootの、

```text
受け渡し/<TASK-ID>_PLANNER_HANDOFF.zip
```

へ出力する。

---

## 6.3 Cleanup

ZIP生成前に `受け渡し/` を確認し、
既存配送物を削除する。

生成後は、

```text
受け渡し/
└── <TASK-ID>_PLANNER_HANDOFF.zip
```

のみになること。

---

## 6.4 ZIP Entry Normalization

ZIPへ追加する際、
すべてのentry nameを明示的にPOSIX形式へ正規化する。

Python実装なら例えば概念上、

```python
relative_path.as_posix()
```

等を利用し、

```text
files/docs/development/...
```

になるようにする。

実OSのPath separatorをそのままZIP entry nameとして使用しない。

---

## 6.5 Forbidden ZIP Entries

ZIP内部に以下を含めない。

- `\` を含むentry name
- absolute path
- drive letter (`C:` 等)
- `..` による親ディレクトリ参照
- `.git/`
- dependency / cache
- 過去Handoff ZIP
- `受け渡し/` 自身
- staging directoryの不要な最上位名

---

## 6.6 Required Root Entries

最低限：

```text
REPORT.md
MANIFEST.md
files/
```

が論理構造として成立すること。

---

# 7. Create ZIP Verification

生成後に自動検証してください。

同じ `create_handoff.py` 内でも、
別の

```text
scripts/verify_handoff.py
```

でも構いません。

過剰に複雑化しない方を選択してください。

最低限以下を検証する。

```text
1. ZIPが存在
2. ZIP <= 500MB
3. CRC / archive integrity OK
4. REPORT.md存在
5. MANIFEST.md存在
6. ZIP entry nameに `\` が0件
7. ZIP entry nameにabsolute pathが0件
8. ZIP entry nameにparent traversal `..` が0件
9. `.git` が含まれない
10. 受け渡し/ 内のZIP数 = 1
11. 受け渡し/ 内の通常ファイル数 = 1
12. 受け渡し/ 内のsubdirectory数 = 0
```

検証に失敗した場合、
Builderは成功扱いで提出してはいけない。

自己修正可能なら修正して再生成・再検証する。

---

# 8. Cross-platform Extraction Verification

本Taskでは可能な範囲で、
生成したZIPを別temporary directoryへ実際に展開してください。

展開後、少なくとも以下が通常の階層として存在することを確認する。

```text
REPORT.md
MANIFEST.md
files/
files/docs/
files/docs/development/
```

Windows環境上でも、
ZIP内部entry listingを確認することで `/` 区切りになっていることを検証する。

可能ならPython `zipfile` を使い、

```text
namelist()
```

等でentry名を直接検証する。

---

# 9. Update HANDOFF_RULES.md

`docs/development/HANDOFF_RULES.md` に、
以下のSectionを追加または統合してください。

```text
Cross-platform ZIP Format
```

最低限：

- ZIP内部pathは常に `/`
- OSネイティブseparatorをZIP entryへ直接使用しない
- `\` entryは禁止
- absolute pathは禁止
- parent traversalは禁止
- HandoffはWindows/macOS/Linuxで展開可能であること
- 標準生成方法は `scripts/create_handoff.py`
- 生成後の検証成功が提出条件

を定義する。

---

# 10. Update BUILDER_RULES.md

BuilderのHandoff作成時に、

```text
標準Handoff generatorを使用
↓
archive verification
↓
成功時のみ最終回答
```

を追加する。

手動ZIP生成やAI固有ZIPコマンドを原則標準手順にしない。

ただし標準スクリプト自体が実行不能な重大問題がある場合は、
同一仕様を満たす代替手段で生成し、理由をREPORTに記載する。

---

# 11. Update DEVELOPMENT_SYSTEM.md

Handoff Principleに、

```text
Handoff ZIPはOS非依存のportable archiveである
```

ことを簡潔に追加し、
詳細は `HANDOFF_RULES.md` へ委譲する。

Development Systemへ実装詳細を大量コピーしない。

---

# 12. Update GIT_RULES.md

Task completion workflowのHandoff部分を、

```text
標準Handoff generatorでZIP生成
↓
archive verification
↓
受け渡し/ 最新1 ZIP確認
```

へ更新する。

---

# 13. Script Documentation

`scripts/` にREADMEがない場合、
必要なら簡潔な `scripts/README.md` を作成してよい。

ただしHandoffルールのSSOTはあくまで、

```text
docs/development/HANDOFF_RULES.md
```

とする。

READMEは実行入口に留める。

---

# 14. Existing DEV-TASK-0004 ZIP

DEV-TASK-0004 ZIPは配送済みの過去成果物なので、
Git履歴や過去Task原文を改ざんする必要はありません。

新しいTask完了時には、
最新1 ZIPルールに従いローカル `受け渡し/` から削除し、

```text
DEV-TASK-0005_PLANNER_HANDOFF.zip
```

のみを残す。

---

# 15. Handoff Staging Area

Handoff ZIP作成のために一時的なstaging directoryを使用して構いません。

ただし以下を守る。

- `受け渡し/` 内にstaging directoryを作らない
- Task完了後に不要staging artifactを残さない
- Git管理対象へ不要なtemporary fileを追加しない
- cleanupが安全であること

実装方法はBuilder判断とする。

---

# 16. Tests

今回のスクリプトに対して、
過剰でない範囲で自動テストまたはself-testを追加してください。

最低限次のケースを確認する。

## Success

入力：

```text
files/docs/example.md
REPORT.md
MANIFEST.md
```

期待：

```text
files/docs/example.md
REPORT.md
MANIFEST.md
```

としてZIP entryに格納される。

## Backslash Rejection / Prevention

Windows pathから生成しても、

```text
files\docs\example.md
```

にならず、

```text
files/docs/example.md
```

になる。

## Unsafe Path

`..` やabsolute entryを生成しない。

実装に応じて、テスト方法はBuilderが合理的に決定する。

---

# 17. Git / GitHub

Canonical Repository：

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

推奨commit：

```text
DEV-TASK-0005: make Handoff ZIP portable
```

Task IDを含む限りsummaryは調整可。

---

# 18. This Task Handoff

本TaskのPlanner提出物は必ず、

```text
受け渡し/DEV-TASK-0005_PLANNER_HANDOFF.zip
```

1個のみ。

標準Handoff generatorを使用して生成してください。

最低限以下を含める。

```text
DEV-TASK-0005_PLANNER_HANDOFF.zip
├── REPORT.md
├── MANIFEST.md
└── files/
    ├── README.md
    ├── scripts/
    │   └── create_handoff.py
    └── docs/
        └── development/
            ├── DEVELOPMENT_SYSTEM.md
            ├── BUILDER_RULES.md
            ├── HANDOFF_RULES.md
            └── GIT_RULES.md
```

実際に追加・変更した関連ファイルも必要に応じて含める。

---

# 19. REPORT.md Additional Verification

REPORTには通常項目に加えて、

```text
## ZIP Portability Verification
```

を追加し、最低限以下を明記する。

```text
Archive integrity:
Entry count:
Entries containing backslash:
Entries containing absolute path:
Entries containing parent traversal:
Extraction test:
Delivery directory file count:
Delivery directory ZIP count:
Delivery directory subdirectory count:
```

期待：

```text
Entries containing backslash: 0
Entries containing absolute path: 0
Entries containing parent traversal: 0
Extraction test: PASS
Delivery directory file count: 1
Delivery directory ZIP count: 1
Delivery directory subdirectory count: 0
```

---

# 20. MANIFEST.md

MANIFESTのIncluded Filesは、
実際のZIP内部entryと同じく `/` 形式で記載する。

例：

```text
files/docs/development/HANDOFF_RULES.md
```

Windowsネイティブ表記にしない。

ただし以下は実環境の絶対パスとしてOS標準表記でよい。

```text
Repository Root Absolute Path
Handoff Directory Absolute Path
Handoff ZIP Absolute Path
```

---

# 21. Verification Commands / Evidence

実装方法に応じてコマンドはBuilder判断とするが、
最低限以下に相当する検証を行う。

```text
git diff --check
git status
git log -1
```

およびZIPについて、

```text
archive integrity check
entry name listing
backslash count
unsafe path count
extraction test
```

を実施。

Git tracked working treeはcleanであること。

---

# 22. Builder Final Response

最終回答は既存ルールを維持する。

最低限：

```text
Task: DEV-TASK-0005
Status: COMPLETE / BLOCKED

実施内容:
- ...

ZIP Portability:
- Entries: ...
- Backslash entries: 0
- Unsafe entries: 0
- Extraction test: PASS

受け渡し:
- Files: 1
- ZIP: DEV-TASK-0005_PLANNER_HANDOFF.zip
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

これをPlannerに渡してください: <実際の絶対パス>\受け渡し\DEV-TASK-0005_PLANNER_HANDOFF.zip
```

**最後の1文より後には何も記載しないこと。**

---

# 23. Acceptance Criteria

以下をすべて満たせばCOMPLETE。

- [ ] ZIP内部entry pathが `/` 区切りで統一されている
- [ ] ZIP内部に `\` を含むentryが0件
- [ ] ZIP内部にabsolute pathが0件
- [ ] ZIP内部にparent traversalが0件
- [ ] Windows / macOS / Linuxで同一論理階層として展開可能な形式
- [ ] 標準Handoff ZIP generatorがRepositoryに存在する
- [ ] generatorが特定Task専用ではない
- [ ] generatorが外部dependencyへ不要に依存しない
- [ ] Handoff Rulesにportable ZIP仕様がSSOT化されている
- [ ] Builder Rulesが標準generator利用を要求している
- [ ] ZIP生成後verificationが提出条件になっている
- [ ] Extraction testがPASS
- [ ] `受け渡し/` に最新ZIP 1個のみ
- [ ] 本TaskZIPが500MB以内
- [ ] GitHubへcommit / push済み
- [ ] tracked working tree clean
- [ ] REPORTにZIP portability検証結果がある
- [ ] MANIFEST内entry一覧が `/` 形式
- [ ] 最終回答最後が実際のZIP絶対パス案内

---

# 24. Scope Boundary

本TaskはHandoff ZIPのクロスプラットフォーム性と再現性に集中する。

以下は後続Taskへ残す。

- Task lifecycle完全版
- Planner Rules完全版
- Review lifecycle
- AI / Session切替完全版
- Definition of Done全体
- Product初期化フロー
- CI/CD

今回の目的は、

**「どのOS・どのBuilder AIで作成しても、Plannerが受け取るZIPの構造と展開結果が同じになる」**

ことです。
