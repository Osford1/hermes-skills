# Walking the user through an assignment, question by question

Trigger: "rework the project with me, starting with question 1(a)", "give me step-by-step
solutions for 1(b)", "relate it back to <vault note>". The deliverable is a *teaching* solution,
not a submission answer — the numbers matter only because the reasoning around them does.

## Order of operations

1. Read two things in the same pass: the brief (use the English `.md` if the original is a Chinese
   PDF) and the vault concept page the user named. Adopt the note's own section headings as your
   vocabulary — the closing map quotes them verbatim.
2. Pull the numbers from the project's verified engine by calling its function for that exact
   sub-question. Never hand-derive and present. Then re-derive the same quantities independently in
   the same script (own matrix ops, ~20 lines) and print both.
3. `inspect.getsource` the engine function you called, so the formula you write matches the
   implementation instead of a textbook variant.
4. Write the solution in the equations' own order (`z → h → H → R → e → S → K → x⁺ → P⁺`, or
   predict-then-update). One heading per step, and each step says what that object is *for* — not
   just its value.
5. Close with: what changed and what did not, a mapping table (step → section of the user's note),
   and where the live program shows the same numbers (file + panel name).

## Restate notation in every message

The user returns with "what is `h` again?" and "what do you mean by state" after a dense solution.
Treat every symbol as unseen unless it was defined in the *same* message: define it where it first
appears, and put a small legend or table in each follow-up rather than assuming carry-over.

Flag notation collisions in the source explicitly — a state vector `x` whose first component is also
`x`, `h` (function) versus `H` (its Jacobian), `H` used for both a Jacobian and a heading. Say
"that's the brief's notation, not mine" and offer the standard alternative ($x_k$, $\hat x$); without
that, the user reads the formula as a self-contradiction.

## Pointing at the lecture slides

"Point me to which slides this is in" wants a step -> slide map, one row per step of the derivation,
not a list of page numbers for the whole topic. Cite the slide that owns each step and give the
deck's own title for it:

| what the step needs | the control / algorithm deck | the mechanics deck |
|---|---|---|
| a point's position from the joint angles | the worked two-link position formula | the general "centre of mass of one link" slide |
| where the mass sits on the link | - | the slide that draws the centre distances for that exact arm |
| velocity is the derivative of position | the Jacobian slides | the centre-of-mass velocity slide |
| kinetic energy summed over the links | the Lagrangian review slide | the slide whose last line is the energy sum |
| the final matrix form and its letters | the same review slide | the standard-form slide |

- Get the titles with the page-map and two-slides-per-image read in
  `references/deriving-source-proofs.md`; a title lifted from extracted text is a guess, because the
  text layer garbles the symbols sitting next to it.
- **Name the single substitution that makes the slide's formula differ from your sheet.** The deck
  writes its worked formula for a different point on the same link: the tip, with the full lengths,
  while the solution needs the link centre, so half-lengths replace them. Say that in one line.
  Presenting the modified formula silently reads as the deck and the answer sheet disagreeing, and the
  student then hunts for an error in one of them.
- Name the slide that justifies the constant the sheet had to choose (which mass distribution gives
  which inertia), so the assumption is citable instead of asserted.
- Save the cited pages as crops and attach them, at `Reference/slide-crops/<deck>-p<page>-<topic>.jpg`.
  The pointer then survives a re-render of the answer sheet, and the slide sits next to the derivation.

## Checks that double as teaching

- **Stacked joint update versus sequential scalar updates.** For independent measurements they agree
  to floating-point error; printing both side by side is what justifies "real code runs them
  sequentially to avoid inverting S".
- **Short form `P⁺ = (I − KH)P⁻` versus Joseph form.** Identical to rounding; names the numerically
  stable version.
- **Measurement-implied point versus the updated estimate.** The gap equals `(1 − K)·(implied −
  prior)`, which shows the filter trusting a sensor without snapping to it. Cheap, and it kills the
  "why is the answer not exactly the reading" question before it is asked.
- **Name the conditions that made the answer clean** (diagonal prior, diagonal R, disjoint nonzero
  rows of H) and say which later question breaks each one — that is the bridge to the next part.
- **A cross term's cosine is the law of cosines.** For a chained arm, the coefficient of the first
  joint's squared rate inside the second link's squared speed equals the squared distance from the
  base to that link's centre, so the cosine sitting in the inertia matrix is the triangle closing and
  nothing more mysterious. Print both expressions, plus that distance straight, at a right angle and
  folded, which answers "where did the cosine come from" before it is asked. Back it with central
  differences of the position formula reproducing the analytic velocity to ~1e-10: that agreement,
  not the algebra, is what shows the sheet and the engine are the same model.

## Pitfalls

- Answer one sub-question per message when that is what was asked. "Starting with 1(a)" means stop at
  (a); offer the next part in a single closing line, not a trailing quiz.
- Every published number comes from a run. If the engine disagrees with your derivation, the engine is
  right — fix the derivation, then say the derivation was wrong rather than quietly printing the
  engine's value.
- Answer the interjected side questions (`what is h`, what a *state* is) fully before resuming the
  assignment; those are the real blockers, and resuming first wastes the explanation.
- Concept pages in the vault can be long (tens of KB); grep them for the section names instead of
  assuming which parts are relevant.
- Confirm the vault's own solutions note is for **this** assignment before adopting its headings as
  your anchor. One course folder holds sibling assignments with different geometry (a planar arm with
  masses at the link centres and no gravity versus an RRP arm with gravity and given inertia tensors);
  match on the geometry and the given data, not on the course name. Adopting a near-miss sibling sends
  the student hunting for a gravity term his sheet never had.
- Tie-ins to the user's other work land well when they are one clause, not a paragraph: the same
  covariance rotation appears in a paper he is reading, the same `S` becomes the gate test later.
