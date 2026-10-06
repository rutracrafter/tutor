---
name: setup
description: Link this engine repo to a learning data folder in your vault. Run once after cloning, or again to switch data folders. Creates the data skeleton, writes CLAUDE.local.md and .claude/settings.local.json, and detects or creates the git repo that keeps the record.
---

# /setup

Links the engine (this repo) to a data folder (your notes). Nothing about teaching
happens here. Run it once after cloning; run it again to point at a different folder.

Do the steps in order and report each one as a single line. Stop and ask if a step fails.

## 1 · Find the data folder

Work out a default before asking:

- If this repo's directory name starts with a dot (the recommended `.tutor-engine/`
  inside a vault), the default is `../Learning` resolved to an absolute path.
- Otherwise there is no default.

Ask once, in one line: the absolute path to the learning folder, offering the default if
there is one. Accept `~`. Do not ask anything else yet.

Then check the path with Bash:

- It exists and is a directory → continue to step 2.
- It does not exist → say so and ask whether to create it. Create it only on a yes.
- It exists and already holds `Learner/profile.md` → this is an existing data folder.
  Skip the skeleton in step 2; say "found an existing data folder" and keep every file.

## 2 · Create the skeleton

Only for a new or empty folder. Create these directories:

```
Learner/  Concepts/  Maps/  Sessions/  Assessments/  Projects/  Workspaces/  Assets/  .keys/
```

Copy `templates/profile.md` to `Learner/profile.md` and `templates/index.md` to
`Learner/index.md`, filling today's date. Write `.keys/README.md` with one line saying
answer keys live here and that Obsidian hides dot-folders. Leave every other folder empty.

Then fill the profile with the user: ask for their name, their first learning goal, and
anything they already know that is relevant to it. Three questions, one message, and
accept short answers. Write them into `Learner/profile.md`. Leave the other profile
settings at their defaults and tell the user in one line that the defaults are
`verbosity: standard`, `show_scores: false`, 45-minute sessions, and that the Manual in
the README lists all of them.

## 3 · Write the two local files

`CLAUDE.local.md` in the repo root — this loads into the tutor and every subagent, so it
is how an examiner or scribe learns where the notes live:

```markdown
# Local configuration

Data folder: `/absolute/path/to/Learning`

Every path in the skills and agent prompts is relative to that folder:
`Learner/`, `Concepts/`, `Maps/`, `Sessions/`, `Assessments/`, `Projects/`,
`Workspaces/`, `Assets/`, `.keys/`.

Read and write notes only inside the data folder. Never write learning notes into the
engine repo.

Bookkeeping script: `python3 scripts/tutor.py --data "/absolute/path/to/Learning" <command>`
Python 3 available: yes | no
```

Set the Python line from `python3 --version` (treat 3.8 or newer as yes). If it is no, add
one line: the scribe does the bookkeeping instead, which is slower but complete.

`.claude/settings.local.json` — grants file access outside the repo. Merge into the file
if it already exists; never drop keys that are already there:

```json
{
  "permissions": {
    "additionalDirectories": ["/absolute/path/to/Learning"]
  }
}
```

Both files are gitignored, so they stay out of the shared engine.

## 4 · Detect or create the git record

Run `git -C "<data folder>" rev-parse --show-toplevel`.

- **Inside a repo** (a vault you already sync with git, say): say which repo, and that
  `/wrap` will commit only paths under the data folder, with messages prefixed `tutor:`,
  and will never push, rebase or touch other files. Record the toplevel path in
  `CLAUDE.local.md` as `Git repo: <toplevel>`.
- **Not in a repo**: offer `git init` in the data folder. On a yes, run it, write a
  `.gitignore` there holding `.obsidian/` and `.trash/`, and make the first commit
  (`tutor: initial data folder`). On a no, write `Git repo: none` in `CLAUDE.local.md`
  and say that the visible edit trail is off.

## 5 · Check it worked

Run the checks, then print the result as a short table:

| Check | How |
| --- | --- |
| Data folder reachable | Read `Learner/profile.md` with the Read tool |
| Skeleton complete | All nine directories exist |
| Guard hook runs | `.claude/hooks/protect-closed-notes.sh` is executable |
| Script runs | `python3 scripts/tutor.py --data "<path>" index --dry-run` (skip if no Python) |
| Git record | Toplevel path, or "none" |

Close with one line: start a learning session with `/learn <topic> [30m]`, or `/diagnose
<topic>` first if the topic is new.

## Switching data folders

Rerun `/setup`. It overwrites both local files and leaves every data folder untouched. Say
in one line which folder is now active.
