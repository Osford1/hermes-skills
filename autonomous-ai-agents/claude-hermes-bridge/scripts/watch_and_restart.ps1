# Wait for a running Hermes job to finish, then restart Claude Desktop so the
# fixed bridge code is loaded. Run to unblock a code change while a job is live.
#
# Two things this MUST do beyond stopping/starting Claude:
#   1. wait for the job's process to exit (restarting kills it otherwise), and
#   2. kill surviving bridge server processes, because Claude Desktop leaves them
#      orphaned and an old-code instance would be reused, so the fix never loads.
#
# Verify afterwards: the new server processes' CreationDate must be later than
# server.py's mtime, and main.log must show 'Connected to hermes'.
$ErrorActionPreference = 'Continue'

$bridge   = 'C:\Users\<you>\Projects\claude-hermes-bridge'
$log      = Join-Path $bridge 'logs\restart-watcher.log'
$auditPid = 16440   # <-- set to the running job's pid
$doneFile = 'C:\path\to\expected\DONE\file'
$mainLog  = Join-Path $env:LOCALAPPDATA 'Claude\logs\main.log'

New-Item -ItemType Directory -Force -Path (Split-Path $log) | Out-Null

function Say($m) {
    $line = "{0}  {1}" -f (Get-Date -Format 'HH:mm:ss'), $m
    Add-Content -Path $log -Value $line
    Write-Output $line
}

Say "=== watcher started; waiting for job pid $auditPid to exit ==="

$deadline = (Get-Date).AddMinutes(150)
while ($true) {
    if (-not (Get-Process -Id $auditPid -ErrorAction SilentlyContinue)) { break }
    if ((Get-Date) -gt $deadline) {
        Say "TIMEOUT: job pid still alive after 150 min - NOT restarting Claude"
        exit 2
    }
    Start-Sleep -Seconds 15
}

Say "job pid $auditPid has exited"
if (Test-Path $doneFile) {
    Say "DONE file present: $((Get-Item $doneFile).Length) bytes"
} else {
    Say "WARNING: DONE file NOT found - job may have ended without finishing"
}

# Mark the log position so the new connection line can be identified afterwards.
$before = 0
if (Test-Path $mainLog) { $before = @(Get-Content $mainLog).Count }

Say "stopping Claude Desktop"
Get-Process -Name claude -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 8
$still = Get-Process -Name claude -ErrorAction SilentlyContinue
if ($still) {
    Say "still alive after 8s; forcing again"
    $still | Stop-Process -Force
    Start-Sleep -Seconds 5
}

# Orphaned bridge servers survive the parent kill and would serve stale code.
$stale = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
         Where-Object { $_.CommandLine -like '*claude-hermes-bridge*' }
foreach ($p in $stale) {
    Say "killing stale bridge server pid $($p.ProcessId)"
    Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
}
if (-not $stale) { Say "no stale bridge servers found" }

Say "relaunching Claude Desktop"
Start-Process 'shell:AppsFolder\Claude_pzs8sxrjxfjjc!Claude'
Start-Sleep -Seconds 45

$new = @()
if (Test-Path $mainLog) { $new = @(Get-Content $mainLog) | Select-Object -Skip $before }
$conn = $new | Select-String -Pattern 'Connected to hermes' | Select-Object -Last 1
if ($conn) { Say "CONNECTED: $($conn.Line.Trim())" }
else { Say "no 'Connected to hermes' line yet; check main.log manually" }

Say "=== watcher done ==="
