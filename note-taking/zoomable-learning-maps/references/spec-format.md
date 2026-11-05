# Spec format — `zoom_subchart.py`

The generator reads one JSON file holding either one object or a list of objects, and writes one HTML
file per object into `--out-dir`:

```
python scripts/zoom_subchart.py spec.json --out-dir "C:/.../Own Notes/<topic-slug>"
python scripts/zoom_subchart.py spec.json --out-dir <dir> --check-only   # dry run, prints overflows
```

Output filename: `<slug>.html` — the slug is the whole file stem, so end it in `-zoom` to keep the
family's naming (`paper-z3-hypothesis-generation-zoom` → `paper-z3-hypothesis-generation-zoom.html`).
Overflows are printed as warnings during generation — treat any
warning as a blocking defect and fix the spec before looking at the page.

## Fields

### Identity and return path (required on every spec)

| Field | Type | Meaning |
|---|---|---|
| `slug` | str | file stem and id prefix, e.g. `paper-z3-hypothesis-generation-zoom` → `paper-z3-hypothesis-generation-zoom.html`. The generator writes `<slug>.html` verbatim, so the `-zoom` suffix lives in the slug. Must match the href of the master's chip. |
| `anchor` | str | the master's chip label, `Z3`. Repeated as the child's own chip, which links back to the master. |
| `zoom_index` / `zoom_total` | int | printed in the child's header as `ZOOM 3 OF 8`. |
| `section` | str | the source section the page covers, `§3.1–3.2`. Must be the section the master's chip claims. |
| `parent_file` | str | the master's filename; the back-out chip's href. |
| `parent_node` | str | the master node this page re-enters, `§3.1–3.2 · Stage 1 — coarse pose hypotheses`. Printed top-right. |

### Page text

| Field | Type | Meaning |
|---|---|---|
| `eyebrow` | str | small uppercase line above the title. |
| `h1` | str | the page title. |
| `sub_lines` | list[str] | monospace sub-lines under the title; one line each, keep them short. |
| `desc` | str | the `<desc>` text — the accessible description of the SVG. Required: the gate checks for it. |

### Body blocks

| Field | Type | Meaning |
|---|---|---|
| `chain` | list | the vertical spine. Each: `{tag, title, lines[], focal?, chip?}`. `tag` is the paper's own number (`3.1`); `focal` draws the accent-left variant; `chip` (bool) draws a chip on this node that links to a deeper zoom. |
| `loop_after` | int | index into `chain`; draws the accent self-loop after that node. |
| `loop_label` | str | the loop's label, `ITERATE`. |
| `rows` | list | side-by-side blocks below the chain. Each: `{header, incoming?, connect?, nodes[{title, lines[]}]}`. `incoming` draws an arrow into the row; `connect` draws the connector continuing out of it. |
| `handoff` | obj | the closing band: `{terminator_title, terminator_sub, next_title, next[{anchor, text, file, built}]}`. `built: false` renders the entry as "still to build" — the honest label for a zoom that does not exist yet. |
| `legend` | list | `{kind, label}` with `kind` ∈ `node` \| `focal` \| `arrow` \| `dashed`. Items wrap into rows automatically. |
| `legend_note` | str | one standalone line under the legend; kept on its own row so it cannot collide with the items. |

### Below the canvas

| Field | Type | Meaning |
|---|---|---|
| `cards` | list | `{n, t, b, focal?, list[]}` — the reading cards under the chart: `n` is the card's index label, `t` the heading, `b` the paragraph, `list` optional bullets. `focal: true` draws the accent-left variant. |
| `footer` | list[str] | monospace provenance lines. State where each value on the page was read from; this is the page's honesty record. |

### Planned zooms

| Field | Type | Meaning |
|---|---|---|
| `placeholder` | bool | `true` emits a "what this zoom will cover" page instead of a chart. Its frame is a real accessible `<svg>` (the gate requires an SVG on every page) drawn as the frame the chart will fill. |
| `placeholder_bullets` | list[str] | what the zoom will answer. Each bullet must be answerable from the source text you already extracted. |
| `placeholder_note` | str | where the content will come from, e.g. `§3.3 + Table 3`. |
| `next_links` | list | `{anchor, text, file}` — forward links out of a placeholder into the zooms that do exist, so a placeholder is not a dead end. |

## Minimal example

```json
[{
  "slug": "paper-z4-filtering-ransac-epnp-zoom",
  "anchor": "Z4", "zoom_index": 4, "zoom_total": 8, "section": "\u00a73.3",
  "parent_file": "paper-structure-flowchart.html",
  "parent_node": "\u00a73.3 \u00b7 filtering \u2014 RANSAC + EPnP",
  "eyebrow": "zoom 4 of 8 \u00b7 \u00a73.3",
  "h1": "Filtering: RANSAC over the hypotheses",
  "sub_lines": ["N_iter = 80 iterations", "inlier threshold from the box size"],
  "desc": "Zoom chart for section 3.3: filtering the coarse hypotheses with RANSAC and EPnP.",
  "chain": [
    {"tag": "3.3", "title": "Score every hypothesis", "lines": ["reproject the model, count inliers (eq. 15)"], "focal": true, "chip": false},
    {"tag": "3.3", "title": "Fit the pose", "lines": ["EPnP on the inlier set (eq. 16)"]}
  ],
  "rows": [],
  "handoff": {
    "terminator_title": "ZOOM BACK OUT",
    "terminator_sub": "re-enters the master chart at \u00a73.3",
    "next_title": "NEXT ZOOMS \u2014 one concept at a time",
    "next": [{"anchor": "Z5", "text": "\u00a73.4 \u2014 what happens to a wrong pose", "file": "paper-z5-differentiable-rendering-zoom.html", "built": true}]
  },
  "legend": [{"kind": "node", "label": "NODE \u2014 one argument beat"}, {"kind": "focal", "label": "THE PIVOT \u2014 where accuracy is made"}],
  "legend_note": "the accent loop is a loop in the method, not decoration",
  "footer": ["every value on this chart was read from the extracted text, not recalled"]
}]
```

Placeholder variant (same identity fields, then):

```json
{
  "...": "identity + eyebrow/h1/sub_lines/desc as above",
  "placeholder": true,
  "placeholder_bullets": ["which baseline each number belongs to", "what the ablation removes, in the paper's own terms"],
  "placeholder_note": "will be drawn from \u00a74.3 and Table 5",
  "next_links": [{"anchor": "Z5", "text": "\u00a73.4 \u2014 the stage the ablation removes", "file": "paper-z5-differentiable-rendering-zoom.html"}]
}
```
