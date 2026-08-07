# Scripts Area

このディレクトリは、開発運用およびタスク自動化（Handoff ZIP 生成・検証、プロジェクト初期化等）のための標準スクリプトを配置する領域です。

## スクリプト一覧
- `create_handoff.py` / `create_handoff.ps1`: Cross-platform Handoff ZIP 生成・POSIX `/` 正規化・アーカイブ自動検証スクリプト。
- `initialize_project.py` / `initialize_project.ps1`: テンプレート複製後のプロジェクト初期化・タスクランタイム状態リセットスクリプト（`-DryRun` / `--dry-run` サポート）。

## 実行方法 (例)

### Handoff ZIP 生成・検証
```powershell
powershell -ExecutionPolicy Bypass -File scripts/create_handoff.ps1 -TaskId DEV-TASK-0009 -StagingDir <STAGING_PATH>
```

### プロジェクト初期化 (-DryRun 対応)
```powershell
powershell -ExecutionPolicy Bypass -File scripts/initialize_project.ps1 -Mode NEW_PRODUCT -Name MyCoolApp -Prefix APP -DryRun
```

### 単体テスト (Self-Test)
```powershell
powershell -ExecutionPolicy Bypass -File scripts/create_handoff.ps1 -Test
```

※ 詳細な運用ルールは [PROJECT_INITIALIZATION_RULES.md](../docs/development/PROJECT_INITIALIZATION_RULES.md) および [HANDOFF_RULES.md](../docs/development/HANDOFF_RULES.md) を参照してください。
