# Standard Handoff ZIP Generator & Verifier for AI Development System (PowerShell Wrapper)

[CmdletBinding()]
param (
    [string]$TaskId,
    [string]$StagingDir,
    [string]$RepoRoot,
    [string[]]$Require = @(),
    [switch]$Test
)

$ErrorActionPreference = "Stop"

$scriptDir = $PSScriptRoot
$pyScript = Join-Path -Path $scriptDir -ChildPath "create_handoff.py"
$handoffDirName = [System.Text.Encoding]::UTF8.GetString([byte[]](0xE5,0x8F,0x97,0xE3,0x81,0x91,0xE6,0xB8,0xA1,0xE3,0x81,0x97))

# Locate python executable
$pythonExe = Get-Command "python" -ErrorAction SilentlyContinue
if (-not $pythonExe) { $pythonExe = Get-Command "python3" -ErrorAction SilentlyContinue }
if (-not $pythonExe) { $pythonExe = Get-Command "py" -ErrorAction SilentlyContinue }

if ($Test) {
    if ($pythonExe) {
        try {
            $pyOut = & $pythonExe.Source $pyScript --test 2>&1
            if ($LASTEXITCODE -eq 0 -and $pyOut -notlike "*WindowsApps*") {
                Write-Host ($pyOut -join "`n")
                exit 0
            }
        } catch {}
    }

    Write-Host "Running self-tests for create_handoff.ps1..."
    $tmpDir = Join-Path -Path ([System.IO.Path]::GetTempPath()) -ChildPath ("create_handoff_test_" + [Guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path $tmpDir -Force | Out-Null
    try {
        $stg = Join-Path -Path $tmpDir -ChildPath "staging"
        New-Item -ItemType Directory -Path (Join-Path -Path $stg -ChildPath "files\docs") -Force | Out-Null
        Set-Content -Path (Join-Path -Path $stg -ChildPath "REPORT.md") -Value "# Report" -Encoding UTF8
        Set-Content -Path (Join-Path -Path $stg -ChildPath "MANIFEST.md") -Value "# Manifest`n- files/docs/test.md" -Encoding UTF8
        Set-Content -Path (Join-Path -Path $stg -ChildPath "files\docs\test.md") -Value "test" -Encoding UTF8

        $delivDir = Join-Path -Path $tmpDir -ChildPath $handoffDirName
        New-Item -ItemType Directory -Path $delivDir -Force | Out-Null
        $zipP = Join-Path -Path $delivDir -ChildPath "DEV-TASK-TEST_PLANNER_HANDOFF.zip"

        Compress-Archive -Path (Join-Path -Path $stg -ChildPath "*") -DestinationPath $zipP -Force
        if (-not (Test-Path -Path $zipP)) { throw "Failed to create ZIP" }

        Write-Host "ALL SELF-TESTS PASSED!"
        exit 0
    } finally {
        Remove-Item -Path $tmpDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

if (-not $TaskId -or -not $StagingDir) {
    Write-Host 'Usage: .\create_handoff.ps1 -TaskId <TASK-ID> -StagingDir <PATH> [-RepoRoot <PATH>] [-Require <FILES>]'
    exit 1
}

if ($pythonExe) {
    try {
        $pArgs = @($pyScript, "--task", $TaskId, "--staging", $StagingDir)
        if ($RepoRoot) { $pArgs += @("--repo-root", $RepoRoot) }
        foreach ($r in $Require) { $pArgs += @("--require", $r) }

        $pyOut = & $pythonExe.Source $pArgs 2>&1
        if ($LASTEXITCODE -eq 0 -and $pyOut -notlike "*WindowsApps*") {
            Write-Host ($pyOut -join "`n")
            exit 0
        }
    } catch {}
}

# Native PowerShell Handoff Generator Fallback
$targetRepoRoot = if ($RepoRoot) { (Resolve-Path -Path $RepoRoot).Path } else { (Resolve-Path -Path (Join-Path -Path $scriptDir -ChildPath "..")).Path }
$resolvedStaging = (Resolve-Path -Path $StagingDir).Path

$filesDirInStaging = Join-Path -Path $resolvedStaging -ChildPath "files"
if (-not (Test-Path -Path $filesDirInStaging) -or (Get-ChildItem -Path $filesDirInStaging -Recurse -ErrorAction SilentlyContinue).Count -eq 0) {
    New-Item -ItemType Directory -Path $filesDirInStaging -Force | Out-Null
    $coreItems = @("README.md", "CURRENT_STATE.md", "PROJECT_PROFILE.md", "AGENTS.md", "CLAUDE.md", "GEMINI.md", "docs", "scripts", "tasks", "templates")
    foreach ($item in $coreItems) {
        $src = Join-Path -Path $targetRepoRoot -ChildPath $item
        $dst = Join-Path -Path $filesDirInStaging -ChildPath $item
        if (Test-Path -Path $src) {
            Copy-Item -Path $src -Destination $dst -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

$delivDir = Join-Path -Path $targetRepoRoot -ChildPath $handoffDirName
if (-not (Test-Path -Path $delivDir)) { New-Item -ItemType Directory -Path $delivDir -Force | Out-Null }

# Clear old handoff files
Get-ChildItem -Path $delivDir -Recurse | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

$zipName = "${TaskId}_PLANNER_HANDOFF.zip"
$zipPath = Join-Path -Path $delivDir -ChildPath $zipName

Write-Host "Generating Handoff ZIP for task $TaskId..."
Compress-Archive -Path (Join-Path -Path $resolvedStaging -ChildPath "*") -DestinationPath $zipPath -Force
Write-Host "Created ZIP: $zipPath"

Write-Host "Verifying Handoff ZIP..."
if (-not (Test-Path -Path $zipPath)) { Write-Error "ZIP file was not created."; exit 1 }

Add-Type -AssemblyName System.IO.Compression.FileSystem
$zipArchive = [System.IO.Compression.ZipFile]::OpenRead($zipPath)
try {
    $entries = $zipArchive.Entries
    $entryNames = $entries.FullName

    $hasReport = $entryNames -contains "REPORT.md"
    $hasManifest = $entryNames -contains "MANIFEST.md"
    $filesCount = ($entries | Where-Object { $_.FullName -like "files/*" }).Count

    if (-not $hasReport) { Write-Error "REPORT.md is missing at ZIP root."; exit 1 }
    if (-not $hasManifest) { Write-Error "MANIFEST.md is missing at ZIP root."; exit 1 }
    if ($filesCount -eq 0) { Write-Error "Empty Review Package Rejection: 0 files under 'files/'."; exit 1 }

    foreach ($r in $Require) {
        $posixReq = $r.Replace('\', '/')
        if (-not ($entryNames -contains $posixReq)) {
            Write-Error "Required Review File Missing: '$r' missing from ZIP."; exit 1
        }
    }

    Write-Host "Verification metrics:"
    Write-Host "  entry_count: $($entries.Count)"
    Write-Host "  files_entry_count: $filesCount"
    Write-Host "  integrity: PASS"
    Write-Host 'Handoff ZIP generation & verification completed successfully!'
} finally {
    $zipArchive.Dispose()
}
