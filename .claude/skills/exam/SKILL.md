---
name: exam
description: Run a cumulative exam at a milestone — 8-15 items across a domain, no help, relying only on mastered concepts for the hard items. Same machinery as /quiz with a wider blueprint and transfer evidence; about every 4-6 sessions in a domain.
---

# /exam `[domain]`

8–15 items, cumulative across a domain, at a milestone — roughly every 4–6 sessions in that
domain. 30–45 minutes.

Everything in `/quiz` applies: learning over scores, no help during, blind grading, a
correction round, results as solid / shaky / gap. The differences are below.

## What makes an exam different

| | Quiz | Exam |
| --- | --- | --- |
| Scope | One cluster | The whole domain so far |
| Items | 5–8 | 8–15 |
| Relies on | Anything `introduced` or better | Hard items only on **mastered** concepts |
| Evidence | Full weight | Full weight, plus transfer evidence |
| Cadence | End of a cluster | Every 4–6 sessions in a domain |

**Hard items rely only on mastered concepts.** A level-4 or level-5 item may *use* a
concept at mastery ≥ 0.85 as a tool, but must *test* something the learner has practised.
Testing a shaky concept at level 5 measures the shakiness, which the model already knows.

**At least two transfer items.** A transfer item applies a concept in a context the learner
has not met — a different field, a different notation, a real problem. These are what the
mastery bar requires, so an exam is usually where a concept finally becomes `mastered`.

**Interleave deliberately.** Spread items across the domain rather than grouping them by
concept, and include at least two items that need two concepts together. Deciding *which*
idea applies is a separate skill from applying it, and a grouped paper never tests it.

## Running it

Build the blueprint from the index and the whole domain, then use the same handoff template
as `/quiz`, changing:

```text
Kind: exam · 12 items · cumulative · no help during
Blueprint: <spread across the domain; level 4-5 items only on mastered concepts>
Include at least 2 transfer items, on: <concept IDs>
Include exactly one explain-it-simply item, on: <the domain's central concept>
Target expected score: 0.78
Write the paper to: Assessments/2026-11-02-exam-probability.md
Write the key to:    .keys/2026-11-02-exam-probability-key.md
```

Record transfer items with `--transfer` so the mastery bar can be met:

```bash
python3 scripts/tutor.py record bayes-theorem --score 1 --transfer \
    --source "2026-11-02-exam-probability#7"
```

## After an exam

Beyond the quiz's correction round:

- **Report the domain, not the paper.** Which concepts are solid enough to build on, which
  need another pass, and what the exam says about the *order* things were learned in.
- **Re-plan.** An exam is the natural point to revise the plan: recompute the frontier, and
  if a cluster is now ready, propose a project (see `/project`). If a prerequisite turned
  out to be weaker than the graph claimed, say so and fix the graph.
- **Check the graph against the result.** Two misses on concepts the graph called unlocked
  usually means a prerequisite is missing from the graph, not that the learner failed.
  Hand that to the cartographer.

Then close the note and commit, as in `/quiz`.
