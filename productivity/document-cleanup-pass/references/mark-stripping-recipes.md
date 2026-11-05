# Mark-stripping recipes

Concrete transform pipeline for a cleanup pass. Every step is a checked
string operation, never a recomposition of the text.

## Ambiguity decision table

One request word covers several distinct things. Resolve before editing.

| User says | Test | Default |
|---|---|---|
| "remove dashes" | is it `—` or `–` in prose | rewrite as `,` `.` or `to` |
| "remove dashes" | is it inside a word (`fault-tolerant`) | **keep**, it is part of the term |
| "remove dashes" | is it a line starting `- ` | **keep**, it is a list bullet |
| "remove dashes" | is it a `|`-separated table cell of `---` | **keep**, it is the table header rule |
| "remove `;`" | anywhere | split into two sentences |
| "remove bold/italic" | `***` alone on a line | **keep**, that is a horizontal rule |

Ask which sense is meant, then apply it consistently. Deleting every hyphen
in a document with a wide table destroys the table.

## Ordered pipeline

Run in this order; later passes depend on earlier ones.

1. **Emphasis**, longest marker first so bold-italic is not left half-stripped:
   ```python
   s = re.sub(r"\*\*\*(.+?)\*\*\*", r"\1", s)
   s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
   s = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"\1", s)
   ```
   No `re.S`. A standalone `***` line has no inner text, so none of the three
   patterns touch it.
2. **Explicit pairs** for punctuation and grammar (semicolons, dashes,
   comma splices). These are not regex work, they are judgement, so they stay
   as literal pairs.
3. **Whitespace**, non-table lines only:
   ```python
   if not line.startswith("|"):
       line = re.sub(r"  +", " ", line).rstrip()
       line = re.sub(r"\s+([,.:;])", r"\1", line)
   ```
   Collapsing spaces on a `|` line breaks the table alignment.
4. **Structural repairs**: blank line after a table block, and between two
   consecutive headings.

## Pair-list assertion pattern

```python
pairs = [
    ("built from 3 and 4", "built from 2 and 3"),
    ("the fault PE S5", "the faulty PE S5"),
]
for old, new in pairs:
    n = s.count(old)
    if n == 0:
        print(f"NOT FOUND: {old[:60]!r}")
    s = s.replace(old, new)
```

Print the count for every pair. A `0` means the key is mistyped or the
surrounding text moved; a count above `1` means a global rename, which is fine
but must be deliberate. This list doubles as the change record you report.

## Word-level diff as a second opinion

The strongest single check is a diff of normalised prose lines: every line of
the new file should appear verbatim in the backup, except the ones you edited.
If the count of differing lines equals the count of pairs that touch prose,
the transform is provably content-preserving. `scripts/verify_mechanical_edit.py`
prints exactly that list.
