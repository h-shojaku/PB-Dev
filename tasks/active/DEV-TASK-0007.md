# DEV-TASK-0007 — Review Evidence Timing修正・Handoff世代境界の明確化

## 0. Role

あなたはこのRepositoryの **Builder** です。

本Taskは、DEV-TASK-0006のPlanner Review結果 `CHANGES_REQUIRED` を受けた修正Taskです。

DEV-TASK-0006でTask Lifecycle / Review Gate自体は概ね正しく整備されましたが、
`docs/development/REVIEW_RULES.md` の **Review Evidence Timing Rule** が広すぎるため、
Builder自身がTask完了前に行った正当なテスト・ビルド・検証まで
Planner評価対象外と読める矛盾があります。

本Taskでは、この境界を正確に修正してください。

新しい大規模機能は追加せず、
**「Builder内部検証」と「人間による外部・実機検証」を明確に分離すること**
に集中します。

---

# 1. Previous Task / Review Result

前Task：

```text
DEV-TASK-0006
```

Planner Review：

```text
CHANGES_REQUIRED
```

修正理由：

現在の `REVIEW_RULES.md` には概ね、

```text
Plannerがレビュー評価に用いる検証エビデンスは、
当該Handoff ZIP生成後に実行された検証のみを対象とする
```

という規則があります。

この表現では、通常TaskでHandoff ZIP生成前に行われる以下まで
無効なEvidenceと解釈できます。

```text
unit test
integration test
build
lint
type check
git diff --check
archive verification前の実装検証
その他BuilderがTask内で実施するVerification
```

これは既存のTask Lifecycle / Git / Handoffルールと矛盾します。

---

# 2. Correct Principle

今回、以下を正式ルールとします。

## 2.1 Builder Verification

BuilderがTask実行中に、
**最終成果物・最終commitを対象として実施した検証**は、
Handoff ZIP生成前に行われていても、
当該Handoffの正式な評価Evidenceとして有効です。

例：

```text
Builder実装
↓
test / build / lint / git diff --check
↓
commit / push
↓
Handoff ZIP生成
↓
Planner Review
```

この場合、Builderの検証結果は有効です。

---

## 2.2 Human / External Validation

一方、

- 人間による実機確認
- 人間による画面目視
- 人間による操作感確認
- Planner以外の外部環境で行う手動確認
- ユーザーが報告した実機挙動

などの**外部・人間側検証**については、
Handoffの世代境界を厳密に扱います。

原則：

> あるHandoff ZIPより前に人間が報告した実機・目視・操作結果は、
> その後Builderが新しいHandoff ZIPを生成した場合、
> 新Handoffの評価材料へ自動的に持ち越さない。

新Handoffについて評価するには、

```text
新Handoff生成
↓
人間が新しい成果物を再確認
↓
その結果をPlannerへ報告
```

を原則とします。

---

## 2.3 Explicit Carry-over Exception

以下の場合のみ例外とします。

人間が明示的に、

```text
この以前の検証結果も今回のHandoff評価に含めてよい
```

など、持ち越しを指示した場合。

その場合はPlannerが当該Evidenceを利用してよい。

BuilderやPlannerが勝手に「変わっていないはず」と推測して
過去の人間検証を新Handoffへ持ち越してはなりません。

---

# 3. Objective

以下を完了してください。

1. `REVIEW_RULES.md` のEvidence Timing規則を修正する
2. Builder内部検証とHuman / External Validationを明確に区別する
3. Handoff世代境界を正式に定義する
4. 過去人間検証の自動持ち越し禁止をSSOT化する
5. 明示的Carry-over例外を定義する
6. `DEVELOPMENT_SYSTEM.md` 等に矛盾する表現がないか確認する
7. `TASK_TEMPLATE.md` / Report Template等に誤解を招く表現があれば最小限修正する
8. Repository全体で旧Evidence Timing表現を検索し、矛盾を残さない
9. 本Taskを通常Task Lifecycleに従ってIntake → Completedまで処理する
10. GitHubへcommit / pushし、標準Handoff ZIPを生成する

---

# 4. Files to Read First

最低限以下を確認してください。

```text
docs/development/DEVELOPMENT_SYSTEM.md
docs/development/REVIEW_RULES.md
docs/development/TASK_RULES.md
docs/development/BUILDER_RULES.md
docs/development/GIT_RULES.md
docs/development/HANDOFF_RULES.md
tasks/TASK_REGISTER.md
templates/TASK_TEMPLATE.md
templates/PLANNER_REPORT_TEMPLATE.md
```

DEV-TASK-0006のInstruction Recordも確認してください。

```text
tasks/completed/DEV-TASK-0006.md
```

---

# 5. Define Evidence Categories

`REVIEW_RULES.md` でEvidenceを最低限以下の2種類に分けてください。

---

## 5.1 Builder Verification Evidence

BuilderがTask scope内で実施する技術検証。

例：

```text
unit test
integration test
build
lint
type check
static analysis
git diff --check
script self-test
archive integrity check
automated extraction test
その他Task Acceptance Criteriaに必要な自動・技術検証
```

### Validity

以下を満たす場合、
Handoff ZIP生成前の実行でも当該Handoffに対して有効。

- Taskの最終成果物を対象としている
- Handoffに記録された最終commitと整合する
- その後、検証対象を無効化する変更が入っていない
- REPORTに検証内容・結果が記録されている

---

## 5.2 Human / External Validation Evidence

Repository外・Builder外で行われる手動または実環境確認。

例：

```text
人間による実機操作
人間によるUI目視
人間による操作感評価
ユーザー報告
端末固有の実機挙動
外部環境での手動確認
```

### Validity

原則として、
**評価対象Handoff ZIPが生成された後に行われた検証**を
そのHandoffのEvidenceとして扱う。

新しいHandoffが生成された時点で、
それ以前の人間検証は新Handoffへ自動継承しない。

---

# 6. Handoff Generation Boundary

正式な概念として、

```text
Handoff Generation Boundary
```

または同等の分かりやすい名称を定義してください。

例：

```text
Handoff A
↓
Human Validation A
↓
Builder修正
↓
Handoff B
```

この場合：

```text
Human Validation A
```

は、

```text
Handoff A
```

に対するEvidenceです。

原則として、

```text
Handoff B
```

のEvidenceではありません。

Handoff Bを評価する場合は再検証します。

---

# 7. Important Example

`REVIEW_RULES.md` に短い具体例を入れてください。

## Valid Builder Verification

```text
Builderが実装
↓
全テストPASS
↓
commit / push
↓
Handoff ZIP生成
```

結果：

```text
全テストPASSは当該Handoffの有効Evidence
```

---

## Human Validation Must Be Re-run

```text
人間が不具合を確認
↓
Builderへ報告
↓
Builderが修正
↓
新Handoff ZIP生成
```

結果：

```text
修正前の人間確認結果を新Handoffへ自動持ち越さない
新Handoffを再度実機確認する
```

---

# 8. Explicit Carry-over

明示的な人間判断がある場合のみ、
古いHuman / External Validationを新Handoff評価へ含めることを許可します。

例：

```text
前回の実機結果は今回も評価材料として含めてください
```

この場合：

```text
Plannerは明示指示に従って利用可能
```

ただし、
EvidenceがどのHandoffに対するものかはレビュー時に明示してください。

---

# 9. Planner Review Behavior

PlannerはHandoff Review時に、
Evidenceを以下のように扱います。

```text
Builder Verification
→ REPORT / Handoff / commitとの整合を確認して利用

Human / External Validation
→ どのHandoff生成後に行われた結果か確認して利用
```

Plannerは、
古い人間検証を「たぶん今回も同じ」と推測して流用しない。

---

# 10. Do Not Invalidate Normal Task Completion

特に重要です。

以下の通常フローを壊してはいけません。

```text
Task実装
↓
Builder Verification
↓
Acceptance Criteria確認
↓
Task Completed登録
↓
commit / push
↓
Handoff ZIP生成
↓
Planner Review
```

Builder VerificationをHandoff生成後にやり直すことを
一般ルールとして要求してはいけません。

Handoff generator自身のZIP検証など、
当然ZIP生成後にしか実施できない検証はそのまま生成後に行います。

---

# 11. Update REVIEW_RULES.md

現在の、

```text
## Review Evidence Timing Rule
```

を修正・再構成してください。

推奨構造：

```text
## Review Evidence Rules

### Builder Verification Evidence
### Human / External Validation Evidence
### Handoff Generation Boundary
### Explicit Carry-over Exception
```

名称は多少変更して構いません。

意味が明確であることを優先します。

---

# 12. Update DEVELOPMENT_SYSTEM.md

Development Systemには詳細を大量コピーしない。

Planner Review Gate付近に、
以下を簡潔に記載してください。

- Builder内部検証は最終成果物に対して実施されていればHandoff前でも有効
- 人間・外部検証はHandoff世代単位で扱う
- 詳細は `REVIEW_RULES.md`

---

# 13. Review Other SSOT / Templates

Repository全体を検索し、
以下の誤った一般化が残っていないか確認してください。

検索概念：

```text
Handoff ZIPが生成された後
生成された後に実行された検証のみ
Review Evidence Timing
再検証
持ち越
```

対象候補：

```text
docs/development/
templates/
tasks/README.md
README.md
AGENTS.md
CLAUDE.md
GEMINI.md
```

過去のcompleted Task Instruction Recordはimmutableなので、
**過去Task本文は修正しないこと。**

現在有効なSSOT / Templateのみ修正する。

---

# 14. Preserve Task Instruction Immutability

DEV-TASK-0006はCompleted Instruction Recordです。

```text
tasks/completed/DEV-TASK-0006.md
```

の本文を、
今回の修正内容に合わせて書き換えてはいけません。

修正履歴は、

```text
DEV-TASK-0007
Git history
TASK_REGISTER
Handoff REPORT
```

で追跡可能にする。

---

# 15. Task Lifecycle

本TaskはDEV-TASK-0006で確立した正式Lifecycleを使用してください。

```text
DEV-TASK-0007.md受領
↓
Task Intake
↓
tasks/active/DEV-TASK-0007.md
↓
TASK_REGISTER = ACTIVE
↓
Intake commit / push
↓
修正・検証
↓
tasks/completed/DEV-TASK-0007.md
↓
TASK_REGISTER = COMPLETED
↓
Final commit / push
↓
Handoff ZIP
↓
Planner Review
```

---

# 16. TASK_REGISTER

DEV-TASK-0007を正式登録してください。

Summary例：

```text
Review Evidence Timing修正・Handoff世代境界の明確化
```

DEV-TASK-0006の履歴を削除・変更しない。

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

最低限以下のTask追跡可能なcommitを行う。

Intake：

```text
DEV-TASK-0007: register task
```

Final例：

```text
DEV-TASK-0007: correct review evidence timing rules
```

すべてpushする。

---

# 18. Verification

最低限以下を確認してください。

- [ ] `REVIEW_RULES.md` が修正されている
- [ ] Builder VerificationとHuman / External Validationが区別されている
- [ ] Builder VerificationはHandoff前でも有効と明示されている
- [ ] 人間検証はHandoff世代単位で扱う
- [ ] 古い人間検証の自動持ち越し禁止が定義されている
- [ ] Explicit Carry-over Exceptionが存在する
- [ ] 通常Task completion flowと矛盾しない
- [ ] Handoff ZIP生成後に全Builder testを再実行するような誤ルールがない
- [ ] 現行SSOT / Templateに旧一般化表現が残っていない
- [ ] 過去Completed Task本文を書き換えていない
- [ ] `TASK_REGISTER.md` にDEV-TASK-0007が登録されている
- [ ] Task Intake commit / push済み
- [ ] Final commit / push済み
- [ ] `git diff --check` PASS
- [ ] tracked working tree clean

---

# 19. Handoff

Planner提出物は必ず、

```text
受け渡し/DEV-TASK-0007_PLANNER_HANDOFF.zip
```

1個のみ。

既存の標準Handoff Generatorを使用する。

500MB以内。

ZIP Portability VerificationをすべてPASSさせる。

最低限以下を含める。

```text
DEV-TASK-0007_PLANNER_HANDOFF.zip
├── REPORT.md
├── MANIFEST.md
└── files/
    ├── tasks/
    │   ├── TASK_REGISTER.md
    │   └── completed/
    │       └── DEV-TASK-0007.md
    └── docs/
        └── development/
            ├── DEVELOPMENT_SYSTEM.md
            └── REVIEW_RULES.md
```

実際に変更したTemplate / SSOTがあれば追加する。

---

# 20. REPORT.md Additional Section

REPORTに、

```text
## Review Evidence Rule Correction
```

を追加してください。

最低限：

```text
Previous problem:
Corrected Builder Verification rule:
Corrected Human / External Validation rule:
Carry-over exception:
Repository-wide search result:
```

を記録する。

---

# 21. Planner Review Guide

REPORTのPlanner Review Guideでは、
最低限以下を案内する。

1. `REVIEW_RULES.md` のEvidence分類
2. Builder VerificationがHandoff前でも有効であること
3. Human / External ValidationのHandoff Generation Boundary
4. Explicit Carry-over Exception
5. DEV-TASK-0006本文が改変されていないこと

---

# 22. Builder Final Response

既存標準に従う。

最低限：

```text
Task: DEV-TASK-0007
Status: COMPLETE / BLOCKED

実施内容:
- ...

Review Evidence:
- Builder Verification rule: ...
- Human / External Validation rule: ...
- Carry-over rule: ...

Task Lifecycle:
- Intake commit: ...
- Final commit: ...
- Register: ...

Git:
- Remote: https://github.com/h-shojaku/PB-Dev.git
- Branch: main
- Push: ...
- Working tree: ...

人間判断:
- 不要
または
- 必要: ...

これをPlannerに渡してください: <実際の絶対パス>\受け渡し\DEV-TASK-0007_PLANNER_HANDOFF.zip
```

**最後の1文より後には何も記載しないこと。**

---

# 23. Acceptance Criteria

以下をすべて満たせばCOMPLETE。

- [ ] DEV-TASK-0006のReview指摘が新Taskとして追跡されている
- [ ] Builder Verification Evidenceが正式定義されている
- [ ] Human / External Validation Evidenceが正式定義されている
- [ ] Builderの最終成果物に対するTask内検証はHandoff前でも有効
- [ ] 人間の実機・目視・操作確認はHandoff世代単位
- [ ] 新Handoff生成後、古い人間検証を自動持ち越ししない
- [ ] 人間明示指示によるCarry-over例外がある
- [ ] Builder標準Task Lifecycleと矛盾しない
- [ ] 現行SSOT / Templateから誤った旧一般化が除去されている
- [ ] 過去Task Instruction Recordはimmutableのまま
- [ ] Task Intake / Register / Completed lifecycleを適用
- [ ] GitHub commit / push完了
- [ ] tracked working tree clean
- [ ] `受け渡し/` にDEV-TASK-0007 ZIP 1個のみ
- [ ] Handoff Verification PASS
- [ ] 最終回答最後がZIP絶対パス案内

---

# 24. Scope Boundary

本TaskではReview Evidence Timingの矛盾修正だけに集中する。

以下は後続Taskへ残す。

- AI / Session切替
- Builder Session Handoff
- Planner Session Handoff
- Context Recovery
- Definition of Done全体統合
- Template Repository最終検証
- Product初期化フロー

今回の目的は、

**「BuilderがTask内で行う正式検証は正しく評価しつつ、古い人間実機結果だけを新しいHandoffへ誤って持ち越さない」**

というレビュー運用を確立することです。
