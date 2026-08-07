# Scripts Area

このディレクトリは、開発運用およびタスク自動化（Handoff ZIP 生成・検証等）のための標準スクリプトを配置する領域です。

## スクリプト一覧
- `create_handoff.py`: Cross-platform Python 3 スクリプト。Handoff ZIP 生成・POSIX `/` 正規化・アーカイブ自動検証を実行。
- `create_handoff.ps1`: Cross-platform PowerShell / .NET スクリプト。Windows PowerShell / PowerShell Core 環境で `create_handoff.py` と同等の生成・検証を実行。

## 実行方法 (例)

### PowerShell
```powershell
powershell -ExecutionPolicy Bypass -File scripts/create_handoff.ps1 -TaskId DEV-TASK-0005 -StagingDir <STAGING_PATH>
```

### Python
```bash
python scripts/create_handoff.py --task DEV-TASK-0005 --staging <STAGING_PATH>
```

### 単体テスト (Self-Test)
```powershell
powershell -ExecutionPolicy Bypass -File scripts/create_handoff.ps1 -Test
python scripts/create_handoff.py --test
```

※ Handoff受渡ルールの正式SSOTは [HANDOFF_RULES.md](../docs/development/HANDOFF_RULES.md) を参照してください。
