# Real Git Integration & Fail-Closed Negative Tests for Project Initializer (PowerShell Test Runner)

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

Write-Host "=== TEST 1: test_real_git_new_product_initialization ==="
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

    Write-Host "PASS: test_real_git_new_product_initialization"
} finally {
    Remove-Item -Path $repo1 -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "=== TEST 2: test_real_git_existing_product_initialization ==="
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

    Write-Host "PASS: test_real_git_existing_product_initialization"
} finally {
    Remove-Item -Path $repo2 -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "=== TEST 3: test_fail_non_git_repository ==="
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
Write-Host "PASS: test_fail_non_git_repository"

Write-Host "=== TEST 4: test_fail_missing_remote ==="
$repo3 = New-MockRepo
try {
    $targetInit = Join-Path -Path $repo3 -ChildPath "scripts\initialize_project.ps1"
    $failed = $false
    try {
        powershell -ExecutionPolicy Bypass -File $targetInit -Mode NEW_PRODUCT -Name "App" -Prefix "APP" 2>$null
        if ($LASTEXITCODE -ne 0) { $failed = $true }
    } catch { $failed = $true }
    if (-not $failed) { throw "FAIL: Missing remote did not fail" }
    Write-Host "PASS: test_fail_missing_remote"
} finally {
    Remove-Item -Path $repo3 -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "=== TEST 5: test_fail_placeholder_remote ==="
$repo4 = New-MockRepo
try {
    $targetInit = Join-Path -Path $repo4 -ChildPath "scripts\initialize_project.ps1"
    $failed = $false
    try {
        powershell -ExecutionPolicy Bypass -File $targetInit -Mode NEW_PRODUCT -Name "App" -Prefix "APP" -Remote "https://github.com/example/App.git" 2>$null
        if ($LASTEXITCODE -ne 0) { $failed = $true }
    } catch { $failed = $true }
    if (-not $failed) { throw "FAIL: Placeholder remote did not fail" }
    Write-Host "PASS: test_fail_placeholder_remote"
} finally {
    Remove-Item -Path $repo4 -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "=== TEST 6: test_fail_invalid_prefix ==="
$repo5 = New-MockRepo
try {
    $targetInit = Join-Path -Path $repo5 -ChildPath "scripts\initialize_project.ps1"
    $failed = $false
    try {
        powershell -ExecutionPolicy Bypass -File $targetInit -Mode NEW_PRODUCT -Name "App" -Prefix "app-invalid!" -Remote "https://github.com/myorg/App.git" 2>$null
        if ($LASTEXITCODE -ne 0) { $failed = $true }
    } catch { $failed = $true }
    if (-not $failed) { throw "FAIL: Invalid prefix did not fail" }
    Write-Host "PASS: test_fail_invalid_prefix"
} finally {
    Remove-Item -Path $repo5 -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "=== TEST 7: test_fail_missing_product_ssot_template ==="
$missingTplRepo = New-MockRepo
try {
    Remove-Item -Path (Join-Path -Path $missingTplRepo -ChildPath "templates\product\05_OPERATION_RULES.md") -Force -ErrorAction SilentlyContinue
    $failed = $false
    try {
        powershell -ExecutionPolicy Bypass -File (Join-Path -Path $missingTplRepo -ChildPath "scripts\initialize_project.ps1") -Mode NEW_PRODUCT -Name "App" -Prefix "APP" -Remote "https://github.com/myorg/App.git" 2>$null
        if ($LASTEXITCODE -ne 0) { $failed = $true }
    } catch { $failed = $true }
    if (-not $failed) { throw "FAIL: Missing Product SSOT template did not fail" }
    Write-Host "PASS: test_fail_missing_product_ssot_template"
} finally {
    Remove-Item -Path $missingTplRepo -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "=== TEST 8: test_fail_missing_analysis_template ==="
$missingAnalysisRepo = New-MockRepo
try {
    Remove-Item -Path (Join-Path -Path $missingAnalysisRepo -ChildPath "templates\product\EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md") -Force -ErrorAction SilentlyContinue
    $failed = $false
    try {
        powershell -ExecutionPolicy Bypass -File (Join-Path -Path $missingAnalysisRepo -ChildPath "scripts\initialize_project.ps1") -Mode EXISTING_PRODUCT -Name "App" -Prefix "APP" -Remote "https://github.com/myorg/App.git" 2>$null
        if ($LASTEXITCODE -ne 0) { $failed = $true }
    } catch { $failed = $true }
    if (-not $failed) { throw "FAIL: Missing EXISTING_PRODUCT Analysis Template did not fail" }
    Write-Host "PASS: test_fail_missing_analysis_template"
} finally {
    Remove-Item -Path $missingAnalysisRepo -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "=== TEST 9: test_fail_existing_product_ssot_protection ==="
$repo6 = New-MockRepo
try {
    $targetInit = Join-Path -Path $repo6 -ChildPath "scripts\initialize_project.ps1"
    $docsP = Join-Path -Path $repo6 -ChildPath "docs\product"
    New-Item -ItemType Directory -Path $docsP -Force | Out-Null
    Set-Content -Path (Join-Path -Path $docsP -ChildPath "00_PRODUCT_OVERVIEW.md") -Value "Important Custom Spec" -Encoding UTF8
    $failed = $false
    try {
        powershell -ExecutionPolicy Bypass -File $targetInit -Mode NEW_PRODUCT -Name "App" -Prefix "APP" -Remote "https://github.com/myorg/App.git" 2>$null
        if ($LASTEXITCODE -ne 0) { $failed = $true }
    } catch { $failed = $true }
    if (-not $failed) { throw "FAIL: Existing product SSOT protection did not fail" }
    Write-Host "PASS: test_fail_existing_product_ssot_protection"
} finally {
    Remove-Item -Path $repo6 -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "=== TEST 10: test_recursive_runtime_reset ==="
$repo7 = New-MockRepo
try {
    $targetInit = Join-Path -Path $repo7 -ChildPath "scripts\initialize_project.ps1"
    $nestedActive = Join-Path -Path $repo7 -ChildPath "tasks\active\nested\deep"
    $nestedCompleted = Join-Path -Path $repo7 -ChildPath "tasks\completed\sub"
    $nestedHandoff = Join-Path -Path $repo7 -ChildPath "$handoffDirName\sub_dir"
    New-Item -ItemType Directory -Path $nestedActive -Force | Out-Null
    New-Item -ItemType Directory -Path $nestedCompleted -Force | Out-Null
    New-Item -ItemType Directory -Path $nestedHandoff -Force | Out-Null
    Set-Content -Path (Join-Path -Path $nestedActive -ChildPath "x.md") -Value "active" -Encoding UTF8
    Set-Content -Path (Join-Path -Path $nestedCompleted -ChildPath "y.md") -Value "completed" -Encoding UTF8
    Set-Content -Path (Join-Path -Path $nestedHandoff -ChildPath "z.zip") -Value "zip" -Encoding UTF8

    powershell -ExecutionPolicy Bypass -File $targetInit -Mode NEW_PRODUCT -Name "RecApp" -Prefix "REC" -Remote "https://github.com/myorg/RecApp.git"

    $activeItems = (Get-ChildItem -Path (Join-Path -Path $repo7 -ChildPath "tasks\active") -Recurse).Count
    $completedItems = (Get-ChildItem -Path (Join-Path -Path $repo7 -ChildPath "tasks\completed") -Recurse).Count
    $handoffItems = (Get-ChildItem -Path (Join-Path -Path $repo7 -ChildPath $handoffDirName) -Recurse).Count

    if ($activeItems -ne 0 -or $completedItems -ne 0 -or $handoffItems -ne 0) {
        throw "FAIL: Recursive runtime reset failed! active: $activeItems, completed: $completedItems, handoff: $handoffItems"
    }
    Write-Host "PASS: test_recursive_runtime_reset"
} finally {
    Remove-Item -Path $repo7 -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "=== TEST 11: test_dry_run_no_mutation ==="
$repo8 = New-MockRepo
try {
    $targetInit = Join-Path -Path $repo8 -ChildPath "scripts\initialize_project.ps1"
    powershell -ExecutionPolicy Bypass -File $targetInit -Mode NEW_PRODUCT -Name "DryApp" -Prefix "DRY" -Remote "https://github.com/myorg/DryApp.git" -DryRun

    $dummyActive = Join-Path -Path $repo8 -ChildPath "tasks\active\DEV-TASK-0010.md"
    if (-not (Test-Path -Path $dummyActive)) { throw "FAIL: Dry run modified files!" }

    Write-Host "PASS: test_dry_run_no_mutation"
} finally {
    Remove-Item -Path $repo8 -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "ALL 11 PROJECT INITIALIZER INTEGRATION TESTS PASSED!"
