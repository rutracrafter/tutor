# PreToolUse guard for Windows. Behaviour matches protect-closed-notes.sh exactly:
# refuse any Write/Edit to a note whose frontmatter holds `status: closed`.
#
# Register it in .claude/settings.json in place of the .sh on Windows:
#   "command": "powershell -NoProfile -ExecutionPolicy Bypass -File \"$CLAUDE_PROJECT_DIR/.claude/hooks/protect-closed-notes.ps1\""
#
# Exit 0 — allow. Exit 2 — block and show the message to the agent.
# Any internal failure allows the call: a broken guard must not stop a lesson.

$ErrorActionPreference = 'Continue'

try {
    $raw = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($raw)) { exit 0 }
    $payload = $raw | ConvertFrom-Json
    $toolInput = $payload.tool_input
    if ($null -eq $toolInput) { exit 0 }

    $target = $toolInput.file_path
    if ([string]::IsNullOrWhiteSpace($target)) { $target = $toolInput.notebook_path }
    if ([string]::IsNullOrWhiteSpace($target)) { exit 0 }
    if (-not (Test-Path -LiteralPath $target -PathType Leaf)) { exit 0 }   # a new file cannot be closed
    if ([System.IO.Path]::GetExtension($target) -ne '.md') { exit 0 }

    # Only the frontmatter counts: it must open on line 1 and ends at the next --- .
    $lines = Get-Content -LiteralPath $target -TotalCount 60 -ErrorAction Stop
    if ($lines.Count -eq 0 -or $lines[0].Trim() -ne '---') { exit 0 }

    $closed = $false
    for ($i = 1; $i -lt $lines.Count; $i++) {
        $line = $lines[$i].Trim()
        if ($line -eq '---' -or $line -eq '...') { break }
        if ($line -match '^status:\s*closed$') { $closed = $true; break }
    }
    if (-not $closed) { exit 0 }
}
catch { exit 0 }

$name = Split-Path -Leaf $target
$message = @"
Blocked: $name is a closed note and the record is append-only.

  Closed notes are evidence. Editing one would make the record claim something that did
  not happen, so the guard hook refuses the write rather than trusting the prompt.

What to do instead:
  - A grade to revise  -> append a new line to the concept's ## Log in Concepts/.
                          A regrade is a new observation, never an edit.
  - Work to carry on   -> open today's session note and write there.
  - A correction round -> it belongs in the session that is still open.
  - The learner's own  -> their notebook, their edit. Leave it; git shows the change and
    later edit            ``tutor.py check`` reports it.
"@
[Console]::Error.WriteLine($message)
exit 2
