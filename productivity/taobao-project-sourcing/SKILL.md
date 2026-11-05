---
name: taobao-project-sourcing
description: "Use when a maker project needs a parts list + build roadmap."
version: 1.1.0
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [bom, sourcing, shopping, maker, roadmap, taobao]
    related_skills: [file-organization, youtube-content]
---

# Maker Project Kit-Out (BoM + Purchase Hints + Build Roadmap)

User wants to build a project from an online tutorial/repo. The agent produces:
1. a normalized BoM with purchase hints (Chinese search terms, expected ¥ ranges, genuine-vs-clone flags),
2. an interactive HTML assembly roadmap,
3. optional customization ideas.

**The USER does all purchasing/sourcing themselves** (their preference, confirmed
2026-08-30). The agent never searches marketplaces or touches carts unless the
user explicitly asks for price research on top.

## User's standing decisions (confirmed 2026-08-30 — do NOT re-ask)

| Decision | Setting |
|---|---|
| Purchasing | USER handles all sourcing/buying. Agent stops at BoM + roadmap (+ price hints only if asked). |
| BoM depth | Per line: qty, spec, why it matters, Chinese/Taobao search terms, expected ¥ range (ESTIMATES), genuine-vs-clone flag, kit consolidation. |
| Quality guidance | Cheapest spec-matched is fine EXCEPT safety/power/compat-critical parts (batteries, PSUs, panels with driver-locked controllers) → flag "buy genuine". Store ratings: soft signal only. |
| Off-platform parts | Flag routing: PCBs → JLCPCB; laser-cut / 3D-printed → Taobao fabrication services (亚克力激光切割定制 / 3D打印定制服务). Quote-first items always flagged. |
| Roadmap | Interactive HTML checklist — tick-off, phone-friendly, progress saved locally (localStorage). |
| Ping | Chat delivery by default; WeChat only when asked (`hermes send --to weixin:...`). |
| Archive | Per `_ORGANIZATION_PROMPT.md` (file-organization skill): `<archive>/Projects/<name>/`, copy-don't-move, one `_manifest.md`. |

## Pipeline

### 0. Intake
- YouTube → description via `yt-dlp --get-description "URL"` or the youtube-content skill; find GitHub repo; clone into `Working/`.
- BoM sources in order: `*BOM*` / `*parts*` / `*shopping*` files → README tables → build guide → video description → **reconstruct from code** (driver imports and pin definitions identify the exact parts — e.g. `import lib.epd7in5b_V2` pins the panel model).

### 1. Normalize BoM (the primary deliverable)
- Per line: `{part, qty, spec, function}`; READMEs under-specify — read the code for exact parts (driver libs, config fields, mounting hole counts).
- Dedupe + consolidate: fasteners → one kit, wires → one bundle; mention a full-kit option (全套散件) when plausible.
- Per line add: Chinese search terms (from `references/taobao-term-mapping.md` — grow it), expected ¥ range (label ESTIMATE), genuine/clone flag.
- Output as `Deliverables/BoM-<project>.md` table + a short "purchasing notes" section (kit option, verify-fastener-sizes-from-STL, own-vs-buy questions to ask the user).

### 2. Roadmap (HTML checklist)
- Template: `templates/roadmap_template.html` — fill `PROJECT`, `STEPS`, `EXTRA`; `LOCAL_KEY` = project slug.
- Steps from README + code: hardware assembly, OS prep, every settings/config field, first-run test points, autostart.
- Include per-step warnings: safety, "don't X while refreshing", plaintext credentials, device handling.
- File to `Deliverables/WebApps/<slug>-roadmap/roadmap.html`.

### 3. Customize ideas (optional section in roadmap)
- From repo features / bundled assets / user's background. Keep brief.

### 4. File + manifest
- `Working/` (repo clone, notes), `Reference/` (spec sheets, screenshots), `Deliverables/` (BoM, roadmap), `_manifest.md` table, one line in `_INDEX.md`.

### 5. Optional ping
- Chat is the default. WeChat only when asked; ≤3,300 chars; long content as attached .md.

## Project folder layout

```
<archive>/Projects/<name>/
├── Deliverables/
│   ├── BoM-<project>.md
│   └── WebApps/<slug>-roadmap/roadmap.html
├── Working/        repo clone, notes
├── Reference/      spec sheets, screenshots
└── _manifest.md    (per file-organization skill)
```

## Pitfalls
- READMEs omit or over-specify parts: check driver imports / config fields in CODE for the real parts (e.g. 7.5" HAT (B) V2 vs HD have different controllers — the import decides).
- ¥ ranges are estimates and drift — label them and tell the user to verify.
- Genuine-vs-clone flags: MCU/sensor clones cheap & fine; panels with driver-locked controllers, PSUs, batteries → genuine.
- Fastener sizes (M2.5 vs M3) come from the STL/PCB, not the README — tell the user to verify or measure.
- State the exchange rate source/date when quoting USD (open.er-api.com).
- Only finished artifacts move to Deliverables; scrapes stay in Working/.
