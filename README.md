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
