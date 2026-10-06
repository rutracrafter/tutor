---
name: review
description: A short session when time is tight — 10-15 minutes of due reviews produced from memory, plus one explain-it-simply item. No new material at all. Use this instead of /learn for a budget under 20 minutes.
---

# /review `[domain]`

10–15 minutes. Due reviews and one explain-it-simply item. **No new material**, not even a
small aside — that is the whole point of the session type. A short session that introduces
something new is a session that leaves an idea half-taught.

Spacing works best when it is never skipped, so this exists to make a tired, busy day still
count.

## 1 · Recover and load

As in `/learn`: wrap any open session note first, then load the working set.

```bash
python3 scripts/tutor.py due --limit 15
python3 scripts/tutor.py due --domain <domain> --json    # if a domain was named
```

Pick 4–6 concepts from the due list, most overdue and weakest first. More than six in
fifteen minutes means rushing each one, which defeats retrieval.

Open `Sessions/YYYY-MM-DD-review.md` with `session_type: review` and the domains touched.

## 2 · Review items

**Produce, don't recognise.** Every item asks the learner to produce the thing from memory:
derive it, state the mechanism, work a small case, sketch the algorithm. Never "do you
remember X?" and never a definition to recognise.

- One item per concept, at the concept's current level.
- **Closed-book.** Say so once at the start: no looking at the old notes first. Retrieval
  from memory is the thing that works; re-reading is the thing that does not.
- The hint ladder still applies, and so does the two-attempts rule.
- A correct answer still gets "why does that work?" if there is time.

A miss here is useful information, not a setback. It resets that concept's interval to one
day, which is exactly what should happen.

## 3 · One explain-it-simply item

Always, and always last. Pick the concept with the most at stake — the one carrying the
most dependents in the graph, or the one that was shakiest today:

> Explain why the borrow checker forbids two mutable references, to someone who knows
> Python but not Rust.

Check accuracy, completeness, plain language, and whether they used a concrete example.
Then one follow-up aimed at the vaguest part. A vague spot usually marks a gap in
understanding rather than a gap in wording, and this is the cheapest way to find one.

## 4 · Wrap

Run `/wrap`. It records the evidence, pushes the intervals, regenerates the maps and
commits.

In the report, say plainly if several concepts missed: that is a sign the intervals have
run ahead of the learner, and the next session should be `/learn` on the weakest rather
than more review.

## When to use something else

| Situation | Use |
| --- | --- |
| Under 20 minutes | `/review` — this |
| 30 minutes or more, and something new to learn | `/learn` |
| A cluster just finished | `/quiz` |
| Nothing is due | `/learn`, or `/quiz` on the last cluster |
| Many concepts due and little time for weeks | `/review` repeatedly; the backlog shrinks because intervals grow |
