# Standard Handoff ZIP Generator & Verifier for AI Development System (PowerShell / .NET).
# Cross-platform: Windows PowerShell and PowerShell Core.

[CmdletBinding()]
param (
    [string]$TaskId,
    [string]$StagingDir,
    [string]$RepoRoot,
    [switch]$Test
)

$ErrorActionPreference = "Stop"

[Reflection.Assembly]::LoadWithPartialName("System.IO.Compression") | Out-Null
[Reflection.Assembly]::LoadWithPartialName("System.IO.Compression.FileSystem") | Out-Null

$MAX_ZIP_SIZE_BYTES = 500 * 1024 * 1024

function Get-DeliveryDirName {
    return [System.Text.Encoding]::UTF8.GetString([byte[]](0xE3,0x81,0x86,0xE3,0x81,0x91,0xE6,0xB8,0xA1,0xE3,0x81,0x97))
}

function Normalize-ZipEntryName([string]$relPath) {
    $posix = $relPath -replace '\\', '/'
    $posix = $posix -replace '^[a-zA-Z]:', ''
    $posix = $posix.TrimStart('/')
    return $posix
}

function Test-ValidEntryName([string]$entryName) {
    if ($entryName.Contains('\')) {
        throw ("Forbidden backslash in ZIP entry name: " + $entryName)
    }
    if ($entryName.StartsWith('/') -or $entryName -match '^[a-zA-Z]:') {
        throw ("Forbidden absolute path in ZIP entry name: " + $entryName)
    }
    $parts = $entryName.Split('/')
    if ($parts -contains '..') {
        throw ("Forbidden parent traversal in ZIP entry name: " + $entryName)
    }
    if ($parts -contains '.git') {
        throw ("Forbidden git directory in ZIP entry name: " + $entryName)
    }
}

function New-HandoffZip([string]$tId, [string]$stagingPath, [string]$repoRootPath) {
    $deliveryDirName = Get-DeliveryDirName
    $deliveryDir = Join-Path -Path $repoRootPath -ChildPath $deliveryDirName
    if (-not (Test-Path -Path $deliveryDir)) {
        New-Item -ItemType Directory -Path $deliveryDir -Force | Out-Null
    }

    Get-ChildItem -Path $deliveryDir -Force | Remove-Item -Recurse -Force

    $zipFilename = $tId + "_PLANNER_HANDOFF.zip"
    $zipPath = Join-Path -Path $deliveryDir -ChildPath $zipFilename

    if (Test-Path -Path $zipPath) { Remove-Item -Force $zipPath }

    $mode = [System.IO.Compression.ZipArchiveMode]::Create
    $zipArchive = [System.IO.Compression.ZipFile]::Open($zipPath, $mode)

    try {
        $stagingResolved = [System.IO.Path]::GetFullPath($stagingPath)
        $files = Get-ChildItem -Path $stagingResolved -Recurse -File

        foreach ($file in $files) {
            $fullFilePath = $file.FullName
            $relPath = $fullFilePath.Substring($stagingResolved.Length).TrimStart('\', '/')
            $entryName = Normalize-ZipEntryName -relPath $relPath
            Test-ValidEntryName -entryName $entryName

            $entry = $zipArchive.CreateEntry($entryName, [System.IO.Compression.CompressionLevel]::Optimal)
            $entryStream = $entry.Open()
            $fileStream = [System.IO.File]::OpenRead($fullFilePath)
            $fileStream.CopyTo($entryStream)
            $fileStream.Dispose()
            $entryStream.Dispose()
        }
    }
    finally {
        $zipArchive.Dispose()
    }

    return $zipPath
}

function Test-HandoffZip([string]$zipPath, [string]$repoRootPath) {
    if (-not (Test-Path -Path $zipPath)) {
        throw ("Handoff ZIP does not exist: " + $zipPath)
    }

    $zipFileItem = Get-Item -Path $zipPath
    $size = $zipFileItem.Length
    if ($size -gt $MAX_ZIP_SIZE_BYTES) {
        throw ("Handoff ZIP size " + $size + " bytes exceeds limit.")
    }

    $deliveryDirName = Get-DeliveryDirName
    $deliveryDir = Join-Path -Path $repoRootPath -ChildPath $deliveryDirName
    $dirItems = Get-ChildItem -Path $deliveryDir -Force
    $deliveryFileCount = ($dirItems | Where-Object { -not $_.PSIsContainer }).Count
    $deliveryZipCount = ($dirItems | Where-Object { $_.Name.EndsWith('.zip') }).Count
    $deliverySubdirCount = ($dirItems | Where-Object { $_.PSIsContainer }).Count

    if ($deliveryFileCount -ne 1 -or $deliveryZipCount -ne 1 -or $deliverySubdirCount -ne 0) {
        throw ("Delivery directory state invalid. Files: " + $deliveryFileCount + ", ZIPs: " + $deliveryZipCount + ", Subdirs: " + $deliverySubdirCount)
    }

    $backslashCount = 0
    $absoluteCount = 0
    $traversalCount = 0
    $entryCount = 0
    $hasReport = $false
    $hasManifest = $false

    $zipArchive = [System.IO.Compression.ZipFile]::OpenRead($zipPath)
    try {
        $entryCount = $zipArchive.Entries.Count
        foreach ($e in $zipArchive.Entries) {
            $name = $e.FullName
            if ($name.Contains('\')) { $backslashCount++ }
            if ($name.StartsWith('/') -or $name -match '^[a-zA-Z]:') { $absoluteCount++ }
            if ($name.Split('/') -contains '..') { $traversalCount++ }
            if ($name -eq 'REPORT.md') { $hasReport = $true }
            if ($name -eq 'MANIFEST.md') { $hasManifest = $true }
        }

        if (-not $hasReport) { throw "REPORT.md is missing at ZIP root." }
        if (-not $hasManifest) { throw "MANIFEST.md is missing at ZIP root." }
        if ($backslashCount -gt 0) { throw ("Found " + $backslashCount + " entries containing backslashes.") }
        if ($absoluteCount -gt 0) { throw ("Found " + $absoluteCount + " entries containing absolute paths.") }
        if ($traversalCount -gt 0) { throw ("Found " + $traversalCount + " entries containing parent traversals.") }

        # Extraction test
        $tmpExtract = Join-Path -Path ([System.IO.Path]::GetTempPath()) -ChildPath ("extract_" + [Guid]::NewGuid().ToString())
        New-Item -ItemType Directory -Path $tmpExtract -Force | Out-Null
        try {
            [System.IO.Compression.ZipFile]::ExtractToDirectory($zipPath, $tmpExtract)
            if (-not (Test-Path -Path (Join-Path -Path $tmpExtract -ChildPath "REPORT.md"))) {
                throw "Extraction test failed: REPORT.md not found."
            }
            if (-not (Test-Path -Path (Join-Path -Path $tmpExtract -ChildPath "MANIFEST.md"))) {
                throw "Extraction test failed: MANIFEST.md not found."
            }
        }
        finally {
            if (Test-Path -Path $tmpExtract) { Remove-Item -Recurse -Force $tmpExtract }
        }
    }
    finally {
        $zipArchive.Dispose()
    }

    return @{
        "integrity" = "PASS"
        "file_size" = $size
        "entry_count" = $entryCount
        "backslash_count" = $backslashCount
        "absolute_count" = $absoluteCount
        "traversal_count" = $traversalCount
        "extraction_test" = "PASS"
        "delivery_file_count" = $deliveryFileCount
        "delivery_zip_count" = $deliveryZipCount
        "delivery_subdir_count" = $deliverySubdirCount
    }
}

function Run-SelfTests {
    Write-Host "Running self-tests for create_handoff.ps1..."

    $norm = Normalize-ZipEntryName -relPath "files\docs\development\HANDOFF_RULES.md"
    if ($norm -ne "files/docs/development/HANDOFF_RULES.md") {
        throw ("Normalization failed: " + $norm)
    }

    $normAbs = Normalize-ZipEntryName -relPath "C:\Users\test\files\README.md"
    if ($normAbs.Contains("C:") -or $normAbs.Contains("\")) {
        throw ("Drive letter/backslash normalization failed: " + $normAbs)
    }

    Test-ValidEntryName -entryName "files/docs/README.md"
    try {
        Test-ValidEntryName -entryName "files\docs\README.md"
        throw "Should fail on backslash"
    } catch { }

    $tmpRoot = Join-Path -Path ([System.IO.Path]::GetTempPath()) -ChildPath ("test_root_" + [Guid]::NewGuid().ToString())
    New-Item -ItemType Directory -Path $tmpRoot -Force | Out-Null
    try {
        $staging = Join-Path -Path $tmpRoot -ChildPath "staging"
        New-Item -ItemType Directory -Path (Join-Path -Path $staging -ChildPath "files\docs") -Force | Out-Null
        Set-Content -Path (Join-Path -Path $staging -ChildPath "REPORT.md") -Value "# Report"
        Set-Content -Path (Join-Path -Path $staging -ChildPath "MANIFEST.md") -Value "# Manifest"
        Set-Content -Path (Join-Path -Path $staging -ChildPath "files\docs\test.md") -Value "Test"

        $zipCreated = New-HandoffZip -tId "DEV-TASK-TEST" -stagingPath $staging -repoRootPath $tmpRoot
        $metrics = Test-HandoffZip -zipPath $zipCreated -repoRootPath $tmpRoot

        if ($metrics["backslash_count"] -ne 0 -or $metrics["extraction_test"] -ne "PASS") {
            throw "Verification metrics failed in self-test."
        }
    }
    finally {
        if (Test-Path -Path $tmpRoot) { Remove-Item -Recurse -Force $tmpRoot }
    }

    Write-Host "ALL SELF-TESTS PASSED!"
}

if ($Test) {
    Run-SelfTests
    exit 0
}

if (-not $TaskId -or -not $StagingDir) {
    Write-Host "Usage: .\create_handoff.ps1 -TaskId <TASK-ID> -StagingDir <PATH> [-RepoRoot <PATH>]"
    exit 1
}

$resolvedRepoRoot = if ($RepoRoot) { (Resolve-Path -Path $RepoRoot).Path } else { (Resolve-Path -Path (Join-Path -Path $PSScriptRoot -ChildPath "..")).Path }
$resolvedStaging = (Resolve-Path -Path $StagingDir).Path

Write-Host ("Generating Handoff ZIP for task " + $TaskId + "...")
$createdZip = New-HandoffZip -tId $TaskId -stagingPath $resolvedStaging -repoRootPath $resolvedRepoRoot
Write-Host ("Created ZIP: " + $createdZip)

Write-Host "Verifying Handoff ZIP..."
$res = Test-HandoffZip -zipPath $createdZip -repoRootPath $resolvedRepoRoot
Write-Host "Verification metrics:"
foreach ($k in $res.Keys) {
    Write-Host ("  " + $k + ": " + $res[$k])
}

Write-Host "Handoff ZIP generation & verification completed successfully!"
