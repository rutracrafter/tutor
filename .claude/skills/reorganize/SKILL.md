---
name: reorganize
description: Split a domain that has grown too broad into nested sub-tags. The cartographer proposes, you approve, the scribe re-tags. Because domains are tags and not folders, nothing moves and no link breaks.
---

# /reorganize `<domain>`

A domain is ready to split at about 60 concepts, or sooner when the learner starts focusing
on one part of it. `tutor.py index` shows the count per domain.

Splitting is cheap by design: domains are **nested tags, not folders**, and a concept's
filename never contains its domain. So a split edits `tags:` lines and nothing else — no
file moves, no broken wikilinks, no rewritten history.

## 1 · Propose

Delegate to the `cartographer`:

```text
Job: propose sub-tags for a domain (job 4 in your prompt).
Domain: <domain>, currently <n> concepts.
Why now: <60+ concepts | the learner is focusing on X>
Return: the proposed sub-tags, each with the concept IDs that belong to it, the concepts
that belong to more than one, and anything that fits nowhere.
```

A good proposal:

- has 3–6 sub-tags, not 15 — a split into too many is a split you will redo;
- follows how the field divides itself, not how this learner happened to meet it;
- keeps the parent tag on every concept, so `math` still finds all of them;
- names the concepts that genuinely belong to two sub-tags rather than forcing a choice.

## 2 · Approve

Show the learner the proposal as a table: sub-tag, concept count, and two or three example
IDs. Ask for a yes, a change, or a no, in one line. Do not re-tag anything before they
answer — a tag scheme is a view of their subject, and they have to recognise it.

## 3 · Re-tag

The scribe edits **only** the `tags:` line of each concept, adding the sub-tag and keeping
the parent:

```yaml
tags: [math, math/probability]
```

Nothing else in the note changes. No file is renamed or moved.

## 4 · Rebuild the views

```bash
python3 scripts/tutor.py index
python3 scripts/tutor.py maps --domain <parent>
python3 scripts/tutor.py maps --domain <each new sub-tag>
```

Then commit, with a message naming the split:

```bash
git -C "<data folder>" add Concepts Maps Learner
git -C "<data folder>" commit -m "tutor: split math into probability, statistics, linear-algebra"
```

Report in one line per new sub-tag: the tag, its concept count, and its frontier count.

## Merging, and other re-tags

The same three steps work for undoing a split, renaming a sub-tag, or moving a handful of
concepts between sub-tags: propose, approve, re-tag the `tags:` lines only. Ask the learner
first in every case.

Renaming a **concept** is different and more expensive: the ID is the filename and wikilinks
point at it, so a rename means editing every `requires:` and `related:` list that mentions
it, plus every log line in other notes. Prefer adding an alias. Rename only when the ID is
genuinely wrong — misspelled, or ambiguous with another field.
