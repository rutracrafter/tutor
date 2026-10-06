# Personal Tutor Agent

A teacher that lives in your terminal and writes in your Obsidian vault.

You run `claude` inside this repo and a tutor agent takes over the session. It teaches at
the edge of what you already know, makes you produce answers rather than recognise them,
withholds solutions until you have genuinely tried, and keeps a durable record of what you
understand in plain Markdown notes you own.

**The principles it is built on**, each one a rule in the agent's prompt rather than a
hope about the model's defaults:

- **Practice pitched at 80–85% success.** Learning is fastest just inside your reach, so
  difficulty and scaffolding move with your recent hit rate.
- **Produce, don't recognise.** Derive it, implement it, explain it. Multiple choice is
  for quick checks only.
- **Guardrails, not answers.** An unguarded AI helper raises practice grades and leaves
  you worse off once it is gone. This one climbs a hint ladder and needs two genuine
  attempts before it will show a solution.
- **Retrieval and spacing.** Every session opens with due reviews, produced from memory,
  on expanding intervals.
- **Fading scaffolds.** Worked example → completion → independent → transfer, one step at
  a time.
- **Prerequisites first.** One shared concept graph across every subject, so the
  statistics you hold counts toward the machine learning you are starting.
- **Use it for real.** When a cluster of concepts is solid, it tells you so and proposes a
  project that needs them together.

**What it is not.** Not an answer machine, not a chatbot that writes your code, and not a
grading engine. It will not hand you a solution you did not work for, it never writes your
project's code or prose, and it shows results as solid, shaky or gap rather than as a
percentage. Scores exist inside the model to steer what you practise next.

**How it is built.** Plain Markdown and JSON: four agent prompts, ten skills, six
templates, one guard hook and one bookkeeping script. There is no framework and no API
key. It runs on your Claude subscription through interactive Claude Code, and everything
in it is text you can read and change.

---

## Installation

### Prerequisites

| Needed | Why |
| --- | --- |
| **Claude Code**, logged in with your Claude account | The whole system runs here. Log in with your Claude plan, not an API key, or every session bills per token. |
| **Obsidian** (recommended) | Renders the callouts, LaTeX, Mermaid diagrams and wikilinks the tutor writes. A plain folder and any editor work too; the formatting just shows as text. |
| **Python 3.8+** (optional) | Runs `tutor.py`, which does the deterministic bookkeeping. Without it the scribe agent does the same work: slower and costlier, but complete. |
| **git** (optional, recommended) | Gives the record an undo and makes any later edit to a closed note visible. |

### Install the engine inside your vault, in a hidden folder

This is the recommended layout. It keeps everything for one vault together, and the
leading dot keeps the engine's own Markdown out of Obsidian's search and graph view.

```text
MyVault/
├── .gitignore          # add the line: .tutor-engine/
├── .tutor-engine/      # this repo
├── Learning/           # your notes — created by /setup
└── …                   # your other notes
```

```bash
cd /path/to/MyVault
git clone <this-repo-url> .tutor-engine
echo '.tutor-engine/' >> .gitignore      # only if the vault is itself a git repo
cd .tutor-engine
```

The `.gitignore` line matters if your vault is a git repo: it stops the vault's git from
ever seeing the engine's repository. The engine updates with its own `git pull`.

### Install it outside the vault instead

Clone to somewhere like `~/tools/tutor` in two cases:

- **Your vault sits in iCloud Drive, Dropbox or OneDrive.** Those services copy
  everything, including the engine's `.git` folder, which can be corrupted when two
  devices write to it at once.
- **You want no tool files in the vault at all.**

`/setup` then asks for the vault path; nothing else changes.

### Run `/setup`

```bash
claude
```

Then, in the session:

```text
/setup
```

It asks for your learning folder (defaulting to `../Learning` when the engine is in a
dot-folder beside it), creates the folder skeleton, asks three questions to fill your
profile, and writes two gitignored files:

| File | What it holds |
| --- | --- |
| `CLAUDE.local.md` | The path to your data folder. Loads into the tutor and every subagent, so each one knows where the notes live. |
| `.claude/settings.local.json` | Your data folder under `additionalDirectories`, which is what grants file access outside this repo. |

It finishes by detecting git: if your data folder is already inside a repo it commits only
paths under the data folder, with messages prefixed `tutor:`, and never pushes, rebases or
touches your other files. If it is not in a repo, it offers `git init`.

Rerun `/setup` any time to point at a different folder.

### Check that it worked

`/setup` prints a check table as its last step. Verify by hand if you prefer:

```bash
cat CLAUDE.local.md                  # shows your data folder path
ls /path/to/MyVault/Learning         # nine folders: Learner, Concepts, Maps, …
```

In the session, `/agents` should show **tutor** as the active agent, and asking it to read
`Learner/profile.md` should return your profile. If it cannot see the folder, the
`additionalDirectories` entry in `.claude/settings.local.json` is the thing to check, and
Claude Code must be restarted after that file changes.

One more thing to check: Claude Code also loads `CLAUDE.md` files from folders *above* the
one it starts in. If your vault root has its own `CLAUDE.md` it joins the tutor's context.
Make sure it does not contradict the tutor's rules, or exclude it with the
`claudeMdExcludes` setting.

---

## Quick start

Your first session, in about five minutes.

### 1 · Open two windows

Obsidian on the left, your terminal on the right. You will read in Obsidian and type in
the terminal, and the note is where everything actually happens.

### 2 · Start a session

```bash
cd /path/to/MyVault/.tutor-engine
claude
```

```text
/learn probability 30m
```

The topic is a slug; the budget is optional (`30m`, `45`, `1h`) and defaults to the one in
your profile. If the topic is new to the system, the tutor will suggest `/diagnose
probability` first so it can map the prerequisites before teaching over a gap.

A new note appears in `Learning/Sessions/2026-10-06-probability.md`. Open it in Obsidian.
The plan is at the top. The chat reply is one line — that is deliberate, everything of
substance is in the note.

### 3 · Answer in the note

Each item looks like this:

```markdown
## Q1 · conditional-probability · level 2 · scaffold: completion
> [!tutor]
> A bag holds 3 red and 2 blue marbles. You draw two without replacement.
> Write $P(\text{second is red} \mid \text{first was red})$ and explain
> why the denominator changes.

> [!answer] Your answer
> 
```

Type inside the `[!answer]` block. Then, in the terminal, **press Enter on an empty line**
(or type a single `.`). That means "read the note". The tutor reads what changed, responds
in the note, and says one line in chat.

You can also just type your answer in the terminal. It gets copied word for word into the
answer slot, marked `(typed in terminal)`, and handled the same way — nothing you type is
lost or paraphrased.

### 4 · Steer at the checkpoints

After each phase:

```markdown
> [!checkpoint] Next: guided practice on bayes-theorem, 3–4 problems · 18 min used of 30
> - [ ] More practice on what we just did
> - [ ] Go deeper on something (say what)
> - [ ] Something else (write below)
> Leave everything unticked to continue as planned.
```

Tick nothing and press Enter to continue. "More practice on X" is always granted; "go
deeper on Y" is granted if you hold Y's prerequisites, and otherwise the tutor shows you
what is missing and offers a detour. To redirect mid-phase, write a `> [!steer]` callout
anywhere in the note and press Enter.

### 5 · Wrap up

```text
/wrap
```

Any time — two minutes in or at the end. It writes the five-line summary, records what you
actually demonstrated into the concept graph, lists what you did not finish as carry-over,
regenerates the maps, closes the note and commits the data folder.

Then close the terminal. The next session starts fresh: `claude`, `/learn <topic>`. All the
continuity lives in the files.

### Three things that surprise people

- **A right answer gets "why does that work?"** A correct answer for the wrong reason is a
  miss nobody found yet.
- **A blank does not get a hint.** It gets an easier sub-question. Hints are for effort you
  have already shown; two genuine attempts come before any solution.
- **There is no score.** Results read solid, shaky or gap, each with its next action. The
  numbers exist inside the model to pick your next question.

---

## Manual

### Commands

| Command | Length | What it does |
| --- | --- | --- |
| `/setup` | 3 min, once | Links the engine to a data folder. Creates the skeleton, fills your profile, writes `CLAUDE.local.md` and `.claude/settings.local.json`, detects or creates the git repo. Rerun to switch folders. |
| `/diagnose <topic>` | 20–30 min, once per topic | Has the cartographer draft the concept graph, then places you on it with 8–15 adaptive questions, each with a confidence rating. Run before the first `/learn` on a new subject. |
| `/learn <topic> [30m]` | Your budget, usually 30–60 min | A normal study session in five timed phases. |
| `/review [domain]` | 10–15 min | Due reviews from memory plus one explain-it-simply item. No new material. |
| `/quiz [topic]` | 15–30 min | 5–8 items on a cluster, no help during, then a correction round. |
| `/exam [domain]` | 30–45 min | 8–15 cumulative items at a milestone, every 4–6 sessions in a domain. |
| `/project [slug]` | Open | Checks readiness and proposes a project, or continues one with a milestone review. |
| `/wrap` | 2–5 min | Closes the session: summary, evidence, carry-over, maps, commit. Works at any moment. |
| `/reorganize <domain>` | 10 min | Splits a domain that has grown broad into nested sub-tags. |

`visualize` is a skill the tutor uses rather than one you call, but asking for "a diagram of
this" invokes the same rules.

### Session types and time budgets

Give a budget (`/learn rust 30m`, or `45`, or `1h`) or let it use `session_default_min`
from your profile. The tutor takes the start time from the system clock and checks it again
at every phase boundary — the timing is measured, not estimated.

| Phase | Share of budget | What happens |
| --- | --- | --- |
| Warm-up retrieval | ~15% | Due reviews, produced from memory. Never cut. |
| New idea | ~25% | A prediction question first, then the explanation in chunks, each followed by an explain-back. |
| Guided practice | ~35% | Worked or partly worked examples fading to full problems. |
| Independent practice | ~15% | No scaffolding, a new context, older concepts mixed in. |
| Wrap-up | ~10% | Explain-it-simply, then your own summary. Never cut. |

Running late, it cuts new material first. With about five minutes left it moves to the
wrap-up wherever it is. Under 20 minutes it suggests `/review` instead. A concept new to
you tilts time toward the explanation; one you partly know tilts it toward practice.

**One learning session is one Claude Code session.** Run `claude` fresh each time, or
`/clear`. All continuity lives in the files — your profile, the index, the maps and the
last session's summary — so a fresh context stays cheap and avoids drift from a long chat.
If a long session fills up, Claude Code compacts it and the note is unaffected.

### Steering

The tutor proposes a plan at the start and adds a checkpoint after each phase. **Leaving
everything unticked means continue** — silence is consent, not a question to answer.

| What you ask | What happens |
| --- | --- |
| "More practice on X" | Always granted. |
| "Go deeper on Y" | Granted if you hold Y's prerequisites. Otherwise it shows what is missing and offers a short detour. |
| "Skip this, I know it" | Two quick check items. Pass and it is skipped, with credit recorded. |
| A tangent | Parked in `## Parking lot` and offered again at wrap-up, or added to the graph. |
| "Shorter" / "more detail" | Treated as a standing preference and written into your profile. |

To redirect mid-phase, write a `> [!steer]` callout anywhere in the note and press Enter.

**Handing the turn back.** Enter on an empty line, or a single `.`, means "read the note".
Type more and it gets sorted: an answer is copied word for word into the slot and marked
`(typed in terminal)`, a steering request is logged under the current checkpoint, a
question is answered in the note. Nothing you type is paraphrased or lost.

### Genuine attempts and the hint ladder

No solution before **two genuine attempts**. An attempt is genuine if it contains at least
one of: a committed answer even if wrong, a step of work or a named rule you think applies,
or a specific point of confusion ("I see why X, but not why Y"). The tutor judges content,
never length or the time you took.

Not genuine: a blank, "idk", restating the question, or a bare guess where reasoning was
asked for. An honest "I don't know where to start" **is** fine and is not penalised — it
earns a smaller sub-question rather than a hint.

| Rung | What you get |
| --- | --- |
| 1 | "What have you tried so far?" |
| 2 | Restate the goal and what you already know |
| 3 | A conceptual nudge — the principle, no steps |
| 4 | The very next step, and no further |
| 5 | A different problem with the same structure, worked fully |
| 6 | The solution step by step, with you explaining each step back |

One rung per turn, with a genuine attempt between rungs. Each rung used costs 0.25 of that
item's credit. Rung 6 counts as a miss and queues a similar item for later.

Several non-attempts in a row stops the lesson for a check-in: whether the level is wrong
or you are tired, with an easier level, a break or `/wrap` on offer.

### Assessments and projects

Assessments are learning events. Feedback leads with what you understood, then **one** gap,
then a correction round where fixing a miss yourself earns half credit — and only then a
model solution, which you explain back. Moving a quiz is free and never lowers mastery.
There are no retakes of the same paper; misses return later as review items in new forms.

| Kind | When | Size | Help | Weight |
| --- | --- | --- | --- | --- |
| Check for understanding | Every few minutes in a lesson | 1 item | Hint ladder | Half |
| Quiz | End of a cluster, or a review day | 5–8 items | None | Full |
| Exam | Milestone, every 4–6 sessions in a domain | 8–15 cumulative | None | Full, plus transfer |
| Project | When a cluster is ready | Milestones over 1+ sessions | Questions, design review | Strongest transfer evidence |

**Projects.** A cluster is ready when at least 80% of it is `practicing` or better with
mastery ≥ 0.7 **and** you have passed a transfer item in it. The tutor tells you at a
checkpoint; you can accept, swap in your own idea, or put it off. Scope scales with level:
beginner is 1–3 sessions with a written spec, intermediate is 3–8 sessions with
requirements only, advanced is open-ended with you defining the problem.

A project lives in `Projects/<slug>/` with `brief.md`, `log.md` and your work files. **The
tutor never writes your code or prose.** It may read your code, run it, run your tests,
create empty stubs or failing tests, and review your design with questions.

### The graph, maps and domains

One graph for everything you learn: one note per concept in `Concepts/<id>.md`, where the
ID is the filename. Prerequisites may cross domains, so the statistics you hold counts
toward the machine learning you start — `logistic-regression` requires
`maximum-likelihood-estimation` whatever each is tagged.

**Domains are tags, not folders.** Nested: `math`, then `math/probability` when it earns
the split. A concept carries several tags where it genuinely belongs to several fields. A
filename never contains a domain, so splitting one is a re-tag — nothing moves and no link
breaks. `/reorganize` does it at about 60 concepts, or sooner if you start focusing on one
part.

**The frontier** is recomputed at every `/wrap`. A concept joins it once every prerequisite
is `practicing` or better with mastery ≥ 0.6 — full mastery is deliberately not required,
or progress would stall. When the frontier runs dry the cartographer extends the graph one
layer, guided by your goals. A goal can also pull it forward: "I want to understand
transformers" has it draft a path backwards from there to what you already hold.

**Maps.** `/wrap` regenerates `Maps/<domain>.md`: a Mermaid graph coloured by stage with
the frontier outlined. Large domains show the frontier and the concepts around it, capped
at 40 nodes; Obsidian's graph view of `Concepts/` shows everything.

**Mastery.**

| Rule | Value |
| --- | --- |
| After a graded item | Mastery moves 30% of the way toward the item's score (1, 0.5 or 0), minus 0.25 per hint level |
| A check inside a lesson | Half weight |
| `mastered` | Mastery ≥ 0.85, at least 3 observations across 2 sessions, including a transfer item or project milestone |
| Review intervals | 1, 3, 7, 16, 35 days, then doubling. A miss resets to 1 day |
| A correct answer | Also pushes each direct prerequisite's next review half an interval later |

Mastery is revocable: if it falls below 0.85 the concept returns to `practicing`.

### Profile settings and their defaults

In `Learner/profile.md`. Each is one line, so changing one is cheap.

| Setting | Default | What the alternative costs |
| --- | --- | --- |
| `verbosity` | `standard` | `brief` gives clipped, note-style replies — good once you know a subject, thin while you are learning it |
| `show_scores` | `false` | `true` shows raw mastery numbers instead of solid / shaky / gap |
| `session_default_min` | `45` | Used when `/learn` is given no budget |
| `hard_lock_closed_notes` | `false` | `true` makes closed notes read-only on disk; some sync services cope badly |
| `submit_watcher` | `false` | `true` lets you hand the turn back by ticking a box in Obsidian (see below) |
| `timezone` | your zone | Used for the clock checks and dated filenames |

Your goals, background, preferences and constraints live in the same file as prose. The
tutor reads it whole at the start of every session, so keep it short.

**Other defaults**, set in the agent prompts and `scripts/tutor.py` rather than the
profile: the success band is 70–90% aiming for 80–85%; the frontier unlocks at prerequisite
mastery 0.6; project readiness is 80% of a cluster at 0.7 plus a transfer pass; a domain
splits at about 60 concepts. The model mix is Opus for the tutor, Sonnet for the examiner
and cartographer, Haiku for the scribe — all on your subscription's limits, which is why
only the teaching runs on the strongest model.

### History, git and editing your own notes

**You can edit anything.** It is your notebook, and locking you out would mean fighting
your editor. Three things keep the record trustworthy anyway:

1. **The model never re-reads old answers as evidence.** Each grade is written to the
   concept's log when it is given, and mastery comes only from those log lines. Improving
   an answer afterwards cannot change what the record says you knew.
2. **Revise below, don't overwrite.** To improve an answer during a session, add a line
   starting with `Revised:` under the original. It is graded as a new attempt, which is
   better practice than silently fixing the first one.
3. **Changes after closing are visible.** `/wrap` commits the data folder, so a later edit
   to a closed note shows in the diff, and `/learn` warns you about it.

**What is enforced in code**, not just asked for: `/wrap` marks notes `status: closed`, and
a hook script runs before every Write and Edit and blocks any change to a closed note. The
agent sees why it was blocked and cannot route around it. Concept logs are append-only; a
regrade is a new line.

**Git.** `/wrap` commits only paths under your data folder, with messages prefixed
`tutor:`. It never pushes, rebases or touches anything else. If your vault is already a git
repo it commits there; otherwise `/setup` offers `git init`. If another tool holds git's
lock — the Obsidian Git plugin syncing at that moment is the usual cause — it retries once
and then tells you; your notes are safe either way and the next wrap includes them.

Turn commits off by setting `Git repo: none` in `CLAUDE.local.md`. You lose the visible
edit trail.

### The bookkeeping script

`scripts/tutor.py` does everything deterministic — no model involved, so it is faster,
cheaper and cannot hallucinate a due date. Python 3.8+, standard library only. Without
Python the scribe agent does the same work from the same rules.

```bash
python3 scripts/tutor.py due --limit 15 [--domain math] [--json]
python3 scripts/tutor.py frontier [--domain math] [--show-blocked] [--json]
python3 scripts/tutor.py index [--dry-run]
python3 scripts/tutor.py record <concept-id> --score 1|0.5|0 [--hints N] [--source REF]
        [--weight full|half] [--scaffold STAGE] [--transfer] [--project]
        [--misconception TEXT] [--no-prereq-credit] [--dry-run]
python3 scripts/tutor.py maps [--domain math] [--dry-run]
python3 scripts/tutor.py check [--strict]
python3 scripts/tutor.py lock [--unlock]
```

It finds your data folder from `CLAUDE.local.md`, or `$TUTOR_DATA`, or `--data DIR`. Add
`--today YYYY-MM-DD` to any command to see what a given day looks like.

`check` is the one worth running by hand: it lists closed notes that differ from their last
commit. It reports and never reverts.

### The optional submit watcher

Off by default. With `submit_watcher: true`, `/learn` starts `scripts/watch-submit.sh`
(`.ps1` on Windows) through Claude Code's Monitor tool, and ticking a `- [ ] Submit` box in
Obsidian hands the turn back without touching the terminal.

It is built so that it cannot make the system less reliable: Enter always works, the
watcher only fires on a ticked box, it waits two seconds for Obsidian's autosave, and
pickup is idempotent because the tutor rewrites the line to `Submitted 14:32` — a second
trigger finds no ticked box. If it dies, nothing happens and you press Enter. `/learn`
re-arms it each session, because background monitors do not survive a resumed session.

**It ships disabled on purpose.** The bar it has to clear is 30 submits across 3 real
sessions with no missed and no duplicate pickups. The mechanism is tested; that run is
yours to do. Until then, Enter is the only method, and nothing is lost by it.

### Updating the engine

```bash
cd /path/to/MyVault/.tutor-engine
git pull
```

Your data folder is untouched — the engine holds no learning data, and the two files that
point at it (`CLAUDE.local.md`, `.claude/settings.local.json`) are gitignored. If a pull
changes `templates/`, existing notes keep their old shape; only new notes use the new one.

### Calibrating after about five sessions

The numbers above are starting values, agreed on October 6 2026, not findings. After about
five real sessions, check them:

- **Is in-session success landing near 80–85%?** Count correct first attempts across a few
  sessions. Consistently higher means the levels are too low; consistently lower means the
  prerequisites are not being checked hard enough. The thresholds live in
  `.claude/agents/tutor.md` and at the top of `scripts/tutor.py`.
- **Re-grade one quiz yourself** and compare with the examiner. A systematic difference is
  worth fixing in `.claude/agents/examiner.md`; a scatter is normal.
- **Read two sessions for verbosity.** Cut repetition, and restore anything that came out
  too terse. The voice rules are in `.claude/agents/tutor.md`.
- **Trim `tutor.md`.** Anything you never saw it use belongs in a skill instead, where it
  loads only when needed.

### Troubleshooting

| Symptom | Cause and fix |
| --- | --- |
| "I cannot access that folder" | The data folder is missing from `additionalDirectories` in `.claude/settings.local.json`. Rerun `/setup`, then restart Claude Code — that file is read at startup. |
| The tutor is not the active agent | `.claude/settings.json` sets `"agent": "tutor"`. Check you started `claude` inside the engine repo, not the vault root. |
| Rules from somewhere else are leaking in | Claude Code loads `CLAUDE.md` files from folders above the start directory. If your vault root has one, exclude it with `claudeMdExcludes`. |
| An edit was blocked and the agent gave up | That is the guard hook working: the note is closed. A regrade belongs in the concept's log; new work belongs in today's note. |
| A Mermaid diagram renders as an error | Write `broken` in your answer slot and press Enter. The common causes are a dash in a node ID and an unquoted `(` or `\|` in a label. |
| `tutor.py: No data folder` | Run `/setup`, or pass `--data /path/to/Learning`. |
| `tutor.py check` reports a change you did not make | A sync conflict, or Obsidian rewriting frontmatter. Compare with `git -C <data folder> diff`. |
| A commit failed at `/wrap` | Another tool held git's lock. The notes are saved; the next wrap commits them too. |
| Reviews have piled up | Use `/review` repeatedly rather than `/learn`. The backlog shrinks on its own, because every correct answer lengthens that concept's interval. |
| A concept is being taught twice under two names | Two concept notes for one idea. Tell the tutor; the cartographer merges them into one with an alias. |
