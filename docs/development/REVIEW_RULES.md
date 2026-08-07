# Review Rules

## 1. Purpose
本ドキュメント（`REVIEW_RULES.md`）は、Builderの成果物（Handoff ZIP）受領後にPlannerが行うレビュー評価手順、エビデンス（検証結果）の分類と有効性規定、レビュー結果の判定3分類、および次Taskへ接続するための標準規定です。

## 2. Evidence Categories & Validity Rules
Plannerがレビュー評価を行う際、エビデンスを以下の2種類に明確に区別し、それぞれの有効性規定に従って取り扱います。

### 2.1 Builder Verification Evidence (Builder技術検証エビデンス)
Builderがタスクスコープ内で実施する自動テスト・技術検証。

- **対象例**:
  - ユニットテスト、インテグレーションテスト
  - ビルド、リンターチェック、型チェック (type check)
  - 静的解析、`git diff --check`
  - スクリプト単体テスト、アーカイブ整合性チェック、自動解凍テスト
  - その他タスクの受入条件（Acceptance Criteria）に必要な技術的検証
- **有効性規定 (Validity Rule)**:
  - **タスクの最終成果物・最終コミットを対象として実施されている限り、Handoff ZIP生成前に実行された検証であっても、当該Handoffに対する正式な評価エビデンスとして完全有効** とします。
  - その後、検証対象を無効化するような追加の変更が入っていないことが条件です。
  - Handoff ZIP生成前に行われたという理由のみで無効化してはなりません。

### 2.2 Human / External Validation Evidence (人間・外部検証エビデンス)
リポジトリ外部、あるいはBuilder外部で行われる手動確認や実環境検証。

- **対象例**:
  - 人間による実機操作・画面目視確認
  - 操作感・UXの官能評価
  - ユーザーからの不具合報告
  - 端末固有・外部環境での手動テスト結果
- **有効性規定 & Handoff世代境界 (Handoff Generation Boundary)**:
  - 原則として、**評価対象の Handoff ZIP が生成された「後」に人間・外部によって実行された検証** のみをその Handoff の評価材料として扱います。
  - ある Handoff ZIP (Handoff A) に対して人間が報告した不具合や実機確認結果は、その後 Builder が修正を行って新しい Handoff ZIP (Handoff B) を生成した場合、**自動的に Handoff B へ持ち越されません**。
  - 新しい Handoff B を評価するには、新しい成果物に対して再度実機・手動確認を行うことが原則です。

### 2.3 Explicit Carry-over Exception (明示的持ち越し例外)
- 人間が明示的に「前回の実機確認結果を今回のHandoff評価材料として含めてよい」と指示した場合に限り、過去の人間検証エビデンスを新Handoffの評価に利用できます。
- BuilderやPlannerが推測で「変更がないはず」と判断して自動持ち越しすることは厳禁とします。

### 2.4 Handoff Generation Boundary Flow
```text
[Handoff A 生成]
    ↓
人間による実機確認 A (不具合発見)
    ↓
Builder 修正 & テスト実行 (Builder Verification B PASS)
    ↓
[Handoff B 生成]
    ↓
※ 実機確認 A の結果は Handoff B へ自動持ち越し不可。
※ Builder Verification B (テストPASS) は Handoff B の有効エビデンス。
※ Handoff B に対する新しい実機確認 B を受けて評価を確定。
```

## 3. Planner Review Gate
Plannerは、Builderから提出された `受け渡し/<TASK-ID>_PLANNER_HANDOFF.zip` を受領した際、以下の要素をレビューします。

1. `REPORT.md`: タスク概要、変更点、Builder検証結果、ZIP Portability検証、受入条件クリア状況
2. `MANIFEST.md`: コンテンツ索引、絶対パス、リポジトリ・コミット情報
3. 対象 Task 文書: `files/tasks/completed/<TASK-ID>.md` （または `active/`）
4. 変更成果物 (`files/` 配下)
5. 自動検証ログ (Verification Metrics) および Git コミット・プッシュ状態

## 4. Review Results Classification (3分類)
Plannerのレビュー結果は、以下の3種類に明確に分類されます。

### 4.1 ACCEPTED (承認)
- **条件**: Taskの受入条件（Acceptance Criteria）がすべて満たされ、検証が正常に通過している場合。
- **後続動作**: 当該Taskのライフサイクルを正式に終了し、必要に応じて次Taskを新規発行します。

### 4.2 CHANGES_REQUIRED (修正要求)
- **条件**: 成果物に不足・不具合・受入条件の未達成がある場合。
- **後続動作**: 完了済みタスク文書や Git 履歴を書き換えて「無かったこと」にしてはなりません。**修正用の新しい Task ID（例: `DEV-TASK-0007`）を新しく発行**します。
- **新Taskでの参照**: 新Task内で前Task IDを参照し、不具合内容および必要な修正事項を明確に指示します。

### 4.3 HUMAN_DECISION_REQUIRED (人間判断要求)
- **条件**: 製品仕様の選択や不確実な判断等、人間（ユーザー）による判断が必要な場合。
- **後続動作**: Plannerは何を決定すべきかを整理・提示します。判断確定後、同じTaskを継続するか、あるいは新Taskを発行するか決定します。

## 5. No Next Task Before Review
- Builderは、**現在提出中のTaskに対するPlanner Reviewが完了する前に、自律的に次の未発行Taskへ着手してはなりません**。
- Builderの「自律実行原則」は、与えられた単一Taskの完了までを自律的に進めることを意味し、未発行の次タスクを独断で開始することを意味しません。

## 6. Planner Next-Task Issuance & Progress Behavior
- Planner Review の結果が `ACCEPTED` であり、次に実行すべきタスクが一意に定まっている場合、Plannerは **同じ応答内で「レビュー結果」＋「次タスク（1 Markdownファイル）」＋「簡潔な進捗レポート」を同時に提示** します。
- 不要な「次へ進めますか？」といった中間確認でユーザー体験を妨げてはなりません。

### 6.1 Progress Report Format
Plannerが提示する進捗レポートは、以下のように簡潔な形式とします。

```text
進捗: 6 / 8 Task 完了

完了:
- DEV-TASK-0001: ...
- DEV-TASK-0005: ...
現在:
- DEV-TASK-0006: ...
残り:
- DEV-TASK-0007: ...
```
