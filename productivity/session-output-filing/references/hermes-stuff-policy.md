# <archive> — filing policy (quick reference)

Mirrors `_ORGANIZATION_PROMPT.md` in the archive root. That file is authoritative;
re-read it if anything here looks stale.

Archive root: `C:\Users\<you>\OneDrive\Documents\<archive>`

## The one rule
Deliverables in `01_Documents/`, everything else in its numbered category. Nothing
loose in the root. Default to filing, not dumping.

## Destination map (decide with the column that fits first)
| Created/modified thing | Destination |
|---|---|
| PDF, report, final document | `01_Documents/PDF/` |
| Word `.docx` deliverable | `01_Documents/DOCX/` |
| Excel `.xlsx` / `.csv` deliverable | `01_Documents/XLSX/` |
| Web app you built (scaffold/source/dist) | `01_Documents/WebApps/<name>/` |
| Other binary/format artifact (CAD `.step`/`.stl`, mesh, etc.) | `01_Documents/<TYPE>/` |
| Reusable knowledge, quality guide, adopted skill docs | `02_Reference/` |
| Safety backup taken before modifying a skill/config | `03_Backups/<name>/` |
| Sketch, WIP, note, scratch, unfinished thing | `02_Reference/` or a scratch subfolder — never loose |
| Session log / what-did-I-do record | `04_Session-Logs/<date>_<topic>/manifest.md` |

Working files under `~` or in Temp are NOT final homes. If you created it for the
user, copy it into the archive.

## Hard rules
1. Filename → the destination folder. Categorize by content type, not by variable name.
2. **Copy, don't move, live/working things.** Skills, config, and anything the system
   must keep running (files under `~/AppData/Local/hermes/...`) stay where they are;
   the archive holds a **copy** plus a manifest note pointing at the real location.
   Only move standalone, finished artifacts.
3. Keep the archive synced with reality: mirror every filing into the session manifest
   and refresh `README.md` if the structure changed.
4. If the target folder doesn't exist, create it under the category that fits. Never
   create a loose file in the archive root.
5. One session = one manifest: `04_Session-Logs/<YYYY-MM-DD>_<topic>/manifest.md`
   with a table of Item | Type | Status | Live path | Archive path, plus Backups and
   Notes sections.

## Manifest template
```markdown
# <date>_<topic> — session manifest
## Created / modified
| Item | Type | Status (created/modified/moved/copied) | Live path | Archive path |
|---|---|---|---|---|
## Backups taken this session
## Notes / caveats
```

## Shared folder caution
Another agent ("kimi") files here too. Leave its files (kimi-*, docskills-backup,
webapp-scaffold, its session manifest) untouched; refresh only the shared root
`README.md` index.
