#!/usr/bin/env bash
# PreToolUse guard: refuse any Write/Edit to a note that is already closed.
#
# History the model cannot trust is worse than no history, so the append-only rule is
# enforced here rather than only requested in the prompts. A note is closed when its
# YAML frontmatter holds `status: closed`, which /wrap writes as its last act.
#
# Exit 0 — allow. Exit 2 — block the tool call and show stderr to the agent.
# Any other failure must still allow the call: a broken guard must not stop a lesson.

set -u

input=$(cat 2>/dev/null) || exit 0
[ -n "$input" ] || exit 0

# --- extract the target path -------------------------------------------------
# python3 parses the JSON properly when it is installed; the sed fallback covers the
# ordinary case of a path with no escaped quotes, which is every real note path.
target=""
if command -v python3 >/dev/null 2>&1; then
  target=$(printf '%s' "$input" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
i = d.get("tool_input") or {}
print(i.get("file_path") or i.get("notebook_path") or "")
' 2>/dev/null)
else
  # Two passes, because BSD sed has no \| alternation in a basic regex.
  for key in file_path notebook_path; do
    target=$(printf '%s' "$input" \
      | sed -n "s/.*\"$key\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p" \
      | head -n 1)
    [ -n "$target" ] && break
  done
fi

[ -n "$target" ] || exit 0
[ -f "$target" ] || exit 0          # a new file cannot be closed
case "$target" in *.md) ;; *) exit 0 ;; esac

# --- is it closed? -----------------------------------------------------------
# Only the frontmatter counts: the first `---` must be line 1, and the block ends at the
# next `---`. A `status: closed` further down the body is prose, not state.
closed=$(awk '
  NR == 1 && $0 != "---" { exit }
  NR == 1 { infm = 1; next }
  infm && ($0 == "---" || $0 == "...") { exit }
  infm && /^status:[[:space:]]*closed[[:space:]]*$/ { print "yes"; exit }
  NR > 60 { exit }
' "$target" 2>/dev/null)

if [ "$closed" = "yes" ]; then
  name=$(basename "$target")
  cat >&2 <<MSG
Blocked: $name is a closed note and the record is append-only.

  Closed notes are evidence. Editing one would make the record claim something that did
  not happen, so the guard hook refuses the write rather than trusting the prompt.

What to do instead:
  - A grade to revise  -> append a new line to the concept's ## Log in Concepts/.
                          A regrade is a new observation, never an edit.
  - Work to carry on   -> open today's session note and write there.
  - A correction round -> it belongs in the session that is still open.
  - The learner's own  -> their notebook, their edit. Leave it; git shows the change and
    later edit            \`tutor.py check\` reports it.
MSG
  exit 2
fi

exit 0
