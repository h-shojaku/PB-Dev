# Project Initializer for AI Development System (100% Thin PowerShell Wrapper)
# Delegates all business logic to canonical implementation: scripts/initialize_project.py

[CmdletBinding()]
param (
    [string]$Mode = "NEW_PRODUCT",
    [string]$Name = "MyNewProduct",
    [string]$Prefix = "APP",
    [string]$Remote = "",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$scriptDir = $PSScriptRoot
$pyScript = Join-Path -Path $scriptDir -ChildPath "initialize_project.py"

# Locate python executable
$pythonExe = Get-Command "python" -ErrorAction SilentlyContinue
if (-not $pythonExe) { $pythonExe = Get-Command "python3" -ErrorAction SilentlyContinue }
if (-not $pythonExe) { $pythonExe = Get-Command "py" -ErrorAction SilentlyContinue }

if (-not $pythonExe) {
    Write-Error "Python executable not found. Python runtime is required to run canonical Project Initializer (initialize_project.py)."
    exit 1
}

$pyArgs = @($pyScript, "--mode", $Mode, "--name", $Name, "--prefix", $Prefix)
if ($Remote) { $pyArgs += @("--remote", $Remote) }
if ($DryRun) { $pyArgs += "--dry-run" }

& $pythonExe.Source $pyArgs
if ($LASTEXITCODE -ne 0) {
    Write-Error "Project initialization failed via initialize_project.py (Exit Code: $LASTEXITCODE)."
    exit $LASTEXITCODE
}
