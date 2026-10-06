# Personal Tutor Agent: Overview & Build Plan (v2)

Oct 6, 2026 · @Artur

This version works through all 19 comments on v1 and the 5 on its own first draft. The biggest change is that the repo is now an engine you point at any vault or folder, not the vault itself.

## TL;DR

The tutor is a git repo of plain Markdown (agent prompts, skills, templates, a guard hook and a small bookkeeping script) that you clone anywhere and point at a learning folder inside any Obsidian vault. You start `claude` in the repo, the `tutor` agent (Opus 5.5) takes over the session, and it reads and writes your notes in that folder. Three cheaper subagents (Sonnet, Sonnet, Haiku) build concept graphs, run assessments and keep the records. Everything bills to your subscription through interactive Claude Code; no API key and no framework.

The teaching follows the research: practice pitched at about 80–85% success, answers you produce rather than recognise, hints only after genuine attempts, spaced retrieval at the start of every session, and projects once a cluster of ideas is ready to be used together. Quizzes and exams exist to teach, not to score you.

The learner model is one shared, cross-subject concept graph: one note per concept, domains as tags rather than folders, and history that is never edited. Each session loads a small working set from it instead of the whole graph, so the context cost stays flat over years of use.

## What changed from v1

Each of your comments, the change it led to, and where to find it.

| Your comment | Change | Section |
| --- | --- | --- |
| The repo must not be the vault | Engine repo and data folder are separate; a `/setup` skill links them | Architecture |
| Visualisations, LaTeX, code blocks | Explicit formatting rules plus a `visualize` skill (Mermaid, SVG) | Tutor voice and output |
| Tell me when I'm ready for a project | Project readiness rule, scope scaled to level, `/project` skill | Assessments and projects |
| Concise, not wordy, not terse | Voice rules in the tutor prompt; a verbosity setting in your profile | Tutor voice and output |
| Retrieval should include producing, not only recalling | "Produce, don't recognise" rule for all practice | Pedagogy |
| Feynman-style questions | Explain-it-simply items, with a gap-finding follow-up | Pedagogy; Assessments |
| The prerequisite graph helps the student too | Generated Mermaid map per domain, coloured by stage | Knowledge graph |
| The frontier must grow | Frontier recomputed at every `/wrap`; the graph is extended when it runs out | Knowledge graph |
| Will this scale over years? | A small working set per session instead of the whole graph; capped evidence; optional script | Knowledge graph |
| Links across subjects | One shared graph; prerequisites may cross domains; reuse before create | Knowledge graph |
| Don't change historical data | Closed notes are locked by a hook script; concept history is append-only | Knowledge graph |
| Splitting a broad domain | Domains are nested tags, not folders, so a split is a retag | Knowledge graph |
| Timing, review-only days, `/wrap`, fresh context | Time budget at start, real clock checks, four session types, wrap anytime, one Claude Code session per learning session | Sessions |
| Your influence over the plan; typing in the terminal | Checkpoints with "continue" as the default; terminal text is logged into the note | Sessions |
| What counts as a genuine attempt | Explicit definition and what happens otherwise | The practice loop |
| Watcher reliability | Opt-in only, Enter always works, a pass/fail reliability test | The practice loop |
| Avoid a purely academic, score-first approach | Assessments framed as learning events; scores are internal | Assessments and projects |
| Dashes in filenames | All filenames use dashes | Repo layout |
| The tutor must brief the examiner | The handoff contents are spelled out | Assessments and projects |
| Where code files go | A `Workspaces/` folder in the data folder | Repo layout |

**Round 2: comments on the first v2 draft.**

| Your comment | Change | Section |
| --- | --- | --- |
| Can I edit my previous answers? | Yes, but grades live in concept logs, you revise below rather than overwrite, and git shows later edits; hard locking is optional | Knowledge graph |
| Git as a read-only record | Now standard: `/wrap` commits the data folder; `/setup` detects or creates the repo | Knowledge graph |
| The script saves usage and context | `tutor.py` is now in the core build, with the scribe as fallback | Knowledge graph; Build plan |
| README as the user guide; nested repos | Four-part README; engine cloned outside the vault, or into an ignored dot-folder | Repo layout |
| Defaults approved | Section renamed "Settings and defaults" | Settings and defaults |

## Running on your subscription

The verdict is unchanged from v1: use interactive Claude Code. It is the route Anthropic explicitly keeps on your plan's usage limits ([help article](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan)), and it already provides everything a harness would: a replaceable system prompt, file and web tools, subagents with a per-agent model, slash-command skills and hooks.

| Route | What it costs today | Verdict |
| --- | --- | --- |
| Interactive Claude Code (`claude` in a terminal) | Your plan's usage limits; subagents draw from the same limits | **Use this** |
| `claude -p` or the Agent SDK from your own script | Plan limits for now; a move to a separate monthly credit was announced, then paused on June 15 | Avoid as the core |
| Pi or another third-party harness on your login | Routed to pay-per-token extra usage since April 4, 2026 ([write-up](https://dev.to/spksoft/using-your-claude-subscription-in-pi-agent-at-your-own-risk-5h1j)) | Skip |
| Any harness with an API key | Pay per token | Not what you want |

Claude Code's terms reserve subscription login for ordinary use of Claude Code and Anthropic's apps ([legal and compliance](https://code.claude.com/docs/en/legal-and-compliance)); a personal tutor you run yourself inside Claude Code fits that. Because every part of the design is plain Markdown, it ports to Pi or the SDK later if the policy changes.

## Architecture

Three parts, kept apart on purpose: an engine repo that anyone can clone, a Claude Code session started inside it, and a data folder in your own vault. The tutor makes every teaching decision; subagents get self-contained jobs and return short results it checks.

&#91;embedded content: architecture · engine repo, session, data folder\]

The session loads its prompts, skills and guard hook from the engine, and reads and writes only your data folder, which Obsidian shows as ordinary notes.

- **Engine and data never mix.** The repo stays generic and shareable, and `git pull` updates it safely. Your notes stay in your vault, under your own sync or backup. `/setup` links the two once (see Repo layout).
- **Tools are Claude Code's built-ins**: file read, write and edit, search, web search and fetch for checking facts, and bash for the guard hook, git and the bookkeeping script. There is no custom tool code; the system's "tools" are its file conventions and skills.
- **Why subagents.** Each runs in its own context with its own prompt, tools and model, and returns only a summary, so routine work doesn't crowd out the lesson. They draw on the same plan limits, which is why they run on cheaper models.
- **What stays with the tutor**: choosing the next question, giving hints, honouring or questioning your steering, and stepping difficulty up or down. Those need the whole lesson in view and the strongest model.

## Pedagogy

Each research finding becomes a rule in the tutor's prompt. The central warning comes from a field experiment with nearly 1,000 students: an unrestricted GPT-4 helper raised practice grades but left students worse off once it was removed, while a version with tutoring guardrails largely avoided that harm ([Bastani et al., PNAS 2025](https://www.semanticscholar.org/paper/Generative-AI-without-guardrails-can-harm-learning:-Bastani-Bastani/60570ad3268871882c65f6ed4ead35db4b220528)).

| Principle | What the research says | Rule in the tutor |
| --- | --- | --- |
| Just-right difficulty | Across a broad class of learning algorithms, learning is fastest at about 85% accuracy ([Wilson et al. 2019](https://www.nature.com/articles/s41467-019-12552-4)). It was derived for simple two-choice tasks, so it is a target band, not a law | Track success over the last 6–8 practice items. Above 90%: harder variant or less scaffolding. Below 70%: worked example, smaller step or a prerequisite. Aim for 80–85% |
| Guardrails, not answers | Unguarded AI help harmed later performance; the guarded tutor mitigated it ([Bastani et al.](https://www.researchgate.net/publication/393011815_Generative_AI_without_guardrails_can_harm_learning_Evidence_from_high_school_mathematics)) | The hint ladder; no solution before two genuine attempts; hints used lower the credit for that item |
| Teach explicitly, by design | A GPT-4 tutor built on the same best practices as an active-learning class produced more learning in less time than the class ([Kestin et al. 2025](https://www.nature.com/articles/s41598-025-97652-6)) | The prompt spells out lesson structure, check-ins and feedback style instead of leaving them to the model's defaults |
| Retrieval and spacing | Practice testing and distributed practice rated high utility among ten study techniques; rereading and highlighting rated low ([Dunlosky et al. 2013](https://www.kent.edu/psychology/all-study-strategies-not-created-equal-according-kent-state-researchers)) | Every session opens with due reviews; reviews follow expanding intervals; summaries are always yours |
| Fade the scaffolding | Worked examples help novices but become redundant or harmful as expertise grows; gradual fading works best ([expertise reversal](https://link.springer.com/article/10.1007/s11251-009-9102-0)) | Each concept carries a scaffold stage: worked → completion → independent → transfer, moving one step at a time |
| Map prerequisites | Math Academy places students with an adaptive diagnostic on a prerequisite graph and counts practice on advanced topics partly toward the simpler ones they use ([how it works](https://www.mathacademy.com/how-our-ai-works)) | A concept graph; new material only at your frontier; success on a concept gives partial review credit to its prerequisites |

Three rules come from your comments, building on the same findings.

**Produce, don't recognise.** Retrieval means producing the thing: deriving the result, writing the proof, sketching the algorithm, explaining the mechanism. Recognition formats such as multiple choice are kept for quick checks only. A review item on Bayes' theorem asks you to derive it from the definition of conditional probability and apply it to a case, not to pick the formula from a list.

**Explain it simply (Feynman items).** Regularly, and always at wrap-up, you get a prompt such as "Explain why the borrow checker forbids two mutable references to someone who knows Python but not Rust." You answer in free text. The tutor checks accuracy, completeness, plain language and whether you used a concrete example, then asks one or two follow-ups aimed at the vaguest part. A vague spot usually marks a gap in understanding, not a gap in wording.

**Use it for real (projects).** When a cluster of related concepts is solid, the tutor proposes a project that needs them together. This is the strongest evidence of transfer, and the antidote to learning that only works on quiz questions (details under Assessments and projects).

## Tutor voice and output

Spell both out in the prompt. Strong models often do these things unprompted, but not consistently, and an explicit rule costs a few lines.

**Voice: concise, never terse.** These rules go in `tutor.md`:

- Lead with the point, then support it. Say each thing once; restate only to connect it to something new.
- No filler: no praise padding, no "Great question!", no recap of what you just wrote.
- Prefer one concrete example to two abstract sentences.
- Use complete sentences, and define each term the first time it appears.
- When unsure, lean slightly fuller rather than shorter. Clipped, note-style replies are for advanced learners who ask for them.

Your profile carries `verbosity: standard` (default) or `brief`, and you can say "shorter" or "more detail" at any checkpoint. The tutor treats that as a standing preference and records it in the profile.

**Math and code.** Obsidian renders LaTeX and code blocks natively, so the prompt requires:

- Inline math in `$…$`, display math in `$$…$$`, never Unicode imitations such as x² or ∑.
- Every code sample in a fenced block with its language tag; the tutor never writes code inline in prose.
- Tables for comparisons; never a wall of bullets.

**Visualisations.** A `visualize` skill tells the tutor when a picture beats prose (structure, process, geometry, a function's shape, data) and how to draw it in a way your notes can hold:

- **Mermaid** in a fenced `mermaid` block for flowcharts, state machines, sequence diagrams, trees and graphs. Obsidian renders it in place, and it stays editable text.
- **SVG** written by hand for geometry, vector diagrams and annotated figures, saved to `Assets/` with a dashed filename and embedded with `![[file.svg]]`.
- **Plots from data or functions**: Python with matplotlib to a PNG, only if you have Python installed (optional, Phase 4).

The skill carries a short list of common Mermaid syntax mistakes and a size limit (around 15 nodes per diagram). The tutor cannot see Obsidian's render, so if a diagram breaks, write "broken" in your answer slot and it repairs or simplifies it.

## Knowledge graph and learner model

There is one graph for everything you learn: one note per concept, a stable dashed ID as the filename, domains as nested tags instead of folders, and an append-only log of how each estimate changed. Each session loads a small working set from this graph rather than the whole thing, so the cost per session stays roughly constant however large it grows.

A concept note, `Concepts/bayes-theorem.md`:

```markdown
---
id: bayes-theorem
aliases: ["Bayes' rule"]
tags: [math/probability, ml/foundations]
requires: ["[[conditional-probability]]", "[[law-of-total-probability]]"]
related: ["[[naive-bayes-classifier]]"]
stage: practicing        # unseen | introduced | practicing | mastered
scaffold: completion     # worked | completion | independent | transfer
mastery: 0.62
evidence_count: 7
last_seen: 2026-10-05
next_review: 2026-10-12
interval_days: 7
misconceptions: ["swaps P(A|B) and P(B|A)"]
---
Objective: derive Bayes' theorem and apply it to base-rate problems.

## Log
- 2026-10-03 · [[2026-10-03-quiz-probability#3]] · 0.48 → 0.55 · correct, 1 hint
- 2026-10-05 · [[2026-10-05-probability#Q4]] · 0.55 → 0.62 · correct
```

**Domains are tags, so splitting one is a retag.** Filenames never contain a domain, so nothing moves and no link breaks when the structure changes. Start broad (`math`) and refine to `math/probability` when needed; in Obsidian, searching the parent tag also finds its nested tags. When a domain passes about 60 concepts, or you start focusing on one part of it, `/reorganize math` has the cartographer propose sub-tags. You approve the proposal and the scribe edits only the `tags` lines. A concept can carry several tags at once, which is how one note belongs to both statistics and machine learning. When the same word means different things in two fields, the IDs say which: `normal-distribution` and `surface-normal`.

**One graph across subjects, so your statistics counts in ML.** Prerequisites may cross domains: `logistic-regression` can require `maximum-likelihood-estimation`. Mastery belongs to the concept, not the course, so the tutor won't re-teach statistics you hold; using it inside an ML problem gives it review credit. The cartographer's prompt says **reuse before create**: it searches existing IDs, aliases and objectives before drafting a new concept. Same idea under a new name or notation becomes an alias plus a one-line notation bridge. Analogies across fields go in `related`. Keep everything in one graph; separate graphs per subject would lose exactly these links.

**The frontier grows as you do.** It is recomputed at every `/wrap`. A concept joins it once every prerequisite is at least `practicing` with mastery ≥ 0.6. Prerequisites don't need full mastery to unlock what follows, or progress would stall, but an exam only relies on mastered ones. When the frontier reaches the edge of the graph drafted so far, the cartographer extends it one layer further, guided by your goals. A goal can also pull the graph forward: "I want to understand transformers" makes it draft a path backwards from that goal to concepts you already hold.

**A map for you too.** `/wrap` regenerates `Maps/<domain>.md`: a Mermaid graph coloured by stage, with the frontier outlined. Large domains show only the frontier and two hops around it, about 40 nodes. Obsidian's graph view of `Concepts/` gives the full picture. The tutor uses the same map to show why today's topic matters: the path from it to your goal.

**History is never rewritten.** Evidence you can't trust is worse than no evidence, so this is enforced in code, not just requested:

- `/wrap` marks session and assessment notes `status: closed`. A small hook script in the repo runs before every Edit or Write and blocks any change to a closed note. Exit code 2 stops the tool call and tells the agent why ([hooks in the subagents docs](https://code.claude.com/docs/en/sub-agents)). Every agent prompt also states the rule.
- While a session is open, agents only append, and never touch your answer blocks.
- In concept notes the frontmatter is the current estimate and may change; the `## Log` is append-only. A regrade is a new log line, not an edit.
- Standard: keep the data folder under git, committed by /wrap after every session (details below).

**Your own edits.** You can edit anything in Obsidian; it is your notebook, and locking you out would mean fighting the editor. The risk is quiet drift: an answer improved after grading makes the record claim you knew something you didn't. Three rules keep the record trustworthy without locking you out:

- **The model never re-reads old answers as evidence.** Each grade is written to the concept's log at grading time, and mastery is computed only from those log lines, so editing an answer afterwards cannot change it.
- **Revise below, don't overwrite.** To improve an answer during a session, add a `Revised:` line under the original. The tutor treats it as a new attempt, which is also better practice than silently fixing the first one.
- **Changes after closing are visible.** Every `/wrap` commits the data folder to git, so any later change to a closed note shows in the diff, and `/learn` warns you if a closed note has changed since its commit.

Hard locking is available but off by default: `/wrap` can mark closed notes read-only at the file-system level, so edits to them won't save. Some sync services handle read-only files badly, so turn it on only if your setup copes.

**Git as the read-only record.** `/setup` checks whether the data folder already sits inside a git repository, such as a vault you sync with git:

- **If it does,** the tutor commits only paths under the data folder to that repository, with messages prefixed `tutor:`. It never pushes, rebases or touches other files.
- **If it doesn't,** `/setup` offers to run `git init` in the data folder.

`/wrap` then commits after every session, for example `tutor: wrap 2026-10-06-probability`. You get the full history of every note, an undo for any agent mistake, and a diff of anything edited afterwards. The engine's settings pre-approve only `git add` and `git commit`, so this doesn't prompt you each time. If a commit fails because another tool, such as the Obsidian Git plugin, holds git's lock at that moment, `/wrap` retries once and otherwise tells you.

**Mastery and reviews.** These rules are unchanged from v1:

- After each graded item, mastery moves 30% of the way toward the item's score: 1, 0.5 or 0, minus 0.25 per hint level used.
- A concept counts as `mastered` at ≥ 0.85, with at least 3 observations across 2 sessions, including a transfer item or a project.
- Review intervals run 1, 3, 7, 16 and 35 days, then double. A miss resets the interval to 1 day.
- A correct answer also pushes each direct prerequisite's next review half a step later.

**Diagnosis for a new topic.**

1. The cartographer drafts the graph, linking it to concepts you already have.
2. The tutor probes adaptively with 8–15 short questions, each with a confidence rating from 1 to 5, skipping concepts the graph already shows you hold.
3. A confident wrong answer is logged as a misconception.
4. Concepts inferred as "probably known" get an early review, so a wrong inference is caught within days.

**Scaling to years of use.** Agents read frontmatter by searching, never whole folders, and each session note opens with a summary of five lines or fewer. The figures below are illustrative, for about three years of steady study.

| What grows | Rough size after \~3 years | What a session actually reads |
| --- | --- | --- |
| Concept notes | \~2,000 | Frontmatter of 20–60: due reviews (capped at 15), today's frontier, and neighbours of today's concepts |
| Concept logs | Dozens of lines each | Only when diagnosing a specific concept |
| Session notes | \~600 | Summary of the last session in today's domain |
| Assessment notes | \~150 | Only the one in its correction round |
| `Learner/index.md` | One line per domain | The whole file, under \~1,000 tokens |

The weak spot at scale is reliability and model usage, not context: a model searching hundreds of files for due dates is slower, costlier and more error-prone than a script. So a small Python script, `tutor.py` (standard library only), is part of the core build. It does all the deterministic bookkeeping, with no model involved:

- `due`, `frontier` and `index` read frontmatter and print the due list, the frontier and the index.
- `record <concept> <score> <hints>` applies the mastery and review-interval rules and appends the log line.
- `maps` regenerates the Mermaid maps.
- `check` lists closed notes changed since their last commit.

The scribe is left with judging and summarising, which is what a model is for. If Python 3 isn't installed, the scribe falls back to doing the bookkeeping itself: slower and costlier, but it works.

## Sessions

One learning session is one fresh Claude Code session. You pick a type and a time budget, the tutor checks the real clock, you steer at checkpoints, and `/wrap` closes things cleanly at any moment.

| Command | Use it when | Length | What happens |
| --- | --- | --- | --- |
| `/learn <topic> [30m]` | Normal study | Your budget, usually 30–60 min | Full structure, scaled to the time you have |
| `/review` | Short on time | 10–15 min | Due reviews plus one explain-it-simply item; no new material |
| `/quiz`, `/exam` | An assessment is due, or you want one | 15–45 min | See Assessments and projects |
| `/project` | Working on a project | Open | Milestone check-in and review of your work |
| `/wrap` | Any time | 2–5 min | Summarises, updates the model, closes the note |

**Time is measured, not guessed.** The tutor asks for your budget (or reads it from `/learn rust 30m`), takes the start time from the system clock and checks it again at each phase boundary. Phase lengths are shares of your budget, not fixed minutes:

1. Warm-up retrieval, \~15%: due reviews from older concepts, produced from memory.
2. New idea, \~25%: a prediction question first, then the explanation in chunks, each followed by an explain-back or "why" question.
3. Guided practice, \~35%: worked or partly worked examples fading to full problems, with the hint ladder.
4. Independent practice, \~15%: no scaffolding, a new context, older concepts mixed in.
5. Wrap-up, \~10%: an explain-it-simply prompt, your own summary, then `/wrap`.

Running late, the tutor cuts new material first and never the warm-up or the wrap-up. With about 5 minutes left it moves to the wrap-up. Given a budget under 20 minutes, it suggests `/review` instead. A concept new to you tilts the time toward step 2; one you partly know tilts it toward steps 3 and 4.

**You steer at checkpoints; doing nothing means "continue".** The tutor proposes a short plan at the start and adds a checkpoint after each phase:

```markdown
> [!checkpoint] Next: guided practice on bayes-theorem, 3–4 problems
> - [ ] More practice on what we just did
> - [ ] Go deeper on something (say what)
> - [ ] Something else (write below)
> Leave everything unticked to continue as planned.
```

You set goals and emphasis; the tutor keeps the evidence and the prerequisites honest:

- **"More practice on X"** is always granted.
- **"Go deeper on Y"** is granted if you hold Y's prerequisites. If not, the tutor shows what's missing and offers a short detour.
- **"Skip this, I know it"** gets two quick check items instead; pass them and it is skipped, with credit.
- **A tangent** is parked in a "Parking lot" section at the bottom of the note and offered at wrap-up, or added to the graph for later.

You can also steer between checkpoints by writing in a `> [!steer]` callout.

**What you type in the terminal is never lost or misread.** Pressing Enter, or typing a single `.`, means "read the note". If you type more, the tutor sorts it before acting:

- An answer is copied word for word into the current answer slot, marked "(typed in terminal)", and handled as usual.
- A steering request is logged under the current checkpoint.
- A question is answered in the note.

`CLAUDE.md` states that the note is the source of truth, so nothing lives only in chat.

**A fresh Claude Code session for each learning session.** Run `claude` anew, or `/clear` an open session. All continuity lives in files: your profile, the index, the maps and the last session's summary. A fresh context keeps each session cheap and avoids drift from a long chat. If a long session fills up, Claude Code compacts it automatically and the note is unaffected.

**`/wrap` works at any moment.** It records only what actually happened:

1. Writes the five-line summary at the top of the note.
2. Updates concepts with the evidence collected.
3. Lists unfinished plan items under "Carry over" for next time.
4. Regenerates the maps, marks the note closed and commits the data folder to git.

If you close the terminal without wrapping, the next `/learn` finds the open note (`status: open`) and wraps it first from its contents, so no evidence is lost.

## The practice loop

Every practice item runs the same loop. A correct answer is followed by "why does that work?", a genuine wrong attempt earns one more level of hint, and a non-attempt earns an easier step, never a hint.

&#91;embedded content: practice loop · 2 decisions, 3 loops\]

The tutor only ever moves one hint level per turn, so help grows in proportion to the effort you show.

**What counts as a genuine attempt.** The tutor judges the content, never the length or the time taken. An attempt is genuine if it contains at least one of:

- a committed answer, even a wrong one
- a step of work, a plan, or a named rule or concept you think applies
- a specific point of confusion: "I see why X, but not why Y"

These are not genuine: a blank, "idk", restating the question, or a bare guess where reasoning was asked for. An honest "I don't know where to start" is fine and isn't penalised. It gets a smaller sub-question that you can answer, rather than a hint toward the original. Several non-attempts in a row prompt a check-in on whether the level is wrong or you're tired, with an easier level, a break or `/wrap` on offer.

**A turn in the note.**

```markdown
## Q4 · bayes-theorem · level 3 · scaffold: completion
> [!tutor]
> A test is 99% accurate and the disease affects 1 in 1,000 people.
> Before calculating, predict roughly how likely a positive result is
> to be correct, then derive the exact value.

> [!answer] Your answer
> 
```

The tutor only appends `[!tutor]` blocks; you only write inside `[!answer]` slots. Its chat reply stays one line, such as "Q5 is up".

**The hint ladder.** One level per turn, a genuine attempt between levels, and every level used is logged against the item:

1. Ask first: "What have you tried so far?"
2. Metacognitive prompt: restate the goal and what you already know.
3. Conceptual nudge: point at the relevant principle, without steps.
4. Next-step hint: only the very next step.
5. Analogous worked example: a different problem with the same structure.
6. Walk-through: the solution step by step, with you explaining each step back. It counts as a miss, and a similar item is queued for later.

**The optional submit watcher, made safe.** Ticking a `- [ ] Submit` box in Obsidian instead of pressing Enter is worth trying only if it never makes the system less reliable. Guardrails:

- Opt-in, and Enter always keeps working, even with the watcher on.
- It triggers only on a ticked Submit line, then waits about 2 seconds for Obsidian's autosave to finish.
- Pickup is idempotent: after processing, the tutor rewrites that line to `Submitted 14:32`, so a second trigger is ignored.
- It is a plain polling loop on the file's modification time in bash or PowerShell, with nothing to install, started through Claude Code's Monitor tool. The tutor wakes only when the script prints a line, so waiting should cost little; check this in `/usage` during the test.
- Background monitor tasks are not restored when a session is resumed ([docs](https://code.claude.com/docs/en/scheduled-tasks)), so `/learn` re-arms the watcher at session start. If it ever dies, nothing happens and you press Enter.

It ships only after passing a test: 30 submits across 3 sessions with no missed and no duplicate pickups. Otherwise Enter stays the only method.

## Assessments and projects

Assessments are learning events, not grading events: every item exists to make you think, and its result decides what you practise next. Scores are internal steering signals.

**Learning over scores.** Five rules keep this from turning into test-taking:

- Feedback leads with what you understood and the single most important gap, then asks a question that makes you find the error yourself.
- No percentage headline. Results show per concept as solid, shaky or gap, each with its next action. Raw numbers stay in the frontmatter, and your profile can turn them on (`show_scores: false` by default).
- Every assessment ends with a correction round and a "what next" line that feeds the next session's plan.
- Moving a quiz is free and never lowers mastery.
- There are no retakes of the same paper. Misses come back later as review items in new forms, so memorising answers doesn't help.

| Kind | When | Size | Help during | Weight in the model |
| --- | --- | --- | --- | --- |
| Check for understanding | Every few minutes in a lesson | 1 item | Hint ladder | Half |
| Quiz | End of a concept cluster, or a review day | 5–8 items | None; correction round after | Full |
| Exam | Milestone, about every 4–6 sessions in a domain | 8–15 items, cumulative | None | Full, plus transfer evidence |
| Project | When a cluster is ready (below) | Milestones over 1+ sessions | Questions and design review | Strongest transfer evidence |

**Item types that make you produce.** The main types are derive or prove, implement, predict-then-explain, find the bug or flaw, compare two approaches, apply to an unfamiliar case, and explain it simply. Each item asks for a confidence rating from 1 to 5. Multiple choice is kept for quick checks, with every wrong option mapped to a known misconception.

**Difficulty.** Items carry a level: (1) recall, (2) apply in a familiar format, (3) apply in a new context, (4) analyse, compare or debug, (5) explain, design or transfer. A paper puts about two-thirds of its items at your current level, a quarter one level above and a tenth on older concepts. It only touches concepts you have at least been introduced to, and aims for an expected 75–85%.

**What the tutor hands the examiner.** A subagent starts fresh: it sees only its own prompt, the `CLAUDE.md` files and the tutor's delegation message, never the conversation ([subagents docs](https://code.claude.com/docs/en/sub-agents)). So the `/quiz` skill gives the tutor a fixed handoff template:

- **To write a paper:** purpose; blueprint (concept IDs, levels, item counts); each concept's mastery, scaffold stage and known misconceptions; item types to favour; the target expected score; output paths for the paper and the key.
- **To grade:** paths to the paper, the key and rubric, and your answers, and nothing else. The data-folder path reaches the examiner automatically through `CLAUDE.local.md`.
- **It returns per item:** score, misconception tag, how sure it is of the grade, and a one-line rationale.

**How a quiz runs.**

1. The examiner writes the paper into `Assessments/`; the key goes to `.keys/`, hidden from Obsidian.
2. You answer in the note and hand back the turn.
3. The examiner grades blind against the rubric, and the tutor rechecks any grade marked uncertain.
4. In the correction round, each miss gets a question pointing at your error. Fixing it yourself earns half credit. Only then do you see a model solution, which you explain back.
5. The scribe updates mastery and the review schedule, and the note closes.

**Projects: the tutor tells you when you're ready.** A cluster of concepts (a sub-tag, or the set behind one of your goals) is ready when at least 80% of it is `practicing` with mastery ≥ 0.7 and you have passed a transfer item in it. The tutor then says so at a checkpoint, names the concepts the project will exercise and proposes one. You can accept it, swap in your own idea (the tutor checks that it uses the right concepts and fits your level), or put it off.

| Level | Scope | Structure | Tutor's role |
| --- | --- | --- | --- |
| Beginner | 1–3 sessions, one clear deliverable | Written spec with milestones and checks; a starter scaffold is allowed | Reviews each milestone with questions |
| Intermediate | 3–8 sessions | Requirements only; you do the design | Design review before you build; hint ladder when stuck |
| Advanced | Open-ended, weeks | You define the problem and scope; the tutor challenges them | Critiques like a senior reviewer |

A project lives in `Projects/<slug>/` with a `brief.md` (goal, concepts exercised, milestones, done criteria), a log and your work files. The tutor never writes your project's code or prose, though it may run your tests. Each finished milestone counts as transfer evidence for the concepts it used.

## Repo layout and file formats

The repo holds only the engine and is identical for every user; your learning data lives in a folder you choose, usually inside an existing Obsidian vault. `git pull` updates the engine without touching your data.

The engine repo, cloned anywhere:

```text
tutor/
├── README.md                  # the user guide (see below)
├── CLAUDE.md                  # conventions, turn protocol, "the note is the source of truth"
├── CLAUDE.local.md            # written by /setup: path to your data folder (gitignored)
├── .gitignore                 # CLAUDE.local.md, .claude/settings.local.json
├── .claude/
│   ├── settings.json          # {"agent": "tutor"} + hook registration
│   ├── settings.local.json    # written by /setup: additionalDirectories (gitignored)
│   ├── agents/                # tutor.md, cartographer.md, examiner.md, scribe.md
│   ├── skills/                # setup, learn, review, quiz, exam, project, wrap,
│   │                          # diagnose, reorganize, visualize
│   └── hooks/                 # protect-closed-notes.sh (+ .ps1 for Windows)
├── templates/                 # session, concept, assessment, project-brief, map, profile
└── scripts/                   # tutor.py: deterministic bookkeeping (Python 3 stdlib)
```

Your data folder, for example `MyVault/Learning/`:

```text
Learning/
├── Learner/        # profile.md, index.md
├── Concepts/       # bayes-theorem.md, conditional-probability.md, …
├── Maps/           # math-probability.md, …  (one per domain tag)
├── Sessions/       # 2026-10-06-probability.md
├── Assessments/    # 2026-10-06-quiz-probability.md, 2026-11-02-exam-probability.md
├── Projects/       # <slug>/brief.md, log.md, your work files
├── Workspaces/     # code exercises: rust-borrowing/2026-10-06-q4/main.rs
├── Assets/         # svg and png figures
└── .keys/          # answer keys and rubrics, hidden in Obsidian
```

**Linking the two.** `/setup` asks for the data folder's path, creates the skeleton there from `templates/` if it is empty, and writes two gitignored files. `CLAUDE.local.md` holds the path, and it loads into the tutor and every subagent automatically. `.claude/settings.local.json` lists the folder under `additionalDirectories`, which grants file access outside the repo ([Claude Code docs](https://code.claude.com/docs/en/large-codebases)). Rerun `/setup` to switch between data folders. A plain folder outside Obsidian works too; callouts, wikilinks and the graph view simply show as text.

**Install the engine inside the vault, in a hidden, git-ignored folder.** The recommended layout:

```text
MyVault/
├── .gitignore          # contains the line: .tutor-engine/
├── .tutor-engine/      # the engine repo, hidden from Obsidian
├── Learning/           # your data folder
└── …                   # your other notes
```

This keeps everything for one vault together and avoids the problems of an engine in plain sight:

- **No nested-repo trouble.** If the vault is a git repo, its `.gitignore` excludes the engine folder, so the vault's git never sees the engine's repository. The engine updates with its own `git pull`.
- **No clutter.** Obsidian ignores folders whose names start with a dot, so the engine's Markdown stays out of search and the graph view.
- **Simpler setup.** `/setup` can default the data folder to `../Learning`, right beside it.

The dot matters more than the name, but a specific name such as `.tutor-engine` avoids clashing with other tools' hidden folders.

Clone the engine outside the vault instead (for example to `~/tools/tutor`, with `/setup` pointing at the vault) in two cases:

- **The vault lives in a sync service that copies everything,** such as iCloud Drive, Dropbox or OneDrive. It would also sync the engine's `.git` folder, which can be corrupted when two devices write at once.
- **You want no tool files in the vault at all.**

Either way, check one thing: Claude Code also loads `CLAUDE.md` files from folders above the one it starts in. If your vault root has its own `CLAUDE.md`, it joins the tutor's context, so make sure it doesn't conflict, or exclude it with the engine's `claudeMdExcludes` setting.

**Filenames.** Lowercase, dashes, no spaces: `YYYY-MM-DD-<topic>.md` for sessions, `YYYY-MM-DD-quiz-<topic>.md` for quizzes, and the concept ID for concepts. Unique dashed IDs also keep wikilinks unambiguous inside a vault that holds other notes.

**Where code goes.** Exercises live in `Workspaces/<topic>/<date>-<item>/`, linked from the session note. Project code lives in its project folder. You edit these in your code editor: Obsidian only lists non-Markdown files if "Detect all file extensions" is on, and build output such as `target/` or `node_modules/` belongs in Obsidian's "Excluded files". The tutor may create empty stubs or failing tests when your scaffold stage calls for them, and may run your code and tests, but it never writes the solution.

**The tutor prompt, in outline.**

```markdown
---
name: tutor
description: Personal teacher. Runs every session.
model: opus
tools: Read, Write, Edit, Glob, Grep, Agent, Skill, WebSearch, WebFetch, Bash
---
You are my teacher. Your goal is my durable understanding, not my output.

Non-negotiables
- No solution before two genuine attempts; follow the hint ladder.
- Keep practice success near 80–85%; adjust difficulty and scaffolding.
- Teach only at my frontier; check prerequisites first.
- The session note is the source of truth; chat replies stay one line.
- Append only. Never edit my answers or any closed note.
- Verify facts before teaching them; search and cite when unsure.

Voice: lead with the point, say it once, no filler; fuller rather than terse.
Formatting: $…$ and $$…$$ for math, fenced code with a language tag,
Mermaid or SVG when a picture beats prose (see the visualize skill).
```

Subagents use the same shape with a cheaper model and narrower tools. The scribe gets `model: haiku` and file tools only. The examiner's prompt states that it works only from the handoff, the paper, the key and your answers.

**`README.md` is the user guide.** It teaches both how to use the system and how it works, in four parts:

| Part | What it covers |
| --- | --- |
| Header | What the tutor is and does, the principles behind it in a few lines, and what it is not: an answer machine |
| Installation | Prerequisites (Claude Code with your Claude login, Obsidian, optionally Python 3 and git); installing the engine into a hidden, git-ignored .tutor-engine/ folder in the vault (or outside it, for cloud-synced vaults); running `/setup`; checking that it worked |
| Quick start | A first session in five minutes: `/learn <topic>`, the note and the terminal side by side, answering in `[!answer]` slots, Enter to hand back the turn, checkpoints, `/wrap` |
| Manual | Every command and its options; session types and time budgets; steering; genuine attempts and the hint ladder; assessments and projects; the graph, maps and domains; profile settings and their defaults; history, git and editing your own notes; updating the engine; troubleshooting |

The README is written alongside the build (see the build plan) and checked against the finished system in Phase 5, so the manual describes what the system actually does.

## Build plan

There are six phases, and each ends with a test you run in a real session; you can stop after any one and still have something that works. Everything except the guard hook and the bookkeeping script is Markdown or JSON.

### Phase 0: Engine and setup

- [ ] Install Claude Code; log in with your Claude account (not an API key)
- [ ] Create the engine repo skeleton, `.gitignore` and `.claude/settings.json` with `"agent": "tutor"`
- [ ] Write the `/setup` skill: ask for the data path, create the data skeleton, write `CLAUDE.local.md` and `settings.local.json`, then detect or create the git repo
- [ ] Write `templates/` (session, concept, profile) with dashed filename patterns
- [ ] README: Header and Installation

Test: following only the README's Installation steps, from a fresh clone into the vault's .tutor-engine/ folder, `/setup` links a data folder, and `claude` shows `@tutor` and can read that folder.

### Phase 1: Tutor and live sessions

- [ ] `tutor.md`: non-negotiables, voice, formatting, lesson structure, hint ladder, genuine-attempt rule
- [ ] `CLAUDE.md`: turn protocol, the note as source of truth, how terminal text is handled
- [ ] `/learn` with time budget, clock checks and checkpoints; `/wrap` with summary and carry-over
- [ ] Open-note recovery: `/learn` wraps a forgotten open session first
- [ ] The `Revised:` convention in the session template
- [ ] README: Quick start

Test: a 30-minute session with one steering request, one answer typed in the terminal and one early `/wrap`; the note contains everything and no answer was given away.

### Phase 2: Graph, memory and the history guard

- [ ] `cartographer` and `scribe` agents; `/diagnose` and `/reorganize`
- [ ] Concept template with tags, aliases, `requires`, `related` and the append-only log
- [ ] `tutor.py` (Python 3 stdlib): `due`, `frontier`, `index`, `record`, `maps`, `check`, with the scribe as fallback
- [ ] The `protect-closed-notes` hook (bash, plus PowerShell for Windows), registered in settings
- [ ] Git commit at `/wrap`, scoped to the data folder

Test: a second session resumes from stored state with no re-diagnosis; a cross-domain prerequisite is reused, not duplicated; an agent's edit to a closed note is blocked; and a hand edit to a closed note shows up in `tutor.py check`.

### Phase 3: Assessments, review and projects

- [ ] `examiner` agent with the handoff template; `/quiz`, `/exam`, `/review`
- [ ] Explain-it-simply items and the correction round
- [ ] Project readiness rule, `/project` and the brief template

Test: a quiz is written from the index, graded blind, corrected, and shown as solid, shaky or gap with next actions; a ready cluster triggers a project proposal at the right scope.

### Phase 4: Visuals and optional tooling

- [ ] `visualize` skill: Mermaid and SVG rules, common syntax mistakes, size limits
- [ ] Optional: matplotlib plots, if Python is installed
- [ ] Optional: the submit watcher, behind its reliability test (see the practice loop)
- [ ] Optional: hard read-only locking of closed notes

### Phase 5: Calibrate after about 5 sessions

- [ ] Is in-session success landing near 80–85%? Shift the thresholds if not
- [ ] Re-grade one quiz yourself and compare it with the examiner
- [ ] Read two sessions for verbosity: cut repetition, restore anything that came out too terse
- [ ] Trim `tutor.md`; move rarely used guidance into skills
- [ ] README: write the Manual and check every statement against the finished system

## Settings and defaults

Agreed on October 6: these are the starting values. Each is one line in a prompt, the profile or the script, so changing one later is cheap.

| Setting | Default | Alternative and trade-off |
| --- | --- | --- |
| Handing the turn back | Enter in the terminal | Submit watcher: one window, more moving parts |
| Checkpoint format | Checkboxes in the note | A multiple-choice prompt in the terminal: faster to pick, but the choice must be copied into the note |
| Model mix | Opus tutor, Sonnet examiner and cartographer, Haiku scribe | Examiner on Opus for proof-heavy subjects; all Sonnet to stretch plan limits |
| Success target band | 70–90%, aim 80–85% | Narrow it after Phase 5 data |
| Unlock threshold for the frontier | Prerequisites `practicing`, mastery ≥ 0.6 | Higher for subjects where gaps compound fast, such as math |
| Mastery bar | ≥ 0.85, 3 observations, 2 sessions, one transfer item | Raise it where errors are costly |
| Project readiness | 80% of the cluster at ≥ 0.7, plus one transfer pass | Lower it to start projects earlier |
| Review intervals | 1, 3, 7, 16, 35 days, then doubling | Shorter for vocabulary-like material |
| Showing scores | Off; solid, shaky or gap instead | On, if numbers motivate you |
| Bookkeeping | `tutor.py` script, scribe as fallback | Scribe only: no Python needed, but slower and costlier |
| Git commits | Every `/wrap`, data folder only | Off, if you rely on other backups (loses the visible edit trail) |
| Hard locking of closed notes | Off; git shows any change | On: edits to closed notes won't save; some sync services cope badly |
| Domain split trigger | About 60 concepts, or a change of focus | Split earlier for clearer maps |

## Sources

- [Use the Claude Agent SDK with your Claude plan](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan), Claude Help Center
- [Legal and compliance](https://code.claude.com/docs/en/legal-and-compliance), Claude Code docs
- [Create custom subagents](https://code.claude.com/docs/en/sub-agents), Claude Code docs (agent files, models, hooks, what a subagent sees)
- [How Claude remembers your project](https://code.claude.com/docs/en/memory), Claude Code docs (`CLAUDE.local.md`)
- [Set up Claude Code in a large codebase](https://code.claude.com/docs/en/large-codebases), Claude Code docs (`additionalDirectories`)
- [Run prompts on a schedule](https://code.claude.com/docs/en/scheduled-tasks), Claude Code docs (Monitor tool, resume limits)
- [Using your Claude subscription in Pi agent](https://dev.to/spksoft/using-your-claude-subscription-in-pi-agent-at-your-own-risk-5h1j), DEV Community
- [The Eighty Five Percent Rule for optimal learning](https://www.nature.com/articles/s41467-019-12552-4), Wilson et al., Nature Communications 2019
- [Generative AI without guardrails can harm learning](https://www.semanticscholar.org/paper/Generative-AI-without-guardrails-can-harm-learning:-Bastani-Bastani/60570ad3268871882c65f6ed4ead35db4b220528), Bastani et al., PNAS 2025
- [AI tutoring outperforms in-class active learning](https://www.nature.com/articles/s41598-025-97652-6), Kestin et al., Scientific Reports 2025
- [All study strategies not created equal](https://www.kent.edu/psychology/all-study-strategies-not-created-equal-according-kent-state-researchers), Kent State on Dunlosky et al. 2013
- [Expertise reversal effect and its instructional implications](https://link.springer.com/article/10.1007/s11251-009-9102-0), Instructional Science
- [How our AI works](https://www.mathacademy.com/how-our-ai-works), Math Academy
