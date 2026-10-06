# Optional submit watcher for Windows. Behaviour matches watch-submit.sh exactly.
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/watch-submit.ps1 -Note <path>
#
# Prints one line when the learner ticks a Submit box in the open session note. Opt-in;
# pressing Enter in the terminal always works, watcher or no watcher. If it dies, nothing
# happens and the learner presses Enter.
#
# Pickup is idempotent through the file: it fires only on `- [x] Submit`, and the tutor
# rewrites that line to `Submitted HH:MM` once it has read the answer.

param(
    [Parameter(Mandatory = $true)][string]$Note,
    [int]$PollSeconds = 1,
    [int]$SettleSeconds = 2
)

if (-not (Test-Path -LiteralPath $Note -PathType Leaf)) {
    [Console]::Error.WriteLine("watch-submit: no such note: $Note")
    exit 66
}

function Get-Mtime([string]$path) {
    try { return (Get-Item -LiteralPath $path -ErrorAction Stop).LastWriteTimeUtc.Ticks }
    catch { return $null }
}

function Test-Submitted([string]$path) {
    try {
        return (Select-String -LiteralPath $path -Pattern '^\s*[-*]\s*\[[xX]\]\s*submit' `
                              -CaseSensitive:$false -Quiet -ErrorAction Stop) -eq $true
    } catch { return $false }
}

$last = Get-Mtime $Note
[Console]::Error.WriteLine("watch-submit: watching $(Split-Path -Leaf $Note) every ${PollSeconds}s — Enter still works")

while ($true) {
    Start-Sleep -Seconds $PollSeconds
    if (-not (Test-Path -LiteralPath $Note -PathType Leaf)) { continue }
    $now = Get-Mtime $Note
    if ($null -eq $now) { continue }
    if ($now -ne $last) {
        $last = $now
        Start-Sleep -Seconds $SettleSeconds     # let Obsidian's autosave finish
        if (Test-Submitted $Note) {
            Write-Output "SUBMIT $Note $(Get-Date -Format 'HH:mm:ss')"
            $last = Get-Mtime $Note             # the settle-window write is not a new trigger
        }
    }
}
