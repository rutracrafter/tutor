#!/usr/bin/env bash
# Optional submit watcher. Prints one line when the learner ticks a Submit box in the
# open session note, so they can hand the turn back from Obsidian instead of the terminal.
#
#   scripts/watch-submit.sh <note-path> [poll-seconds] [settle-seconds]
#
# Start it through Claude Code's Monitor tool at the beginning of a session. The tutor
# wakes only when a line is printed, so idle polling costs nothing in tokens.
#
# This is a convenience, never a dependency:
#   - Opt-in, via `submit_watcher: true` in the profile.
#   - Pressing Enter in the terminal always works, watcher or no watcher.
#   - If it dies, nothing happens and the learner presses Enter. There is no recovery path
#     to get wrong, which is the only reason it is safe to add at all.
#   - Background monitors do not survive a resumed session, so /learn re-arms it.
#
# Pickup is idempotent through the file itself, not through state kept here: it fires only
# on `- [x] Submit`, and the tutor rewrites that line to `Submitted HH:MM` once it has read
# the answer. A second trigger finds no ticked box and prints nothing.

set -u

note="${1:-}"
poll="${2:-1}"
settle="${3:-2}"

if [ -z "$note" ]; then
  echo "usage: watch-submit.sh <note-path> [poll-seconds] [settle-seconds]" >&2
  exit 64
fi
if [ ! -f "$note" ]; then
  echo "watch-submit: no such note: $note" >&2
  exit 66
fi

# BSD stat (macOS) and GNU stat (Linux) disagree on every flag that matters.
if stat -f %m "$note" >/dev/null 2>&1; then
  mtime() { stat -f %m "$1" 2>/dev/null; }
else
  mtime() { stat -c %Y "$1" 2>/dev/null; }
fi

# A ticked box, allowing any indentation, `*` or `-`, and any case of "submit".
submitted() {
  grep -Eqi '^[[:space:]]*[-*][[:space:]]*\[[xX]\][[:space:]]*submit' "$1" 2>/dev/null
}

last="$(mtime "$note")"
echo "watch-submit: watching $(basename "$note") every ${poll}s — Enter still works" >&2

while true; do
  sleep "$poll"
  [ -f "$note" ] || continue            # a sync service may briefly replace the file
  now="$(mtime "$note")"
  [ -n "$now" ] || continue
  if [ "$now" != "$last" ]; then
    last="$now"
    # Wait for Obsidian's autosave to finish writing before reading the file.
    sleep "$settle"
    if submitted "$note"; then
      echo "SUBMIT $note $(date +%H:%M:%S)"
      last="$(mtime "$note")"           # the settle-window write is not a new trigger
    fi
  fi
done
