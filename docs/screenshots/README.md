# Screenshots the README needs

No image is in this repo. The README carries a marked `TODO(owner)` comment instead of image links, so
nothing renders broken. These are the shots to take. Two of them have to be captured live — the
verification one only means something if it shows a failure being caught.

Suggested capture: viewport 1280 px, device scale 2 (so the PNG is 2560 px wide), no browser chrome.
For the two page shots, capture full page height.

| Filename | What it must show | Suggested size |
|---|---|---|
| `docs/img/verification-caught.png` | `web-deliverable-verification` in a real session catching a bad render: the page on one side, the failing check's output on the other, with the specific defect legible (overflow, overlapping text, or a canvas that rendered blank). This is the repo's central claim, so it should be a genuine failure, not a passing run. | 2560 × ~1600 px |
| `docs/img/particle-page.png` | `particle-art-pages`: the finished particle page mid-interaction — spiral arms, the DOM labels synced to orbits, and enough of the page chrome that it reads as one file rather than a screenshot of a canvas. | 2560 × ~1600 px |
| `docs/img/learning-map.png` | `zoomable-learning-maps`: a master chart page with its chips visible, and if the shot is wide enough, one zoom child beside it so the zoom-in/zoom-out relationship is obvious. Do not use anything from the unpublished example. | 2560 × ~2200 px (full page) |

Once the files exist, replace the `TODO(owner)` comment near the bottom of `## What works and what
does not` in `README.md` with a short gallery:

```markdown
![a verification check catching a bad render](docs/img/verification-caught.png)
```

Keep each caption to one clause naming which skill it came from.
