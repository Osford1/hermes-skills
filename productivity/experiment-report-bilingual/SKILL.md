---
name: experiment-report-bilingual
description: "Use when building a bilingual (EN+CN) report with media."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [report, bilingual, html, video, experiment, so-101, srt]
    related_skills: [lerobot-embodied-ai, dokument-skiel, web-design-recipes]
---

# Bilingual EN+CN experiment report (self-contained, embedded media)

Build the user's lab-experiment report as a **single self-contained HTML file** with the
photographs and videos embedded (base64), so it opens/plays anywhere and shares as one file.
Produce **both English and Chinese** versions (EN first, then CN).

## When to Use
- User asks for a lab-experiment report that must include photos and videos.
- The report should be bilingual (English + Chinese) and self-contained/shareable.
- Any video that must play in a browser when the source `.mp4` is HEVC/H.265.

## Media & location conventions
- Raw media (images + MP4s) and the report live in the experiment date folder, e.g.
  `C:\Users\<you>\OneDrive\Documents\Desktop\Others\SRT project\<YYYY-MM-DD>\`.
  Put the report HTML *next to* the media; keep a `_report_work\` subdir for transcoded copies.
- During recording, the demo/policy videos come in as separate `.mp4` files; figure/video
  captions must be written from **what the images actually show** (`vision_analyze`), not assumed.

## THE ffmpeg transcode quirk (must-do)
The miniconda FFmpeg (6.1.1, Windows clang build) ships **only `h264_mf`** — there is **no
libx264**, so `-crf`/`-preset` are **unrecognized and fail** (`Unrecognized option 'preset'`).
The source arm videos are **HEVC/H.265**, which most browsers won't play. So transcode to H.264
with the MediaFoundation encoder:
```bash
"$MINICONDA/Library/bin/ffmpeg" -hide_banner -y -i "in.mp4" \
  -c:v h264_mf -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 96k "out.h264.mp4"
```
(drop `-preset`/`-crf`; they only exist for x264). Probe specs with
`ffprobe -show_entries format=duration,size -show_entries stream=width,height,r_frame_rate`.

## Reusable builder — `scripts/build_consolidated_report.py`
Don't hand-write a new build script per report. This template takes two content files written in a
tiny markup (`# / ## / ###` headings, `~ ` meta lines, `| ` tables, `- ` bullets, `> ` note
callouts, ``` code blocks, `[FIG:key|caption]`, `[VID:key|caption]`) and emits **all four
deliverables** in one run: self-contained EN + CN HTML (base64 media, videos play) and EN + CN
.docx (posters + captions). Edit only the three project-specific blocks at the top — `BASE`/`SRC`
paths, the `COPIES` media map, and the `FIG_FILE`/`VID_FILE`/`VID_LABEL` maps. It re-saves every
JPEG through PIL into `_report_work/clean/` before docx embedding, which is what avoids
`UnrecognizedImageError`. Verify after running (it prints the counts): `<video>`=n, `<img>`=n,
`placeholders=0`, plus `docx_validate.py` ok and `word/media/` entry count.

## Consolidation reports (multi-session, not just one lab day)
When asked to "put all the experiment data in a report", the deliverable is an *audit* of the
whole series, not a prettier version of one day's report. Same structure plus:
- a **master run log** table — every run ever (date, cell, E, S, observed outcome, evidence file);
- a **results table with its real status**, using `NOT MEASURED` / `not recorded` for values that
  were never actually captured, never a plausible-looking number;
- a **data-gap table** (what's missing, why it matters, how to close it) and an ordered next-session plan;
- a **provenance table** mapping every claim to the file it came from, closing with a line stating
  nothing was inferred or interpolated.
Gaps outrank polish here: the most useful sentence in a consolidation report is usually "every
success-rate cell is empty", not a summary of what the runs looked like.

## Appending a late finding to an existing report (surgical edit)
A result often arrives **after** the report was written ("add the 300,000-step findings to the report
you wrote"). Add one section — do **not** rewrite or re-expand the rest. The standing complaint about
these reports is that they carry too much project detail, and a rewrite reintroduces it.

1. **Back up first**: copy each report HTML into `<date-folder>\_report_work\backup_before_<change>\`
   (copy, never move). These are deliverables; a bad splice is otherwise unrecoverable.
2. Transcode the new clip to H.264 and extract a poster (see the ffmpeg section above), then embed it
   with the **same markup shape the existing figures use** — `<figure><video controls
   preload="metadata" playsinline src="data:video/mp4;base64,…">` + `<figcaption>` — so the file stays
   uniform.
3. **Splice by anchor, never rebuild**: locate the heading of the section the new one should precede
   (`re.search(r'<h2>7\.', t)`), assert the anchor is unique, and insert. Renumber the later headings
   **in descending order** (`8.`→`9.` then `7.`→`8.`); ascending order renumbers the section you just
   moved.
4. Attach the new row to a results table by anchoring on a known cell value (`<td>30,000</td>`) and
   inserting after the next `</tr>` — never by table index, which shifts.
5. **Kill the self-contradiction**: an earlier "next session" line now promises a run that has since
   happened. Append a short "(Superseded — later extended to N steps; see §7.)" *in place* rather than
   deleting the original plan, and stamp a revision date in the footer so the version is identifiable.
6. **Apply the same edit to both language files** even when only one path was given — the EN/CN pair is
   one deliverable, and a half-updated pair is worse than a stale one. Translate the new table row too.
7. **Verify by decoding, not by eye**: `re.findall(r'src="data:video/mp4;base64,([^"]+)"', t)`,
   base64-decode the new entry to a temp file, `ffprobe` it for the expected codec/duration, then count
   `<video>` / `<h2>` and confirm zero leftover `{TOKEN}`s. A malformed splice still looks fine in a
   browser tab that has not been reloaded.
- Values never actually measured stay `not measured` / `未测量` in the added rows. Do not fill a
  success-rate cell just to make the row look complete.
- **Attribute the agent's own analysis visibly** (e.g. `<span class="badge">Hermes</span>` on the
  hypothesis heading): the operator's observations and yours must not read as one voice in a report
  that goes to a supervisor.

## Filling a batch of video placeholders (phone clips → §5 robustness section)

When a placeholder section is filled with a folder of clips the operator filmed on a phone:
- **Probe first**: these are usually **HEVC 720×1280 portrait**, one clip per condition per policy.
  Transcode to H.264 with `-vf scale=480:-2 -c:v h264_mf -rate_control pc_vbr -b:v 350k
  -pix_fmt yuv420p -movflags +faststart -an` — 14 portrait clips ≈ 20 MB → a ≈ 29 MB
  self-contained page. `-an` drops phone audio.
- **Pair by condition, not by filename order**: build one `.vs` grid per condition with the ACT
  clip left, DP clip right, column labels above. Clips whose filenames don't match a placeholder
  (a repeat run, an extra axis) go inside the matching column as a second `<figure>`.
- **Portrait clips need a height cap** or six conditions become a 6000 px wall of video:
  `video.pv{width:auto;max-height:520px;max-width:100%;margin:0 auto}` in a 2-col grid
  (`@media(max-width:760px){grid-template-columns:1fr}`).
- **Do not write per-clip outcome claims.** A vision pass over frames is useful for orientation and
  scene facts, but on these dark, wide shots it gave *contradictory* reads of which tape mark held
  the tin, between two passes over the same clips. Captions therefore stay condition-descriptive
  (condition + clip length + control rate), and placement stays "the operator's judgement" — feeding
  a vision guess into a report that goes to a supervisor is exactly the failure to avoid.
- Verify the finished page **in a browser**, not by eye: `document.querySelectorAll('video').length`,
  every `duration > 0` and `readyState === 4`, `.vs` grid columns resolve to 2, no horizontal
  overflow, and each portrait video centred in its column (`gap_left == gap_right`).

## Stripping a report to one language (EN-only revision)
`report.template.html` is the source of truth — edit the template and re-run the embedder, never
hand-edit `report.html` (it is mostly base64, and a hand edit is unrecoverable). Back up
`report.html`, the template, the embedder and the summary into
`_report_work/backup_before_<change>/` first (copy, never move). Then:
- delete the `.cn` blocks, the `/ 中文` heading halves, and the CN `kpi`/summary text;
- **add a guard to the embedder** so the revision can't silently ship mixed: scan the output for
  `[\u3000-\u303f\u4e00-\u9fff\uff00-\uffef]` and fail the build, plus the usual leftover-token and
  `<video>`/`<source>` count checks. `python scripts/embed_report.py` then prints size + counts.
- keep the bilingual version reachable: the CN half is a regeneration, not a rewrite.

### Producing the other language as a second build
Once one language is clean, build the second as a parallel template — `report.template.html` →
`report.html` (EN) and `report.template.zh.html` → `report.zh.html` (中文) — from one script and one
`TOKENS` map, so the media inventory can never diverge. Three guards earn their keep:
- **language direction both ways**: the EN output must contain *zero* CJK, the CN output must contain
  *thousands* (a count floor, e.g. `> 500`). Only checking "no CJK in EN" lets a language swap ship an
  English file under a Chinese filename.
- **structure parity**: `<h2>` / `<figure>` / `<table>` / `<video>` counts must be equal between the two
  builds; the build fails otherwise. This is what catches a clip or condition added to one template and
  forgotten in the other.
- **slot identity**: hash each `data:` URI in document order and compare the two lists — proves every
  clip sits in the *same* slot in both languages, which `grep`-style checks can't see.
- A green CJK regex still renders as tofu boxes when no CJK font is present. Load the page and read a
  screenshot: quote a heading and two table rows back. Text checks alone cannot detect this.
- Translate table *cells* (result values like `reference`, `operator judgement`) as well as headers;
  leaving them English is the classic half-translated report, and leftover-English greps catch it.

### Bilingual *deck* variants (generator-built, one layout)
When the deliverable is a python-pptx deck built by a generator script rather than HTML, do NOT fork
the generator per language:
- put the second language in a **text-only overlay module** (`content_zh.py`) holding nothing but the
  strings, and select it with an env var (`DECK_LANG=zh`). Sizes, row heights, table columns and
  highlight flags stay in the source-language content list, so the layouts cannot drift;
- have the builder **assert slide count and every list length** against the source language before
  saving. That one assert is what catches a string added to one language and forgotten in the other
  (the deck's equivalent of the `<h2>`/`<figure>` parity guard above);
- add a slide by **appending to the content list and adding its index to the `ORDER` list**, and mirror
  the entry in the overlay in the same edit. Inserting mid-list renumbers every index in `ORDER` and in
  the overlay, so the build reorders silently or trips the assert;
- build to a temp output path via an env var (`DECK_OUT`), never over the delivered file: PowerPoint
  holding the open deck makes `prs.save()` fail *after* truncating the destination;
- review the result as a 4-per-row Pillow contact sheet of the rendered slide PNGs, so one vision pass
  covers every slide of both languages instead of slide-by-slide reads.

## Build the self-contained HTML (Python)
Read each media file, `base64.b64encode`, and inject as a data URI:
- images → `data:image/jpeg;base64,...` in `<img>`
- videos → `data:video/mp4;base64,...` in `<video controls preload="metadata" playsinline>`
Replace template tokens (`{IMG_INIT}`, `{VID_N}`…) then write the file (UTF-8, `<html lang="zh-CN">`
for the CN version). Verify with a count of `<video>`/`<img>` and that no `{TOKEN}` remains.
A 3-video report is ~6 MB — acceptable. Placeholder sections (pending videos, eval numbers,
repo_id) stay as bracketed muted text until supplied.

## Report structure (matches the user's expectation)
1. `Title/meta` (date, robot, task, policy, dataset) → 2. Task background (Figures: start pose,
   goal/end pose) → 3. Setup hardware issue (the camera/arm USB contention — see
   `lerobot-embodied-ai`) → 4. Data collection (episodes) → 5. Single-demo video →
   6. Training runs (smoke vs full; note per-run effect) → 7. Evaluation & results table →
   8. Issues & fixes table. Caption each figure/video with duration/resolution where known.

## Workflow (how the user operates a lab day)
The user **drip-feeds events** while the experiment runs; keep a live
`session-log-<date>.md` (in the project, e.g. `C:\Users\<you>\Desktop\robot_101\`) appending each
event, then **compile the report at day's end**. Mark provisional facts (step counts, outcomes)
and confirm ambiguous numbers — e.g. the user wrote "20000" but the file/plan said **2000**; go
with the filename/plan and flag it.

## Pitfall notes
- Native Windows path with spaces: quote it; pass `C:/...` forward-slash native paths to tools.
- When a shell one-liner gets blocked for over-quoting, verify with `search_files`
  (`output_mode: count`) rather than a shell pipe.
- **Never `grep` one of these reports in the shell.** A self-contained report is mostly base64, so a
  single match prints megabytes into context (and a broad `find` over the home tree can time out).
  Search with `search_files` (ripgrep, bounded output), or filter by extension in Python and skip
  media/asset dirs. Same trap in any directory holding embedded-media reports.
- When generating report HTML from Python, keep the f-string `{…}` expressions free of backslashes and
  same-type nested quotes — the parser rejects them; precompute into a variable and interpolate the name.
- Do NOT re-store the camera-USB arm-connection pitfall here — it lives in
  `lerobot-embodied-ai` under USB bus/port contention.
