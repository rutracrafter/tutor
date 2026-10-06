---
name: diagnose
description: Map a new topic and find out what you already know about it. The cartographer drafts the concept graph, then an adaptive probe of 8-15 short questions with confidence ratings places you on it. Run this before the first /learn on any new subject.
---

# /diagnose `<topic>`

A new topic has no graph, so teaching it means teaching blind to prerequisites. This builds
the graph and places the learner on it. 20–30 minutes, once per topic.

## 1 · Draft the graph

Read `Learner/profile.md` for the goals and background. Then delegate to the
`cartographer` with everything it needs, since it cannot see this conversation:

```text
Topic: <topic>
Learner's goal for it: <from the profile, verbatim>
Relevant background: <from the profile>
Job: draft a graph for a new topic (job 1 in your prompt).
Depth: the path from what they already hold to that goal, 8-20 concepts.
Return: IDs in dependency order, what you reused, the widest gap, what you are unsure of.
```

Check what comes back before using it:

- Does any new concept duplicate one that exists under another name? If so, say so and
  have it alias instead. A duplicate splits the evidence and reviews twice.
- Is any `requires:` list inflated with merely-related concepts? That blocks the frontier.
- Did it reuse concepts from other domains where it could?

Then show the learner the graph as a short list in dependency order, grouped by layer, and
say which parts you expect they already hold. Do not show them the whole Mermaid map yet;
it is more useful after the probe, coloured by what they know.

## 2 · Probe adaptively

8–15 short questions. Open a session note (`session_type: diagnose`) and run the probe in
it, as normal items so every answer is citable evidence.

Rules for the probe:

- **Skip what the graph already settles.** A concept already `practicing` or better from
  another domain is not re-probed; say in one line that it is being taken as held.
- **Produce, don't recognise** — even here. A probe item asks for a derivation, a
  prediction, a mechanism or a worked step, not a definition to recognise.
- **Adaptive.** Start mid-graph. A correct answer moves up a layer; a wrong one moves down
  to its prerequisites. The aim is to find the boundary, not to cover everything, which is
  why 15 items can place a 20-concept graph.
- **Every item carries a confidence rating, 1–5.** Ask for it in the answer slot.
- **No hints and no teaching during the probe.** Say so at the start: an "I don't know" here
  is information, not a failure, and is far more useful than a guess.

## 3 · Read the result

| Answer | Confidence | What it means | What to record |
| --- | --- | --- | --- |
| Correct | High | Held | A graded observation, full weight |
| Correct | Low | Fragile or guessed | A graded observation, and an early review |
| Wrong | Low | A plain gap | `stage: introduced` at most, no misconception |
| Wrong | **High** | **A misconception** | Record it verbatim in `misconceptions:` |

A confident wrong answer is the most valuable thing the probe produces: it is a belief that
will keep producing wrong answers until it is named. Write it in the learner's own words.

Concepts the graph implies are "probably known" but that were never probed get
`next_review` within 2–3 days, so a wrong inference surfaces within days rather than
weeks.

## 4 · Record and report

Record each probed item with `tutor.py record` (or the scribe), then regenerate the index
and the maps so the map is coloured by what the probe found:

```bash
python3 scripts/tutor.py index
python3 scripts/tutor.py maps --domain <domain>
```

Then report, in the note:

- **Where you are**, as three groups: solid, shaky, not yet started. No percentages.
- **The misconceptions found**, each in one line of plain language.
- **The starting point**: which concept the first `/learn` should open on, and why.
- **The map**, as a link to `Maps/<domain>.md`.

Close with `/wrap`, which commits everything.

## Re-diagnosing

Do not. A second `/learn` resumes from stored state; re-probing wastes a session and
overwrites evidence with a snapshot. Re-run `/diagnose` only for a genuinely new topic, or
when the learner says their knowledge changed outside the system — a course, a job, a
year away.
