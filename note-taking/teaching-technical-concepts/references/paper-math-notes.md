# Writing an equation-by-equation math note from a paper

Companion to the paper walk-through in SKILL.md. This is the procedure for the `math.md` half of the
two-file deliverable: the algebra, derived rather than transcribed, with the paper's own printing
errors named. The user asks for "the math in deep detail" because they intend to reimplement or
extend, so an unverified transcription is worse than useless.

## 1. Get the text out once, as per-page files

Extract every page with PyMuPDF into one JSON, then write **per-page `.txt` files** and read those
with `read_file`.

```python
import json, pathlib, pymupdf
doc = pymupdf.open(PDF)
pages = [{"page": i + 1, "text": p.get_text()} for i, p in enumerate(doc)]
pathlib.Path("pages.json").write_text(json.dumps(pages), encoding="utf-8")
out = pathlib.Path("txt"); out.mkdir(exist_ok=True)
for pg in pages:
    (out / f"p{pg['page']:02d}.txt").write_text(pg["text"], encoding="utf-8")
```

Do **not** print page text to stdout to read it — a multi-KB `print(p[n-1]['text'])` comes back
truncated or demoted, so the content never reaches you and you end up writing from memory. Per-page
files plus `read_file` (offset/limit and pagination) is the reliable read, and it leaves a cache the
next session on the same paper can grep.

Reading order that works: the intro's contribution list and the reference list first (they fix what is
actually new and who else's work is being reused), then the methods pages, then the results tables.

## 2. Locate and read every equation by its number

- Build an index of the equation numbers per page (`page.search_for("(16)")`), or just print each
  page's `get_text("blocks")` as `[x0,y0,x1,y1] text` tuples.
- **The block geometry is a second, independent read of the layout.** The text stream linearises
  fractions, so a term printed as `cφ` over `f` arrives as a bare `cφ` with the `f` sitting on a
  different baseline further along — that is how a dropped denominator escapes notice. The block
  coordinates tell you where each fragment actually sat, which is what lets you decide whether a
  bracket encloses a term or multiplies it.
- Then render the region at 600 dpi (`page.get_pixmap(dpi=600, clip=Rect(...))`) and ask the vision
  model a **character-level** question ("is the last term inside the parentheses `c φ` or a fraction
  `c φ / f`? Say if a glyph is unclear"). Require the crop and the block geometry to agree; when they
  disagree, the crop wins on glyph identity and the blocks win on layout.
- Crop the equations you will actually write out. A whole-paper sweep is not needed — the note only
  carries the equations it derives.

## 3. Derive before you accuse

Redo every equation from its own definition, then compare **term by term**. This is where the value of
the note comes from, and it cuts both ways:

- **An apparent inconsistency is often a different variable.** Two equations in the same paper carried
different denominators for what looked like the same quantity; deriving it showed one reports the
Lagrange multiplier `λ` and the other uses `Λ = λ(1+c/f)/(1+δ)`, so the pair is self-consistent. Say
so explicitly — "these are not a typo, here is why" — because a reader who 'fixes' it breaks the
algorithm. Reporting a false error destroys trust in the whole audit.
- **A real slip usually repeats.** A dropped factor in one term showed up identically in three
equations, while the constraint equation that the derivation starts from printed it correctly. When
something is wrong, count how many equations carry the wrong form, and name the one that is right.
- **Check the algebra that converts the paper's constants into the weights actually used.** A
continuous-time weight `δ_c` and the discrete weight `δ = δ_c f²` differ by `f²` — with a 50 Hz layer
and `δ_c = 0.5` the effective weight is 1250, not 0.5, which changes the reading of the whole objective
(one term carries 99.92% of the weight). Compute these before explaining what the objective does.
- **Do the arithmetic on any stated budget**: reward fractions of the task bonus, discounted values
(`γ^N`), step-count × stage counts against a stated total, hours against steps. Inconsistencies here
are common and cheap to find.
- **Look for the step the paper never writes out.** Typically a gradient that must chain through
forward kinematics, a Hessian silently dropped by a linearisation, or a feasibility condition that is
asserted rather than proved. Name it under "what you would have to derive yourself to reimplement".

## 4. Shape of the note

1. Frontmatter, then a one-line "printed vs derived, and why both are shown".
2. **Notation table**, including any symbol the paper reuses for two different quantities and any
   word it reuses for two different decouplings — flag those as collisions in the table itself.
3. Sections in pipeline order (perception → constraint → optimisation → closed form → the novel
   connector → the learning side), each: equation as printed, then the derivation step by step, then
   one paragraph of "what this says in physical terms".
4. **A "where the printed equations are loose" list** — numbered, each with (a) what is printed,
   (b) what is correct, (c) the consequence for someone reimplementing.
5. **A "what you would have to derive yourself" list** — the unstated steps.
6. Numeric sanity values computed in the terminal and quoted (`δ`, `c/f`, the discount factors, the
   reward ratios) — never estimated in your head.

## 5. Pitfalls

- **Never relay a printed constant as derived truth** before doing step 3. "The paper says `δ = 0.5`"
  and "the weight in the implemented objective is 1250" are different claims and both are useful.
- **Do not paper over the paper's undefined symbol semantics.** When a variable is defined as a
  configuration in one place and a position in another, the gradient's meaning changes with it — spell
  out which reading the algorithm requires and say the paper never states it.
- **Keep the audit honest about what a finding does and does not undermine.** A dropped factor in a
  presentation equation does not invalidate the experiments; say which claims survive.
- **Report the corrections you made to your own earlier output.** If an earlier chat message quoted a
  parameter wrong, correct it in the reply when filing — the filed note is the version that persists.
