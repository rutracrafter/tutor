---
name: quiz
description: Run a quiz on a concept cluster — 5-8 items, no help during, then a correction round. The examiner writes the paper to a blueprint and grades it blind against a hidden key. Results show as solid, shaky or gap with next actions, never as a percentage.
---

# /quiz `[topic]`

5–8 items at the end of a concept cluster, or on a review day. 15–30 minutes.

A quiz is a learning event, not a grading event. Every item exists to make the learner
think, and its result decides what they practise next. The score is an internal steering
signal.

## 1 · Build the blueprint

Pick the concepts: the cluster just finished, plus about a tenth of the items on older
concepts for interleaving. Only concepts at `introduced` or better — never quiz something
never taught.

```bash
python3 scripts/tutor.py due --domain <domain> --json
python3 scripts/tutor.py frontier --domain <domain> --json
```

Item mix, by the learner's current level on each concept:

| Share | Level |
| --- | --- |
| ~2/3 | at their current level |
| ~1/4 | one level above |
| ~1/10 | older concepts, mixed in |

Target an expected score of 0.75–0.85. Easier than that and it measures nothing; harder and
it teaches discouragement.

## 2 · Hand off to the examiner

The examiner starts fresh and cannot see the lesson, so the message must be complete. Use
this template verbatim — a missing field is the usual cause of a bad paper:

```text
Job: write a paper (job 1 in your prompt).
Purpose: <e.g. close the probability cluster before moving to inference>
Kind: quiz · 6 items · no help during

Blueprint:
  bayes-theorem           · level 3 · 2 items
  conditional-probability · level 2 · 2 items
  law-of-total-probability· level 3 · 1 item
  independence            · level 2 · 1 item   (older, interleaved)

Concept state:
  bayes-theorem           · mastery 0.62 · scaffold completion
                          · misconceptions: swaps P(A|B) and P(B|A)
  conditional-probability · mastery 0.72 · scaffold independent · misconceptions: none
  ...

Favour these item types: derive, predict-then-explain, apply to an unfamiliar case.
Include exactly one explain-it-simply item, on bayes-theorem.
Target expected score: 0.80
Write the paper to: Assessments/2026-10-06-quiz-probability.md
Write the key to:    .keys/2026-10-06-quiz-probability-key.md
```

Check what comes back: the expected-score estimate against your target, that no answer
leaked into the paper, and that every blueprint concept is covered. Read the paper itself —
not the key — before handing it to the learner.

## 3 · The learner answers

Say in one line: the item count, that there is no help during the paper, and that a
correction round follows. Then hand over the turn.

- **No hints, no nudges, no clarifications of content.** A question about what an item is
  *asking* may be answered; a question about how to answer it may not.
- Answers go in the `[!answer]` slots, each with a confidence rating 1–5.
- Moving a quiz is free and never lowers mastery. If they are tired, say so and offer to
  move it.

## 4 · Grade blind

Delegate grading as a separate message, with the paths and nothing else:

```text
Job: grade blind (job 2 in your prompt).
Paper:   Assessments/2026-10-06-quiz-probability.md
Key:     .keys/2026-10-06-quiz-probability-key.md
Answers: in the paper, in the [!answer] blocks.
```

**Re-grade every item the examiner marked `unsure` yourself.** That is what the flag is
for. Also re-check any item where a confident answer was marked wrong — a misconception and
a bad grade look identical in the output.

## 5 · Feedback, then the correction round

Write the feedback into the note, in this order:

1. **What they understood** — specific, one or two lines, naming the reasoning that worked.
   Not praise; evidence.
2. **The single most important gap** — one gap, not a list. The examiner's closing line
   names a candidate.
3. **The correction round.** For each miss, one question that points at the error without
   naming it: "In Q3 you wrote $P(B \mid A)$ where the problem asked for $P(A \mid B)$ —
   what does each one mean in words here?" Fixing it themselves earns **half credit**.
4. **Only then**, a model solution for anything still unresolved — and have them explain it
   back. An unexplained model solution is the thing that harms learning.

No percentage headline, ever. Per concept: **solid**, **shaky** or **gap**, each with its
next action.

```markdown
## Results
| Concept | Where you stand | Next |
| --- | --- | --- |
| conditional-probability | solid | review in a week |
| bayes-theorem | shaky | two base-rate problems next session |
| law-of-total-probability | gap | re-teach from the partition idea |
```

Raw numbers stay in the frontmatter unless `show_scores: true` in the profile.

## 6 · Record and close

Record each item with `tutor.py record` at **full** weight (a quiz item is not a check for
understanding), passing the hint count as 0 — there was no help — and crediting the
correction round separately at 0.5 where it earned it.

Set the note's `status: closed`, write the `## What next` line that feeds the next session's
plan, and commit. There are **no retakes of this paper**: misses return later as review
items in new forms, so memorising answers cannot help.
