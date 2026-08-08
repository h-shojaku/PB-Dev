# Project Initializer for AI Development System (PowerShell Implementation)

[CmdletBinding()]
param (
    [string]$Mode = "NEW_PRODUCT",
    [string]$Name = "MyNewProduct",
    [string]$Prefix = "APP",
    [string]$Remote = "",
    [switch]$Force,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

# Validations
if ($Mode -notin @("NEW_PRODUCT", "EXISTING_PRODUCT", "TEMPLATE")) {
    Write-Error "Invalid mode '$Mode'. Must be NEW_PRODUCT, EXISTING_PRODUCT, or TEMPLATE."
    exit 1
}

if ($Prefix -notmatch '^[A-Z0-9]{2,10}$') {
    Write-Error "Invalid Task Prefix '$Prefix'. Must be 2-10 uppercase alphanumeric characters."
    exit 1
}

if ($Name -notmatch '^[a-zA-Z0-9_\-]{2,50}$') {
    Write-Error "Invalid Project Name '$Name'. Must be 2-50 alphanumeric, underscore, or hyphen characters."
    exit 1
}

if ($Mode -ne "TEMPLATE") {
    if ([string]::IsNullOrWhiteSpace($Remote)) {
        Write-Error "--Remote is required for NEW_PRODUCT and EXISTING_PRODUCT modes."
        exit 1
    }

    $invalidPatterns = @("example\.com", "github\.com/example/", "^TODO$", "^TBD$")
    foreach ($pat in $invalidPatterns) {
        if ($Remote -match $pat) {
            Write-Error "Invalid placeholder remote URL detected: '$Remote'"
            exit 1
        }
    }

    if ($Remote -notmatch '^(https://|git@|ssh://)') {
        Write-Error "Remote URL must be a valid Git URL (https:// or git@): '$Remote'"
        exit 1
    }
}

$repoRoot = (Resolve-Path -Path (Join-Path -Path $PSScriptRoot -ChildPath "..")).Path

# 1. Git Repository Check
try {
    $isGit = (git -C $repoRoot rev-parse --is-inside-work-tree 2>$null).Trim()
    if ($isGit -ne "true") {
        Write-Error "Not a Git Repository: Project Initialization requires a valid Git repository with .git directory."
        exit 1
    }
} catch {
    Write-Error "Not a Git Repository: Project Initialization requires a valid Git repository with .git directory."
    exit 1
}

# 2. Template and Existing SSOT Preflight Check
$productTplDir = Join-Path -Path $repoRoot -ChildPath "templates\product"
$productDocsDir = Join-Path -Path $repoRoot -ChildPath "docs\product"
$requiredTpls = @("00_PRODUCT_OVERVIEW.md", "01_PRODUCT_PLAN.md", "02_REQUIREMENTS.md", "03_UI_STRUCTURE.md", "04_IMPLEMENTATION_SPEC.md", "05_OPERATION_RULES.md")

if ($Mode -eq "NEW_PRODUCT") {
    foreach ($tpl in $requiredTpls) {
        if (-not (Test-Path -Path (Join-Path -Path $productTplDir -ChildPath $tpl))) {
            Write-Error "Missing Product Template: '$tpl' in templates/product/"
            exit 1
        }
    }

    if ((Test-Path -Path $productDocsDir) -and -not $Force) {
        $existingFiles = Get-ChildItem -Path $productDocsDir -File -Filter "*.md" -ErrorAction SilentlyContinue
        foreach ($ef in $existingFiles) {
            if ($ef.Length -gt 0) {
                Write-Error "Existing Product SSOT detected in docs/product/'$($ef.Name)'. Use -Force to overwrite."
                exit 1
            }
        }
    }
}

$statusLabel = if ($DryRun) { "DRY-RUN" } else { "EXEC" }
Write-Host ("[" + $statusLabel + "] Initializing Project: " + $Name + " (Mode: " + $Mode + ", Prefix: " + $Prefix + ")")

$nowIso = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$profilePath = Join-Path -Path $repoRoot -ChildPath "PROJECT_PROFILE.md"
$registerPath = Join-Path -Path $repoRoot -ChildPath "tasks\TASK_REGISTER.md"
$statePath = Join-Path -Path $repoRoot -ChildPath "CURRENT_STATE.md"
$activeDir = Join-Path -Path $repoRoot -ChildPath "tasks\active"
$completedDir = Join-Path -Path $repoRoot -ChildPath "tasks\completed"

# Dynamic UTF-8 decode for delivery directory name
$handoffDirName = [System.Text.Encoding]::UTF8.GetString([byte[]](0xE5,0x8F,0x97,0xE3,0x81,0x91,0xE6,0xB8,0xA1,0xE3,0x81,0x97))
$handoffDir = Join-Path -Path $repoRoot -ChildPath $handoffDirName

$reportsAnalysisDir = Join-Path -Path $repoRoot -ChildPath "reports\analysis"

$bt = '`'

$profileContent = @"
# Project Profile

## Project Identity
- Project Name: $bt$Name$bt
- Project Mode: $bt$Mode$bt
- Task Prefix: $bt$Prefix$bt

## Repository
- Canonical Remote: $bt$Remote$bt
- Default Branch: ${bt}main$bt

## Product
- Product SSOT Root: ${bt}docs/product/${bt}

## Development Standard
- Source Template: ${bt}PB-Dev${bt}
- Planner Role: Browser AI
- Builder Role: VSCode + CLI AI

## Initialization
- Initialized At: $bt$nowIso$bt
- Initialized By Task: ${bt}INIT${bt}
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

$nextActionMsg = if ($Mode -eq "NEW_PRODUCT") { "Planner issues first product planning task ($bt$Prefix-TASK-0001$bt)." } else { "Planner issues first Baseline Analysis task ($bt$Prefix-TASK-0001$bt)." }

$stateContent = @"
# Current State

当リポジトリにおける現在の開発運用状態を示すインデックス・スナップショット（Current State Index）です。

## Repository
- Project Profile: [PROJECT_PROFILE.md](PROJECT_PROFILE.md)
- Project Name: $bt$Name$bt
- Task Prefix: $bt$Prefix$bt
- Canonical Remote: $bt$Remote$bt
- Default Branch: ${bt}main${bt}

## Workflow Phase
${bt}IDLE${bt}

## Current Task
- Task ID: ${bt}None${bt} (現在実行中のActive Taskはありません)

## Latest Completed Task
- Task ID: ${bt}None${bt}

## Git State
- Branch: ${bt}main${bt}
- Working Tree Status: ${bt}Clean${bt}
- HEAD Commit: Resolved dynamically via ${bt}git rev-parse HEAD${bt}

## Human Decision Status
- Status: ${bt}None${bt}

## Known Blocking Issues
- Blocking Issues: ${bt}None${bt}

## Relevant SSOT
- Development System: [DEVELOPMENT_SYSTEM.md](docs/development/DEVELOPMENT_SYSTEM.md)
- Project Initialization Rules: [PROJECT_INITIALIZATION_RULES.md](docs/development/PROJECT_INITIALIZATION_RULES.md)
- Task Register: [TASK_REGISTER.md](tasks/TASK_REGISTER.md)

## Recovery Entry Point
- Builder: `README.md` -> `AGENTS.md` -> `CURRENT_STATE.md` -> `tasks/TASK_REGISTER.md`

## Next Expected Action
$nextActionMsg

## Last Updated
$nowIso
"@

if (-not $DryRun) {
    # 3. Apply Git Remote
    if ($Mode -ne "TEMPLATE" -and $Remote) {
        $remotes = (git -C $repoRoot remote 2>$null)
        if ($remotes -contains "origin") {
            git -C $repoRoot remote set-url origin $Remote 2>$null
        } else {
            git -C $repoRoot remote add origin $Remote 2>$null
        }
        $actualOrigin = (git -C $repoRoot remote get-url origin 2>$null).Trim()
        if ($actualOrigin -ne $Remote) {
            Write-Error "Remote Mismatch: actual origin '$actualOrigin' does not match requested remote '$Remote'."
            exit 1
        }
    }

    Set-Content -Path $profilePath -Value $profileContent -Encoding UTF8
    Set-Content -Path $registerPath -Value $registerContent -Encoding UTF8
    Set-Content -Path $statePath -Value $stateContent -Encoding UTF8

    if (Test-Path -Path $activeDir) {
        Get-ChildItem -Path $activeDir -File | Remove-Item -Force
    }

    if ($Mode -in @("NEW_PRODUCT", "EXISTING_PRODUCT") -and (Test-Path -Path $completedDir)) {
        Get-ChildItem -Path $completedDir -File | Remove-Item -Force
    }

    if (Test-Path -Path $handoffDir) {
        Get-ChildItem -Path $handoffDir -Force | Remove-Item -Recurse -Force
    }

    if ($Mode -eq "NEW_PRODUCT") {
        if (-not (Test-Path -Path $productDocsDir)) { New-Item -ItemType Directory -Path $productDocsDir -Force | Out-Null }
        foreach ($f in $requiredTpls) {
            $src = Join-Path -Path $productTplDir -ChildPath $f
            if (Test-Path -Path $src) {
                Copy-Item -Path $src -Destination (Join-Path -Path $productDocsDir -ChildPath $f) -Force
            }
        }
    }

    if ($Mode -eq "EXISTING_PRODUCT") {
        if (-not (Test-Path -Path $reportsAnalysisDir)) { New-Item -ItemType Directory -Path $reportsAnalysisDir -Force | Out-Null }
        $srcAnalysis = Join-Path -Path $productTplDir -ChildPath "EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md"
        if (Test-Path -Path $srcAnalysis) {
            Copy-Item -Path $srcAnalysis -Destination (Join-Path -Path $reportsAnalysisDir -ChildPath "EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md") -Force
        }
    }

    # Final Post-Condition Verification
    if (-not (Test-Path -Path $profilePath) -or -not (Test-Path -Path $statePath) -or -not (Test-Path -Path $registerPath)) {
        Write-Error "Final Post-Condition Failed: Required initialization files were not created."
        exit 1
    }

    if ($Mode -eq "NEW_PRODUCT") {
        $pDocsCount = (Get-ChildItem -Path $productDocsDir -File -ErrorAction SilentlyContinue).Count
        if ($pDocsCount -lt 6) {
            Write-Error "Final Post-Condition Failed: docs/product expected 6 files, found $pDocsCount."
            exit 1
        }
    }
}

Write-Host ("[" + $statusLabel + "] Project initialization completed successfully.")
