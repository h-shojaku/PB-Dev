# Scripts Area

このディレクトリは、開発運用およびタスク自動化（Handoff ZIP 生成・検証、プロジェクト初期化、自動テスト等）のための標準スクリプトを配置する領域です。

## スクリプト一覧
- `create_handoff.py` / `create_handoff.ps1`: Cross-platform Handoff ZIP 生成・POSIX `/` 正規化・アーカイブ自動検証スクリプト。
- `initialize_project.py` / `initialize_project.ps1`: テンプレート複製後のプロジェクト初期化・タスクランタイム状態リセットスクリプト（`-DryRun` / `--dry-run` サポート）。
- `test_initialize_project.py` / `test_initialize_project.ps1`: Project Initializer の自動結合テスト＆ネガティブテストスイート（実ファイルシステム状態検証）。

## 実行方法 (例)

### Project Initializer 自動テスト実行
```powershell
powershell -ExecutionPolicy Bypass -File scripts/test_initialize_project.ps1
```

### プロジェクト初期化 (New Product, -DryRun 対応)
```powershell
powershell -ExecutionPolicy Bypass -File scripts/initialize_project.ps1 -Mode NEW_PRODUCT -Name MyCoolApp -Prefix APP -Remote https://github.com/myorg/MyCoolApp.git -DryRun
```

### Handoff ZIP 生成・検証
```powershell
powershell -ExecutionPolicy Bypass -File scripts/create_handoff.ps1 -TaskId DEV-TASK-0010 -StagingDir <STAGING_PATH>
```

※ 詳細な運用ルールは [PROJECT_INITIALIZATION_RULES.md](../docs/development/PROJECT_INITIALIZATION_RULES.md) および [HANDOFF_RULES.md](../docs/development/HANDOFF_RULES.md) を参照してください。
