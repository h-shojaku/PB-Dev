# Project Initialization & Runtime State Reset Tool for AI Development System (PowerShell)

[CmdletBinding()]
param (
    [string]$Mode = "NEW_PRODUCT",
    [string]$Name = "MyNewProduct",
    [string]$Prefix = "APP",
    [string]$Remote = "",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path -Path (Join-Path -Path $PSScriptRoot -ChildPath "..")).Path
$profilePath = Join-Path -Path $repoRoot -ChildPath "PROJECT_PROFILE.md"
$registerPath = Join-Path -Path $repoRoot -ChildPath "tasks\TASK_REGISTER.md"
$statePath = Join-Path -Path $repoRoot -ChildPath "CURRENT_STATE.md"
$activeDir = Join-Path -Path $repoRoot -ChildPath "tasks\active"

$statusLabel = if ($DryRun) { "DRY-RUN" } else { "EXEC" }
Write-Host ("[" + $statusLabel + "] Initializing Project: " + $Name + " (Mode: " + $Mode + ", Prefix: " + $Prefix + ")")

$canonicalRemote = ""
if ($Remote) {
    $canonicalRemote = $Remote
} else {
    $canonicalRemote = "https://github.com/example/" + $Name + ".git"
}

$profileContent = @"
# Project Profile

## Project Identity
- Project Name: `$Name`
- Project Mode: `$Mode`
- Task Prefix: `$Prefix`

## Repository
- Canonical Remote: `$canonicalRemote`
- Default Branch: `main`

## Product
- Product SSOT Root: `docs/product/`

## Development Standard
- Source Template: `PB-Dev`
- Planner Role: Browser AI
- Builder Role: VSCode + CLI AI

## Initialization
- Initialized At: `2026-08-08T00:00:00+09:00`
- Initialized By Task: `INIT`
"@

$registerContent = @"
# Task Register

当リポジトリにおけるすべてのTaskの現在状態および発行履歴を管理するレジスタです。

## Current Active Task

| Task ID | Status | Location | Started | Summary |
|---|---|---|---|---|
| (なし) | - | - | - | 現在進行中のActive Taskはありません |

## Task History

| Task ID | Status | Location | Started | Completed | Summary |
|---|---|---|---|---|---|
"@

$stateContent = @"
# Current State

当リポジトリにおける現在の開発運用状態を示すインデックス・スナップショット（Current State Index）です。

## Repository
- Project Profile: [PROJECT_PROFILE.md](PROJECT_PROFILE.md)
- Project Name: `$Name`
- Task Prefix: `$Prefix`
- Canonical Remote: `$canonicalRemote`
- Current Branch: `main`

## Workflow Phase
`IDLE`

## Current Task
- Task ID: `None` (現在実行中のActive Taskはありません)

## Latest Completed Task
- Task ID: `None`

## Git State
- Branch: `main`
- Working Tree Status: `Clean`
- HEAD Commit: Resolved dynamically via `git rev-parse HEAD`

## Human Decision Status
- Status: `None`

## Known Blocking Issues
- Blocking Issues: `None`

## Relevant SSOT
- Development System: [DEVELOPMENT_SYSTEM.md](docs/development/DEVELOPMENT_SYSTEM.md)
- Project Initialization Rules: [PROJECT_INITIALIZATION_RULES.md](docs/development/PROJECT_INITIALIZATION_RULES.md)
- Task Register: [TASK_REGISTER.md](tasks/TASK_REGISTER.md)

## Recovery Entry Point
- Builder: `README.md` -> `AGENTS.md` -> `CURRENT_STATE.md` -> `tasks/TASK_REGISTER.md`

## Next Expected Action
Planner issues first product planning task (`$Prefix-TASK-0001`).

## Last Updated
2026-08-08T00:00:00+09:00
"@

if (-not $DryRun) {
    Set-Content -Path $profilePath -Value $profileContent -Encoding UTF8
    Set-Content -Path $registerPath -Value $registerContent -Encoding UTF8
    Set-Content -Path $statePath -Value $stateContent -Encoding UTF8

    if (Test-Path -Path $activeDir) {
        Get-ChildItem -Path $activeDir -File | Remove-Item -Force
    }
}

Write-Host ("[" + $statusLabel + "] Project initialization completed successfully.")
