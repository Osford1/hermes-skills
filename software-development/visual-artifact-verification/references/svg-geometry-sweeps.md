# SVG / diagram geometry sweeps (rendered-DOM pass)

A static checker reads markup; it cannot see font metrics, wrap, overlap or stacking. For any generated diagram, render it and measure the live DOM as a second gate.

```python
new_tab("file:///C:/.../artifact.html"); wait_for_load(); js(PROBE)   # PROBE = the IIFE below
```

## Probe shape
```js
(() => {
  const svg = document.querySelector('svg');
  const vb = svg.viewBox.baseVal;
  const bb = e => { const b = e.getBBox(); return {x:b.x, y:b.y, w:b.width, h:b.height}; };
  // adapt these three selectors to the artifact's own markup
  const boxes = [...svg.querySelectorAll('rect')].filter(r => bb(r).w > 60 && bb(r).h > 20);
  const texts = [...svg.querySelectorAll('text')];
  const conns = [...svg.querySelectorAll('path')].filter(p => p.getAttribute('fill') === 'none' || p.getAttribute('marker-end'));
  const masks = [...svg.querySelectorAll('rect')].filter(r => bb(r).w <= 60 || bb(r).h <= 20);  // label chips
})()
```

## Sweeps
| Check | Test |
|---|---|
| Text outside any box | text centre not inside any node rect and not a band label / footer |
| Text overflow | text bbox inside its rect with ≥8px margin on the fixed axis |
| Text-on-text | two text bboxes intersect (mask rects excepted) |
| Mask over a node | a chip rect intersects a node rect |
| Connector crosses a box | a sampled path point inside a node rect — **excluding the path's own endpoints** |
| Mask clearance | min distance from each chip rect to any connector sample ≥6px |
| Canvas + legibility | every element inside the viewBox; report `getBoundingClientRect().width / vb.width` and the smallest rendered font size |

Sample connectors with `path.getPointAtLength(s)` at ~1px steps. `getBBox()` on a path reports a bounding box that overlaps boxes the line never touches, so bounding-box tests produce false crossings.

## Pitfalls
- **Exclude the path endpoints or every legal attach point reports as a violation.** A connector drawn box-edge to box-edge starts *on* a rect, so a whole-length sample flags the first and last ~10px of every arrow. Shrinking the rects by ≤3px does not fix it. Skip the ends instead — sample from ~10 to `getTotalLength() - 10`. A run whose violations are all coordinates sitting on box edges is a probe bug, not dozens of defects.
- **Measure mask clearance numerically.** Distance from the chip rect to the nearest connector sample must be ≥6px in source coordinates; labels and strokes look separated on screen long before they are separated in the file.
- **Mono labels are often 7px in source coordinates**, so the rendered scale decides legibility: below ~0.9 the smallest rendered text drops under 6.5px. Report the scale instead of assuming 1.0.
- **Report counts and coordinates, and name the checks that could not run.** "Looks fine" is not a verification result.
