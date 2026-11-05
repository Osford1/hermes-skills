---
name: session-output-filing
description: File a task's deliverables into the user's archiving scheme.
version: 1.0.0
metadata:
  hermes:
    tags: [filing, organizing, archive, deliverables, session-log]
    category: productivity
---

# Session output filing & archive organization

## Use when
A Hermes task finished and produced deliverable files for the user (a document, CAD
file, web-app scaffold, backup, config, reference note) sitting in a working dir,
Temp, or the project folder. The user keeps an organized archive; the agent is
responsible for filing outputs and never leaving loose files the user must hunt for.

## The user's archive
Path: `C:\Users\<you>\OneDrive\Documents\<archive>`
A standing policy lives there: `_ORGANIZATION_PROMPT.md` — **READ IT FIRST**. It may
have been updated and is authoritative (takes precedence over this summary). Load
`references/hermes-stuff-policy.md` for the full destination map + rules.

### Verify the live layout before creating anything
The archive gets restructured. The numbered-category map (`01_Documents/`,
`04_Session-Logs/`) has in practice been superseded by a **scope-first** layout, so
`ls` the archive root and the intended target dir first, and copy the shape of the
neighbouring entries instead of trusting this file or your memory of it:

- `Sessions/<YYYY-MM-DD>-<topic>/` — one dir per session/task, containing
  `Deliverables/` (what the user asked for), `Working/` (extracted source text,
  intermediate data worth keeping), `Reference/` (source material), plus
  `_manifest.md` at the session-dir root (underscored, not `manifest.md`, not nested).
- `Projects/<name>/` — same three subdirs, for ongoing work.

Manifest body that has worked: a **What this is** line tying the files to the user's
request, **Source** (input paths), **Deliverables** (path + one line each), then
**Notes/Flags** for anything the user should check or that you got wrong first and
corrected. Never invent a top-level catch-all folder to satisfy a stale map — the live
tree and `_ORGANIZATION_PROMPT.md` win, and this skill gets patched.

## Top rules
1. Deliverables → `01_Documents/<type>/`; everything else → its numbered category.
2. **Copy, don't move** live/working things (installed skills, config, venvs, files
   under `~/AppData/Local/hermes`). The archive holds a copy + a pointer note; only
   move standalone finished artifacts.
3. Categorize by content type (format), not by what you happened to name a variable.
4. Never put a loose file in the archive root. If a category folder doesn't exist,
   create it under the correct numbered category.
5. One session = one manifest at `04_Session-Logs/<YYYY-MM-DD>_<topic>/manifest.md`,
   tabular: Item | Type | Status (created/modified/moved/copied) | Live path | Archive
   path, plus a Backups-taken section and a Notes/Caveats section.

## Gotchas (learned the hard way this session)
- **Check for a concurrent/sibling agent.** The archive may be shared — another
  agent may be filing into it. Don't clobber its README/manifest; leave its files
  alone, and only refresh the shared root `README.md` index to reflect both.
- **Don't invent a new top-level category** the policy map doesn't define (a bare
  `Markdown/`, a flat top-level session-log file). Fold reference `.md` into
  `02_Reference/` and session text into the session manifest instead.
- **Skim `_ORGANIZATION_PROMPT.md` before filing** — it encodes the user's real
  preference. Misfiling then realigning wastes effort.
- If you write a root `README.md`, verify you weren't clobbering another agent's
  version; rebuild it as an index covering both sessions.

## Verify
After filing: list the tree (`find "<archive>" -maxdepth 2`), confirm each category
has only expected content and the manifest exists, confirm sibling files are
untouched, then report the resulting map to the user.
