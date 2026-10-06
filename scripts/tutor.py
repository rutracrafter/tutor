#!/usr/bin/env python3
"""Deterministic bookkeeping for the personal tutor.

Everything here is arithmetic and file surgery: due dates, the frontier, the index,
recording a grade, regenerating the Mermaid maps, and checking whether a closed note has
been edited since it was committed. None of it needs a model, and a model searching
hundreds of files for due dates is slower, costlier and more error-prone than this.

Python 3.8+, standard library only. No YAML dependency: notes use a small, fixed subset of
frontmatter (scalars, inline lists, block lists) and writes are targeted line edits, so
comments and key order in a note survive untouched.

Usage:
    tutor.py [--data DIR] [--today YYYY-MM-DD] <command> [options]

Commands:
    due        concepts whose review is due
    frontier   concepts unlocked for new teaching
    index      regenerate Learner/index.md
    record     apply a graded observation to a concept
    maps       regenerate Maps/<domain>.md
    check      closed notes changed since their last commit
    lock       make closed notes read-only (optional, off by default)
"""

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys

STAGES = ["unseen", "introduced", "practicing", "mastered"]
INTERVAL_LADDER = [1, 3, 7, 16, 35]

# Thresholds. Each is one line on purpose: these are the numbers Phase 5 calibrates.
UNLOCK_STAGE = "practicing"      # a prerequisite must be at least this
UNLOCK_MASTERY = 0.6             # ...and at least this mastered
MASTERY_BAR = 0.85               # mastered at or above this
MASTERY_MIN_EVIDENCE = 3         # ...with at least this many observations
MASTERY_MIN_SESSIONS = 2         # ...across at least this many sessions
MASTERY_STEP = 0.30              # a full-weight item moves mastery this far toward it
HINT_PENALTY = 0.25              # per hint level used
PRACTICING_MIN_EVIDENCE = 2      # introduced -> practicing
MAP_NODE_BUDGET = 40             # large domains show the frontier and two hops
MAP_HOPS = 2                     # ...a minimum radius of two hops from it
MAP_MAX_HOPS = 12                # ...and never more rings than this, for a long chain

# --------------------------------------------------------------------------- errors

class TutorError(Exception):
    pass


# ------------------------------------------------------------------- frontmatter I/O

def split_frontmatter(text):
    """Return (frontmatter_lines, body_lines). Both empty-safe.

    A note has frontmatter only when its very first line is `---`. A `---` further down
    is a horizontal rule, and `status: closed` in the body is prose, not state.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return [], lines
    for i in range(1, len(lines)):
        if lines[i].strip() in ("---", "..."):
            return lines[1:i], lines[i + 1:]
    return [], lines  # unterminated: treat as no frontmatter rather than guessing


def _strip_comment(value):
    """Drop a trailing `# comment`, but not a `#` inside quotes or a wikilink anchor."""
    out, quote = [], None
    for i, ch in enumerate(value):
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
            out.append(ch)
            continue
        if ch == "#":
            prev = value[i - 1] if i else " "
            if prev in " \t":
                break
            out.append(ch)
            continue
        out.append(ch)
    return "".join(out).strip()


def _unquote(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def _split_inline_list(inner):
    """Split `a, "b, c", d` on top-level commas only."""
    items, buf, quote, depth = [], [], None, 0
    for ch in inner:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
            buf.append(ch)
        elif ch == "[":
            depth += 1
            buf.append(ch)
        elif ch == "]":
            depth -= 1
            buf.append(ch)
        elif ch == "," and depth == 0:
            items.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    items.append("".join(buf))
    return [_unquote(x) for x in items if _unquote(x) != ""]


def parse_frontmatter(text):
    """Parse the subset of YAML the notes use. Returns a dict of str | list."""
    fm_lines, _ = split_frontmatter(text)
    data, pending_key = {}, None
    for raw in fm_lines:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        stripped = raw.strip()
        if stripped.startswith("- ") and pending_key:
            data[pending_key].append(_unquote(_strip_comment(stripped[2:])))
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_\-]*)\s*:\s*(.*)$", raw)
        if not m:
            continue
        key, value = m.group(1), _strip_comment(m.group(2))
        if value == "":
            data[key] = []          # may become a block list on the next lines
            pending_key = key
        elif value.startswith("[") and value.endswith("]"):
            data[key] = _split_inline_list(value[1:-1])
            pending_key = None
        else:
            data[key] = _unquote(value)
            pending_key = None
    return data


def format_scalar(value):
    if isinstance(value, list):
        return "[" + ", ".join(_quote_if_needed(v) for v in value) + "]"
    return str(value)


def _quote_if_needed(item):
    item = str(item)
    if item.startswith("[[") or any(c in item for c in " ,:#\"'[]{}") or item.strip() != item:
        return '"%s"' % item.replace('"', '\\"')
    return item


def write_frontmatter_values(path, updates):
    """Set keys in a note's frontmatter, preserving every other line verbatim.

    Targeted line edits rather than a YAML round-trip, so the comments that explain the
    fields — and the author's key order — survive. A key that is absent is appended at the
    end of the block.
    """
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise TutorError("%s has no frontmatter" % path)
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() in ("---", "..."):
            end = i
            break
    if end is None:
        raise TutorError("%s has unterminated frontmatter" % path)

    remaining = dict(updates)
    for i in range(1, end):
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_\-]*)(\s*:\s*)(.*)$", lines[i])
        if not m:
            continue
        key = m.group(1)
        if key not in remaining:
            continue
        comment = ""
        cm = re.search(r"\s{2,}#.*$", m.group(3))
        if cm:
            comment = cm.group(0)
        lines[i] = "%s: %s%s" % (key, format_scalar(remaining.pop(key)), comment)

    extra = ["%s: %s" % (k, format_scalar(v)) for k, v in remaining.items()]
    lines = lines[:end] + extra + lines[end:]
    newline = "\n" if text.endswith("\n") else ""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + newline)


def append_log_line(path, line):
    """Append to a concept's `## Log` section, creating it if absent. Append-only."""
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    if not text.endswith("\n"):
        text += "\n"
    if re.search(r"(?m)^##\s+Log\s*$", text):
        text = text.rstrip("\n") + "\n" + line + "\n"
    else:
        text = text.rstrip("\n") + "\n\n## Log\n" + line + "\n"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


# ------------------------------------------------------------------------- utilities

def as_float(value, default=0.0):
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return default


def as_int(value, default=0):
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return default


def parse_date(value):
    if not value:
        return None
    try:
        return dt.date.fromisoformat(str(value).strip())
    except ValueError:
        return None


def wikilink_ids(values):
    """`["[[bayes-theorem|Bayes]]", "x"]` -> `["bayes-theorem", "x"]`."""
    out = []
    for value in values or []:
        text = str(value).strip()
        m = re.match(r"^\[\[(.+?)\]\]$", text)
        if m:
            text = m.group(1)
        text = text.split("|")[0].split("#")[0].strip()
        text = text.rsplit("/", 1)[-1]
        if text:
            out.append(text)
    return out


def stage_rank(stage):
    try:
        return STAGES.index(str(stage).strip())
    except ValueError:
        return 0


def next_interval(current, score):
    """1, 3, 7, 16, 35, then doubling. A miss resets to 1; a partial holds."""
    current = as_int(current, 0)
    if score == 0:
        return 1
    if score < 1:
        return max(current, 1)
    if current <= 0:
        return INTERVAL_LADDER[0]
    for step in INTERVAL_LADDER:
        if current < step:
            return step
    return current * 2


def sanitize_node_id(concept_id):
    """Mermaid reads `-` inside an arrow, so node ids use underscores and a label."""
    return re.sub(r"[^A-Za-z0-9_]", "_", concept_id)


def tag_to_filename(tag):
    return re.sub(r"[^a-z0-9]+", "-", str(tag).lower()).strip("-")


# ------------------------------------------------------------------------- the graph

class Concept(object):
    def __init__(self, path, fm):
        self.path = path
        self.fm = fm
        self.id = str(fm.get("id") or os.path.splitext(os.path.basename(path))[0]).strip()
        self.tags = [str(t).strip() for t in (fm.get("tags") or []) if str(t).strip()]
        self.requires = wikilink_ids(fm.get("requires"))
        self.related = wikilink_ids(fm.get("related"))
        self.stage = str(fm.get("stage") or "unseen").strip()
        self.scaffold = str(fm.get("scaffold") or "worked").strip()
        self.mastery = as_float(fm.get("mastery"))
        self.evidence_count = as_int(fm.get("evidence_count"))
        self.last_seen = parse_date(fm.get("last_seen"))
        self.next_review = parse_date(fm.get("next_review"))
        self.interval_days = as_int(fm.get("interval_days"))
        self.misconceptions = [str(m) for m in (fm.get("misconceptions") or [])]

    def in_domain(self, domain):
        if not domain:
            return True
        return any(t == domain or t.startswith(domain + "/") for t in self.tags)

    def unlocked(self, graph):
        """Every prerequisite at least `practicing` with mastery >= 0.6.

        Full mastery of a prerequisite is deliberately not required: demanding it would
        stall progress, and an exam is where only mastered concepts are relied on.
        """
        for req in self.requires:
            parent = graph.get(req)
            if parent is None:
                return False       # an unknown prerequisite is a gap, not a pass
            if stage_rank(parent.stage) < stage_rank(UNLOCK_STAGE):
                return False
            if parent.mastery < UNLOCK_MASTERY:
                return False
        return True

    def missing_prereqs(self, graph):
        out = []
        for req in self.requires:
            parent = graph.get(req)
            if (parent is None or stage_rank(parent.stage) < stage_rank(UNLOCK_STAGE)
                    or parent.mastery < UNLOCK_MASTERY):
                out.append(req)
        return out


def load_concepts(data_dir):
    folder = os.path.join(data_dir, "Concepts")
    graph = {}
    if not os.path.isdir(folder):
        return graph
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".md") or name.startswith("."):
            continue
        path = os.path.join(folder, name)
        try:
            with open(path, "r", encoding="utf-8") as fh:
                fm = parse_frontmatter(fh.read())
        except (IOError, OSError, UnicodeDecodeError):
            continue
        concept = Concept(path, fm)
        if concept.id:
            graph[concept.id] = concept
    return graph


def load_notes(data_dir, subdir):
    out = []
    folder = os.path.join(data_dir, subdir)
    if not os.path.isdir(folder):
        return out
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".md") or name.startswith("."):
            continue
        path = os.path.join(folder, name)
        try:
            with open(path, "r", encoding="utf-8") as fh:
                out.append((path, parse_frontmatter(fh.read())))
        except (IOError, OSError, UnicodeDecodeError):
            continue
    return out


def all_domains(graph):
    """Every tag that appears, plus the parents implied by a nested tag."""
    domains = set()
    for concept in graph.values():
        for tag in concept.tags:
            parts = tag.split("/")
            for i in range(1, len(parts) + 1):
                domains.add("/".join(parts[:i]))
    return sorted(domains)


# ------------------------------------------------------------------------- commands

def cmd_due(args, ctx):
    graph, today = ctx["graph"], ctx["today"]
    due = [c for c in graph.values()
           if c.next_review and c.next_review <= today and c.in_domain(args.domain)]
    # Most overdue first, then weakest: the thing most likely to be forgotten leads.
    due.sort(key=lambda c: (c.next_review, c.mastery, c.id))
    shown = due[:args.limit] if args.limit and args.limit > 0 else due

    if args.json:
        print(json.dumps([{
            "id": c.id, "stage": c.stage, "scaffold": c.scaffold,
            "mastery": round(c.mastery, 3), "days_overdue": (today - c.next_review).days,
            "next_review": c.next_review.isoformat(), "tags": c.tags,
            "misconceptions": c.misconceptions,
        } for c in shown], indent=2))
        return 0

    if not due:
        print("Nothing due on %s%s." % (today, " in %s" % args.domain if args.domain else ""))
        return 0
    print("Due on %s%s — %d concept(s)%s"
          % (today, " in %s" % args.domain if args.domain else "", len(due),
             ", showing %d" % len(shown) if len(shown) < len(due) else ""))
    print("%-34s %-11s %-12s %7s %9s  %s"
          % ("concept", "stage", "scaffold", "mastery", "overdue", "misconceptions"))
    for c in shown:
        print("%-34s %-11s %-12s %7.2f %7dd  %s"
              % (c.id[:34], c.stage, c.scaffold, c.mastery,
                 (today - c.next_review).days, "; ".join(c.misconceptions)[:40]))
    return 0


def cmd_frontier(args, ctx):
    graph = ctx["graph"]
    pool = [c for c in graph.values() if c.in_domain(args.domain)]
    frontier, in_progress, blocked = [], [], []
    for c in pool:
        if stage_rank(c.stage) >= stage_rank("practicing"):
            if c.stage != "mastered":
                in_progress.append(c)
            continue
        if c.unlocked(graph):
            frontier.append(c)
        else:
            blocked.append(c)
    frontier.sort(key=lambda c: (-len(c.requires), c.id))
    in_progress.sort(key=lambda c: (c.mastery, c.id))

    if args.json:
        print(json.dumps({
            "frontier": [{"id": c.id, "stage": c.stage, "tags": c.tags,
                          "requires": c.requires} for c in frontier],
            "in_progress": [{"id": c.id, "mastery": round(c.mastery, 3),
                             "scaffold": c.scaffold} for c in in_progress],
            "blocked": [{"id": c.id, "missing": c.missing_prereqs(graph)}
                        for c in blocked],
            "exhausted": not frontier and not in_progress,
        }, indent=2))
        return 0

    scope = " in %s" % args.domain if args.domain else ""
    if not frontier:
        if not pool:
            print("No concepts%s yet. Run /diagnose <topic> to have the cartographer draft "
                  "the graph." % scope)
        elif in_progress:
            print("Frontier%s is empty; %d concept(s) still in progress." % (scope, len(in_progress)))
        else:
            print("Frontier%s is exhausted — every concept in the graph is practicing or "
                  "better. Have the cartographer extend the graph." % scope)
    else:
        print("Frontier%s — %d concept(s) ready to teach" % (scope, len(frontier)))
        for c in frontier:
            print("  %-34s %-11s requires: %s"
                  % (c.id[:34], c.stage, ", ".join(c.requires) or "nothing"))
    if in_progress:
        print("\nIn progress — %d" % len(in_progress))
        for c in in_progress:
            print("  %-34s mastery %.2f  scaffold %s" % (c.id[:34], c.mastery, c.scaffold))
    if blocked and args.show_blocked:
        print("\nBlocked — %d" % len(blocked))
        for c in blocked:
            print("  %-34s missing: %s" % (c.id[:34], ", ".join(c.missing_prereqs(graph))))
    return 0


def _last_session_per_domain(data_dir):
    last = {}
    for _, fm in load_notes(data_dir, "Sessions"):
        date = parse_date(fm.get("date"))
        if not date:
            continue
        for tag in (fm.get("domains") or []):
            tag = str(tag).strip()
            if not tag:
                continue
            parts = tag.split("/")
            for i in range(1, len(parts) + 1):
                parent = "/".join(parts[:i])
                if parent not in last or last[parent] < date:
                    last[parent] = date
    return last


def cmd_index(args, ctx):
    data_dir, graph, today = ctx["data"], ctx["graph"], ctx["today"]
    last_session = _last_session_per_domain(data_dir)

    rows = []
    for domain in all_domains(graph):
        members = [c for c in graph.values() if c.in_domain(domain)]
        if not members:
            continue
        counts = {s: 0 for s in STAGES}
        for c in members:
            counts[c.stage if c.stage in counts else "unseen"] += 1
        due = sum(1 for c in members if c.next_review and c.next_review <= today)
        frontier = sum(1 for c in members
                       if stage_rank(c.stage) < stage_rank("practicing") and c.unlocked(graph))
        rows.append({
            "domain": domain, "concepts": len(members), "mastered": counts["mastered"],
            "practicing": counts["practicing"], "introduced": counts["introduced"],
            "due": due, "frontier": frontier,
            "last_session": last_session.get(domain).isoformat()
                            if last_session.get(domain) else "—",
        })

    lines = ["---", "type: index", "updated: %s" % today, "---", "# Learner index", "",
             "One line per domain. Regenerated by `tutor.py index` at every `/wrap`.", ""]
    lines.append("| Domain | Concepts | Mastered | Practicing | Introduced | Due now | "
                 "Frontier | Last session |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for r in rows:
        lines.append("| %s | %d | %d | %d | %d | %d | %d | %s |"
                     % (r["domain"], r["concepts"], r["mastered"], r["practicing"],
                        r["introduced"], r["due"], r["frontier"], r["last_session"]))
    if not rows:
        lines.append("| _no concepts yet_ | 0 | 0 | 0 | 0 | 0 | 0 | — |")
    lines += ["", "Total concepts: %d · due now: %d"
              % (len(graph), sum(1 for c in graph.values()
                                 if c.next_review and c.next_review <= today)), ""]

    path = os.path.join(data_dir, "Learner", "index.md")
    existing_threads = ""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            m = re.search(r"(?ms)^##\s+Open threads\s*$.*", fh.read())
        if m:
            existing_threads = m.group(0).rstrip() + "\n"
    lines.append(existing_threads or "## Open threads\n<!-- Carry-over items and parked "
                                     "tangents worth returning to. -->\n")
    content = "\n".join(lines)

    if args.dry_run:
        print(content)
        return 0
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content if content.endswith("\n") else content + "\n")
    print("Wrote %s — %d domain(s), %d concept(s)."
          % (os.path.relpath(path, data_dir), len(rows), len(graph)))
    return 0


def _session_dates_in_log(path):
    """Distinct observation dates already in a concept's log."""
    dates = set()
    try:
        with open(path, "r", encoding="utf-8") as fh:
            body = fh.read()
    except (IOError, OSError):
        return dates
    log = re.search(r"(?ms)^##\s+Log\s*$(.*)", body)
    if not log:
        return dates
    for m in re.finditer(r"^\s*-\s+(\d{4}-\d{2}-\d{2})", log.group(1), re.M):
        dates.add(m.group(1))
    return dates


def cmd_record(args, ctx):
    data_dir, graph, today = ctx["data"], ctx["graph"], ctx["today"]
    concept = graph.get(args.concept)
    if concept is None:
        raise TutorError(
            "No concept note for '%s'. The cartographer drafts concepts (reuse before "
            "create); this script only records evidence against one that exists."
            % args.concept)
    if args.score not in (0.0, 0.5, 1.0):
        raise TutorError("--score must be 0, 0.5 or 1 (got %s)" % args.score)
    if args.hints < 0:
        raise TutorError("--hints cannot be negative")

    weight = 0.5 if args.weight == "half" else 1.0
    effective = max(0.0, args.score - HINT_PENALTY * args.hints)
    old_mastery = concept.mastery
    new_mastery = old_mastery + MASTERY_STEP * weight * (effective - old_mastery)
    new_mastery = min(1.0, max(0.0, new_mastery))

    evidence = concept.evidence_count + 1
    sessions = len(_session_dates_in_log(concept.path) | {today.isoformat()})
    transfer_seen = args.transfer or "transfer" in " ".join(concept.misconceptions).lower()

    stage = concept.stage
    if stage_rank(stage) < stage_rank("introduced"):
        stage = "introduced"
    if stage == "introduced" and evidence >= PRACTICING_MIN_EVIDENCE:
        stage = "practicing"
    if (new_mastery >= MASTERY_BAR and evidence >= MASTERY_MIN_EVIDENCE
            and sessions >= MASTERY_MIN_SESSIONS and (args.transfer or args.project)):
        stage = "mastered"
    elif stage == "mastered" and new_mastery < MASTERY_BAR:
        stage = "practicing"       # mastery is revocable; the bar is not a ratchet

    interval = next_interval(concept.interval_days, args.score)
    next_review = today + dt.timedelta(days=interval)

    updates = {
        "stage": stage,
        "mastery": "%.2f" % new_mastery,
        "evidence_count": evidence,
        "last_seen": today.isoformat(),
        "next_review": next_review.isoformat(),
        "interval_days": interval,
    }
    if args.scaffold:
        updates["scaffold"] = args.scaffold
    if args.misconception:
        misconceptions = list(concept.misconceptions)
        if args.misconception not in misconceptions:
            misconceptions.append(args.misconception)
        updates["misconceptions"] = misconceptions

    verdict = {0.0: "miss", 0.5: "partial", 1.0: "correct"}[args.score]
    detail = [verdict]
    if args.hints:
        detail.append("%d hint%s" % (args.hints, "" if args.hints == 1 else "s"))
    if weight == 0.5:
        detail.append("half weight")
    if args.transfer:
        detail.append("transfer")
    if args.project:
        detail.append("project milestone")
    source = args.source or "unrecorded"
    log_line = "- %s · [[%s]] · %.2f → %.2f · %s" % (
        today, source, old_mastery, new_mastery, ", ".join(detail))

    if args.dry_run:
        print("would set: %s" % json.dumps(updates, sort_keys=True))
        print("would append: %s" % log_line)
        return 0

    write_frontmatter_values(concept.path, updates)
    append_log_line(concept.path, log_line)
    print("%s · %.2f → %.2f · %s · stage %s · next review %s (in %dd)"
          % (concept.id, old_mastery, new_mastery, verdict, stage, next_review, interval))

    # A correct answer gives each direct prerequisite partial review credit: the
    # prerequisite was just exercised inside a harder problem, so its next review moves
    # half an interval later. Mastery does not move — this is credit, not an observation.
    if args.score == 1.0 and not args.no_prereq_credit:
        for req in concept.requires:
            parent = graph.get(req)
            if parent is None or not parent.next_review or parent.interval_days <= 0:
                continue
            shift = max(1, parent.interval_days // 2)
            shifted = parent.next_review + dt.timedelta(days=shift)
            write_frontmatter_values(parent.path, {"next_review": shifted.isoformat()})
            append_log_line(parent.path,
                            "- %s · [[%s]] · review credit from [[%s]] · +%dd, "
                            "next review %s" % (today, source, concept.id, shift, shifted))
            print("  prereq %s · next review %s (+%dd)" % (parent.id, shifted, shift))
    return 0


def _stage_class(concept, frontier_ids):
    if concept.id in frontier_ids:
        return "frontier"
    return concept.stage if concept.stage in STAGES else "unseen"


def cmd_maps(args, ctx):
    data_dir, graph, today = ctx["data"], ctx["graph"], ctx["today"]
    domains = [args.domain] if args.domain else all_domains(graph)
    if not domains:
        print("No domains yet — nothing to map.")
        return 0
    written = []
    for domain in domains:
        members = {c.id: c for c in graph.values() if c.in_domain(domain)}
        if not members:
            continue
        frontier_ids = {c.id for c in members.values()
                        if stage_rank(c.stage) < stage_rank("practicing") and c.unlocked(graph)}

        # Large domains show the frontier and two hops around it; Obsidian's graph view of
        # Concepts/ is the place to see everything at once.
        selected, truncated = set(members), False
        if len(members) > MAP_NODE_BUDGET:
            truncated = True
            seeds = frontier_ids or {c.id for c in members.values() if c.stage == "practicing"}
            seeds = seeds or set(list(members)[:1])
            selected = set(seeds)
            # Two hops is the minimum radius; keep adding rings while the budget allows,
            # because in a long chain two hops is only five nodes and reads as nothing.
            for hop in range(MAP_MAX_HOPS):
                if hop >= MAP_HOPS and len(selected) >= MAP_NODE_BUDGET:
                    break
                ring = set()
                for cid in selected:
                    concept = members.get(cid)
                    if not concept:
                        continue
                    ring |= {r for r in concept.requires if r in members}
                    ring |= {other.id for other in members.values() if cid in other.requires}
                if not ring - selected:
                    break
                selected |= ring
            selected = set(sorted(selected)[:MAP_NODE_BUDGET])

        lines = ["```mermaid", "graph TD"]
        for cid in sorted(selected):
            concept = members[cid]
            lines.append('    %s["%s"]' % (sanitize_node_id(cid), cid))
        for cid in sorted(selected):
            for req in members[cid].requires:
                if req in selected:
                    lines.append("    %s --> %s" % (sanitize_node_id(req), sanitize_node_id(cid)))
        lines += [
            "    classDef mastered fill:#b7e4c7,stroke:#2d6a4f,color:#081c15",
            "    classDef practicing fill:#bde0fe,stroke:#1d4e89,color:#03045e",
            "    classDef introduced fill:#ffe5a5,stroke:#b07d00,color:#3d2c00",
            "    classDef unseen fill:#e9ecef,stroke:#adb5bd,color:#343a40",
            "    classDef frontier fill:#ffd6e0,stroke:#c9184a,stroke-width:4px,color:#590d22",
        ]
        by_class = {}
        for cid in sorted(selected):
            by_class.setdefault(_stage_class(members[cid], frontier_ids), []).append(
                sanitize_node_id(cid))
        for klass, ids in sorted(by_class.items()):
            lines.append("    class %s %s" % (",".join(ids), klass))
        lines.append("```")

        header = [
            "---", "type: map", "domain: %s" % domain, "updated: %s" % today,
            "nodes: %d" % len(selected), "---", "# Map · %s" % domain, "",
        ]
        if truncated:
            header += ["Showing the frontier and at least %d hops around it — %d of %d concepts. "
                       "Obsidian's graph view of `Concepts/` shows the whole domain."
                       % (MAP_HOPS, len(selected), len(members)), ""]
        footer = ["", "Legend: mastered (green), practicing (blue), introduced (amber), "
                      "unseen (grey). Frontier concepts are outlined in pink.", ""]

        path = os.path.join(data_dir, "Maps", "%s.md" % tag_to_filename(domain))
        content = "\n".join(header + lines + footer)
        if args.dry_run:
            print(content)
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(content if content.endswith("\n") else content + "\n")
            written.append((os.path.relpath(path, data_dir), len(selected)))
    for rel, count in written:
        print("Wrote %s — %d node(s)." % (rel, count))
    if not written and not args.dry_run:
        print("No maps written.")
    return 0


def _git(data_dir, argv):
    return subprocess.run(["git", "-C", data_dir] + argv, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, universal_newlines=True)


def cmd_check(args, ctx):
    """List closed notes that differ from their last commit.

    This is what makes a hand edit to the record visible rather than silent. It reports;
    it never reverts. The notebook belongs to the learner.
    """
    data_dir = ctx["data"]
    top = _git(data_dir, ["rev-parse", "--show-toplevel"])
    if top.returncode != 0:
        print("Not a git repository — no commit to compare against. "
              "Run /setup to create one if you want the visible edit trail.")
        return 0
    toplevel = top.stdout.strip()

    closed = []
    for subdir in ("Sessions", "Assessments"):
        for path, fm in load_notes(data_dir, subdir):
            if str(fm.get("status") or "").strip() == "closed":
                closed.append(path)
    if not closed:
        print("No closed notes yet.")
        return 0

    changed, untracked = [], []
    for path in closed:
        rel = os.path.relpath(os.path.abspath(path), toplevel)
        status = _git(data_dir, ["status", "--porcelain", "--", rel])
        if status.returncode != 0:
            continue
        line = status.stdout.strip()
        if not line:
            continue
        code = line[:2]
        (untracked if code.strip() == "??" else changed).append((rel, code))

    if not changed and not untracked:
        print("All %d closed note(s) match their last commit." % len(closed))
        return 0
    if changed:
        print("Closed notes changed since their last commit — %d:" % len(changed))
        for rel, code in changed:
            print("  [%s] %s" % (code.strip(), rel))
    if untracked:
        print("Closed notes never committed — %d:" % len(untracked))
        for rel, _ in untracked:
            print("  %s" % rel)
    print("\nThe record stands as committed; mastery came from the concept logs, not from "
          "these files. Mention the change and carry on.")
    return 2 if (changed or untracked) and args.strict else 0


def _closed_notes(data_dir):
    out = []
    for subdir in ("Sessions", "Assessments"):
        for path, fm in load_notes(data_dir, subdir):
            if str(fm.get("status") or "").strip() == "closed":
                out.append(path)
    return out


def cmd_lock(args, ctx):
    """Optionally make closed notes read-only at the file-system level.

    Off by default, and git already makes a later edit visible, so this is belt and
    braces. Some sync services handle read-only files badly — hence the warning rather
    than making it the default.
    """
    data_dir = ctx["data"]
    notes = _closed_notes(data_dir)
    if not notes:
        print("No closed notes yet.")
        return 0
    changed = 0
    for path in notes:
        mode = os.stat(path).st_mode & 0o777
        want = mode & ~0o222 if not args.unlock else mode | 0o200
        if want != mode:
            os.chmod(path, want)
            changed += 1
    verb = "unlocked" if args.unlock else "locked"
    print("%s %d of %d closed note(s)." % (verb.capitalize(), changed, len(notes)))
    if not args.unlock and changed:
        print("Edits to them will no longer save. Turn this off with `tutor.py lock "
              "--unlock` if your sync service copes badly with read-only files.")
    return 0


# ----------------------------------------------------------------------------- setup

def resolve_data_dir(explicit):
    """--data, then $TUTOR_DATA, then the `Data folder:` line in CLAUDE.local.md."""
    if explicit:
        return os.path.abspath(os.path.expanduser(explicit))
    env = os.environ.get("TUTOR_DATA")
    if env:
        return os.path.abspath(os.path.expanduser(env))
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    local = os.path.join(repo, "CLAUDE.local.md")
    if os.path.exists(local):
        with open(local, "r", encoding="utf-8") as fh:
            m = re.search(r"(?im)^\s*Data folder:\s*`?([^`\n]+)`?\s*$", fh.read())
        if m:
            return os.path.abspath(os.path.expanduser(m.group(1).strip()))
    raise TutorError(
        "No data folder. Pass --data DIR, set TUTOR_DATA, or run /setup to write "
        "CLAUDE.local.md.")


def build_parser():
    p = argparse.ArgumentParser(
        prog="tutor.py", description="Deterministic bookkeeping for the personal tutor.")
    p.add_argument("--data", help="path to the learning data folder")
    p.add_argument("--today", help="override today's date, YYYY-MM-DD (for testing)")
    sub = p.add_subparsers(dest="command")

    d = sub.add_parser("due", help="concepts whose review is due")
    d.add_argument("--domain")
    d.add_argument("--limit", type=int, default=15,
                   help="cap the list (default 15); 0 for no cap")
    d.add_argument("--json", action="store_true")
    d.set_defaults(func=cmd_due)

    f = sub.add_parser("frontier", help="concepts unlocked for new teaching")
    f.add_argument("--domain")
    f.add_argument("--show-blocked", action="store_true")
    f.add_argument("--json", action="store_true")
    f.set_defaults(func=cmd_frontier)

    i = sub.add_parser("index", help="regenerate Learner/index.md")
    i.add_argument("--dry-run", action="store_true", help="print instead of writing")
    i.set_defaults(func=cmd_index)

    r = sub.add_parser("record", help="apply a graded observation to a concept")
    r.add_argument("concept")
    r.add_argument("--score", type=float, required=True, help="1, 0.5 or 0")
    r.add_argument("--hints", type=int, default=0, help="hint levels used")
    r.add_argument("--source", help="note anchor, e.g. 2026-10-06-probability#Q4")
    r.add_argument("--weight", choices=["full", "half"], default="full",
                   help="half for a check for understanding inside a lesson")
    r.add_argument("--scaffold", choices=["worked", "completion", "independent", "transfer"])
    r.add_argument("--transfer", action="store_true", help="this was a transfer item")
    r.add_argument("--project", action="store_true", help="this was a project milestone")
    r.add_argument("--misconception", help="tag a misconception on the concept")
    r.add_argument("--no-prereq-credit", action="store_true")
    r.add_argument("--dry-run", action="store_true")
    r.set_defaults(func=cmd_record)

    m = sub.add_parser("maps", help="regenerate Maps/<domain>.md")
    m.add_argument("--domain", help="one domain tag; omit for all")
    m.add_argument("--dry-run", action="store_true")
    m.set_defaults(func=cmd_maps)

    k = sub.add_parser("lock", help="make closed notes read-only (optional, off by default)")
    k.add_argument("--unlock", action="store_true", help="make them writable again")
    k.set_defaults(func=cmd_lock)

    c = sub.add_parser("check", help="closed notes changed since their last commit")
    c.add_argument("--strict", action="store_true", help="exit 2 if anything changed")
    c.set_defaults(func=cmd_check)
    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 1
    try:
        data_dir = resolve_data_dir(args.data)
        if not os.path.isdir(data_dir):
            raise TutorError("Data folder does not exist: %s" % data_dir)
        today = parse_date(args.today) or dt.date.today()
        if args.today and today is None:
            raise TutorError("--today must be YYYY-MM-DD")
        ctx = {"data": data_dir, "today": today, "graph": load_concepts(data_dir)}
        return args.func(args, ctx)
    except TutorError as exc:
        sys.stderr.write("tutor.py: %s\n" % exc)
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
