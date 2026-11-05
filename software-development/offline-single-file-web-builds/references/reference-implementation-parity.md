# Reference-implementation parity: a page that must print the same numbers

When: the page computes values that will be quoted elsewhere — a coursework program graded on its
numbers, a lab instrument, a figure in a report, a simulator whose table the user will copy. The
Python (or MATLAB) engine is the source of truth and the page is a port of it. This file is the recipe
that makes "the page agrees with the engine" a checked fact instead of an impression.

## 1. Write the engine once, in a plain language, under `Working/`

- `Working/engine/<name>.py`: plain Python, no numpy in the simulation path, so the arithmetic is
  readable line-by-line beside the JS. Every downstream claim comes from a run of this file.
- **Deterministic PRNG, portable draw order.** `mulberry32` (or xorshift) plus Box–Muller that does
  **not** cache the second normal — a cached pair makes the consumption order language-dependent and
  every later comparison meaningless.
- **Verify the PRNG against the other runtime before anything else.** Print the first 5 uniforms for a
  fixed seed and check them against a 20-line Node script; that single check is what licenses the
  parity harness later.
- **The gate is a report, not a green tick.** `tests.py` prints one line per check as
  `V<n> <what> | PASS/FAIL | <the number that proves it>`, and writes the same table to
  `Working/results/verify_report.md`. Count PASS/FAIL and read the exit code, and quote both. Checks
  that earn their place: analytic vs finite-difference Jacobians; sequential-vs-batch update
  equivalence (exact zero difference when `R` is diagonal); noise-free trajectories against closed-form
  endpoints; observability rank; budget/price assertions; and the study-level claims — consistency
  (NEES), empirical covariance vs the covariance the filter reports, and the effect size of the thing
  being studied (e.g. RMSE with a gate on vs off).
- **Never assert a result from prose.** Every experiment writes one CSV (or run-txt) into
  `Working/results/`; a number that only exists in the console did not happen.

## 2. Port verbatim, not "equivalently"

- Same formulas, same update order, same PRNG consumption order, same iteration bounds.
- **Accumulation order is part of the port.** `S = sum(H[i]*PHt[i]) + R` is not the same float as
  `R + sum(...)`; keep the order and leave the Python expression in a comment so the next editor does
  not "tidy" it back. This exact class of bug shows up as a parity field off by ~1e-2 while everything
  else matches.
- Write random draws in a form both languages agree on (`-0.15 + 0.30*rng.uniform()`, not
  `rng.uniform(-0.15, 0.15)`), and do not mix `Math.hypot` on one side with `sqrt(x*x+y*y)` on the other.

## 3. The parity harness (this is the gate)

- **One shared case list, written twice**: the same `(case, config, seed)` tuples in `dump.py` and
  `dump.js`. Both sides write JSON with identical field names into `Working/parity/`.
- `compare.py` walks the two JSONs element-wise and writes `parity_check.md`: per field, the float
  count, how many are bit-identical, and the worst absolute difference.
- Read the result like this: worst diff ~1e-11 with most values bit-identical is expected (a few ULP
  from `sin`/`cos`/`log`/`hypot` differing between V8 and libm). A field off by ~1e-2 is a **real port
  bug** — check the accumulation order and the draw order before suspecting the harness.
- Quote the number in the hand-over ("82,800 floats, worst diff 1.3e-11"). It is the evidence that the
  page's numbers are the engine's numbers, and it is cheaper for the user to trust than a screenshot.

## 4. Generate the shipped file from the sources

- `build.py` inlines the engine JS + UI JS into the HTML shell and writes the shipped `index.html`.
  Say in the README that `index.html` is a **build product**: edits go in the sources, then rebuild.
- A stale build is silent — the page still works, running last week's code. Rebuild after every edit,
  and re-load the built file (not the sources) for the browser checks.

## 5. Cross-check the page's own aggregates

Single-run parity is not enough when the page displays an aggregate (a batch table, a mean over
seeds). Compute the same table independently in Python and assert 4-decimal agreement — that is what
catches UI-side arithmetic: a mean over the wrong window, a config list that drifted from the engine's,
seeds averaged in the browser only.

## 6. Verifying the canvas and the scientific panels

- **You cannot read canvas text back.** For labels, take the element's rect
  (`getBoundingClientRect()` + `scrollX/Y`) and read that region of a full-page screenshot with
  `vision_analyze`. For geometry — where a wall, a marker or a curve actually is — probe the canvas in
  JS (a pixel scan for the brightest column/row). Do not accept a rendered-pixel reading that
  contradicts the data: a vertical wall reported at the wrong coordinate was a misread of rotated axis
  labels, and the pixel probe put it 0.02 units from the exact position.
- **Scale each axis to the data's real range, and go logarithmic when the range spans decades.**
  Variances and uncertainties run 1e-4 … 25; on a linear axis every curve lies flat on the bottom line
  and the panel reads as blank. Plot `log10`, label the ticks `10^x`, and name the scale in the panel
  title.
- **Give each sub-plot its own y-scale.** One shared scale across quantities of different magnitude
  hides all but the largest.
- **Sweep every control after the last rebuild** with an error collector installed before the page
  script runs (`window.addEventListener('error', …)`), and include the invalid states: the refusals
  (over-budget, nothing selected) must print a message — not crash, and not silently do nothing.
- **A control that appears dead may be refusing legitimately.** A step/advance button with no visible
  effect was the guard rejecting an over-budget config; check the readouts and the toast text before
  touching the handler.
