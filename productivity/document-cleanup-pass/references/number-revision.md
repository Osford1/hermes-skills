# Number revision: verifying and re-issuing a document's figures

For corrections whose evidence is a re-run of an experiment rather than the document's own text. Do this as a pass, in this order, and never skip step 2.

## 1. Restore points first

- Timestamped backup of the source file and of the built artifact, before any edit: `_archive/<name>.before-<pass>-<YYYYmmdd-HHMMSS>.<ext>`.
- Copy the working tree (engine + results) to a scratch directory and run the re-runs there, so the stored results are only replaced deliberately. Archive the results directory before regenerating into it: `results/_archive_before_<change>/`.
- Invoke the interpreter explicitly (the venv python, not `python`) so a re-run does not quietly use a different environment.

## 2. The validation gate: reproduce before you recompute

For every cell you intend to change, first reproduce the **current** number with the **current** protocol, and print both. This is the only proof that your code-to-cell mapping is right; when it fails, the recomputation is worthless even if it looks more accurate.

The trap that costs the most time: **the tabulated ± may be the population sd while the engine writes the sample sd.** A report showing `0.037` next to a CSV `stdev` of `0.0392` over ten runs is consistent, because `0.0392 * sqrt(9/10) = 0.0372`. Check `statistics.stdev` and `statistics.pstdev` (and their n-1/n factors) before concluding your recomputation disagrees.

Other shape mismatches to test before declaring a difference: a per-run mean of RMSEs versus a pooled RMS over all steps and runs; the window (`t >= 5 s` as `k >= 50` or `k >= 51`); error measured against the estimate at the previous step versus the current one; an offline derivation with no code at all.

A column you cannot reproduce is **frozen**, not fixed. Note it in the reply as not verifiable from the stored outputs and leave the printed value alone.

## 3. Re-run at the new protocol, then diff cell by cell

- Print old, new and delta for every affected CSV cell; a delta that changes a sentence's conclusion is the finding, a delta that does not is noise you should not propagate into the tables.
- Never re-baseline the whole document for one interesting change. Put the new protocol's result where it decides the argument, in prose, with the mechanism, and list the untouched tables in the reply.

## 4. Tail check before believing any comparison

Compute per-run values, then mean, sd, min, max and quantiles at the old and the new sample size. A distribution that looks tight at n and grows a long tail at 2n means the old conclusion was sampling noise. Find the mechanism and state it (for example: an estimate sliding along the locus the sensor cannot observe, where the filter's own covariance stays small and the error does not).

Per-run extremes are also what tells you *how many* runs fail, which is the honest form of the claim: "two of twenty converge to 5 m" beats "the mean is 0.73 m".

## 5. Reproducibility sweep of the document's own configurations

List every suite, configuration or dataset the document names; grep the engine's combination matrix for each name. Anything quoted in the report but absent from the matrix was run ad hoc and cannot be regenerated: add it, re-run, and assert the published values are reproduced exactly (print published vs regenerated side by side). Do this before telling the reader the code reproduces the report.

## 6. Separate truncation from rounding with exact forms

Composite rules have closed-form errors, which is the only way to distinguish an algorithm's truncation error from floating-point accumulation. For `∫cos` over a full period with step `h = 2π/n`:

```
T_n = (h/2) * cot(h/2)          # trapezoid
M_n = (h/2) / sin(h/2)          # midpoint
S_n = (4*T_n - T_{n/2}) / 3     # Simpson
```

Evaluate them with `decimal.getcontext().prec = 60` and compare against the double-precision sum of the same rule: the closed form is the true truncation error, the gap to the double sum is rounding. A table whose errors stop improving near `1e-15` is reporting accumulation, not convergence, and only this comparison shows it.

## 7. Rebuild and verify the artifact

- Build twice (`xelatex -interaction=nonstopmode`); run 1's nonzero exit is normal.
- Count Overfull and Underfull warnings in the new log and compare them with the **pre-edit** build log. A pre-existing Underfull is not your regression; report only the difference.
- An Overfull hbox inside a wide table is fixed by restructuring (transposed layout with short trajectory columns, a `p{}` label column, `\footnotesize`/`\scriptsize`), not by dropping columns.
- `pdftotext -layout` output mangles wrapped table cells, so verify inserted values by grepping the extracted text for the exact token (`0.6320`), not by reading the layout dump.

## 8. Reply shape

One line per change with the reason, the verification line (pages, errors, overfull count, values present in the PDF), the backup paths, the list of cells and tables deliberately left alone, and the offer to run the full re-baseline as separate work.
