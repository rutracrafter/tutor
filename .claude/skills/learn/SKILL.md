---
name: learn
description: Run a normal study session on a topic, with a time budget. Opens a session note, loads the working set from the concept graph, teaches in five timed phases with steering checkpoints, and wraps up. Use for ordinary study; use /review for a short session with no new material.
---

# /learn `<topic>` `[budget]`

`/learn rust-borrowing 30m` · `/learn probability` (asks for the budget) · `/learn`
(asks for both).

A single learning session, start to finish. Run it in a fresh Claude Code session: all
continuity lives in files, and a fresh context stays cheap and avoids drift from a long
chat.

## 0 · Before anything, recover an open note

Glob `Sessions/*.md` and check the frontmatter of the most recent few for `status: open`.
An open note means a previous session ended without `/wrap` — the terminal was closed, or
the laptop shut.

If you find one:

1. Say in one line which session it was and that you are wrapping it first.
2. Run `/wrap` on **that** note, recording only what the note actually shows: graded items
   become evidence, ungraded ones become carry-over. Invent nothing.
3. Then continue with today's session.

No evidence is ever lost to a forgotten wrap. Do not ask permission for this; it is
bookkeeping, and asking costs more attention than it saves.

Then run `python3 scripts/tutor.py check` (skip without Python). If it reports a closed
note changed since its commit, say so in one line and carry on — the record stands, the
change is simply visible.

## 1 · Budget and type

Parse the budget from the command (`30m`, `45`, `1h`). If absent, read
`session_default_min` from `Learner/profile.md` and ask in one line, offering it.

- **Under 20 minutes** → say `/review` fits better and offer it. Proceed only if I insist.
- Take the start time from the system clock: `date +%H:%M`. Do not guess it, and do not
  reuse a time from earlier in the conversation.

## 2 · Load the working set

Read only what today needs. Never read a whole folder.

| What | How |
| --- | --- |
| Profile | Read `Learner/profile.md` in full — verbosity, goals, show_scores, constraints |
| Index | Read `Learner/index.md` in full — it is one line per domain |
| Due reviews | `python3 scripts/tutor.py due --limit 15` |
| Frontier | `python3 scripts/tutor.py frontier --domain <domain>` |
| Last session | The `## Summary` and `## Carry over` of the newest closed session note in this domain — those sections only |
| Today's concepts | Frontmatter of the concepts you will teach, plus their direct prerequisites and `related` |

Without Python, Grep the frontmatter fields instead (`next_review:`, `stage:`, `mastery:`)
and cap the result at 15 due concepts. Never read concept bodies in bulk; a concept's
`## Log` is for diagnosing that one concept.

**If the topic is new** — no concepts carry a matching tag — stop and offer `/diagnose
<topic>` instead. Teaching without a graph means teaching blind to prerequisites.

## 3 · Open the session note

Create `Sessions/YYYY-MM-DD-<topic>.md` from `templates/session.md`. Topic slug in
lowercase with dashes. If the file exists (a second session on the same topic the same
day), append `-2`.

Fill the frontmatter: date, topic, domains, `session_type: learn`, `budget_min`, `started`,
`status: open`. Leave `concepts: []` to fill as you go.

Then write the plan into `## Plan` as real items, not the template's placeholders — the
concepts, the phase shares in minutes for today's budget, and what each phase will cover.
Tell me the plan in the note, and in chat only: "Plan is in the note — Enter to start."

## 4 · Teach

Follow the lesson structure, the practice loop and the hint ladder from your prompt. Per
phase:

1. **Warm-up (~15%)** — due reviews, produced from memory. One item per due concept, up to
   about 4. A correct answer here also pushes each direct prerequisite's next review half a
   step later.
2. **New idea (~25%)** — a prediction question *before* any explanation, then the
   explanation in chunks, each chunk followed by an explain-back or a "why".
3. **Guided practice (~35%)** — scaffold stage decides the form: `worked` means you work
   one and I explain it back, `completion` means you leave the last steps to me,
   `independent` means I do it whole, `transfer` means a new context.
4. **Independent practice (~15%)** — no scaffolding, a context I have not seen, at least
   one older concept mixed in.
5. **Wrap-up (~10%)** — an explain-it-simply item, then *my* summary in my words, never
   yours. Then `/wrap`.

Check the clock at every phase boundary with `date +%H:%M` and write the elapsed time into
the checkpoint. Running late: cut new material first, never the warm-up or wrap-up. About
5 minutes left: go to the wrap-up.

Each item gets its own `##` heading, so it can be cited as evidence:

```markdown
## Q4 · bayes-theorem · level 3 · scaffold: completion
> [!tutor]
> A test is 99% accurate and the disease affects 1 in 1,000 people.
> Before calculating, predict roughly how likely a positive result is
> to be correct, then derive the exact value.

> [!answer] Your answer
> 
```

After each phase, a checkpoint:

```markdown
> [!checkpoint] Next: guided practice on bayes-theorem, 3–4 problems · 18 min used of 45
> - [ ] More practice on what we just did
> - [ ] Go deeper on something (say what)
> - [ ] Something else (write below)
> Leave everything unticked to continue as planned.
```

Code exercises go in `Workspaces/<topic>/<date>-<item>/`, linked from the item. You may
create stubs or failing tests, and run my code — never write the solution.

## 5 · Close

Run `/wrap`. If I stop replying or say we are done, run it anyway: a session that is not
wrapped leaves its evidence uncounted.

## Notes

- The optional submit watcher, if `submit_watcher: true` in my profile, is re-armed here at
  session start — background monitors do not survive a session. Enter always works
  regardless, and if the watcher dies, nothing breaks.
- One learning session is one Claude Code session. If this one has been going a long time,
  say so at wrap-up and suggest `/clear` before the next.
