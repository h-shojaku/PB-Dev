# Real Git Integration & Fail-Closed Negative Tests for Project Initializer (PowerShell)

$ErrorActionPreference = "Stop"

$scriptDir = $PSScriptRoot
$initScript = Join-Path -Path $scriptDir -ChildPath "initialize_project.ps1"
$handoffDirName = [System.Text.Encoding]::UTF8.GetString([byte[]](0xE5,0x8F,0x97,0xE3,0x81,0x91,0xE6,0xB8,0xA1,0xE3,0x81,0x97))

function New-MockRepo {
    $tempDir = Join-Path -Path ([System.IO.Path]::GetTempPath()) -ChildPath ("test_git_init_" + [Guid]::NewGuid().ToString("N"))

    # 1. Initialize real git repository
    git init $tempDir 2>$null | Out-Null
    git -C $tempDir config user.name "TestUser"
    git -C $tempDir config user.email "test@example.com"
    git -C $tempDir remote add origin "https://github.com/temp/Initial.git"

    # 2. Create mock directories
    New-Item -ItemType Directory -Path (Join-Path -Path $tempDir -ChildPath "tasks\active") -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path -Path $tempDir -ChildPath "tasks\completed") -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path -Path $tempDir -ChildPath $handoffDirName) -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path -Path $tempDir -ChildPath "templates\product") -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path -Path $tempDir -ChildPath "reports\analysis") -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path -Path $tempDir -ChildPath "scripts") -Force | Out-Null

    # 3. Place dummy runtime task files
    Set-Content -Path (Join-Path -Path $tempDir -ChildPath "tasks\active\DEV-TASK-0010.md") -Value "# Dummy Active" -Encoding UTF8
    Set-Content -Path (Join-Path -Path $tempDir -ChildPath "tasks\completed\DEV-TASK-0009.md") -Value "# Dummy Completed" -Encoding UTF8
    Set-Content -Path (Join-Path -Path $tempDir -ChildPath "$handoffDirName\DEV-TASK-0009_PLANNER_HANDOFF.zip") -Value "Dummy ZIP" -Encoding UTF8

    # 4. Copy actual templates and scripts to mock repo
    Copy-Item -Path (Join-Path -Path $scriptDir -ChildPath "..\templates\product\*") -Destination (Join-Path -Path $tempDir -ChildPath "templates\product\") -Force
    Copy-Item -Path $initScript -Destination (Join-Path -Path $tempDir -ChildPath "scripts\") -Force

    return $tempDir
}

Write-Host "=== TEST 1: Real Git NEW_PRODUCT Initialization ==="
$repo1 = New-MockRepo
try {
    $targetInit = Join-Path -Path $repo1 -ChildPath "scripts\initialize_project.ps1"
    $remote1 = "https://github.com/myorg/RealApp.git"
    powershell -ExecutionPolicy Bypass -File $targetInit -Mode NEW_PRODUCT -Name "RealApp" -Prefix "APP" -Remote $remote1

    # Assert actual git origin remote updated
    $actualOrigin = (git -C $repo1 remote get-url origin 2>$null).Trim()
    if ($actualOrigin -ne $remote1) { throw "FAIL: actual git origin ($actualOrigin) does not match requested remote ($remote1)" }

    # Assert runtime state reset
    $activeCount = (Get-ChildItem -Path (Join-Path -Path $repo1 -ChildPath "tasks\active") -File).Count
    $completedCount = (Get-ChildItem -Path (Join-Path -Path $repo1 -ChildPath "tasks\completed") -File).Count
    $handoffCount = (Get-ChildItem -Path (Join-Path -Path $repo1 -ChildPath $handoffDirName) -File).Count
    $productDocs = Get-ChildItem -Path (Join-Path -Path $repo1 -ChildPath "docs\product") -File

    if ($activeCount -ne 0) { throw "FAIL: tasks/active is not empty (Count: $activeCount)" }
    if ($completedCount -ne 0) { throw "FAIL: tasks/completed is not empty (Count: $completedCount)" }
    if ($handoffCount -ne 0) { throw "FAIL: delivery directory is not empty (Count: $handoffCount)" }
    if ($productDocs.Count -ne 6) { throw "FAIL: docs/product count is not 6 (Count: $($productDocs.Count))" }

    $profileTxt = Get-Content -Path (Join-Path -Path $repo1 -ChildPath "PROJECT_PROFILE.md") -Raw
    if ($profileTxt -notlike "*RealApp*") { throw "FAIL: PROJECT_PROFILE does not contain RealApp" }
    if ($profileTxt -notlike "*NEW_PRODUCT*") { throw "FAIL: PROJECT_PROFILE does not contain NEW_PRODUCT" }
    if ($profileTxt -notlike "*APP*") { throw "FAIL: PROJECT_PROFILE does not contain APP" }

    Write-Host "PASS: TEST 1 (NEW_PRODUCT)"
} finally {
    Remove-Item -Path $repo1 -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "=== TEST 2: Real Git EXISTING_PRODUCT Initialization ==="
$repo2 = New-MockRepo
try {
    $srcDir = Join-Path -Path $repo2 -ChildPath "src"
    New-Item -ItemType Directory -Path $srcDir -Force | Out-Null
    $mainPy = Join-Path -Path $srcDir -ChildPath "main.py"
    Set-Content -Path $mainPy -Value "print('Hello Legacy')" -Encoding UTF8

    $targetInit = Join-Path -Path $repo2 -ChildPath "scripts\initialize_project.ps1"
    $remote2 = "https://github.com/myorg/LegacyApp.git"
    powershell -ExecutionPolicy Bypass -File $targetInit -Mode EXISTING_PRODUCT -Name "LegacyApp" -Prefix "LEG" -Remote $remote2

    if (-not (Test-Path -Path $mainPy)) { throw "FAIL: Existing source file main.py was deleted!" }
    $mainContent = Get-Content -Path $mainPy -Raw
    if ($mainContent -notlike "*Hello Legacy*") { throw "FAIL: Existing source content was modified!" }

    $actualOrigin2 = (git -C $repo2 remote get-url origin 2>$null).Trim()
    if ($actualOrigin2 -ne $remote2) { throw "FAIL: actual git origin ($actualOrigin2) does not match requested remote ($remote2)" }

    $activeCount = (Get-ChildItem -Path (Join-Path -Path $repo2 -ChildPath "tasks\active") -File).Count
    $completedCount = (Get-ChildItem -Path (Join-Path -Path $repo2 -ChildPath "tasks\completed") -File).Count
    if ($activeCount -ne 0 -or $completedCount -ne 0) { throw "FAIL: Runtime task state was not reset in EXISTING_PRODUCT mode" }

    $analysisTpl = Join-Path -Path $repo2 -ChildPath "reports\analysis\EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md"
    if (-not (Test-Path -Path $analysisTpl)) { throw "FAIL: EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md was not placed" }

    Write-Host "PASS: TEST 2 (EXISTING_PRODUCT)"
} finally {
    Remove-Item -Path $repo2 -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "=== TEST 3: Negative Tests (Fail-Closed Validations) ==="
$repo3 = New-MockRepo
try {
    $targetInit = Join-Path -Path $repo3 -ChildPath "scripts\initialize_project.ps1"

    # 1. Non-git directory -> FAIL
    $nonGitDir = Join-Path -Path ([System.IO.Path]::GetTempPath()) -ChildPath ("non_git_" + [Guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path (Join-Path -Path $nonGitDir -ChildPath "templates\product") -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path -Path $nonGitDir -ChildPath "scripts") -Force | Out-Null
    Copy-Item -Path $initScript -Destination (Join-Path -Path $nonGitDir -ChildPath "scripts\") -Force
    $failed = $false
    try {
        powershell -ExecutionPolicy Bypass -File (Join-Path -Path $nonGitDir -ChildPath "scripts\initialize_project.ps1") -Mode NEW_PRODUCT -Name "App" -Prefix "APP" -Remote "https://github.com/myorg/App.git" 2>$null
        if ($LASTEXITCODE -ne 0) { $failed = $true }
    } catch { $failed = $true }
    Remove-Item -Path $nonGitDir -Recurse -Force -ErrorAction SilentlyContinue
    if (-not $failed) { throw "FAIL: Non-git directory did not fail" }

    # 2. Omitted Remote -> FAIL
    $failed = $false
    try {
        powershell -ExecutionPolicy Bypass -File $targetInit -Mode NEW_PRODUCT -Name "App" -Prefix "APP" 2>$null
        if ($LASTEXITCODE -ne 0) { $failed = $true }
    } catch { $failed = $true }
    if (-not $failed) { throw "FAIL: Missing remote did not fail" }

    # 3. Placeholder Remote -> FAIL
    $failed = $false
    try {
        powershell -ExecutionPolicy Bypass -File $targetInit -Mode NEW_PRODUCT -Name "App" -Prefix "APP" -Remote "https://github.com/example/App.git" 2>$null
        if ($LASTEXITCODE -ne 0) { $failed = $true }
    } catch { $failed = $true }
    if (-not $failed) { throw "FAIL: Placeholder remote did not fail" }

    # 4. Invalid Prefix -> FAIL
    $failed = $false
    try {
        powershell -ExecutionPolicy Bypass -File $targetInit -Mode NEW_PRODUCT -Name "App" -Prefix "app-invalid!" -Remote "https://github.com/myorg/App.git" 2>$null
        if ($LASTEXITCODE -ne 0) { $failed = $true }
    } catch { $failed = $true }
    if (-not $failed) { throw "FAIL: Invalid prefix did not fail" }

    # 5. Missing Product SSOT Template -> FAIL
    $missingTplRepo = New-MockRepo
    Remove-Item -Path (Join-Path -Path $missingTplRepo -ChildPath "templates\product\05_OPERATION_RULES.md") -Force -ErrorAction SilentlyContinue
    $failed = $false
    try {
        powershell -ExecutionPolicy Bypass -File (Join-Path -Path $missingTplRepo -ChildPath "scripts\initialize_project.ps1") -Mode NEW_PRODUCT -Name "App" -Prefix "APP" -Remote "https://github.com/myorg/App.git" 2>$null
        if ($LASTEXITCODE -ne 0) { $failed = $true }
    } catch { $failed = $true }
    Remove-Item -Path $missingTplRepo -Recurse -Force -ErrorAction SilentlyContinue
    if (-not $failed) { throw "FAIL: Missing Product SSOT template did not fail" }

    # 6. Existing Product SSOT Protection -> FAIL (unless -Force)
    $docsP = Join-Path -Path $repo3 -ChildPath "docs\product"
    New-Item -ItemType Directory -Path $docsP -Force | Out-Null
    Set-Content -Path (Join-Path -Path $docsP -ChildPath "00_PRODUCT_OVERVIEW.md") -Value "Important Custom Spec" -Encoding UTF8
    $failed = $false
    try {
        powershell -ExecutionPolicy Bypass -File $targetInit -Mode NEW_PRODUCT -Name "App" -Prefix "APP" -Remote "https://github.com/myorg/App.git" 2>$null
        if ($LASTEXITCODE -ne 0) { $failed = $true }
    } catch { $failed = $true }
    if (-not $failed) { throw "FAIL: Existing product SSOT without -Force did not fail" }

    # With -Force -> PASS
    powershell -ExecutionPolicy Bypass -File $targetInit -Mode NEW_PRODUCT -Name "App" -Prefix "APP" -Remote "https://github.com/myorg/App.git" -Force
    Write-Host "PASS: TEST 3 (Negative Tests)"
} finally {
    Remove-Item -Path $repo3 -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "=== TEST 4: Dry Run Test ==="
$repo4 = New-MockRepo
try {
    $targetInit = Join-Path -Path $repo4 -ChildPath "scripts\initialize_project.ps1"
    powershell -ExecutionPolicy Bypass -File $targetInit -Mode NEW_PRODUCT -Name "DryApp" -Prefix "DRY" -Remote "https://github.com/myorg/DryApp.git" -DryRun

    $dummyActive = Join-Path -Path $repo4 -ChildPath "tasks\active\DEV-TASK-0010.md"
    if (-not (Test-Path -Path $dummyActive)) { throw "FAIL: Dry run modified files!" }

    Write-Host "PASS: TEST 4 (Dry Run)"
} finally {
    Remove-Item -Path $repo4 -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "ALL PROJECT INITIALIZER INTEGRATION TESTS PASSED!"
