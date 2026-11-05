# Wording pass on an existing document

The pass where the user asks for concision or a house voice on a document they already wrote or own.
Rewriting is expected here; what is not allowed is losing the change record.

## Order of work

1. **Fresh read, line by line, with `repr()`.** `for n in range(a,b+1): print(n, repr(lines[n-1]))`. Markdown/LaTeX prose wraps at the author's margins, and `repr()` is how you see the exact spacing and the real backslash count (`\\ref` versus `\ref` destroys a reference silently). Never edit from a rendered view or a previous session's read.
2. **Inventory the marks to remove, excluding comments.**
   ```python
   [i for i,l in enumerate(lines,1) if '---' in l and not l.strip().startswith('%')]
   [i for i,l in enumerate(lines,1) if ' -- ' in l]
   ```
   Also count every remaining hyphen, so which ones survive is a decision rather than an accident.
3. **Back up** to `Working/<kind>/_archive/<name>.before-wording-pass-<YYYYmmdd-HHMMSS>.<ext>` and give the path in the reply.
4. **Apply pairs against `lines[n-1]`**, asserting count first:
   ```python
   assert lines[n-1].count(old) == 1
   lines[n-1] = lines[n-1].replace(old, new)
   ```
   Keep every `old` inside one line. When an assertion fails on text you can see in the file, the phrase starts one line earlier (or ends one line later) than your string does.
5. **Write back with `newline=""`**, otherwise Windows converts every `\n` to `\r\n` and the diff is a full-file rewrite.
6. **Diff against the backup** (`difflib.unified_diff(old_lines, new_lines, n=0)`) and read it once as the change record. Confirm no line moved that you did not intend.
7. **Re-run the mark inventory on the new file.** The target mark must be zero outside comments; a survivor is a missed pair or one you introduced.
8. **Build it.** For LaTeX:
   ```bash
   xelatex -interaction=nonstopmode -halt-on-error f.tex >/dev/null 2>&1; echo "run1=$?"
   xelatex -interaction=nonstopmode -halt-on-error f.tex >/dev/null 2>&1; echo "run2=$?"
   grep -n '^!' f.log; grep -n 'undefined\|multiply defined' f.log; grep -n 'Output written' f.log
   ```
   **Run 1 exiting nonzero is normal** when cross-references or the table of contents need a second pass; judge run 2. Report page count, and any undefined reference you leave in place.

## Dash decision table

| Occurrence | Action |
| --- | --- |
| `---` or ` -- ` between clauses | Replace: aside, advisory or apposition becomes brackets; explanation becomes a comma or colon; enumeration becomes a colon |
| `---` in a table cell as "not applicable" | Replace with a word (`none`) |
| Hyphen inside a compound word (`wheel-only`) | Keep |
| En dash in a numeric range (`$0.41$--$0.51\unit{m}$`, `$8\unit{s}$--$12\unit{s}$`) | Keep |
| En dash in a reference or figure range (`Eqs.~(4)--(5)`, `Figures~8--12`) | Keep |
| En dash joining two names (`Box--Muller`) | Keep |
| Dash inside a section or subsection heading | Keep (the user's rule exempts headings) |

## Rewrite examples (register, not content)

- "The cost of pure prediction is honest: the variance grows at exactly the rate the process model predicts, and the next real reading pulls it back." becomes "With nothing to correct, the variance grows at exactly the rate the process model predicts and the next real reading pulls it back down."
- "A sensor you cannot rely on is worse than no sensor." becomes "a sensor whose error varies by a factor of $30$ between runs is not usable as the only position source." A verdict sentence is replaced by the measured spread already sitting in the paragraph.
- "The sum of a rounded quantity cannot be improved for free." becomes "a sum that is already limited by rounding does not improve with more terms."
- "the consequence is dramatic." Cut. Let the sentence stop at the observable difference and let the table carry the size of it.
- "better in every direction, not on average" becomes "in every direction rather than on average".
- Parenthetical dash pair becomes brackets: "all five of them -- a, b, c -- in the six instants" becomes "all five of them (a, b, c) in the six instants".
- A dash pair that carries the main clause must not be bracketed into an aside: "Second -- and this is the dominant term -- the initial offset ..." becomes "Second, and this is the dominant term in the numbers above, the initial offset ...".
- Broken mid-clause grammar ("A worse outcome would be if it multiply the same noise realisation ... several times") is rewritten to the plain statement of the same mechanism, and reported.

## Leave alone

- The user's own claims, deletions and parked sections: never restore one in new words, never uncomment one unasked.
- Allow-list dashes above; table separators; `\path{}` names other than a mismatch you verified on disk.
- Note any inconsistency you notice between what the document says and the tree it lives in, in the reply, in one line each.
