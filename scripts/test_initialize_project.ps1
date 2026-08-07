# Comprehensive Integration & Negative Tests for Project Initializer (PowerShell)

$ErrorActionPreference = "Stop"

$scriptDir = $PSScriptRoot
$initScript = Join-Path -Path $scriptDir -ChildPath "initialize_project.ps1"
$handoffDirName = [System.Text.Encoding]::UTF8.GetString([byte[]](0xE5,0x8F,0x97,0xE3,0x81,0x91,0xE6,0xB8,0xA1,0xE3,0x81,0x97))

function New-MockRepo {
    $tempDir = Join-Path -Path ([System.IO.Path]::GetTempPath()) -ChildPath ("test_init_" + [Guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path (Join-Path -Path $tempDir -ChildPath "tasks\active") -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path -Path $tempDir -ChildPath "tasks\completed") -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path -Path $tempDir -ChildPath $handoffDirName) -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path -Path $tempDir -ChildPath "templates\product") -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path -Path $tempDir -ChildPath "reports\analysis") -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path -Path $tempDir -ChildPath "scripts") -Force | Out-Null

    Set-Content -Path (Join-Path -Path $tempDir -ChildPath "tasks\active\DEV-TASK-0009.md") -Value "# Dummy Active" -Encoding UTF8
    Set-Content -Path (Join-Path -Path $tempDir -ChildPath "tasks\completed\DEV-TASK-0008.md") -Value "# Dummy Completed" -Encoding UTF8
    Set-Content -Path (Join-Path -Path $tempDir -ChildPath "$handoffDirName\DEV-TASK-0008_PLANNER_HANDOFF.zip") -Value "Dummy ZIP" -Encoding UTF8

    Copy-Item -Path (Join-Path -Path $scriptDir -ChildPath "..\templates\product\*") -Destination (Join-Path -Path $tempDir -ChildPath "templates\product\") -Force
    Copy-Item -Path $initScript -Destination (Join-Path -Path $tempDir -ChildPath "scripts\") -Force

    return $tempDir
}

Write-Host "=== TEST 1: NEW_PRODUCT Initialization ==="
$repo1 = New-MockRepo
try {
    $targetInit = Join-Path -Path $repo1 -ChildPath "scripts\initialize_project.ps1"
    powershell -ExecutionPolicy Bypass -File $targetInit -Mode NEW_PRODUCT -Name "NewApp" -Prefix "APP" -Remote "https://github.com/myorg/NewApp.git" -AllowRemoteMismatch

    $activeCount = (Get-ChildItem -Path (Join-Path -Path $repo1 -ChildPath "tasks\active") -File).Count
    $completedCount = (Get-ChildItem -Path (Join-Path -Path $repo1 -ChildPath "tasks\completed") -File).Count
    $handoffCount = (Get-ChildItem -Path (Join-Path -Path $repo1 -ChildPath $handoffDirName) -File).Count
    $productDocs = Get-ChildItem -Path (Join-Path -Path $repo1 -ChildPath "docs\product") -File

    if ($activeCount -ne 0) { throw "FAIL: tasks/active is not empty (Count: $activeCount)" }
    if ($completedCount -ne 0) { throw "FAIL: tasks/completed is not empty (Count: $completedCount)" }
    if ($handoffCount -ne 0) { throw "FAIL: delivery directory is not empty (Count: $handoffCount)" }
    if ($productDocs.Count -ne 6) { throw "FAIL: docs/product count is not 6 (Count: $($productDocs.Count))" }

    $profileTxt = Get-Content -Path (Join-Path -Path $repo1 -ChildPath "PROJECT_PROFILE.md") -Raw
    if ($profileTxt -notlike "*NewApp*") { throw "FAIL: PROJECT_PROFILE does not contain NewApp" }
    if ($profileTxt -notlike "*NEW_PRODUCT*") { throw "FAIL: PROJECT_PROFILE does not contain NEW_PRODUCT" }
    if ($profileTxt -notlike "*APP*") { throw "FAIL: PROJECT_PROFILE does not contain APP" }

    Write-Host "PASS: TEST 1 (NEW_PRODUCT)"
} finally {
    Remove-Item -Path $repo1 -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "=== TEST 2: EXISTING_PRODUCT Initialization ==="
$repo2 = New-MockRepo
try {
    $srcDir = Join-Path -Path $repo2 -ChildPath "src"
    New-Item -ItemType Directory -Path $srcDir -Force | Out-Null
    $mainPy = Join-Path -Path $srcDir -ChildPath "main.py"
    Set-Content -Path $mainPy -Value "print('Hello Legacy')" -Encoding UTF8

    $targetInit = Join-Path -Path $repo2 -ChildPath "scripts\initialize_project.ps1"
    powershell -ExecutionPolicy Bypass -File $targetInit -Mode EXISTING_PRODUCT -Name "LegacyApp" -Prefix "LEG" -Remote "https://github.com/myorg/LegacyApp.git" -AllowRemoteMismatch

    if (-not (Test-Path -Path $mainPy)) { throw "FAIL: Existing source file main.py was deleted!" }
    $mainContent = Get-Content -Path $mainPy -Raw
    if ($mainContent -notlike "*Hello Legacy*") { throw "FAIL: Existing source content was modified!" }

    $activeCount = (Get-ChildItem -Path (Join-Path -Path $repo2 -ChildPath "tasks\active") -File).Count
    $completedCount = (Get-ChildItem -Path (Join-Path -Path $repo2 -ChildPath "tasks\completed") -File).Count
    if ($activeCount -ne 0 -or $completedCount -ne 0) { throw "FAIL: Runtime task state was not reset in EXISTING_PRODUCT mode" }

    $analysisTpl = Join-Path -Path $repo2 -ChildPath "reports\analysis\EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md"
    if (-not (Test-Path -Path $analysisTpl)) { throw "FAIL: EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md was not placed" }

    Write-Host "PASS: TEST 2 (EXISTING_PRODUCT)"
} finally {
    Remove-Item -Path $repo2 -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "=== TEST 3: Negative Tests (Validations) ==="
$repo3 = New-MockRepo
try {
    $targetInit = Join-Path -Path $repo3 -ChildPath "scripts\initialize_project.ps1"

    # 1. Omitted Remote -> Fail
    $failed = $false
    try {
        powershell -ExecutionPolicy Bypass -File $targetInit -Mode NEW_PRODUCT -Name "App" -Prefix "APP" -AllowRemoteMismatch 2>$null
        if ($LASTEXITCODE -ne 0) { $failed = $true }
    } catch { $failed = $true }
    if (-not $failed) { throw "FAIL: Missing remote did not fail" }

    # 2. Placeholder Remote -> Fail
    $failed = $false
    try {
        powershell -ExecutionPolicy Bypass -File $targetInit -Mode NEW_PRODUCT -Name "App" -Prefix "APP" -Remote "https://github.com/example/App.git" -AllowRemoteMismatch 2>$null
        if ($LASTEXITCODE -ne 0) { $failed = $true }
    } catch { $failed = $true }
    if (-not $failed) { throw "FAIL: Placeholder remote did not fail" }

    # 3. Invalid Prefix -> Fail
    $failed = $false
    try {
        powershell -ExecutionPolicy Bypass -File $targetInit -Mode NEW_PRODUCT -Name "App" -Prefix "app-invalid!" -Remote "https://github.com/myorg/App.git" -AllowRemoteMismatch 2>$null
        if ($LASTEXITCODE -ne 0) { $failed = $true }
    } catch { $failed = $true }
    if (-not $failed) { throw "FAIL: Invalid prefix did not fail" }

    Write-Host "PASS: TEST 3 (Negative Tests)"
} finally {
    Remove-Item -Path $repo3 -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "=== TEST 4: Dry Run Test ==="
$repo4 = New-MockRepo
try {
    $targetInit = Join-Path -Path $repo4 -ChildPath "scripts\initialize_project.ps1"
    powershell -ExecutionPolicy Bypass -File $targetInit -Mode NEW_PRODUCT -Name "DryApp" -Prefix "DRY" -Remote "https://github.com/myorg/DryApp.git" -AllowRemoteMismatch -DryRun

    $dummyActive = Join-Path -Path $repo4 -ChildPath "tasks\active\DEV-TASK-0009.md"
    if (-not (Test-Path -Path $dummyActive)) { throw "FAIL: Dry run modified files!" }

    Write-Host "PASS: TEST 4 (Dry Run)"
} finally {
    Remove-Item -Path $repo4 -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "ALL PROJECT INITIALIZER INTEGRATION TESTS PASSED!"
