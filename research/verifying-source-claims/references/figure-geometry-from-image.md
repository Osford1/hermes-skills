# Reading a figure's geometry from an image

For when the answer depends on the *picture* — which axis is which, where a dimension starts, which way an
arrow points, which label names which line — and the source is a screenshot, a photo, or a rasterised page
with no usable text layer.

**The rule of the whole file: measurements converge, interpretations do not.** Label positions and straight
segments can be extracted exactly. Which label belongs to which arrow, and which way that arrow points,
cannot be settled by better crops — so budget the attempts and have a stopping rule ready before starting.

## 1. Mask first, then split glyphs from line work

```python
import numpy as np
from PIL import Image
a = np.array(Image.open(path).convert("L"))
print(a.shape, a.min(), a.max())            # min/max set the threshold — check before choosing one
mask = a < 170
H, W = mask.shape
for r in range(0, H, 6):                    # coarse ASCII map: where the ink actually is
    print("".join("#" if mask[r:r+6, c:c+4].any() else "." for c in range(0, W, 4)))
```

```python
from scipy import ndimage as ndi
lab, n = ndi.label(mask)
strokes = np.zeros_like(mask); glyphs = np.zeros_like(mask)
for i, sl in enumerate(ndi.find_objects(lab), start=1):
    if sl is None: continue
    h = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start
    (strokes if (h > 45 or w > 45) else glyphs)[lab[sl] == i] = True
print(n, strokes.sum(), glyphs.sum())
```

The ~45 px cutoff is a rule of thumb for an image around 1000 px wide: strokes are long or wide, single
glyphs are not. Sweep the threshold (140 / 170 / 200) and keep whichever stroke mask looks like the
drawing in the ASCII map.

## 2. Render one decluttered view and read *that*

Write strokes black and glyphs red, at 2×, both in their true positions, and hand that single image to
`vision_analyze`. Prefer this over any number of crops of the original: the model describes line work
without OCR noise competing for attention. Colour-coded original-versus-cleaned side-by-sides are worth
one look for orientation and no more.

## 3. Label positions come from the mask, never from the model

Cluster glyph components into label boxes (merge boxes whose gap is under ~8 px). Those box centres are
ground truth to the pixel. The vision tool's quoted "approximate pixel coordinates" are estimates —
routinely off by tens of pixels — and are useful only as hints for pairing.

## 4. Read many small labels in one call: the numbered montage

Crop each label cluster at 3×, stack the crops vertically in one image, and draw a red index number
beside each row. Ask for the labels in order. Ten to twenty labels per call, each shown large, is far
more reliable than asking for labels inside a crowded full view.

## 5. Bound every question, one fact per call

Working phrasing — short answers also survive where a long analysis gets elided before you can read it:

> "5 short numbered lines, under 450 characters, no preamble: 1. <one fact> 2. <one fact> …"

Ask direction questions and identity questions **separately**. Multi-part asks come back partially
contradictory: one reply read the same axis as both "tilted/horizontal" and vertical across its own
numbered answers.

## 6. Straight segments without cv2: a hand-rolled Hough

When only numpy is available, sweep θ, accumulate ρ, take the peak, project the inliers and cut them into
runs:

```python
th = np.arange(0, 180, 0.2)                       # degrees
cos, sin = np.cos(np.radians(th)), np.sin(np.radians(th))
ys, xs = np.nonzero(line_mask)
rho = xs[:, None] * cos[None, :] + ys[:, None] * sin[None, :]
rb = np.round(rho - rho.min()).astype(int)
acc = np.zeros((rb.max() + 1, th.size)); np.add.at(acc, (rb, np.arange(th.size)[None, :].repeat(rb.shape[0], 0)), 1)
ri, ti = np.unravel_index(np.argmax(acc), acc.shape)   # acc is (rho, theta) — keep that order
```

Pitfalls that cost real time here:

- **Index order.** `acc` is `(rho_bins, theta_bins)`; unpack as `ri, ti` and index `acc[ri, ti]`. The
  swapped form silently selects a different line and returns plausible garbage.
- **Guard short runs** before `np.diff(s) > 6` (the break test between contiguous inliers): a component
  with fewer than two pixels raises.
- **Inliers only** — keep pixels within ~2 px of the line, project them onto the line's normal, sort, and
  split where consecutive gaps exceed ~6 px. Those runs are the segments.

**Anything you classified as a glyph is missing from this mask**, so short arrows vanish entirely and "no
segment found" is not evidence of absence. Print every segment's endpoints and angle, and match labels to
the nearest segment endpoint within ~100 px — that pairing is the part that stays ambiguous (see §7).

## 7. Keep readings and interpretations apart in the write-up

Report a measured label box, a measured segment, and a *proposed* label-to-arrow pairing. Never promote the
pairing to a fact: it is the item to flag when the answer depends on it.

## 8. Close the loop with the domain, not with another crop

An identity the object must satisfy is the real oracle, and it usually collapses the space of readings.
In robotics: $x_i \perp z_{i-1}$ by construction, so a figure labelling $x_1$ along the gravity arrow has
its base joint axis horizontal — the drawing and the assumed vertical base cannot both be right. Ask what
constraint the source object must obey, then test each candidate reading against it. A reading that breaks
an identity is wrong, not difficult.

Then stop after **two independent attempts** (attempt = a genuinely different method or prompt, not the
same question re-asked) and write the caveat in this shape:

> "Assuming <convention>. If your figure's <label> is <the other reading>, then <exactly which terms
> change>; everything else is unaffected."

Naming the part the ambiguity *cannot* touch is what makes the caveat useful rather than a hedge.

## Escalation that did not resolve ambiguity

Tiling the figure into a 3×3 grid, 2× and 6× upscales, threshold sweeps, repeated crops, and re-asking the
same open-ended question all failed to settle a *direction* reading (they did settle small-glyph
*identity*). That matches the rule at the top of this file: spend the extra calls on measuring positions and
forming identities, not on re-asking, and treat the residual ambiguity as a stated assumption in the answer.
