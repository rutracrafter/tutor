# Conventions for every agent in this repo

This file loads into the tutor and every subagent. `CLAUDE.local.md`, written by `/setup`,
holds the path to the data folder. Read it before touching any note.

## The note is the source of truth

Nothing of substance lives only in the terminal. Questions, answers, explanations,
decisions, grades and summaries all go into the note. A chat reply is one line — a pointer,
not content ("Q5 is up", "wrapped, 3 concepts updated").

The reason is continuity: every learning session is a fresh Claude Code session, so the
conversation is gone next time and the files are all that survive. If it matters and it is
not in a file, it did not happen.

## Who writes what

| Block | Written by | Rule |
| --- | --- | --- |
| `> [!tutor]` | the tutor | Append only. Never revise one you already wrote. |
| `> [!answer] Your answer` | the learner | Never edit the contents. Not to fix a typo, not to tidy formatting. |
| `> [!checkpoint]` | the tutor | The learner ticks boxes inside it. |
| `> [!steer]` | the learner | Read it, act on it, acknowledge it under the current checkpoint. |
| `## Log` in a concept note | tutor.py or the scribe | Append only. A regrade is a new line. |
| frontmatter of a concept | tutor.py or the scribe | The current estimate; may change. |

## The turn protocol

A turn ends when the learner hands it back from the terminal. **Pressing Enter on an empty
line, or typing a single `.`, means "read the note".** Re-read the open session note and
continue from what changed.

If the learner types more than that, sort it before acting:

- **An answer** — copy it word for word into the current `[!answer]` slot, append
  `(typed in terminal)` on its own line, and handle it exactly as if it had been written
  in the note. Never paraphrase it, never correct its spelling.
- **A steering request** — log it under the current checkpoint as a `> [!steer]` callout,
  then act on it.
- **A question** — answer it in the note, in a `> [!tutor]` block, not in chat.

Anything typed in the terminal is copied into the note before it is acted on, so the note
stays complete even for a session conducted entirely from the keyboard.

## Revising an answer

The learner may improve an answer during a session by adding a line starting with
`Revised:` underneath the original, inside the same `[!answer]` block. Treat it as a new
attempt and grade it as one; it is better practice than silently fixing the first try.

Never overwrite the original on their behalf, and never ask them to.

## History is never rewritten

- `status: closed` in a note's frontmatter means the note is evidence. The
  `protect-closed-notes` hook blocks any Write or Edit to it and exits 2. Being blocked is
  the system working; do not look for another route to the same change.
- While a note is open, append; never touch an answer block.
- In a concept note, frontmatter is the current estimate and may change. `## Log` is
  append-only.
- Mastery is computed only from log lines written at grading time, never by re-reading old
  answers. This is what makes a later edit harmless.
- The learner may edit anything in Obsidian; it is their notebook. `/wrap` commits the data
  folder to git, so a change to a closed note shows in the diff and `tutor.py check`
  reports it.

## Filenames

Lowercase, dashes, no spaces, ever.

| What | Pattern |
| --- | --- |
| Session | `Sessions/YYYY-MM-DD-<topic>.md` |
| Quiz | `Assessments/YYYY-MM-DD-quiz-<topic>.md` |
| Exam | `Assessments/YYYY-MM-DD-exam-<topic>.md` |
| Answer key | `.keys/YYYY-MM-DD-<kind>-<topic>-key.md` |
| Concept | `Concepts/<concept-id>.md` — the ID is the filename |
| Map | `Maps/<domain-tag-with-dashes>.md` |
| Project | `Projects/<slug>/brief.md`, `log.md` |
| Code exercise | `Workspaces/<topic>/<YYYY-MM-DD>-<item>/` |
| Figure | `Assets/<dashed-name>.svg` |

A concept ID never contains its domain, so re-tagging a domain moves no files and breaks
no links. When the same word means different things in two fields, the ID disambiguates:
`normal-distribution` and `surface-normal`.

## Domains are tags, not folders

Nested tags: `math`, then `math/probability` when it earns the split. Searching the parent
tag in Obsidian finds its children. A concept may carry several tags at once — that is how
one note belongs to both statistics and machine learning. Splitting a domain is a re-tag,
never a move.

## Two folders, kept apart

The engine repo is generic and shareable; the data folder is the learner's. Never write a
learning note into the engine repo, and never write engine configuration into the data
folder. `git pull` must stay safe to run.

## Links

Wikilinks: `[[concept-id]]` for concepts, `[[2026-10-06-probability#Q4]]` to cite a
specific item as evidence. Every log line cites the item it came from, so any number in
the record can be traced back to the answer that produced it.
