---
name: media-reports
description: "Use when producing reports with embedded figures and video."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [report, html, docx, video, ffmpeg, media]
    category: productivity
---

# Media-embedded reports (figures + video)

Produce a report/deliverable that embeds images AND video for a research user
(experiment/paper reports). The user's preferred deliverable set: **a
self-contained HTML page (bilingual EN + CN) that plays the videos anywhere**,
plus a **Word .docx** for editing/submission (the .mp4s travel alongside).

## When to Use
- The user asks for a report, write-up, or deliverable that must include images
  and/or video (experiment reports, project write-ups, demo/showcase pages).
- The figures and a demo/rollout video need to live in one document that will be
  shared or shown.
- Producing a self-contained HTML page where video plays offline/anywhere, or a
  Word file for editing/submission.

## Deliverable preferences (always-on)
- Produce English first, then a Chinese version (user preference).
- HTML must be **self-contained**: embed images AND videos so it opens and plays
  offline and is trivial to send. Do not use relative paths to local files —
  that breaks the moment the file moves or is shared.
- Sharing over WeChat: WeChat does not render arbitrary HTML inside the chat
  bubble, so the recipient must download and open it in a browser (it plays
  there). A PDF opens instantly everywhere but does NOT play video — state this
  trade-off instead of silently picking one.
- Word is for editing/submission, not playback: Word and mobile viewers do not
  reliably play embedded video. Embed a poster frame per video, caption it, and
  list the .mp4 filenames, shipping the files alongside.

## Workflow
1. **Ground the content before writing**: list the media folder, probe video
   specs (`ffprobe -show_entries format=duration,size -show_entries stream=width,height,r_frame_rate,codec_name`),
   and VIEW each image before captioning. Never invent a caption from a filename.
2. **Transcode videos to H.264 for browser playback.** HEVC/H.265 source does not
   play in most browsers (Firefox especially). Pitfall: the conda `ffmpeg` build
   on this machine ships only `h264_mf` (no libx264), so `-preset`/`-crf` fail
   with "Unrecognized option". Check `ffmpeg -encoders`, then encode with
   `-c:v h264_mf -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 96k`.
3. **Build the self-contained HTML** by base64-embedding the images and the
   transcoded videos as `data:` URIs (`data:image/jpeg;base64,...`,
   `data:video/mp4;base64,...`). A ~6 MB page with three clips is fine. Build it
   programmatically (read file bytes → base64 → write HTML) so the large strings
   never round-trip through the chat.
4. **Word version (python-docx):**
   - Pitfall: python-docx raises `UnrecognizedImageError` on some valid JPEGs
     (ffmpeg writes a non-JFIF comment header `FF D8 FF FE`). Re-save a clean
     baseline JPEG with PIL first:
     `Image.open(f).convert('RGB').save(out,'JPEG',quality=88,subsampling=0)`.
   - Pitfall: `doc.add_table(rows=N, cols=M)` — for a header + D data rows create
     with `rows = 1 + len(data)`, and DEFINE the `hdr`/data lists BEFORE the
     `add_table` call (declaring them after raises NameError; creating rows=2
     when there are 2 data rows raises IndexError).
   - Extract a poster frame per video
     (`ffmpeg -ss N -i in.mp4 -frames:v 1 -q:v 3 out.jpg`) for the Word doc,
     captioned with duration/resolution.
5. **Verify before delivering**: no leftover placeholder tokens, expected media
   count (`<video>` tags, embedded `data:` URIs, `word/media/` entries in a
   .docx), and validate a generated .docx (`docx_validate.py`) then read back its
   structure.

## Pitfalls
- Transcode BEFORE embedding; embedding HEVC gives the reader a video they cannot
  play.
- Re-save ffmpeg JPEGs via PIL, or the .docx build fails at embed time.
- Keep placeholders for data the user will supply later (eval numbers, a
  not-yet-recorded video) rather than fabricating claims.
- The user streams output during an active experiment; log events into a dated
  session log as they arrive so the final report assembles from recorded facts
  rather than one big retrospective.
