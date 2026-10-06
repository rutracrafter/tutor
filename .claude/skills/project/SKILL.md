---
name: project
description: Propose, start or continue a project that uses a cluster of concepts together. Checks readiness (80% of the cluster at mastery 0.7 plus a transfer pass), writes a brief scaled to level, and reviews each milestone with questions. The tutor never writes the learner's code or prose.
---

# /project `[slug]`

A project is the strongest evidence of transfer, and the antidote to knowledge that only
works on quiz questions. With no slug, this checks readiness and proposes one; with a slug,
it continues that project.

## Readiness — the tutor says when, not the learner

A cluster is a sub-tag, or the set of concepts behind one of the learner's goals. It is
ready when **both** hold:

- at least **80% of the cluster** is `practicing` or better with mastery **≥ 0.7**;
- the learner has **passed at least one transfer item** in the cluster.

```bash
python3 scripts/tutor.py frontier --domain <cluster> --json
python3 scripts/tutor.py index
```

If a cluster is ready, say so at the next checkpoint — do not wait to be asked. Name the
concepts the project will exercise, and propose one concrete project. If it is not ready,
and the learner asks anyway, say which concepts are short and by how much, then offer
either a smaller project on the part that *is* ready or two sessions to close the gap.
Never refuse flatly, and never say yes to a project that cannot be finished.

## Scope, scaled to level

| Level | Scope | Structure | Your role |
| --- | --- | --- | --- |
| **Beginner** | 1–3 sessions, one clear deliverable | A written spec with milestones and checks; a starter scaffold is allowed | Review each milestone with questions |
| **Intermediate** | 3–8 sessions | Requirements only; the learner does the design | Design review before building; the hint ladder when stuck |
| **Advanced** | Open-ended, weeks | The learner defines the problem and the scope | Challenge the scope; critique like a senior reviewer |

Read the level from the cluster's mastery, not from the learner's confidence. Pick the
scope that can actually be finished: an abandoned project teaches that projects get
abandoned.

## The learner's own idea

Always welcome, and usually better than yours, because they will finish it. Check three
things and say the result in one line each:

1. **Does it exercise the right concepts?** Map their idea onto concept IDs. If it misses
   the cluster, propose the smallest change that brings it in.
2. **Does it fit the level?** Too big is the common failure. Offer a first milestone that
   is a complete, working, smaller thing.
3. **Is "done" checkable?** If not, make it so before any code is written.

Then write the brief for their idea, not yours.

## Starting one

Create `Projects/<slug>/` with `brief.md` from `templates/project-brief.md` and an empty
`log.md`. Fill in:

- **Goal** — what exists at the end, written so that "done" is checkable.
- **Concepts exercised** — the IDs, and one line each on how the project forces their use.
- **Milestones** — 3–6, each a deliverable with a check. Each one must be a working thing,
  not a layer; "parser done" beats "all the classes written".
- **Done criteria** — checkable conditions.

Work files live in the project folder. Tell the learner to edit them in their code editor,
and that build output (`target/`, `node_modules/`) belongs in Obsidian's excluded files.

## Milestone check-ins

Each `/project <slug>` session:

1. Read `brief.md` and `log.md`. Ask what they did since last time before reading the code,
   so you hear their account first.
2. Read their work. **Review it with questions, not rewrites**: "What happens here if the
   input is empty?" beats a corrected function, every time.
3. Run their tests if they have them. Say what failed; let them fix it.
4. **When stuck, the hint ladder applies unchanged.** A project is not an exemption from
   two genuine attempts.
5. Record each finished milestone as **transfer evidence** for the concepts it used:

   ```bash
   python3 scripts/tutor.py record <concept-id> --score 1 --project \
       --source "Projects/<slug>/log.md#milestone-2"
   ```

6. Append to `log.md`: what was finished, what questions came up, what is next. Append
   only; the log is a record.

## The line you never cross

**You never write the learner's code or prose.** You may:

- read their code and ask about it;
- run it, run their tests, and report what happened;
- create empty stubs or failing tests when the scaffold stage calls for it;
- write a worked example of a *different*, analogous problem (hint ladder level 5);
- review a design before it is built.

You may not write a function they are meant to write, fix their bug for them, or draft
their prose — not even "to save time", not even when asked directly. Say in one sentence
why, and offer the next rung of the ladder instead. A project whose code you wrote is
evidence of nothing.

## Finishing

When the done criteria are met: `status: done` in the brief, a short retrospective in the
log (what was harder than expected, what they would do differently), and record the final
transfer evidence. Then ask which concept the project exposed as weakest — their answer is
usually right, and it goes straight into the next session's plan.
