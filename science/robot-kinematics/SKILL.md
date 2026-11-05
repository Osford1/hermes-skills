---
name: robot-kinematics
description: "Use when deriving or checking manipulator kinematics or dynamics."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [robotics, kinematics, dh-parameters, jacobian, manipulator, sympy, numpy]
    category: science
    related_skills: [sympy, coursework-assignment-reports, urdf, verifying-source-claims]
---

# Manipulator kinematics and dynamics (DH → FK → Jacobian → EOM)

Deriving or checking the model of a serial arm: the DH table, forward kinematics as a
homogeneous matrix, the orientation as RPY/Euler angles, the Jacobian of position and orientation, and the
equation of motion by Lagrange or Newton–Euler.
The output is a derivation, so every boxed result must be checked before it ships. Every rule below applies
to all of these; the dynamics-specific steps sit in their own section.

## When to Use
- "Give the D-H table / forward kinematic equation / Jacobian of this manipulator."
- A coursework or exam question showing an arm schematic and asking for one of the derivations above.
- Checking a Jacobian that came from a textbook, a paper, or an earlier session.
- A question asking for the arm's equation of motion — Lagrange, Newton–Euler, or an assembled
  $D(q)\ddot q + C(q,\dot q)\dot q + G(q) = \tau$.
- Any time the model is reconstructed from a drawing rather than from a URDF/spec sheet.

## Procedure

1. **Fix the model before any algebra.** Number the joints and name each joint type (revolute /
   prismatic). Then place frames: $z_i$ runs along the axis of joint $i+1$ (see the first pitfall),
   $x_i$ along the common normal, $y_i = z_i \times x_i$ right-handed. Write down the drawn zero pose
   as the numeric target for step 3.

2. **Build the DH table with the standard transform** $T_i = R_z(\theta_i)T_z(d_i)T_x(a_i)R_x(\alpha_i)$.
   Column semantics: $\theta_i$ about $z_{i-1}$, $d_i$ along $z_{i-1}$, $a_i$ along $x_i$, $\alpha_i$ the
   twist from $z_{i-1}$ to $z_i$ about $x_i$. Geometry gives the entries without guesswork:
   - axes intersect → $a_i = 0$, and a lateral offset between them appears in the **d** column, not the a column;
   - axes parallel → $\alpha_i = 0$; perpendicular → $|\alpha_i| = 90^\circ$, signs alternating along a chain;
   - a sliding joint's displacement is the $d$ entry and its $\theta$ is a constant (usually 0);
   - every $a_i$ of an intersecting/spherical wrist is 0, and the tool offset is $d_6$.

3. **Do the FK symbolically (sympy), then check it three ways:** the position vector at the zero
   configuration equals the drawn pose; the number of variable-bearing entries matches the degrees of
   freedom; and any collapsed rotation product is confirmed numerically against the raw product.
   Elementary DH products collapse through the conjugation identity $R\,R_a(\theta)\,R^{-1} =
   R_{Ra}(\theta)$, e.g. $R_x(-90^\circ)R_z(\theta)R_x(90^\circ) = R_y(\theta)$, which is what turns an
   alternating $\pm90^\circ$ twist chain into a short product of $R_z/R_y$ factors. Show the compact
   form *and* the expanded elements; state the wrist centre explicitly ($^0T_3$ usually prints it).

4. **Orientation: extract with two-argument `atan2`, never `atan` of a ratio.** Give the general
   extraction formulas, then substitute the elements from step 3. Name the singular case and the
   convention you adopt for it (see the reference). If the question names no convention, use RPY with
   $R = R_z(\varphi)R_y(\vartheta)R_x(\psi)$ and say so.

5. **Build the Jacobian by the route the question names — three are equivalent, and the answer should
   say which one it used.**
   - **Vector-product, base frame (the default).** Column $i$ is $[\,z_{i-1}\times(p_e-p_{i-1});\; z_{i-1}]$
     for a revolute joint and $[\,z_{i-1};\; 0]$ for a prismatic one, with $z_{i-1}$ the 3rd column of
     $^0R_{i-1}$ and $p_{i-1}$ the origin of frame $i-1$, both in the base frame, and $p_e$ the tool point
     (or the wrist centre when the tool offset is zero). **When the ask is "explain the method", derive the
     rule instead of quoting it:** with the other joints frozen and joint $j$ running at unit rate, the tool is
     welded to the downstream body, so a rotation $dq_j$ displaces a point at offset $r = p_e - p_{j-1}$ by
     $(z_{j-1}\times r)\,dq_j$ — divide by $dq_j$ and the column follows, where $|z_{j-1}\times r|$ is the
     tool's distance from the axis (zero when it sits on the axis, which is the real reason a spherical
     wrist's last columns carry no linear part). Then the recipe: build the $^0T_i$, read the 3rd/4th columns,
     take the cross products, locate the zeros by geometry. Phrasing and check table in the reference.
   - **Differentiation of the forward-kinematic matrix** — the route for *"get the Jacobian FROM the FK
     matrix"*, and what a lecture's 微分变换法 / differential-transformation slides describe:
     $J_v(:,i)=\partial p/\partial q_i$ and $J_\omega(:,i)=\operatorname{vee}(\partial R/\partial q_i\,R^{\mathsf T})$,
     whose skew part carries the joint axis. The derivative collapses: $(\partial A_i/\partial\theta_i)A_i^{\mathsf T}
     =\operatorname{skew}(\hat z)$ for *every* DH row, so $J_\omega(:,i)=z_{i-1}$ — the 3rd column of
     $^0R_{i-1}$, which is the vector-product rule's own axis. Say so in the answer: the two routes are one
     theorem, not rivals.
     **Present this route skew-free when teaching it** (this user asked for exactly that): do not name
     `skew`/`vee`. Calibrate the reading rule on the principal-axis rotations, whose $\omega$ is known by
     inspection — $(M_{32},M_{13},M_{21})$ returns $(0,0,1)$, $(0,1,0)$, $(1,0,0)$ — then show the middle
     bracket by plain $3\times3$ multiplication (the $\theta$'s cancel, leaving $[[0,-1,0],[1,0,0],[0,0,0]]$
     for *any* $\alpha$), then prove the third-column result algebraically as
     $RBR^{\mathsf T}=r_2r_1^{\mathsf T}-r_1r_2^{\mathsf T}\Rightarrow(M_{32},M_{13},M_{21})=r_1\times r_2=r_3$,
     the 3rd column of $^0R_{j-1}$. Two supporting facts to quote from the run: $M+M^{\mathsf T}=0$ holds
     because the frame's columns are unit and mutually perpendicular (so nine numbers *must* collapse to
     three), and the joint variable of DH row $i$ lives only in $T_{i-1}^{i}$ — show it by printing which of
     the six matrices changes under each $\partial/\partial q_j$ (an entry that changes moves by $O(h)$, so a
     check whose job is *which* matrix changed must compare against $h\cdot|entry|$ or $10^{-10}$ absolute — a
     round $10^{-6}$ threshold sits above the perturbation and reports "nothing changed"). Asked *why* the
     right-multiplication by $R^{\mathsf T}$ is there, give its three jobs: it turns nine unreadable derivative
     entries into a fixed antisymmetric shape carrying three numbers, it cancels every factor downstream of
     joint $j$, and it fixes the frame the axis is reported in ($\dot RR^{\mathsf T}$ = base frame,
     $R^{\mathsf T}\dot R$ = tool frame — different matrices off the identity pose; check numerically, the
     wrong one still looks plausible). Recipe, frame trap, MATLAB form and the purpose paragraph in the
     reference.
   - **Read the column off the T matrices, no calculus** — the same numbers once the frame bookkeeping
     is right: $M_i={}^{i-1}T_n=A_i\cdots A_n$, then the column rule and the tool-frame→base conversion
     in the reference (worked column included).
   Report the axes/points table, the per-column derivation, and the final matrix; say which rows are
   linear and which are angular. **Give each column's magnitude and the unit vector it lies along**: with
   intersecting axes the columns factor into (scalar) × (an axis of the moving frame), the scalar is the
   physical radius of that motion, and the sum-of-squares test on the bracket is free. That one table
   answers "how did you get this column?" (differentiate component by component, then factor) and exposes
   the perpendicularity behind a diagonal $J^{\mathsf T}J$ and a $\det J$ that is the product of the
   magnitudes — table and spherical-coordinate parallel in the reference.

6. **Verify numerically before writing anything up** — every column, both blocks. The independent route
   for a symbolic derivation is finite differences; `templates/verify_jacobian.py` does it and prints a
   per-column error table. Expect max error ~1e-9…1e-11 with float64 and $h=10^{-6}$; anything larger
   means an axis, index or sign error, not rounding.

7. **State the assumptions the source does not fix, at the top of the answer.** A drawing rarely
   determines the sense of the drawn $z$ axes, the tool offset, or the symbols for unlabelled links.
   One short assumptions block ("frames as drawn; $d_1$ = column height, $a_2$ = upper arm;
   $d_6 = 0$") makes the whole answer checkable, and lets you add the flip rule — reversing a drawn
   $z$ reverses the sign of the matching $\alpha$ — instead of asking. When they hand back their own
   table with the opposite twist signs, the answer is that only the **relative** sign of consecutive
   twists is geometric: matched signs put the zero pose one way, opposite signs mirror the arm about the
   base axis and flip only $\theta_1$'s sense. So check their table against the systematic rule
   ($x_i = z_{i-1}\times z_i$, equivalently the right-hand rule about $+x_i$) rather than against a
   remembered key, and say which one it is. Accepting their signs means **propagating** them: an isotropic
   inertia leaves the kinetic terms untouched, but the zero pose moves and the gravity term in that joint's
   row flips sign. **The gravity *form*, though, is set by where $\hat g$ points, not by the twist signs:** $V = m_3gb_3\cos\theta_2$ holds only when the base axis lies along $\hat g$; the reading with $\hat g \perp z_0$ gives $V = -m_3gb_3\sin\theta_2\cos\theta_1$ and puts gravity in $\theta_1$'s row as well. Tell them to flip both or neither, never mix, and to
   put the convention line plus the zero-pose self-test on the answer sheet.

## Dynamics — the equation of motion for the same arm

Same discipline: fix the model, state the assumptions, derive, then *check every row* before it ships.

1. **Assign the coordinates and their positive senses.** $\theta$ for a revolute joint, $d$ for a
   prismatic one; state that a positive torque/force acts in the direction of increasing $\theta$/$d$.
   Name the vertical the angles are measured from: for a spherical/polar arm, measuring the elevation from
   the base axis (arm along that axis at the angle's zero) is the choice that keeps gravity in one row.
   If the figure leaves it ambiguous, take the standard arrangement, say so in the assumptions line, and
   flag it in the closing caveat. **Read the problem's own gravity line before assuming which axis is vertical — it is an arbiter, not a caveat.** Since $x_i \perp z_{i-1}$ holds by construction, a statement that $\hat g$ lies along a frame $x$-axis ("重力方向与 $X_1$ 相同") says the **base joint axis is perpendicular to gravity**: the base joint *swings* the arm in a vertical plane instead of turning it like a turntable, gravity enters $\theta_1$'s row, and $V$ takes the $\sin\theta_2\cos\theta_1$ form. $\hat g \parallel z_0$ is the vertical-base reading and confines gravity to $\theta_2$'s row. Data saying $\hat g \parallel x_1$ while you assumed a vertical base axis is a model error to fix, not an ambiguity to hedge — and it is decidable in one line, before any algebra.
2. **Kinetic energy link by link — translational plus rotational.** Two shortcuts to look for before any
   algebra:
   - **An isotropic inertia tensor removes the frame orientation entirely.** With $I=\mathrm{diag}(A,A,A)$
     the rotational energy about the centre of mass is $\tfrac12 A|\omega|^2$ about *any* axis, so no link
     frame rotation matrix ever enters $T$ — the link-frame convention stops mattering for the energy. A
     problem handing you $\mathrm{diag}(A,A,A)$ for every link is hand-solvable by design; say so.
   - **A link whose centre of mass lies on its joint axis never moves — it only spins.** No $\tfrac12mv^2$
     term, and no change of height, so it leaves only $\tfrac12I\omega^2$ plus a constant in $V$.
   - Two rotation rates **add in quadrature** when their axes are perpendicular:
     $|\omega|^2 = \dot\theta_a^2 + \dot\theta_b^2$.
3. **$V$ from centre-of-mass heights alone.** Only coordinates that move a mass vertically may appear in
   $G$ — write $V$ and let it say so; a coordinate that cannot change a height has no gravity row. Which coordinates those are is already fixed by step 1's gravity direction: $G_1 = 0 \iff \hat g \parallel z_0$. Hand that equivalence to the user as the check — it is one line and it catches a wrong base-axis assumption.
   **The gravity vector is the Jacobian's gravity row:** for a moving mass, $G=-mg\,\hat g^{\mathsf T}J$
   with $\hat g$ the down unit vector, so the $G$ built from heights and the $G$ read off $J$ must agree term
   by term — test that equality symbolically rather than by eye; the reference carries its form on this arm.
4. **Euler–Lagrange per coordinate**, $\frac{d}{dt}\frac{\partial L}{\partial\dot q} - \frac{\partial L}{\partial q} = Q$,
   with $L = T - V$ and $Q$ the actuator torque/force, then tidy into the lecture's matrix form
   $D(q)\ddot q + C(q,\dot q)\dot q + G(q) = \tau$. Name the velocity terms as you group them (Coriolis =
   a length changing under a rotation; centrifugal = a spin flinging a mass outward) so the user can read
   what each term does instead of just accepting it. **Carry the collapse to the matrix form explicitly — it is the part they ask about as its own question** ("from $L$ and Euler–Lagrange, how do we get $\tau = M(\theta)\ddot q + h(\theta,\dot q)$?"): $\partial L/\partial\dot q_i = \sum_j M_{ij}\dot q_j$ is linear in the rates and $\partial L/\partial q_i = \tfrac12\sum_{j,k}(\partial M_{jk}/\partial q_i)\dot q_j\dot q_k$ holds *all* the pose dependence, so the product rule inside $d/dt$ supplies one extra sum and the leftover bracket, $\sum_{j,k}[\partial M_{ij}/\partial q_k - \tfrac12\partial M_{jk}/\partial q_i]\dot q_j\dot q_k$ (equivalently $\sum_{j,k}c_{ijk}\dot q_j\dot q_k$, Christoffel), *is* $h$. No separate Coriolis step exists where new physics enters. **Net $M$ from the Jacobians you already built** ($M = \sum_i m_iJ_i^TJ_i$ plus rotational terms) and match it term by term against the assembled $M$: it is the mass-matrix twin of the gravity-row identity $G = -mg\,\hat g^TJ$, and it explains the off-diagonal coupling. Algebra, worked planar arm, letter mapping and the two checks: `references/manipulator-dynamics-lagrange.md`.
5. **Static sign test before shipping.** Set $\ddot q = \dot q = 0$ and hand-check every row: arm along the
   axis $\Rightarrow$ the telescoping force is exactly $m_3g$; arm perpendicular to it $\Rightarrow$ zero;
   a link held horizontally $\Rightarrow$ $\tau = -mg \times$ moment arm; base axis vertical $\Rightarrow$
   no gravity entry in $\theta_1$'s row. A wrong sign in a $G$ entry surfaces here as an actuator that has
   to push the wrong way.
6. **If the question names Newton–Euler**, do it per link with the reaction forces, use it for inverse
   dynamics / real-time control, and show that both routes must end at the same $D/C/G$ term by term.
   Then name which question the answer answers. It is the *same* equation, and $\tau$ and $q$ are both
   joint-space vectors — what flips is which side you solve for. This is not a map from torque space into
   coordinate space, and the equation itself is neither forward nor inverse dynamics. **Inverse dynamics**
   = given $(q,\dot q,\ddot q)$, evaluate the right-hand side: algebra, no matrix inverse, which is why
   Newton–Euler does it in real time. **Forward dynamics** = given $\tau$, solve
   $\ddot q = D^{-1}(\tau - C\dot q - G)$ and integrate — what a simulator does. A homework asking for the
   equation of motion wants the *inverse-dynamics* form written out as scalar $\tau_1,\tau_2,f_3$
   expressions in the joint variables and their rates; the matrix form is the arrangement you tidy into,
   not the answer.
7. Worked end-to-end example, both frame readings, plus the figure-reading procedure:
   `references/manipulator-dynamics-lagrange.md`.

## Pitfalls

- **Joint $i$'s axis is $z_{i-1}$, one frame back — the joints are offset against the frames.** And
  when $\alpha_i = 0$ the neighbouring frames share the same $z$, so a one-frame index error is
  *invisible* for that joint and only corrupts the columns on either side. Symptom: a Jacobian whose
  linear and angular blocks are wrong in a couple of columns while the rest matches to 1e-10. Re-index
  and re-verify; do not re-derive the algebra. The offset is a *labelling* choice, so sources disagree:
  a deck printing $J_i=[z_i\times{}^ip_n^0;\;z_i]$ numbers by frame, one less than the joint number.
  When the user holds up that form, answer with the mapping between the two index systems — the formulas
  are identical, and an unexplained $z_{i-1}$ reads as a contradiction. Never mix the two numberings
  inside one matrix. The same shift moves the $\alpha$ row labels when a figure numbers the base frame 1
  and the deck attaches frame 0 to the base: the angles are unchanged, only the labels move by one — quote
  both numberings once and move on.
- **$\alpha_i$ in a DH table is the link twist; the dynamics chapter reuses the same letter for angular
  acceleration.** A question that asks you to define $\alpha_i$ wants 杆件扭角 — the rotation from $z_{i-1}$
  to $z_i$ measured about $x_i$, positive by the right-hand rule about $+x_i$, $\alpha_i\in(-\pi,\pi]$ — a
  *fixed constant* of the arm's geometry, not a rate of anything. Never let it drift into $\ddot\theta$ when
  both appear in the same problem set; state the distinction in one line before the algebra starts.
- **Check the convention before doubting the algebra.** A DH table that "does not work" is often the
  modified (Craig) convention rather than the standard one — every row meaning shifts by one index.
  Match the table to the course's book or to the figure's frame placement, not to a remembered form.
- **Zero linear entries in a spherical wrist's last three columns are the correct answer**, not a bug:
  the tool point coincides with the wrist centre when $d_4=d_5=d_6=0$. With a tool offset those columns
  are $z_i \times d_6 a$.
- **The differential-transformation column is taken in the frame *before* the joint's own A-matrix, and
  it lands in the TOOL frame.** $M_i=A_i\cdots A_n$ (cancel the factors in front of the joint, so for
  joint 1 it is $T_n$ itself), *not* $T_n^{-1}T_i$ — that plausible variant is off by a rotation and
  yields O(1) column errors that read exactly like sign or index bugs, so it can be attempted two or
  three times before the real cause shows. Forgetting the $\operatorname{blkdiag}(R_{0n},R_{0n})$
  conversion afterwards is the second silent error in the same step. One finite-difference run settles
  both; never ship the column rule on faith.
- **Do not differentiate the whole symbolic chain with a CAS — restructure it instead.** Forming
  $\partial R/\partial\theta_i\,R^{\mathsf T}$ on the full $3\times3$ $R$ of a five- or six-joint chain and
  then simplifying is a trig simplification of dozens of angle products; it runs past a foreground tool
  timeout and returns nothing usable. Prove the per-joint identity once on a generic one-angle $A_i$,
  assemble the columns structurally from $^0R_{i-1}$, and verify numerically by central differences on
  $R$. Compare symbolically only per entry (or numerically at two or three configurations) — one
  `simplify` over all 36 entries is the single most expensive line in the script. Redirect a long CAS
  run's stdout to a file and read it back with `read_file` — a file survives both a timeout and the harness truncating a long printed matrix down to a single line.
- **Never print a singularity, rank or degeneracy claim you have not checked numerically.** Compute the
  determinant or rank of the block at a few configurations; a plausible-looking determinant formula is
  the cheapest thing in the write-up to get wrong and the easiest to check.
- **Do not try to recover geometry the figure does not print.** Repeated cropping, upscaling and
  enhancement of a hand-drawn sketch does not manufacture link lengths, joint senses or axis
  directions that were never drawn. Fix the model from the standard convention for that arm, state the
  assumptions, list the two or three items to confirm against the lecture notes, and solve. Front-load
  the assumptions; do not stall the answer on the picture. But do not declare the figure unusable before
  testing a candidate model against it: repeated reads of a small hand-drawn sketch (tool-assisted
  included) return *contradictory* axis directions from call to call, while the printed frame labels and
  the marked tool point are unambiguous. Take the standard convention for that arm, then check the
  identities it must satisfy — each frame's $x$ axis along the drawn link, the origin of the last frame
  at the marked point, the joint axes as the 3rd columns, and $z_{i-1}\times\hat u=\partial\hat u/\partial\theta_i$
  for the link directions $\hat u$. One symbolic pass settles what cropping cannot. **Run the frame-algebra filter before spending more crops
  on a figure whose printed axis looks impossible:** $x_i \perp z_{i-1}$ holds by construction, so a figure
  that labels $x_1$ along the gravity arrow is saying frame 1's joint does not turn about the vertical —
  the picture and the assumed base axis cannot both be right. That turns an unreadable drawing into a
  two-way choice you can state in one line ("assuming the base axis is vertical as the classification slide
  shows; if your $X_1$ is the frame axis along $g$, only the gravity terms rotate by 90°"), which is a
  finished answer — a third round of crops is not.
- **A central difference applied to an already-differentiated expression returns the *second* derivative — FD the raw function and take each derivative once.** Differencing an expression that is already $\partial L/\partial\theta_i$ in order to "compute" $\partial L/\partial\theta_i$ silently yields $\partial^2L/\partial\theta_i^2$, and the error is invisible exactly where the true derivative is identically zero (a coordinate the kinetic energy does not depend on — the base joint of a fixed-base arm): that row agrees to machine precision. So a verification table that matches one row at 1e-11 and misses another by an O(1) amount is a bug in the *checker*, not a missing term in the derivation — reconcile the numbers by hand before touching the algebra. Accept mark: ~1e-11 on every row.
- **One letter, two meanings: in this lecture's dynamics chapter $C(q)$ is the gravity vector, not Coriolis.** The deck writes $D(q)\ddot q + H(q,\dot q)\dot q + C(q) = \tau$, so $H$ is the Coriolis/centrifugal *matrix* while a sheet may write $h$ for the *vector* $h = H\dot q$; reading $C$ as Coriolis inverts the physical meaning of a whole term, the same failure mode as $\alpha$ (link twist) vs $\ddot\theta$. Whenever the answer's letters differ from the lecture's, the mapping line ($M = D$, $h = H\dot q$, gravity folded into $C$ and zero when no mass changes height) belongs in the deliverable, in the lecture's own notation with its slide number.
- **Keep symbols symbolic; substitute only the numbers the problem states.** A question that gives
  $d_2 = 0.1$ m wants 0.1 in that one entry — not every length converted to a number.

## Output conventions (this user)
- English prose and LaTeX even when the assignment is Chinese; no pinyin, no bilingual by default
  (offer the CN version in one closing line instead).
- Deliver the solved derivation in chat with real math, and save the same content as a `.md` beside the
  course material (copy, don't move files).
- **"Explain step by step how to get X from Y" is a teaching request, not a restatement request.**
  Answer with the numbered steps and the definition each step rests on, then ONE worked instance on
  their own problem — the intermediate numbers quoted (the $n/o/a/p$ entries, the resulting column) and
  the check that reconciles it to the finished answer — plus a saved script that re-runs it. A second
  copy of the boxed matrix teaches nothing. Where the lecture has its own route for that step, present
  that route explicitly (it is what the exam marks against) and name the better-conditioned alternative
  beside it.
- **Name every symbol at the point of first use, in the lecture's own notation.** A re-teaching answer
  that introduces shorthand — an $A_i$ for the slides' $T_{i-1}^{i}$, a $q$ for the joint-variable
  vector — stalls the user on the *definition*, not the algebra: "what is $A_i$?" and "what is $q$ in
  $h(q)$?" arrive before any misunderstanding of the math does. Give the slide's own symbol and page
  number, then the shorthand, then its value on their own arm, in one breath. For a **full solution to a
  fresh problem** whose figure prints no link symbols, use a three-column table at the top instead
  (symbol | what it is | where it comes from: printed in the question, drawn but unlabelled, or my
  shorthand) — a request for the full solution that adds "explain any unfamiliar notation" is telling you
  the answer is unreadable until the names are on the page. Declare symbols that exist only to keep a
  cross product on one line (an $R=a_2c_2+a_3c_{23}$) as pure shorthand, and close by naming the two or
  three things the figure leaves open for the user to confirm.
- **Pre-empt the two misreadings that each cost a whole reply:** $\dot R$ is not the angular velocity
  (nine entries; $\omega=\operatorname{vee}(\dot R R^{\mathsf T})$, which is why the extra
  multiplication is there), and $J$ maps joint velocities to task velocities rather than positions to
  velocities — it is *derived* from the position map but does not *do* what the position map does.
- **When they ask for a result "without" a named symbol, substitute every occurrence — never restate the
  rule.** These asking-a-cleaner-form requests escalate ("without `skew`", then "without $z$"), because every
  piece of shorthand left in the answer is a place they cannot check. Swap the axis symbols for their explicit
  vectors, keep the structure visible — split the matrix into its linear rows and angular rows, or list it
  column by column with a provenance table naming what each block came from — and re-run the numeric check on
  the substituted form, so what is printed is what was verified. Flag genuine coincidences inside it (a
  prismatic column's linear block equals the next joint's angular block — same axis, one translating and one
  rotating), since that is what makes the substituted form readable rather than just noisier.
- **When they hand you their own recipe and ask "is this right?", grade it line by line** — ✓/✗ per step,
  then name the step that is mis-filed and the one that is missing, then give the corrected numbered list.
  Do not re-teach from zero. The two errors that recur: conflating "form $L = T - V$" (one scalar, built
  once, no per-variable work) with "apply Euler–Lagrange" ($n$ equations, one per coordinate), and stopping
  after the raw equations without collecting the terms into $D$, $C$ and $G$ — a correct derivation that
  never reaches the lecture's matrix form reads as incomplete.
- **When they ask *why* a derivation is needed, answer with its uses on their own project**, not its place
  in the syllabus: inverse dynamics evaluated along a desired trajectory *is* a feedforward controller (and
  the baseline any learned feed-forward block has to beat), $G(q)$ alone is gravity compensation, $D(q)$
  sets motor sizing and shows how the load moves with pose, and $\ddot q = D^{-1}(\cdots)$ plus integration
  is simulation. Four short lines, each tied to something they have already built.
- **When a re-derivation changes something you already delivered, mark the changed block in one line, at the point of change** ("this is where the earlier form changes"), then give the replacement in full and one clause of why. Work headed for hand-in must not carry two live versions — the user cannot tell which is current, and a silent correction reads as an unreported risk.
- Close with a one-line offer (PDF, numeric substitution, an interactive figure), not a quiz. Keep the
  convention-dependent items in a short caveat line so the user can check them against the lecture.

## Support files
- `references/manipulator-kinematics-reference.md` — DH table semantics and the standard/modified
  trap, standard arm tables (Stanford/Scheinman, 3R planar), the rotation-conjugation identities, RPY
  and ZYZ extraction with their singular branches, the vector-product Jacobian rules, analytic vs
  geometric Jacobian, the two routes that start from the FK matrix (differentiate $T_n$, or read each
  column off $M_i=A_i\cdots A_n$ with the tool-frame trap and a worked column), why the right-multiplication
  by $R^{\mathsf T}$ is there, the derivation to give when the ask is "explain the vector-product method"
  with its exam recipe, the column-magnitude table (each column = scalar × a moving-frame axis, with the
  spherical-coordinate parallel, the constant-matrix factorization and the gravity-row identity
  $G=-mg\,\hat g^{\mathsf T}J$), and the cheap self-checks.
- `references/manipulator-dynamics-lagrange.md` — Lagrange recipe, the collapse from $L$ to $M\ddot q + h$ (planar 2-link worked, with the $\cos\theta_2$ origin, the $V^TV$ gloss, the deck-vs-sheet letter mapping and the symbolic + finite-difference verification recipe), the spherical (球坐标式) RRP arm worked
  end to end with its assembled $D/C/G$, the static sign checks, the gravity-direction test that decides which reading applies, the assembled result *and* the $\theta_2$-zero translation for the perpendicular-gravity reading, and how to read a
  figure's labels reliably when vision keeps contradicting itself.
- `templates/verify_jacobian.py` — copy into `Working/`, fill in the DH table (or paste the claimed
  Jacobian), run: finite-difference linear and angular blocks plus a per-column error table.
