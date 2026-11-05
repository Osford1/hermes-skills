# Manipulator kinematics — conventions, formulas, checks

## DH table semantics

Standard ("classic") DH, the form used by most robotics courses and by Paul:

$$T_i = R_z(\theta_i)\,T_z(d_i)\,T_x(a_i)\,R_x(\alpha_i)$$

- $\theta_i$: rotation about $z_{i-1}$; $d_i$: translation along $z_{i-1}$; $a_i$: translation along
  $x_i$; $\alpha_i$: rotation about $x_i$ (the twist from $z_{i-1}$ to $z_i$).
- Frame $i$ is attached at the **far end** of link $i$; the joint variables of joint $i$ are $\theta_i$
  (revolute) or $d_i$ (prismatic).
- Courses usually print the columns as $(\theta, \alpha, d, a)$ — the ordering differs between books,
  the semantics do not.

Modified (Craig) DH: $T_i = R_x(\alpha_{i-1})T_x(a_{i-1})R_z(\theta_i)T_z(d_i)$ — frame $i$ sits at
joint $i$, so every index shifts by one relative to the standard form. A table that "does not generate
the right FK" is very often the other convention, not an error.

Geometry → entry rules: axes intersect ⇒ $a_i = 0$ (a lateral offset between the axes appears in $d$);
axes parallel ⇒ $\alpha_i = 0$; axes perpendicular ⇒ $|\alpha_i| = 90^\circ$ with alternating signs
along the chain; sliding joint ⇒ its variable occupies $d_i$ and $\theta_i$ is constant (usually 0).

## Rotation-conjugation identities (collapse FK products)

$$R\,R_a(\theta)\,R^{-1} = R_{Ra}(\theta)$$

with $z\mapsto y$ for $R_x(-90^\circ)$ and $z\mapsto -y$ for $R_x(+90^\circ)$:

$$R_x(-90^\circ)R_z(\theta)R_x(90^\circ) = R_y(\theta), \qquad
R_x(90^\circ)R_z(\theta)R_x(-90^\circ) = R_y(-\theta)$$

A chain of alternating $\pm90^\circ$ twists therefore collapses to a short product of $R_z/R_y$
factors — the Stanford arm's orientation is $R_z(\theta_1)R_y(\theta_2)R_z(\theta_4)R_y(\theta_5)R_z(\theta_6)$.
Always confirm the collapsed form against the raw matrix product numerically.

## Standard arm tables

Stanford / Scheinman arm (standard DH; joint 3 is prismatic):

| $i$ | $\theta_i$ | $\alpha_i$ | $d_i$ | $a_i$ |
|---|---|---|---|---|
| 1 | $\theta_1$ | $-90^\circ$ | 0 | 0 |
| 2 | $\theta_2$ | $+90^\circ$ | $d_2$ | 0 |
| 3 | 0 | $0^\circ$ | $d_3$ | 0 |
| 4 | $\theta_4$ | $-90^\circ$ | 0 | 0 |
| 5 | $\theta_5$ | $+90^\circ$ | 0 | 0 |
| 6 | $\theta_6$ | $0^\circ$ | 0 | 0 |

Position with $d_6 = 0$: $\mathbf p = (d_3c_1s_2 - d_2s_1,\; d_3s_1s_2 + d_2c_1,\; d_3c_2)$ — the wrist
centre, which is also the tool point when the tool offset is zero. A shoulder offset parallel to the
base axis is a $d$, never an $a$; that is why it never shows up in the $a$ column.

3R arm with a vertical base joint and two in-plane links (column height $d_1$, upper arm $a_2$,
forearm $a_3$, angles from the horizontal) — the standard "arm on a rotating turret" figure. Standard DH:

| $i$ | $\theta_i$ | $\alpha_i$ | $d_i$ | $a_i$ |
|---|---|---|---|---|
| 1 | $\theta_1$ | $+90^\circ$ | $d_1$ | 0 |
| 2 | $\theta_2$ | $0^\circ$ | 0 | $a_2$ |
| 3 | $\theta_3$ | $0^\circ$ | 0 | $a_3$ |

What that table pins down: frame 2's $x$ axis *is* the upper arm and frame 3's *is* the forearm, so the
origin of frame 3 is the tip; $z_1=z_2=(s_1,-c_1,0)=\hat r_1\times z_0$ with $\hat r_1=(c_1,s_1,0)$ the
horizontal direction of the arm plane; angles are elevations above horizontal, so the forearm direction
uses $\theta_2+\theta_3$.

$$\mathbf O_c = \big[(a_2c_2 + a_3c_{23})c_1,\; (a_2c_2 + a_3c_{23})s_1,\; d_1 + a_2s_2 + a_3s_{23}\big]$$

Jacobian (three revolute; $R=a_2c_2+a_3c_{23}$, $Z=a_2s_2+a_3s_{23}$):

$$J=\begin{bmatrix}-Rs_1 & -Zc_1 & -a_3c_1s_{23}\\ Rc_1 & -Zs_1 & -a_3s_1s_{23}\\ 0 & R & a_3c_{23}\\
0&s_1&s_1\\ 0&-c_1&-c_1\\ 1&0&0\end{bmatrix}$$

Columns 2 and 3 repeat their angular block because the axes are parallel — correct, not a copy-paste slip.

## Orientation extraction

RPY ($R = R_z(\varphi)R_y(\vartheta)R_x(\psi)$):

$$\varphi = \operatorname{atan2}(r_{21}, r_{11}), \quad
\vartheta = \operatorname{atan2}\!\big(-r_{31}, \sqrt{r_{11}^2+r_{21}^2}\big), \quad
\psi = \operatorname{atan2}(r_{32}, r_{33})$$

Singular at $\vartheta = \pm90^\circ$ ($r_{11}=r_{21}=0$): only $\varphi\pm\psi$ is determined. Take
$\varphi = 0$, then $\vartheta=+90^\circ \Rightarrow \psi = \operatorname{atan2}(r_{12}, r_{22})$ and
$\vartheta=-90^\circ \Rightarrow \psi = \operatorname{atan2}(-r_{12}, -r_{13})$.

ZYZ ($R = R_z(\varphi)R_y(\vartheta)R_z(\psi)$):
$\vartheta = \operatorname{atan2}(\sqrt{r_{13}^2+r_{23}^2}, r_{33})$,
$\varphi = \operatorname{atan2}(r_{23}, r_{13})$,
$\psi = \operatorname{atan2}(r_{32}, -r_{31})$; singular at $\vartheta = 0, 180^\circ$ where only
$\varphi+\psi$ (or $\varphi-\psi$) survives.

Never use $\arctan$ of a ratio: it loses the quadrant and divides by zero at the singular pose — and
the same applies to the $\arccos$-of-a-ratio forms some decks print
($\vartheta=\sin^{-1}(-r_{31})$, $\psi=\arccos(r_{33}/\cos\vartheta)$,
$\varphi=\arccos(r_{11}/\cos\vartheta)$): they divide by $\cos\vartheta$, so near $\vartheta=\pm90^\circ$
the round-trip error grows from ~0.06° to several degrees. Use the deck's version in an exam that asks
for it, and say in the answer that `atan2` is the conditioned form and why.

The `atan2` extraction fixes $\vartheta\in(-90^\circ,90^\circ)$. Outside that branch the same matrix
returns the equivalent triple $(\varphi+180^\circ,\ 180^\circ-\vartheta,\ \psi+180^\circ)$ — the same
pose, not an error. Checked over 2000 random poses: exact to $\sim10^{-16}$ inside the branch, the
flipped triple outside it. State the branch when the question does not fix it.

## Jacobians

Geometric Jacobian by the vector-product method, all quantities in the base frame from the FK
matrices ($z_{i-1}$ = 3rd column of $^0R_{i-1}$, $p_{i-1}$ = origin of frame $i-1$):

$$\text{revolute: } J_i = \begin{bmatrix} z_{i-1}\times(p_e - p_{i-1})\\ z_{i-1}\end{bmatrix}, \qquad
\text{prismatic: } J_i = \begin{bmatrix} z_{i-1}\\ \mathbf 0\end{bmatrix}$$

- **The vector is measured from *that* joint's own frame origin, never all from the base.**
  $p_e-p_{i-1}$ is the deck's ${}^{i-1}p_n^0$; using $p_e$ itself in every column is the classic slip, and
  its signature is that the trailing columns come out *equal to each other* (same axis, same vector). The
  deck's own worked example shows the shift: in a 2-DOF planar arm column 0 uses the full
  $l_1c_1+l_2c_{12}$, column 1 only $l_2c_{12}$.
- **Reconcile index labels before arguing about them.** A deck that prints
  $J_i=[z_i\times{}^ip_n^0;\;z_i]$ indexes by *frame*: $z_i$ = 3rd column of $^0T_i$ and
  ${}^ip_n^0=p_e-p_i$ with $p_i$ the origin of frame $i$ — one less than the joint number, so its
  $J_0,J_1,J_2$ are this reference's $J_1,J_2,J_3$. Answer a "isn't it $z_i$?" with that mapping table;
  the formulas agree.
- Prismatic columns have a zero angular block and a unit-norm linear block — quick sanity check.
- Column 1 of a base-rotation joint: $z_0\times p_e = (-p_y, p_x, 0)$ — a rotation about $z_0$ cannot
  change the height or the radius of the tip. Cheap first check on any base-jointed arm.
- Geometric vs analytic Jacobian: the geometric one gives $\omega = J_\omega\dot q$; the analytic one
  differentiates the chosen Euler triple and differs by $E^{-1}$ in the angular rows
  ($E = \partial\omega/\partial\dot q$, a function of the orientation angles). State which one is wanted.
- Worked determinant (3R arm with base joint and in-plane links $a_2, a_3$):
  $\det J_v = -a_2a_3 s_3\,(a_2c_2 + a_3c_{23})$ — singular when the arm is folded/straight or the tip
  lies on the base axis. Evaluate any determinant you intend to print numerically at a few
  configurations before printing it.

## Reading the columns back: magnitudes and the moving-frame axes

Factor each column as (scalar) × (unit vector) and the two things a reader wants come out separately.
Spherical RRP arm ($P = b_3\hat u$, base axis up, elevation $\theta_2$ from that axis):

| column | value | magnitude | the unit vector is |
|---|---|---|---|
| $\partial p/\partial\theta_1$ | $b_3\sin\theta_2\,(-\sin\theta_1,\cos\theta_1,0)^{\mathsf T}$ | $b_3\sin\theta_2$ = $P$'s distance from the base axis ($=\sqrt{p_x^2+p_y^2}$) | $-\hat y_2$ |
| $\partial p/\partial\theta_2$ | $b_3(\cos\theta_1\cos\theta_2,\ \sin\theta_1\cos\theta_2,\ \sin\theta_2)^{\mathsf T}$ | $b_3$ = $P$'s distance from the shoulder axis | $\hat x_2$ |
| $\partial p/\partial b_3$ | $(\sin\theta_2\cos\theta_1,\ \sin\theta_1\sin\theta_2,\ -\cos\theta_2)^{\mathsf T}$ | 1 | $\hat z_2$ (the arm itself) |

Each bracket is a column of $^0R_2$ up to sign, so the unit-length test is free (sum the squares: each
collapses to 1). **The magnitudes are the physical radii of the three motions** ($v = r\dot q$). This is the
shape to use when asked "how did you get this column?": differentiate one component at a time (watch the
minus in $\mathrm d\cos\theta_2/\mathrm d\theta_2$; a zero component means that variable does not appear in
it), then factor out the common scalar and check the remainder is a unit vector. A second copy of the
finished matrix teaches nothing.

Why the columns are perpendicular — the pattern to name: $p = b_3\hat z_2(q)$, so the columns are a scaled
orthonormal triad of the arm's own moving frame (one radial, two angular). That is the calculus
spherical-coordinate Jacobian with $r\leftrightarrow b_3$, $\theta\leftrightarrow\theta_2$,
$\phi\leftrightarrow\theta_1$: $\partial\mathbf r/\partial r=\hat r$,
$\partial\mathbf r/\partial\theta=r\hat\theta$, $\partial\mathbf r/\partial\phi=r\sin\theta\,\hat\phi$.
Same fact gives $J^{\mathsf T}J=\operatorname{diag}(b_3^2\sin^2\theta_2,b_3^2,1)$ with zero off-diagonals,
no cross terms in the kinetic energy, and $\det J$ = **product of the three magnitudes**: singular exactly
when a magnitude dies ($b_3=0$: tip at the origin; $\sin\theta_2=0$: arm on the base axis, $\theta_1$ no
longer moves the tip).

In the arm's own frame the matrix is **constant**: $J=R_2M$ with $M=[[0,b_3,0],[-b_3\sin\theta_2,0,0],[0,0,1]]$
— all pose dependence sits in $R_2$. Verify a proposed factorization as a *product* symbolically, not column
by column: one wrong multiplier (a $1$ where $b_3$ belongs) leaves all three columns looking plausible.

**The gravity row of $J$ is the gravity vector.** With $\hat g$ the *down* unit vector and
$h=-p\cdot\hat g$ the mass's height along gravity, $V=-mg\,p\cdot\hat g$ and
$G=\partial V/\partial q=-mg\,\hat g^{\mathsf T}J$ — the Jacobian row along the gravity direction, times
$-mg$. On this arm $\hat g\parallel x_0$, so $G=-m_3g\,(\text{1st row of }J)$, reproducing the dynamics
worked example term for term. Take the sign from the algebra and settle it with the equality test
(`G == -m*g*ghat.T*J`) — the potential written by hand is $-m_3gb_3\sin\theta_2\cos\theta_1$ here and the
sign is trivial to invert by eye.

**Why the rule is true — the paragraph to give when asked to "explain the vector-product method".** Freeze the
other joints and run joint $j$ at unit rate. The tool is welded to the downstream body, so it swings on a
circle about the line through $p_{j-1}$ along $z_{j-1}$, and a rotation $dq_j$ moves a point at offset
$r = p_e - p_{j-1}$ by $(z_{j-1}\times r)\,dq_j$; dividing by $dq_j$ gives the linear block, and the angular
block is that same axis. $|z_{j-1}\times r|$ is the tool's perpendicular distance from the axis — the whole
reason a zero-offset spherical wrist has no linear part in its last three columns. A prismatic joint slides
the downstream body along $z_{j-1}$: axis on top, zeros below. Give it in that order (axis and point → small
rotation → divide); the formula alone does not answer an "explain" question.

Recipe in the order that is fastest under exam pressure: (1) build $^0T_1\dots^0T_n$ (needed for the position
anyway); (2) per joint read $z_i$ = 3rd column, $p_i$ = 4th column; (3) $p_e$ = 4th column of $^0T_n$;
(4) revolute columns by the cross product, prismatic by the axis alone; (5) find the zeros by asking "does the
tool lie on this axis?" — back it up by printing the frame origins ($p_3=p_4=p_5=p_6$ for a zero-offset
spherical wrist) instead of asserting it. Verify the *rule*, not only the final matrix: print
$z_{i-1}\times(p_e-p_{i-1})$ against the finite-difference $\partial p/\partial q_i$ column by column — the
wrist columns come out exactly 0, the rest to $\sim10^{-10}$.

## Jacobian from the forward-kinematic matrices

Two routes that start from $T_n$ rather than from the drawn axes. Both give the same Jacobian as the
vector-product rule above; use them when the question says "from the forward kinematics" or when the
lecture's method is the differential transformation (微分变换法).

**Route A — differentiate $T_n$ (the definition, and the one to program).**

$$J_v(:,i)=\frac{\partial p}{\partial q_i}, \qquad
J_\omega(:,i)=\operatorname{vee}\!\Big(\frac{\partial R}{\partial q_i}R^{\mathsf T}\Big),
\qquad \operatorname{vee}(S)=(S_{32},\,S_{13},\,S_{21})$$

- Only $p$ (3 numbers) and $R$ (9 numbers) of $T_n$ depend on $q$; the bottom row is dead weight.
- $(\partial R/\partial q_i)R^{\mathsf T}$ is *always* skew: differentiating $RR^{\mathsf T}=I$ gives
  $S=-S^{\mathsf T}$. A skew matrix is a cross-product operator, so the axis falls out of the
  derivative — never guess which axis a joint turns about.
- Prismatic joints need no special case here: $\partial p/\partial d_i$ is already the slide direction.

**What the $R^{\mathsf T}$ is for (recurring question: "M = dR/dt RT is for?").** Three jobs, all visible in
one line of algebra: (1) the raw $\partial R/\partial q_i$ is nine unreadable entries, while the product has a
fixed shape — zero diagonal, antisymmetric — so nine numbers carry only three; (2) the multiplication cancels
every factor downstream of the joint, leaving $R_{0,j-1}BR_{0,j-1}^{\mathsf T}$ with $B=[[0,-1,0],[1,0,0],[0,0,0]]$,
which is why the result is the joint's *own* axis and not something mixed with the wrist; (3) it fixes the frame
the axis is reported in — $\dot RR^{\mathsf T}$ reports it in the BASE frame (what a base-frame task space
wants), $R^{\mathsf T}\dot R$ in the tool frame. Those two products are different matrices once the orientation
is not the identity: verify numerically rather than reasoning about it, because the wrong one still looks
plausible and only finite differences expose it.
- MATLAB with the Symbolic Math Toolbox (user has R2024a, no robotics toolbox): `Jv = jacobian(p, q)`,
  then `S = simplify(diff(R,q(i))*R.')` per column; run headless as `matlab -batch "scriptname"` and
  check with `subs(J, q, qn)`. Pass `sym(pi)/2`, not the double `pi/2`, whenever the DH table carries
  90° twists — otherwise the symbolic product keeps a float and simplification stalls.

**Route A done by hand: the derivative collapses to the joint axis.** Only $A_i$ contains $\theta_i$, so
$R=R_{0,i-1}A_i^{\mathrm{rot}}(\text{rest})$ and right-multiplying by $R^{\mathsf T}$ cancels *rest*
against its own transpose:

$$\frac{\partial R}{\partial\theta_i}R^{\mathsf T}
= R_{0,i-1}\Big[\frac{\partial A_i}{\partial\theta_i}A_i^{\mathsf T}\Big]R_{0,i-1}^{\mathsf T},
\qquad \frac{\partial A_i}{\partial\theta_i}A_i^{\mathsf T}=\operatorname{skew}(\hat z)
=\begin{bmatrix}0&-1&0\\1&0&0\\0&0&0\end{bmatrix}$$

The bracket is a **constant — independent of $\alpha_i, d_i, a_i$** (checked symbolically for a generic
$\alpha$: the difference is the exact $3\times3$ zero matrix). A skew matrix *is* a cross-product
operator, so$^\dagger$

$$\frac{\partial R}{\partial\theta_i}R^{\mathsf T}=R_{0,i-1}\operatorname{skew}(\hat z)R_{0,i-1}^{\mathsf T}
=\operatorname{skew}\big(R_{0,i-1}\hat z\big) \;\Longrightarrow\; J_\omega(:,i)=z_{i-1}$$

the 3rd column of $R_{0,i-1}$ — a column of a matrix already built for the FK. A prismatic joint has no
$\theta$ in $R$ at all, so $\partial R/\partial d_i=0$ and its angular block is zero, while
$\partial p/\partial d_i$ needs no special case. $^\dagger$The same conjugation argument gives the general
$\dot RR^{\mathsf T}=\operatorname{skew}(\omega)$ with $\omega$ the axis the joint turns about.

So "differentiate the FK matrix" and "use the vector product" are the *same theorem*: the differentiation
route is what proves the vector-product rule, and quoting $J_\omega(:,i)=z_{i-1}$ as the result of step (b)
is a legitimate derivation rather than a shortcut. Write-up shape for "show me step by step by
differentiation": (1) $p$; (2) $\partial p/\partial q_i$ for all joints — this *is* rows 1–3, and the zero
columns for a spherical wrist need their physics stated ("the tool point is fixed at the wrist centre"),
not left blank; (3) the identity above; (4) read the six $z_{i-1}$ off $T_0^1\dots T_0^5$; (5) stack. Six
lines of real work for a 6-DOF arm. Verification pair: symbolic assembly of the differentiation route
against the claimed matrix (expect 0 mismatched entries out of $36$), plus central differences on the
numeric $R$ feeding $\operatorname{vee}(\dot RR^{\mathsf T})$ (expect $\le 10^{-9}$).

Cost note: never form and simplify $\partial R/\partial\theta_i\,R^{\mathsf T}$ for the full chain — do the
identity once on a generic $A_i$, then work structurally.

A deck that teaches all three routes names them 直接微分法 (differentiate $T_n$, this section's Route A),
矢量积法 (vector product) and 速度传递法 (velocity propagation): answer under the name the question uses.
When the presentation must avoid naming `skew`/`vee` at all, use the calibrated reading rule
$(M_{32},M_{13},M_{21})$ (the principal-axis rotations fix it: $(0,0,1)$, $(0,1,0)$, $(1,0,0)$) with
$M=RBR^{\mathsf T}$ and $B=[[0,-1,0],[1,0,0],[0,0,0]]$ — same result, no skew-symmetric formalism on the page
(SKILL.md step 5 carries the full ordering of that explanation).

**Route B — read each column off the T matrices (no calculus; this is the slides' rule).**

For joint $i$, form $M_i={}^{i-1}T_n=(A_1\cdots A_{i-1})^{-1}T_n=A_i\cdots A_n$ — *cancel the factors in
front of the joint*, so $M_1=T_n$ itself. Write $M_i=[\,n\ o\ a\ p\,]$:

$$\text{revolute } J_i=\begin{bmatrix}-n_xp_y+n_yp_x\\ -o_xp_y+o_yp_x\\ -a_xp_y+a_yp_x\\ n_z\\ o_z\\ a_z\end{bmatrix},
\qquad \text{prismatic } J_i=\begin{bmatrix}n_z\\ o_z\\ a_z\\ 0\\ 0\\ 0\end{bmatrix}$$

Those six numbers are in the **tool** frame, so rotate them into the base frame:
$J_{\text{base}}=\operatorname{blkdiag}(R_{0n},R_{0n})J_{\text{tool}}$.

Worked column (Stanford arm, $q=(0.3,-0.4,0.25,0.2,0.6,-0.5)$, $d_2=0.1$, $M_1=T_6$):
$n=(0.9891,-0.0352,-0.1429)$, $o=(0.0111,0.9860,-0.1662)$, $a=(0.1467,0.1628,0.9757)$,
$p=(-0.1226,0.0668,0.2303)$ → tool frame $(-0.0617,-0.1216,-0.0298\mid-0.1429,-0.1662,0.9757)$ →
base frame $(-0.0668,-0.1226,0\mid 0,0,1)$ = column 1 of the vector-product answer. Reproduce it before
using the rule on a new arm; any deviation means $M_i$ was taken in the wrong frame.

**The trap.** $M_i$ is *not* $T_n^{-1}T_i$ (frame $i$ in tool coordinates): off by a rotation, O(1)
column errors, indistinguishable from a sign slip until finite differences are run. Verified on five
arms — 2R planar, RPR with a prismatic joint, 3R planar, 6R PUMA-like, Stanford — all $\le 5\times10^{-10}$
against central differences. A symbolic run of Route B against Route A should reduce to exactly zero
(a $10^{-73}$ residual is zero).

## Cheap self-checks

| check | catches |
|---|---|
| FK position vector at the zero pose vs. the drawn pose | a $\theta$ measured from the wrong reference direction |
| finite differences vs. the derived columns (`templates/verify_jacobian.py`) | axis index errors ($z_i$ vs $z_{i-1}$), sign flips, a forgotten rotation |
| $\dot RR^{T}$ skew extraction vs. the angular rows | a wrong joint-axis assignment in the wrist |
| $\det$/rank at 2–3 configurations | any singularity claim printed in the write-up |
| $z_{i-1}\times\hat u = \partial\hat u/\partial\theta_i$ for every link direction $\hat u$ | an axis whose sign contradicts the angle convention (elevation measured from the wrong reference) |
| origin of the last frame = the marked tool point, frame $x$ axes along the drawn links | a figure read wrong (frame placed at the wrong joint) — the check that settles a contradictory sketch |
| two trailing columns coming out equal | the tool vector taken from the base origin instead of from that joint |
| column norm vs. the physical radius ($b_3\sin\theta_2$, $b_3$, 1 on a spherical arm) | a sign or direction error inside one column while the others verify |
| $\det J$ vs. the product of the column magnitudes (valid when the columns are mutually orthogonal) | printing a singularity condition without evaluating it |
| $G=-mg\,\hat g^{\mathsf T}J$ vs. the $G$ from the centre-of-mass heights | a sign error in the gravity vector — the two routes differ by a sign, which no magnitude check sees |
