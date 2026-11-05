---
name: session-transcript-recovery
description: "Use when a file is overwritten: rebuild from the transcript."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [recovery, sessions, state-db, transcript, concurrent-writes]
    related_skills: [session-librarian, file-organization]
---

# Recovering lost work from a session transcript

Every message **and every tool call** a Hermes session makes is stored in `state.db`, including
the full content passed to `write_file` and both sides of every `patch`. A file that no longer
exists on disk can therefore be rebuilt exactly enough to trust.

## When to use

- A deliverable was **overwritten** — usually two sessions (or two runs of the same brief)
  writing one path.
- A file was deleted, reverted, or truncated and there is no backup.
- A build stopped mid-way and the surviving artifact has to match documentation that cites it.
- **The user's own request is the thing that went missing** — "how is the X I asked for going?" arrives
  after compaction has dropped which file X was. Recover their words from the store (`role='user'` and
  `content LIKE '%<phrase they actually used>%'`), not by guessing from the topic sentence in front of
  you, then read the sessions after that timestamp to establish how far the work really got — an abandoned
  half-build and a finished artifact need opposite replies.

## Prevention first

**One writer per output path.** Two sessions must never target one output path; give parallel
builds their own scope folder so each has exactly one `index.html` (or one report, one notebook).

When `write_file` warns that a **sibling session modified the file** and you have not read it,
treat that as a stop signal: read the file first, or write somewhere else. That warning is the
last chance before the other build is destroyed — writing through it is how the loss happens.

## Procedure

**1. Find the session.** Query the message store for anything that touched the path. Both
`tool_calls` (the request) and `content` (results and messages) are searchable:

```python
con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)          # db = .../hermes/state.db
rows = con.execute("""SELECT s.id, s.title, s.last_activity_at, s.message_count
                      FROM sessions s WHERE s.id IN
                        (SELECT DISTINCT session_id FROM messages
                         WHERE tool_calls LIKE ? OR content LIKE ?)
                      ORDER BY s.last_activity_at DESC""", (f"%{frag}%", f"%{frag}%")).fetchall()
```

Session ids are `<YYYYMMDD>_<HHMMSS>_<hash>`; `last_activity_at` sorts them. Confirm the id and
title against the work you are hunting before going further. Open read-only (`mode=ro`) — the app
is usually running and holds the database.

**2. Pair each call with its RESULT.** A call's request arguments hold whatever the author typed —
often a bare filename — so two different files look identical in a truncated print. The message
whose `tool_call_id` matches the call id carries the authoritative `resolved_path` and `success`:

```python
results = {m[4]: m for m in msgs if m[4]}     # tool_call_id -> result row
res = results.get(call_id)
info = json.loads(res[5]) if res else {}      # {'resolved_path': ..., 'success': True, ...}
```

Tool calls live in `messages.tool_calls` as JSON: `[{id, call_id, function:{name, arguments}}]`
where `arguments` is itself a JSON string. Print `resolved_path`, not the request path, when
deciding which file an operation touched.

**3. Replay.** Take the **last full-file write as the base**, then apply every later `patch` to
that same path **in timestamp order**, skipping any whose result reported `success: false` — the
author almost always retried it, and applying a failed patch double-applies the change. Patch
matching is exact for these: the `old_string` came from the file as it really was. If an exact
match fails, fall back to a line-ending / trailing-whitespace-normalised match, and report any
step that needed the fallback.

**4. Verify before restoring.** Write the reconstruction to a temporary name **inside the target
folder** first — relative paths to `lib/`, `assets/` or sibling files only resolve from there —
and then:

- check the line count against any documentation the author left (a `NOTES.md` claiming
  "~1820 lines" is a real assertion you can test);
- grep for markers that must be present;
- actually run it (open the page, parse the file).

Only then swap it into place.

**5. Keep both, and record it.** Move the other artifact aside under a distinct name rather than
deleting it — the user decides which survives. Append to the scope's `_manifest.md`: what was
recovered, the evidence, and which file was the second writer's.

## Recovering a tool's OUTPUT, not a file

The same table is the record of what a tool actually returned — which matters when the reading was
lossy and one-shot:

- A `vision_analyze` transcription of a photographed problem statement or slide, a long command's
  stdout, an extraction dump: all of it sits in the result row's `content`.
- **Check the store before reading the image again.** Fresh reads of one photograph disagree with each
  other — a crop drops the sub-part numbering the full frame carried, and a re-read re-words a
  transcribed sentence — whereas the stored first read is a fixed artifact you can quote and diff
  against. This is also how a question's exact literal wording is recovered after compaction has taken
  the visible context.
- **Those differences are the signal, not noise.** When two readings of the same figure disagree (how
  many sub-parts the sheet has, which symbol a label uses), the discrepancy itself is worth reporting to
  the user rather than silently picking one.
- Query shape: filter `messages` on `content LIKE '%<distinctive fragment>%'`, print
  `substr(content,1,2000)` with the message id and timestamp, then widen by `session_id` once the right
  session is known. Column names for role and tool name differ across schema versions — run
  `PRAGMA table_info(messages)` instead of assuming them.

## What you can and cannot claim

**Byte-identity is not provable.** Say what you actually have: every patch applied with an exact
match, the line count matching the author's own documentation, the required markers present, and
the artifact running. Anyone reading that can judge the reconstruction; "recovered perfectly"
cannot be judged and is not true.

## Pitfalls

- **Do not trust the request path.** It is what the author typed. Only the result's
  `resolved_path` says which file an operation actually touched.
- **Do not replay a failed patch.** Read each result's `success` first.
- **Reconstruct before overwriting.** Verify the rebuild at a temporary path; swapping first
  destroys the only other copy.
- **A stale comment in the recovered file is a defect to report, not to silently fix.** If the
  header says one stage and the body contains a later stage's code, say so and leave the fix to
the stage that owns it.
- **Session search tools are for content; this is for payloads.** `session_search` surfaces
  conversational context, not tool-call arguments — go to `state.db` for the bytes.
