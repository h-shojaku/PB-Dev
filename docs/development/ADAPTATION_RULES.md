# Adaptive Workflow Rules (適応型ワークフロー規則)

## 1. Purpose (目的)
本ドキュメント（`ADAPTATION_RULES.md`）は、AI Development Standard において、事前定義された「手順（Procedure）」が状況の変化や問題の発生によって不適切・非効率となった際、Planner および Builder が人間の介入を要求することなく、**自律的に最も確実な代替手法へ切り替えるための適応型ワークフロー原則（Adaptive Workflow Principle）**を定義します。

---

## 2. Core Principle: Outcome-over-Procedure (目的優先の原則)

> **Procedure is replaceable. Objective / SSOT / Acceptance Criteria / Safety are not.**  
> (手順は置換可能である。目的・SSOT・受入条件・安全性は不可変である。)

タスクの目的（Objective）、受入条件（Acceptance Criteria）、SSOT、および開発セーフティ制約を満たす限り、Planner および Builder は過去に定義された特定の手順やツールに固執してはなりません。

---

## 3. Boundary Definition: Stable vs Replaceable (不可変領域と可変領域の境界)

自律的な変更が許容される範囲と、人間の明示的判断（Human Decision）を要する範囲を明確に定義します。

### 3.1 Stable Boundaries (不可変領域 — 自律変更禁止)
以下の項目は、人間の明示的許可なしに Planner / Builder が勝手に変更・緩和・破棄してはなりません。

1. **Human Explicit Decisions**（人間が明示指示した決定・方針）
2. **Product Requirements & Product SSOT**（製品要件および `docs/product/` 仕様）
3. **Development Safety Constraints**（破壊的変更禁止・無効バイパス禁止・Git安全規定）
4. **Task Objective & Acceptance Criteria**（タスクの到達ゴールおよび合格基準）
5. **Data & Security Constraints**（認証情報・機密データ・アクセス制御）
6. **External Boundaries**（外部公開・本番デプロイ・課金・サードパーティ連携）

### 3.2 Replaceable Elements (可変領域 — 自律変更・改善必須)
以下の項目は、タスク目的と安全性を維持・向上させる目的において、Planner / Builder が事前の人間承認なしに自律的に最も確実な方法へ変更可能です。

1. **Implementation Technique**（内部コードの実装技法・リファクタリング手法）
2. **Testing Technique**（テストの組み立て・モック方式・検証スクリプト構造）
3. **Review Technique**（レビューにおける差分検出・検証ツール・検証手順）
4. **Tool & Language Choice**（スクリプト言語選択: Python / PowerShell、内部ユーティリティ）
5. **Directory & Staging Strategy**（一時ディレクトリの配置・ステージング管理手法）
6. **File Discovery Method**（手動ファイル列挙 vs `git ls-files` / `git archive` 等の機械検出）
7. **Handoff Packaging Implementation**（Handoff ZIP 内のデータ構造および生成実装）
8. **Investigation & Debugging Approach**（調査手法・ログ出力・デバッグアプローチ）

---

## 4. Adaptive Triggers & Repeated Known-Bad Prevention (適応トリガーと再発防止)

### 4.1 Repeated Known-Bad Prevention (同一失敗の反復禁止)
- 一度失敗した、または非効率であることが発覚した手法を、理由なく同じ方法で繰り返すことを厳禁とします（"No Known-Bad Retries"）。
- 手順の不不備によってエラーや矛盾が発生した場合、Planner / Builder は直ちに原因を特定し、ワークフロー自体をより堅牢な方法へ自律改修しなければなりません。

### 4.2 Adaptive Triggers (自動切替トリガー)
以下の事象が発生した場合、適応型切替（Adaptive Switching）を発動します:

1. **Procedural Inconsistency**（手順に基づく出力と実際の状態に解離が発生した場合）
2. **Tool Failure / Platform Flakiness**（特定 OS やツール環境で動作が不確定な場合）
3. **Omitting / Human Error Risks**（手動指定によって選択漏れや転記ミスが発生しやすい場合）
4. **Efficiency Bottleneck**（従来の手順が非効率であり、機械的自動化へ置換可能な場合）

---

## 5. Escalation Ladder (エスカレーション規定)

1. **手法変更のみ（Scope 内）**:
   - タスク目的・SSOT・受入条件を変えずに手段・ツール・パッケージ構造を改善する場合 ➔ **即座に自律実行（人間確認不要）**
2. **Scope / SSOT の変更を伴う場合**:
   - 要件の変更、安全制約の緩和、本番システムへの影響が発生する場合 ➔ **直ちに BLOCK し人間判断（Human Decision）を要求**
