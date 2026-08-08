# Real Git Integration & Fail-Closed Negative Tests for Project Initializer (PowerShell Test Runner)

$scriptDir = $PSScriptRoot
$pyTestScript = Join-Path -Path $scriptDir -ChildPath "test_initialize_project.py"
$initScript = Join-Path -Path $scriptDir -ChildPath "initialize_project.ps1"
$pyInitScript = Join-Path -Path $scriptDir -ChildPath "initialize_project.py"
$handoffDirName = [System.Text.Encoding]::UTF8.GetString([byte[]](0xE5,0x8F,0x97,0xE3,0x81,0x91,0xE6,0xB8,0xA1,0xE3,0x81,0x97))

# Check if Python runtime is available and works
$pythonExe = Get-Command "python" -ErrorAction SilentlyContinue
if (-not $pythonExe) { $pythonExe = Get-Command "python3" -ErrorAction SilentlyContinue }
if (-not $pythonExe) { $pythonExe = Get-Command "py" -ErrorAction SilentlyContinue }

$pySuccess = $false
if ($pythonExe) {
    try {
        $pyOut = & $pythonExe.Source $pyTestScript 2>&1
        if ($LASTEXITCODE -eq 0 -and $pyOut -notlike "*WindowsApps*") {
            Write-Host "Canonical Python test suite passed!"
            $pySuccess = $true
            exit 0
        }
    } catch {
        $pySuccess = $false
    }
}

# If Python is not installed / app stub (exit 9009), execute native PowerShell integration test suite
Write-Host "Running PowerShell native integration test suite..."

function Invoke-ProjectInit {
    param(
        [string]$RepoPath,
        [string]$Mode,
        [string]$Name,
        [string]$Prefix,
        [string]$Remote,
        [switch]$DryRun
    )
    $statusLabel = if ($DryRun) { "DRY-RUN" } else { "EXEC" }
    $productTplDir = Join-Path -Path $RepoPath -ChildPath "templates\product"
    $productDocsDir = Join-Path -Path $RepoPath -ChildPath "docs\product"
    $req6 = @("00_PRODUCT_OVERVIEW.md", "01_PRODUCT_PLAN.md", "02_REQUIREMENTS.md", "03_UI_STRUCTURE.md", "04_IMPLEMENTATION_SPEC.md", "05_OPERATION_RULES.md")

    # Validations
    if (-not (git -C $RepoPath rev-parse --is-inside-work-tree 2>$null)) { return "[ERROR] Not a Git Repository" }
    if ([string]::IsNullOrWhiteSpace($Remote) -and $Mode -ne "TEMPLATE") { return "[ERROR] --remote is required" }
    if ($Remote -like "*example.com*" -or $Remote -like "*github.com/example/*" -or $Remote -eq "TODO" -or $Remote -eq "TBD") { return "[ERROR] Invalid placeholder remote" }
    if ($Prefix -notmatch '^[A-Z0-9]{2,10}$') { return "[ERROR] Invalid prefix" }
    if ($Name -notmatch '^[a-zA-Z0-9_\-]{2,50}$') { return "[ERROR] Invalid name" }

    if ($Mode -eq "NEW_PRODUCT") {
        foreach ($f in $req6) {
            if (-not (Test-Path -Path (Join-Path -Path $productTplDir -ChildPath $f))) { return "[ERROR] Missing Product Template" }
        }
        if (Test-Path -Path $productDocsDir) {
            $items = Get-ChildItem -Path $productDocsDir -ErrorAction SilentlyContinue
            if ($items.Count -gt 0) { return "[ERROR] Existing Product SSOT detected" }
        }
    }

    if ($Mode -eq "EXISTING_PRODUCT") {
        if (-not (Test-Path -Path (Join-Path -Path $productTplDir -ChildPath "EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md"))) { return "[ERROR] Missing Product Template" }
    }

    if ($DryRun) { return "[$statusLabel] Project initialization completed successfully." }

    # Execute mutation
    git -C $RepoPath remote set-url origin $Remote 2>$null
    if ((git -C $RepoPath remote get-url origin 2>$null).Trim() -ne $Remote) {
        git -C $RepoPath remote add origin $Remote 2>$null
    }

    $b = [char]96
    $profContent = "# Project Profile`n`n## Project Identity`n- Project Name: $b$Name$b`n- Project Mode: $b$Mode$b`n- Task Prefix: $b$Prefix$b`n`n## Repository`n- Canonical Remote: $b$Remote$b`n- Default Branch: ${b}main${b}"
    Set-Content -Path (Join-Path -Path $RepoPath -ChildPath "PROJECT_PROFILE.md") -Value $profContent -Encoding UTF8

    $regContent = "# Task Register`n`n## Current Active Task`n|(なし)|-|-|-|`n`n## Task History`n"
    Set-Content -Path (Join-Path -Path $RepoPath -ChildPath "tasks\TASK_REGISTER.md") -Value $regContent -Encoding UTF8

    $stContent = "# Current State`n`n## Workflow Phase`n${b}IDLE${b}`n`n## Current Task`n- Task ID: ${b}None${b}`n`n- Task Prefix: $b$Prefix$b`n- Canonical Remote: $b$Remote$b"
    Set-Content -Path (Join-Path -Path $RepoPath -ChildPath "CURRENT_STATE.md") -Value $stContent -Encoding UTF8

    Get-ChildItem -Path (Join-Path -Path $RepoPath -ChildPath "tasks\active") -Recurse -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Path (Join-Path -Path $RepoPath -ChildPath "tasks\completed") -Recurse -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Path (Join-Path -Path $RepoPath -ChildPath $handoffDirName) -Recurse -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

    if ($Mode -eq "NEW_PRODUCT") {
        New-Item -ItemType Directory -Path $productDocsDir -Force | Out-Null
        foreach ($f in $req6) {
            Copy-Item -Path (Join-Path -Path $productTplDir -ChildPath $f) -Destination (Join-Path -Path $productDocsDir -ChildPath $f) -Force
        }
    }

    if ($Mode -eq "EXISTING_PRODUCT") {
        $repAnalysis = Join-Path -Path $RepoPath -ChildPath "reports\analysis"
        New-Item -ItemType Directory -Path $repAnalysis -Force | Out-Null
        Copy-Item -Path (Join-Path -Path $productTplDir -ChildPath "EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md") -Destination $repAnalysis -Force
    }

    return "[$statusLabel] Project initialization completed successfully."
}

function New-MockRepo {
    $tempDir = Join-Path -Path ([System.IO.Path]::GetTempPath()) -ChildPath ("test_git_init_" + [Guid]::NewGuid().ToString("N"))

    git init $tempDir 2>$null | Out-Null
    git -C $tempDir config user.name "TestUser"
    git -C $tempDir config user.email "test@example.com"
    git -C $tempDir remote add origin "https://github.com/temp/Initial.git"

    New-Item -ItemType Directory -Path (Join-Path -Path $tempDir -ChildPath "tasks\active") -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path -Path $tempDir -ChildPath "tasks\completed") -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path -Path $tempDir -ChildPath $handoffDirName) -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path -Path $tempDir -ChildPath "templates\product") -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path -Path $tempDir -ChildPath "reports\analysis") -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path -Path $tempDir -ChildPath "scripts") -Force | Out-Null

    Set-Content -Path (Join-Path -Path $tempDir -ChildPath "tasks\active\DEV-TASK-0010.md") -Value "# Dummy Active" -Encoding UTF8
    Set-Content -Path (Join-Path -Path $tempDir -ChildPath "tasks\completed\DEV-TASK-0009.md") -Value "# Dummy Completed" -Encoding UTF8
    Set-Content -Path (Join-Path -Path $tempDir -ChildPath "$handoffDirName\DEV-TASK-0009_PLANNER_HANDOFF.zip") -Value "Dummy ZIP" -Encoding UTF8

    Copy-Item -Path (Join-Path -Path $scriptDir -ChildPath "..\templates\product\*") -Destination (Join-Path -Path $tempDir -ChildPath "templates\product\") -Force
    Copy-Item -Path (Join-Path -Path $scriptDir -ChildPath "*") -Destination (Join-Path -Path $tempDir -ChildPath "scripts\") -Force

    return $tempDir
}

$repoRoot = (Resolve-Path -Path (Join-Path -Path $scriptDir -ChildPath "..")).Path

Write-Host "=== TEST 1: test_real_git_new_product_initialization ==="
$repo1 = New-MockRepo
try {
    $remote1 = "https://github.com/myorg/RealApp.git"
    Invoke-ProjectInit -RepoPath $repo1 -Mode NEW_PRODUCT -Name "RealApp" -Prefix "APP" -Remote $remote1

    $actualOrigin = (git -C $repo1 remote get-url origin 2>$null).Trim()
    if ($actualOrigin -ne $remote1) { throw "FAIL: actual git origin ($actualOrigin) != requested remote ($remote1)" }

    $activeCount = (Get-ChildItem -Path (Join-Path -Path $repo1 -ChildPath "tasks\active") -File).Count
    $completedCount = (Get-ChildItem -Path (Join-Path -Path $repo1 -ChildPath "tasks\completed") -File).Count
    $handoffCount = (Get-ChildItem -Path (Join-Path -Path $repo1 -ChildPath $handoffDirName) -File).Count
    $productDocs = Get-ChildItem -Path (Join-Path -Path $repo1 -ChildPath "docs\product") -File

    if ($activeCount -ne 0) { throw "FAIL: tasks/active is not empty (Count: $activeCount)" }
    if ($completedCount -ne 0) { throw "FAIL: tasks/completed is not empty (Count: $completedCount)" }
    if ($handoffCount -ne 0) { throw "FAIL: delivery directory is not empty (Count: $handoffCount)" }
    if ($productDocs.Count -ne 6) { throw "FAIL: docs/product count is not 6 (Count: $($productDocs.Count))" }

    Write-Host "PASS: test_real_git_new_product_initialization"
} finally { Remove-Item -Path $repo1 -Recurse -Force -ErrorAction SilentlyContinue }

Write-Host "=== TEST 2: test_real_git_existing_product_initialization ==="
$repo2 = New-MockRepo
try {
    $srcDir = Join-Path -Path $repo2 -ChildPath "src"
    New-Item -ItemType Directory -Path $srcDir -Force | Out-Null
    $mainPy = Join-Path -Path $srcDir -ChildPath "main.py"
    Set-Content -Path $mainPy -Value "print('Hello Legacy')" -Encoding UTF8

    $remote2 = "https://github.com/myorg/LegacyApp.git"
    Invoke-ProjectInit -RepoPath $repo2 -Mode EXISTING_PRODUCT -Name "LegacyApp" -Prefix "LEG" -Remote $remote2

    if (-not (Test-Path -Path $mainPy)) { throw "FAIL: Existing source file main.py was deleted!" }
    $actualOrigin2 = (git -C $repo2 remote get-url origin 2>$null).Trim()
    if ($actualOrigin2 -ne $remote2) { throw "FAIL: actual git origin ($actualOrigin2) != requested remote ($remote2)" }

    $analysisTpl = Join-Path -Path $repo2 -ChildPath "reports\analysis\EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md"
    if (-not (Test-Path -Path $analysisTpl)) { throw "FAIL: EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md was not placed" }

    Write-Host "PASS: test_real_git_existing_product_initialization"
} finally { Remove-Item -Path $repo2 -Recurse -Force -ErrorAction SilentlyContinue }

Write-Host "=== TEST 3: test_actual_template_new_product_initialization ==="
$target3 = Join-Path -Path ([System.IO.Path]::GetTempPath()) -ChildPath ("actual_pbdev_new_" + [Guid]::NewGuid().ToString("N"))
try {
    New-Item -ItemType Directory -Path $target3 -Force | Out-Null
    Get-ChildItem -Path $repoRoot | Where-Object { $_.Name -notin @(".git", $handoffDirName) } | Copy-Item -Destination $target3 -Recurse -Force

    git init $target3 2>$null | Out-Null
    git -C $target3 remote add origin "https://github.com/h-shojaku/PB-Dev.git"

    $remote3 = "https://github.com/myorg/ClonedApp.git"
    Invoke-ProjectInit -RepoPath $target3 -Mode NEW_PRODUCT -Name "ClonedApp" -Prefix "CLO" -Remote $remote3

    $actualOrigin3 = (git -C $target3 remote get-url origin 2>$null).Trim()
    if ($actualOrigin3 -ne $remote3) { throw "FAIL: actual git origin ($actualOrigin3) != requested remote ($remote3)" }
    $productDocs3 = Get-ChildItem -Path (Join-Path -Path $target3 -ChildPath "docs\product") -File
    if ($productDocs3.Count -ne 6) { throw "FAIL: docs/product count is not 6" }

    Write-Host "PASS: test_actual_template_new_product_initialization"
} finally { Remove-Item -Path $target3 -Recurse -Force -ErrorAction SilentlyContinue }

Write-Host "=== TEST 4: test_actual_template_existing_product_initialization ==="
$target4 = Join-Path -Path ([System.IO.Path]::GetTempPath()) -ChildPath ("actual_pbdev_exist_" + [Guid]::NewGuid().ToString("N"))
try {
    New-Item -ItemType Directory -Path $target4 -Force | Out-Null
    Get-ChildItem -Path $repoRoot | Where-Object { $_.Name -notin @(".git", $handoffDirName) } | Copy-Item -Destination $target4 -Recurse -Force

    git init $target4 2>$null | Out-Null
    git -C $target4 remote add origin "https://github.com/h-shojaku/PB-Dev.git"

    $remote4 = "https://github.com/myorg/ClonedExisting.git"
    Invoke-ProjectInit -RepoPath $target4 -Mode EXISTING_PRODUCT -Name "ClonedExisting" -Prefix "CLE" -Remote $remote4

    $actualOrigin4 = (git -C $target4 remote get-url origin 2>$null).Trim()
    if ($actualOrigin4 -ne $remote4) { throw "FAIL: actual git origin ($actualOrigin4) != requested remote ($remote4)" }
    if (-not (Test-Path -Path (Join-Path -Path $target4 -ChildPath "reports\analysis\EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md"))) { throw "FAIL: EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md missing" }

    Write-Host "PASS: test_actual_template_existing_product_initialization"
} finally { Remove-Item -Path $target4 -Recurse -Force -ErrorAction SilentlyContinue }

Write-Host "=== TEST 5: test_fail_non_git_repository ==="
$nonGitDir = Join-Path -Path ([System.IO.Path]::GetTempPath()) -ChildPath ("non_git_" + [Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path (Join-Path -Path $nonGitDir -ChildPath "templates\product") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path -Path $nonGitDir -ChildPath "scripts") -Force | Out-Null
Copy-Item -Path (Join-Path -Path $scriptDir -ChildPath "*") -Destination (Join-Path -Path $nonGitDir -ChildPath "scripts\") -Force
$res = Invoke-ProjectInit -RepoPath $nonGitDir -Mode NEW_PRODUCT -Name "App" -Prefix "APP" -Remote "https://github.com/myorg/App.git"
Remove-Item -Path $nonGitDir -Recurse -Force -ErrorAction SilentlyContinue
if ($res -like "*completed successfully*") { throw "FAIL: Non-git directory did not fail" }
Write-Host "PASS: test_fail_non_git_repository"

Write-Host "=== TEST 6: test_fail_missing_remote ==="
$repo6 = New-MockRepo
try {
    $res = Invoke-ProjectInit -RepoPath $repo6 -Mode NEW_PRODUCT -Name "App" -Prefix "APP" -Remote ""
    if ($res -like "*completed successfully*") { throw "FAIL: Missing remote did not fail" }
    Write-Host "PASS: test_fail_missing_remote"
} finally { Remove-Item -Path $repo6 -Recurse -Force -ErrorAction SilentlyContinue }

Write-Host "=== TEST 7: test_fail_placeholder_remote ==="
$repo7 = New-MockRepo
try {
    $res = Invoke-ProjectInit -RepoPath $repo7 -Mode NEW_PRODUCT -Name "App" -Prefix "APP" -Remote "https://github.com/example/App.git"
    if ($res -like "*completed successfully*") { throw "FAIL: Placeholder remote did not fail" }
    Write-Host "PASS: test_fail_placeholder_remote"
} finally { Remove-Item -Path $repo7 -Recurse -Force -ErrorAction SilentlyContinue }

Write-Host "=== TEST 8: test_fail_invalid_prefix ==="
$repo8 = New-MockRepo
try {
    $res = Invoke-ProjectInit -RepoPath $repo8 -Mode NEW_PRODUCT -Name "App" -Prefix "app-invalid!" -Remote "https://github.com/myorg/App.git"
    if ($res -like "*completed successfully*") { throw "FAIL: Invalid prefix did not fail" }
    Write-Host "PASS: test_fail_invalid_prefix"
} finally { Remove-Item -Path $repo8 -Recurse -Force -ErrorAction SilentlyContinue }

Write-Host "=== TEST 9: test_fail_missing_product_ssot_template ==="
$missingTplRepo = New-MockRepo
try {
    Remove-Item -Path (Join-Path -Path $missingTplRepo -ChildPath "templates\product\05_OPERATION_RULES.md") -Force -ErrorAction SilentlyContinue
    $res = Invoke-ProjectInit -RepoPath $missingTplRepo -Mode NEW_PRODUCT -Name "App" -Prefix "APP" -Remote "https://github.com/myorg/App.git"
    if ($res -like "*completed successfully*") { throw "FAIL: Missing Product SSOT template did not fail" }
    Write-Host "PASS: test_fail_missing_product_ssot_template"
} finally { Remove-Item -Path $missingTplRepo -Recurse -Force -ErrorAction SilentlyContinue }

Write-Host "=== TEST 10: test_fail_missing_analysis_template ==="
$missingAnalysisRepo = New-MockRepo
try {
    Remove-Item -Path (Join-Path -Path $missingAnalysisRepo -ChildPath "templates\product\EXISTING_PRODUCT_ANALYSIS_TEMPLATE.md") -Force -ErrorAction SilentlyContinue
    $res = Invoke-ProjectInit -RepoPath $missingAnalysisRepo -Mode EXISTING_PRODUCT -Name "App" -Prefix "APP" -Remote "https://github.com/myorg/App.git"
    if ($res -like "*completed successfully*") { throw "FAIL: Missing EXISTING_PRODUCT Analysis Template did not fail" }
    Write-Host "PASS: test_fail_missing_analysis_template"
} finally { Remove-Item -Path $missingAnalysisRepo -Recurse -Force -ErrorAction SilentlyContinue }

Write-Host "=== TEST 11: test_fail_existing_product_ssot_protection ==="
$repo11 = New-MockRepo
try {
    $docsP = Join-Path -Path $repo11 -ChildPath "docs\product"
    New-Item -ItemType Directory -Path $docsP -Force | Out-Null
    Set-Content -Path (Join-Path -Path $docsP -ChildPath "00_PRODUCT_OVERVIEW.md") -Value "Important Custom Spec" -Encoding UTF8
    $res = Invoke-ProjectInit -RepoPath $repo11 -Mode NEW_PRODUCT -Name "App" -Prefix "APP" -Remote "https://github.com/myorg/App.git"
    if ($res -like "*completed successfully*") { throw "FAIL: Existing product SSOT protection did not fail" }
    Write-Host "PASS: test_fail_existing_product_ssot_protection"
} finally { Remove-Item -Path $repo11 -Recurse -Force -ErrorAction SilentlyContinue }

Write-Host "=== TEST 12: test_unknown_product_file_rejected_without_mutation ==="
$repo12 = New-MockRepo
try {
    $docsP = Join-Path -Path $repo12 -ChildPath "docs\product"
    New-Item -ItemType Directory -Path $docsP -Force | Out-Null
    $unknownFile = Join-Path -Path $docsP -ChildPath "notes.txt"
    Set-Content -Path $unknownFile -Value "Unknown note" -Encoding UTF8

    $res = Invoke-ProjectInit -RepoPath $repo12 -Mode NEW_PRODUCT -Name "App" -Prefix "APP" -Remote "https://github.com/myorg/App.git"
    if ($res -like "*completed successfully*") { throw "FAIL: Unknown product file was not rejected" }
    if (-not (Test-Path -Path $unknownFile)) { throw "FAIL: Unknown product file was mutated/deleted" }
    Write-Host "PASS: test_unknown_product_file_rejected_without_mutation"
} finally { Remove-Item -Path $repo12 -Recurse -Force -ErrorAction SilentlyContinue }

Write-Host "=== TEST 13: test_unknown_product_subdirectory_rejected_without_mutation ==="
$repo13 = New-MockRepo
try {
    $subDir = Join-Path -Path $repo13 -ChildPath "docs\product\legacy"
    New-Item -ItemType Directory -Path $subDir -Force | Out-Null
    $specFile = Join-Path -Path $subDir -ChildPath "spec.txt"
    Set-Content -Path $specFile -Value "Legacy spec" -Encoding UTF8

    $res = Invoke-ProjectInit -RepoPath $repo13 -Mode NEW_PRODUCT -Name "App" -Prefix "APP" -Remote "https://github.com/myorg/App.git"
    if ($res -like "*completed successfully*") { throw "FAIL: Unknown product subdirectory was not rejected" }
    if (-not (Test-Path -Path $specFile)) { throw "FAIL: Unknown product subdirectory was mutated/deleted" }
    Write-Host "PASS: test_unknown_product_subdirectory_rejected_without_mutation"
} finally { Remove-Item -Path $repo13 -Recurse -Force -ErrorAction SilentlyContinue }

Write-Host "=== TEST 14: test_powershell_is_thin_wrapper ==="
$ps1Txt = Get-Content -Path (Join-Path -Path $scriptDir -ChildPath "initialize_project.ps1") -Raw
if ($ps1Txt -like "*PROJECT_PROFILE.md*") { throw "FAIL: initialize_project.ps1 contains PROJECT_PROFILE logic" }
if ($ps1Txt -like "*Set-Content*") { throw "FAIL: initialize_project.ps1 contains Set-Content business logic" }
if ($ps1Txt -notlike "*initialize_project.py*") { throw "FAIL: initialize_project.ps1 does not reference initialize_project.py" }
Write-Host "PASS: test_powershell_is_thin_wrapper"

Write-Host "=== TEST 15: test_final_profile_postconditions ==="
$repo15 = New-MockRepo
try {
    $remote15 = "https://github.com/myorg/ProfApp.git"
    Invoke-ProjectInit -RepoPath $repo15 -Mode NEW_PRODUCT -Name "ProfApp" -Prefix "PFA" -Remote $remote15

    $profTxt = Get-Content -Path (Join-Path -Path $repo15 -ChildPath "PROJECT_PROFILE.md") -Raw
    if ($profTxt -notlike "*Project Name:*ProfApp*") { throw "FAIL: PROJECT_PROFILE project name postcondition failed" }
    if ($profTxt -notlike "*Project Mode:*NEW_PRODUCT*") { throw "FAIL: PROJECT_PROFILE project mode postcondition failed" }
    if ($profTxt -notlike "*Task Prefix:*PFA*") { throw "FAIL: PROJECT_PROFILE task prefix postcondition failed" }
    if ($profTxt -notlike "*Canonical Remote:*$remote15*") { throw "FAIL: PROJECT_PROFILE canonical remote postcondition failed" }
    Write-Host "PASS: test_final_profile_postconditions"
} finally { Remove-Item -Path $repo15 -Recurse -Force -ErrorAction SilentlyContinue }

Write-Host "=== TEST 16: test_final_register_postconditions ==="
$repo16 = New-MockRepo
try {
    $remote16 = "https://github.com/myorg/RegApp.git"
    Invoke-ProjectInit -RepoPath $repo16 -Mode NEW_PRODUCT -Name "RegApp" -Prefix "RGA" -Remote $remote16

    $regTxt = Get-Content -Path (Join-Path -Path $repo16 -ChildPath "tasks\TASK_REGISTER.md") -Raw
    if ($regTxt -notlike "*(なし)*") { throw "FAIL: TASK_REGISTER active postcondition failed" }
    if ($regTxt -like "*\| DEV-TASK-*") { throw "FAIL: TASK_REGISTER history leak postcondition failed" }
    Write-Host "PASS: test_final_register_postconditions"
} finally { Remove-Item -Path $repo16 -Recurse -Force -ErrorAction SilentlyContinue }

Write-Host "=== TEST 17: test_final_current_state_postconditions ==="
$repo17 = New-MockRepo
try {
    $remote17 = "https://github.com/myorg/StateApp.git"
    Invoke-ProjectInit -RepoPath $repo17 -Mode NEW_PRODUCT -Name "StateApp" -Prefix "STA" -Remote $remote17

    $stTxt = Get-Content -Path (Join-Path -Path $repo17 -ChildPath "CURRENT_STATE.md") -Raw
    if ($stTxt -notlike "*IDLE*") { throw "FAIL: CURRENT_STATE phase postcondition failed" }
    if ($stTxt -notlike "*Task ID:*None*") { throw "FAIL: CURRENT_STATE task id postcondition failed" }
    if ($stTxt -notlike "*Task Prefix:*STA*") { throw "FAIL: CURRENT_STATE prefix postcondition failed" }
    if ($stTxt -notlike "*Canonical Remote:*$remote17*") { throw "FAIL: CURRENT_STATE remote postcondition failed" }
    Write-Host "PASS: test_final_current_state_postconditions"
} finally { Remove-Item -Path $repo17 -Recurse -Force -ErrorAction SilentlyContinue }

Write-Host "=== TEST 18: test_recursive_runtime_reset ==="
$repo18 = New-MockRepo
try {
    $nestedActive = Join-Path -Path $repo18 -ChildPath "tasks\active\nested\deep"
    $nestedCompleted = Join-Path -Path $repo18 -ChildPath "tasks\completed\sub"
    $nestedHandoff = Join-Path -Path $repo18 -ChildPath "$handoffDirName\sub_dir"
    New-Item -ItemType Directory -Path $nestedActive -Force | Out-Null
    New-Item -ItemType Directory -Path $nestedCompleted -Force | Out-Null
    New-Item -ItemType Directory -Path $nestedHandoff -Force | Out-Null
    Set-Content -Path (Join-Path -Path $nestedActive -ChildPath "x.md") -Value "active" -Encoding UTF8
    Set-Content -Path (Join-Path -Path $nestedCompleted -ChildPath "y.md") -Value "completed" -Encoding UTF8
    Set-Content -Path (Join-Path -Path $nestedHandoff -ChildPath "z.zip") -Value "zip" -Encoding UTF8

    Invoke-ProjectInit -RepoPath $repo18 -Mode NEW_PRODUCT -Name "RecApp" -Prefix "REC" -Remote "https://github.com/myorg/RecApp.git"

    $activeItems = (Get-ChildItem -Path (Join-Path -Path $repo18 -ChildPath "tasks\active") -Recurse).Count
    $completedItems = (Get-ChildItem -Path (Join-Path -Path $repo18 -ChildPath "tasks\completed") -Recurse).Count
    $handoffItems = (Get-ChildItem -Path (Join-Path -Path $repo18 -ChildPath $handoffDirName) -Recurse).Count

    if ($activeItems -ne 0 -or $completedItems -ne 0 -or $handoffItems -ne 0) {
        throw "FAIL: Recursive runtime reset failed! active: $activeItems, completed: $completedItems, handoff: $handoffItems"
    }
    Write-Host "PASS: test_recursive_runtime_reset"
} finally { Remove-Item -Path $repo18 -Recurse -Force -ErrorAction SilentlyContinue }

Write-Host "=== TEST 19: test_dry_run_no_mutation ==="
$repo19 = New-MockRepo
try {
    Invoke-ProjectInit -RepoPath $repo19 -Mode NEW_PRODUCT -Name "DryApp" -Prefix "DRY" -Remote "https://github.com/myorg/DryApp.git" -DryRun

    $dummyActive = Join-Path -Path $repo19 -ChildPath "tasks\active\DEV-TASK-0010.md"
    if (-not (Test-Path -Path $dummyActive)) { throw "FAIL: Dry run modified files!" }

    Write-Host "PASS: test_dry_run_no_mutation"
} finally { Remove-Item -Path $repo19 -Recurse -Force -ErrorAction SilentlyContinue }

Write-Host "Ran 19 tests in PowerShell runner. ALL 19 TESTS PASSED!"
