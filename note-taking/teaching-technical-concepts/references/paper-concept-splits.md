# Concept inventories and split tables for a methods paper

Two asks arrive on the same paper days apart. "Explain X and Y" wants the **explanation** (SKILL.md
Method). "List out all the concepts used in it" wants the **inventory** — the map they re-read the
paper against. Build the inventory so the explanations can be lifted straight out of it.

## 1. The inventory: group by JOB, never as a flat list

A methods paper carries 50–80 terms. A flat alphabetical glossary is unreadable and teaches nothing,
because the reading order *is* the lesson. Group them into pipeline families, in pipeline order, and
give each its own table with a one-line plain-English gloss — your gloss, not the paper's definition.

| Family | What lives there |
|---|---|
| A. The stage | the setting: agents, their state variables, the space their state lives in, the task spec |
| B. The model | how state maps to the measured quantity: the forward model, the sensitivity matrix, the parameterisation of a pose, the transform convention |
| C. The hard constraint | signed distances, the primitive shapes that make those distances differentiable, the stacked worst-case quantity |
| D. The geometry of allowed | manifolds, feasible region, tangent space, half-space, null space — and *why the set is thin* (zero measure is the reason a projection step exists at all) |
| E. The optimisation machinery | objective, constraint, convex/nonconvex, the specific program classes (QP, QCQP, SDP, LMI), the duality vocabulary, the linear-algebra tools |
| F. Getting the output | decomposition, reference/warm start, interpolation, path parameterisation, the final command |
| G. The named competitors | baselines plus the metric names |

**Verify completeness by grepping, not by re-reading.** After drafting, grep the extracted page JSON
for each family's key terms and confirm nothing in the paper is missing from the inventory. Count
families, not terms.

## 2. The splits table: the part they actually keep

The user's restates weld independent axes into one idea, and a methods paper is full of genuine two-way
splits. Close the inventory with a two-column table — *looks like one thing / actually two* — and lead
with the split that is load-bearing for **that** paper. Recurring axes, by kind:

| Looks like one thing | The two things | Where it bites |
|---|---|---|
| A quantity at one **stage** vs the same quantity at another | built once while constructing the target / evaluated every step in the loop | one word counted by two different loops, reported as one number |
| The **primal** vs the **dual** | the whole solution vector / one scalar that determines it | quoting the scalar as though it were the solution |
| A **hard** vs a **soft** constraint | cannot be broken / breakable at a cost | which one wins when they conflict, and the accuracy number that results |
| An **equality** vs an **inequality** constraint | must be exactly on it / must stay on one side | they linearise into *different* shapes — a tangent plane vs a half-space — and get different treatment |
| A **category** vs **one member of it** | the class of problem / one named instance of it | the paper's contribution is usually the instance, not the category |
| The **null space** vs the **task space** | directions that move nothing you care about / directions that do | the search lives in the first, the constraint in the second |
| One word with two **meanings** | e.g. "convex decomposition": rewriting a problem as convex subproblems vs chopping a shape into convex pieces | a paper may use both and define only one — say which sense each use is |
| An **approximation** vs the exact thing | the straight-line stand-in / the curve it stands in for | why steps must stay small, and why a projection step is needed afterwards |
| A method **name** vs the **axis** it is scored on | a whole method / a solver swapped into the framework / an external framework | one success-rate column covering three different questions |

Add rows for whatever the specific paper splits. The deciding question for any stage-split row: **does
this number exist at run time, or did it shape the input before the run?**

## 3. The "which part is actually new" table

Journals bury the contribution in the abstract's adjectives. Give a three-row table instead: *piece /
status (the paper's contribution, or borrowed) / the reference it came from.* Read the related-work
section as a ledger — the paper names its borrowings there, and the contribution is whatever is left
over once you have listed them. This is the table that lets the user answer "so what is new here?" in a
supervisor conversation, which is usually why they are reading it.

## 4. The cost decomposition: multiply the paper's own two numbers

A method presented as a hierarchy almost always reports **per-iteration times** in one place (a
complexity or scalability table) and **iteration counts per step** in another. Multiply them out and you
get each stage's real share of the total — which is usually the fact that explains *why the hierarchy
exists at all*. The cheap stage runs on everything; the expensive stage runs on the few inputs that
needed rescuing. Papers rarely say this in prose, so deriving it is a genuine contribution to the
user's understanding.

Keep the counters apart when you do it: where a method reports two different loops over the same step
(an outer solve and an inner repair), that is the stage-split row in §2, and summing or averaging them
into one "iterations" number destroys the cost story. Then rebuild the headline total from the parts
and check it lands near the number the paper claims — the same sum check that catches a mis-paired
extraction (§8d in SKILL.md).
