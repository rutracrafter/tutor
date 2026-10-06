---
name: wrap
description: Close the current session at any moment. Writes the five-line summary, records the evidence collected into the concept graph, lists unfinished items as carry-over, regenerates the maps, marks the note closed and commits the data folder to git.
---

# /wrap

Works at any moment — two minutes in or at the end of the full budget. It records only
what actually happened. An item I never answered is carry-over, not a miss.

Takes 2–5 minutes. Do the steps in order; each one is cheap and the order matters, because
step 7 closes the note and the guard hook then refuses every further write to it.

## 1 · Wrap-up items, if there is time and they are missing

If the session never reached its wrap-up phase and more than about three minutes remain,
do these two things first — they are the highest-value part of the session:

- One explain-it-simply item on today's main concept.
- My own summary, in my words. Ask for it; never write it for me.

If I am out of time, skip both and note it in the carry-over.

## 2 · The summary

Write five lines or fewer at the top of the note, under `## Summary`. This is the only
part a later session reads, so it carries the whole session:

- What we covered, by concept ID.
- Where I actually stand on each — solid, shaky or gap.
- The misconception worth remembering, if one appeared.
- What should happen next.

No praise, no narration of the session's shape, no restating the questions.

## 3 · Gather the evidence

For each graded item in the note, collect: the concept ID, the score (1 correct, 0.5
partial, 0 miss), the number of hint levels used, and the item's anchor (`#Q4`).

Credit rules:

- A check for understanding inside a lesson counts **half**; a quiz or exam item counts
  **full**.
- Each hint level used subtracts 0.25 from the item's score, floored at 0.
- A walk-through (ladder level 6) is a miss, score 0.
- A correct answer gives each direct prerequisite partial review credit: push its
  `next_review` half an interval step later. Mastery itself does not move.

Ungraded items — asked but never answered — produce no evidence at all.

## 4 · Record it

With Python:

```bash
python3 scripts/tutor.py record <concept-id> --score <0|0.5|1> --hints <n> \
    --source "2026-10-06-probability#Q4"
```

once per graded item. The script applies the mastery and interval rules, appends the log
line and updates the frontmatter. It is deterministic, so prefer it over doing the
arithmetic yourself.

Without Python, delegate to the `scribe` with one message listing every observation, the
rules to apply, and the concept paths. Then read back two of the concept notes it touched
and check the arithmetic.

The rules the script applies, for reference:

- Mastery moves 30% of the way toward the item's score: `m ← m + 0.3 × (score − m)`.
- `mastered` at mastery ≥ 0.85, with at least 3 observations across 2 sessions, including
  a transfer item or a project milestone.
- Intervals run 1, 3, 7, 16, 35 days, then double. A miss resets to 1 day.
- A concept joins the frontier once every prerequisite is `practicing` or better with
  mastery ≥ 0.6.

New concepts that came up today and are not in the graph yet: hand them to the
`cartographer`, which drafts them linked to what I already hold. Do not create concept
notes yourself; reuse-before-create needs a search of existing IDs and aliases.

## 5 · Carry over

Under `## Carry over`, list every unticked plan item and anything we started and did not
finish, one line each with enough context to resume cold. Then offer the `## Parking lot`
tangents: one line naming them, and whether to add them to the graph for later.

## 6 · Regenerate the maps and index

```bash
python3 scripts/tutor.py maps --domain <each domain touched today>
python3 scripts/tutor.py index
```

The frontier is recomputed here, at every wrap. If a domain's frontier has run dry — every
concept in the graph is `practicing` or better — hand the cartographer the goal from my
profile and have it extend the graph one layer further. Say in one line that it grew.

Without Python, the scribe does both.

## 7 · Close the note

Set `status: closed` and `ended: HH:MM` in the frontmatter, from the real clock. Write the
concept IDs touched into `concepts:`.

Do this **last**. The guard hook blocks every Write and Edit to the note from this point
on, which is the intended behaviour: the note is now evidence.

If `hard_lock_closed_notes: true` in my profile, also `chmod a-w` the note.

## 8 · Commit

```bash
git -C "<data folder>" add <paths under the data folder only>
git -C "<data folder>" commit -m "tutor: wrap 2026-10-06-probability"
```

Stage paths explicitly, never `git add -A` or `.` — the data folder may sit inside a vault
repo holding notes that are none of the tutor's business. Never push, never rebase, never
touch a file outside the data folder.

If the commit fails because another tool holds git's index lock — the Obsidian Git plugin
syncing at that moment is the usual cause — wait a moment and retry once. If it fails
again, tell me in one line and stop. The notes are safe either way; only the commit is
missing, and the next wrap will include it.

If `Git repo: none` in `CLAUDE.local.md`, skip this step silently.

## 9 · Report

One short block in chat, not in the note:

```text
Wrapped 2026-10-06-probability · 38 min
bayes-theorem solid · conditional-probability shaky · base-rate-fallacy gap
Next: base rates in a new context, and the quiz on this cluster is due
```

Use solid / shaky / gap, not numbers, unless `show_scores: true`.
