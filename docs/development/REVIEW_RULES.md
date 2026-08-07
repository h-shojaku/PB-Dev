# Review Rules

## 1. Purpose
本ドキュメント（`REVIEW_RULES.md`）は、Builderの成果物（Handoff ZIP）受領後にPlannerが行うレビュー評価手順、レビュー結果の分類、および次Taskへ接続するための標準規定です。

## 2. Planner Review Gate
Plannerは、Builderから提出された `受け渡し/<TASK-ID>_PLANNER_HANDOFF.zip` を受領した際、以下の要素を検証・レビューします。

1. `REPORT.md`: タスク概要、変更点、検証結果、受入条件クリア状況
2. `MANIFEST.md`: コンテンツ索引、絶対パス、リポジトリ・コミット情報
3. 対象 Task 文書: `files/tasks/completed/<TASK-ID>.md` （または `active/`）
4. 変更成果物 (`files/` 配下)
5. 自動検証ログ (Verification Metrics) および Git コミット・プッシュ状態

## 3. Review Results Classification (3分類)
Plannerのレビュー結果は、以下の3種類に明確に分類されます。

### 3.1 ACCEPTED (承認)
- **条件**: Taskの受入条件（Acceptance Criteria）がすべて満たされ、検証が正常に通過している場合。
- **後続動作**: 当該Taskのライフサイクルを正式に終了し、必要に応じて次Taskを新規発行します。

### 3.2 CHANGES_REQUIRED (修正要求)
- **条件**: 成果物に不足・不具合・受入条件の未達成がある場合。
- **後続動作**: 完了済みタスク文書や Git 履歴を書き換えて「無かったこと」にしてはなりません。**修正用の新しい Task ID（例: `DEV-TASK-0007`）を新しく発行**します。
- **新Taskでの参照**: 新Task内で前Task IDを参照し、不具合内容および必要な修正事項を明確に指示します。

### 3.3 HUMAN_DECISION_REQUIRED (人間判断要求)
- **条件**: 製品仕様の選択や不確実な判断等、人間（ユーザー）による判断が必要な場合。
- **後続動作**: Plannerは何を決定すべきかを整理・提示します。判断確定後、同じTaskを継続するか、あるいは新Taskを発行するか決定します。

## 4. No Next Task Before Review
- Builderは、**現在提出中のTaskに対するPlanner Reviewが完了する前に、自律的に次の未発行Taskへ着手してはなりません**。
- Builderの「自律実行原則」は、与えられた単一Taskの完了までを自律的に進めることを意味し、未発行の次タスクを独断で開始することを意味しません。

## 5. Planner Next-Task Issuance & Progress Behavior
- Planner Review の結果が `ACCEPTED` であり、次に実行すべきタスクが一意に定まっている場合、Plannerは **同じ応答内で「レビュー結果」＋「次タスク（1 Markdownファイル）」＋「簡潔な進捗レポート」を同時に提示** します。
- 不要な「次へ進めますか？」といった中間確認でユーザー体験を妨げてはなりません。

### 5.1 Progress Report Format
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

## 6. Review Evidence Timing Rule
- Plannerがレビュー評価に用いる検証エビデンスは、**「当該Handoff ZIPが生成された後に実行された検証」** のみを対象とします。
- Handoff提出前に行われた人間の観察結果や過去の検証は、その後に新Handoffが作成された場合、自動的に新Handoffの評価結果へ引き継がれません（再検証が必要）。
