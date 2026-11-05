# Manipulator dynamics — Lagrange route, the collapse to $M\ddot q + h$, planar 2-link and spherical (RRP) arms worked

## Recipe, in the order that works

1. Model + coordinates: joint types, positive sense, the vertical the angles are measured from.
2. $T$ per link: $\tfrac12 m|v_c|^2 + \tfrac12\omega^T I\omega$. With $I=\mathrm{diag}(A,A,A)$ this collapses
   to $\tfrac12 A|\omega|^2$.
3. $V$ from centre-of-mass heights.
4. Euler–Lagrange per coordinate; assemble $D\ddot q + C\dot q + G = \tau$.
5. Static sign test (set $\ddot q=\dot q=0$) before shipping.
6. Verify the assembled form: symbolic identity plus an independent finite-difference route (below).

## From $L$ to $M(\theta)\ddot q + h(\theta,\dot q)$ — the collapse step

Asked on its own ("from $L$ and Euler–Lagrange, how do we get $\tau = M\ddot q + h$?"), give the four lines
and the reason each holds:

1. $L = \tfrac12\dot q^TM(\theta)\dot q$ (plus gravity if any). $\dot q$ appears only as squared products; $\theta$
   appears only inside $M$.
2. Per coordinate, $\frac{d}{dt}\frac{\partial L}{\partial\dot q_i} - \frac{\partial L}{\partial q_i} = \tau_i$,
   with two facts doing the work: $\partial L/\partial\dot q_i = \sum_j M_{ij}\dot q_j$ (linear in the rates) and
   $\partial L/\partial q_i = \tfrac12\sum_{j,k}\frac{\partial M_{jk}}{\partial q_i}\dot q_j\dot q_k$ (all pose
   dependence sits in $M$).
3. Because $M$ depends on $\theta$, the product rule inside $d/dt$ adds one sum:
   $\frac{d}{dt}\frac{\partial L}{\partial\dot q_i} = \sum_j M_{ij}\ddot q_j + \sum_{j,k}\frac{\partial M_{ij}}{\partial q_k}\dot q_j\dot q_k$.
   Subtract fact 2 and the first sum is the matrix product:
   $$\tau_i = \underbrace{\sum_j M_{ij}\ddot q_j}_{(M\ddot q)_i} + \sum_{j,k}\left[\frac{\partial M_{ij}}{\partial q_k} - \frac12\frac{\partial M_{jk}}{\partial q_i}\right]\dot q_j\dot q_k$$
   The bracket *is* $h_i$, already closed. There is no separate Coriolis step where new physics enters.
4. The bracket looks asymmetric but is not: $M$ is symmetric, so renaming the dummy indices gives
   $\sum_{j,k}\frac{\partial M_{ik}}{\partial q_j}\dot q_j\dot q_k = \sum_{j,k}\frac{\partial M_{ij}}{\partial q_k}\dot q_j\dot q_k$ and the
   bracket is the Christoffel symbol
   $c_{ijk} = \tfrac12\big(\frac{\partial M_{ij}}{\partial q_k} + \frac{\partial M_{ik}}{\partial q_j} - \frac{\partial M_{jk}}{\partial q_i}\big)$, i.e. $h = C(\theta,\dot q)\dot q$.
   Say what that buys: $\dot M - 2C$ skew-symmetric, which is the energy identity — with $\tau = 0$,
   $\frac{d}{dt}\tfrac12\dot q^TM\dot q = 0$. That identity is itself a check on the assembled pair.

### Planar 2-link arm, point masses at the link centres ($V = 0$, so $L = K$)

$l_1 = 0.3$, $l_2 = 0.2$ m, $m_1 = 2$, $m_2 = 1$ kg. $\theta_1$ from the horizontal, $\theta_2$ from the
*extension* of link 1, so link 2 points at $\theta_1+\theta_2$. Centres:
$r_1 = \tfrac{l_1}2(\cos\theta_1,\sin\theta_1)$, elbow $l_1(\cos\theta_1,\sin\theta_1)$,
$r_2 = l_1(\cos\theta_1,\sin\theta_1) + \tfrac{l_2}2(\cos(\theta_1+\theta_2),\sin(\theta_1+\theta_2))$.

- **Why the halves:** a point mass at the centre gives $m(l/2)^2 = ml^2/4$, which is the $0.045$ sitting in
  $M_{11}$. A uniform rod about its end would be $ml^2/3$ and a point mass at the tip $ml^2$ — say which one
  the figure drew before any algebra starts.
- **Where $\cos\theta_2$ comes from.**
  $v_2 = l_1\dot\theta_1\hat e_{1\perp} + \tfrac{l_2}2(\dot\theta_1+\dot\theta_2)\hat e_{2\perp}$ splits the centre's
  velocity into the piece carried by the turning shoulder and the piece swinging on its own link; the angle
  between those two vectors is exactly $\theta_2$, so $|A+B|^2 = |A|^2+|B|^2+2|A||B|\cos\theta_2$ puts the cosine
  in. Same fact by hand expansion:
  $\sin\theta_1\sin(\theta_1+\theta_2) + \cos\theta_1\cos(\theta_1+\theta_2) = \cos((\theta_1+\theta_2)-\theta_1) = \cos\theta_2$.
  It is the dot product of the two Jacobian columns, so it appears twice on the page — inside $|v_2|^2$ and as
  the off-diagonal $M_{12}$. One origin, two places.
- **$V_2^TV_2$ is the same number as $|v_2|^2$:** for a *column* vector $V^TV$ is the sum of squares of its
  entries, i.e. $\dot x_2^2+\dot y_2^2$. Worth using because it is frame-invariant and turns the speed into
  $\dot q^T(J^TJ)\dot q$. Two traps to name: $V^TV$ is a squared length only for a vector (for a matrix it is a
  matrix of dot products), and a book that packs $V = (v,\omega)$ into one 6-vector has a $V^TV$ mixing
  translation with rotation — the deck keeps linear $V_i$ and $\omega_i$ in separate energy terms, so its
  $V_i^TV_i$ really is a squared speed.

$$M = \begin{bmatrix} 0.145+0.06\cos\theta_2 & 0.01+0.03\cos\theta_2\\ 0.01+0.03\cos\theta_2 & 0.01\end{bmatrix},\qquad
h = \begin{bmatrix} -0.03\,\dot\theta_2(2\dot\theta_1+\dot\theta_2)\sin\theta_2\\ 0.03\,\dot\theta_1^2\sin\theta_2\end{bmatrix}$$

Reading $M$ back (the answer to "what *is* $M(\theta)$?"): kg·m² of inertia seen through the joints; from
$\tau = M\ddot q + h$ with the arm held still, entry $M_{ij}$ is the torque joint $i$ needs per unit
acceleration at joint $j$; the diagonal is each joint's own inertia, the off-diagonal is what makes it a
matrix rather than two separate motors. Only two derivatives of $M$ exist here —
$\partial M_{11}/\partial\theta_2 = -0.06\sin\theta_2$, $\partial M_{12}/\partial\theta_2 = -0.03\sin\theta_2$,
$\partial M_{22}/\partial\theta_2 = 0$, $\partial M/\partial\theta_1 = 0$ — so the sums collapse by hand: joint 1's
$\partial L/\partial\theta_1$ is zero and its $h_1$ is one product rule; joint 2's two $\dot\theta_1\dot\theta_2$ terms
are equal and opposite and cancel, leaving only $\dot\theta_1^2$. That cancellation is the same structure as the
skew-symmetry identity, not a coincidence.

**Structural checks, one line each**

- $\partial M/\partial\theta_1 = 0$: the base joint rotates the whole arm rigidly and changes no distance.
- $M_{22}$ constant: link 2's centre is always $l_2/2$ from joint 2's own axis.
- $M = m_1J_1^TJ_1 + m_2J_2^TJ_2$ with $J_i = \partial r_i/\partial q$ reproduces the assembled matrix; here
  $J_1^TJ_1 = \mathrm{diag}((l_1/2)^2, 0)$, because joint 2 cannot move link 1's centre, so that row and column are
  empty and every interesting entry comes from link 2. The mass-matrix twin of $G = -mg\,\hat g^TJ$.
- Invertibility as a computed claim: $\det M = 0.00045 + 0.0009\sin^2\theta_2 > 0$, smallest eigenvalue 0.00211.
- Two misreadings to pre-empt: $M$ is not the link masses (kg·m², not kg), and it is not constant (only
  $M_{22}$ is).

### Verifying a claimed $M/h$ pair

1. Symbolically: build $L$ from the claimed $M$, apply the Euler–Lagrange operator, and require the difference
   from the claimed $M\ddot q + h$ to simplify to exactly $0$ — per coordinate, not in norm.
2. Independently, numerically, by central differences on $L$ alone (no algebra reused). Take the derivative of
   the **raw $L$** for $\partial L/\partial\theta_i$ — never difference an expression that is already a
   derivative, since that returns the second derivative — and get $d/dt(\partial L/\partial\dot q_i)$ by
   differencing along a constant-acceleration state, $\theta(t) = \theta_0 + \dot\theta_0t + \tfrac12\ddot\theta_0t^2$.
   With $h = 10^{-6}$ expect ~1e-11 on every row; a match on one row and an O(1) miss on another is a bug in the
   checker, not a missing term.
3. Energy: integrate the passive system ($\tau = 0$) and check $\tfrac12\dot q^TM\dot q$ is conserved to round-off.

### Letters, because three of them collide

The lecture's dynamics equation is $D(q)\ddot q + H(q,\dot q)\dot q + C(q) = \tau$, with $D$ the 惯性矩阵, $H$ the
科氏矩阵 and $C(q)$ the 重力矩. So $C$ is **gravity**, not Coriolis, and $H$ is a matrix where a hand-in sheet's
$h$ is the vector $h = H\dot q$. Give the mapping in one line with the slide number ($M = D$, $h = H\dot q$, $C = 0$
when no mass changes height) and never read the deck's $C$ as Coriolis.

## Spherical RRP (球坐标式): the hand-solvable case

What makes it hand-solvable, and worth naming out loud in the answer:

- Both revolute axes cross at $O_1$, and links 1 and 2 each have their centre of mass **at** $O_1$ — so both
  links only spin, they never translate and never change height.
- The prismatic arm's centre of mass is at the tip $P$, a distance $b_3$ from $O_1$.
- Every link's inertia is isotropic ($A$, $B$, $C$), so no link-frame rotation matrix is needed.

Coordinates: $\theta_1$ about the base axis, $\theta_2$ the elevation measured from that axis (arm along
it at $\theta_2 = 0$), $b_3$ the arm length. Take the base axis as up; then $P = b_3\hat u$ with
$\hat u = (\sin\theta_2\cos\theta_1,\ \sin\theta_2\sin\theta_1,\ \cos\theta_2)$.

**Kinetic energy**

- link 1: $\tfrac12 A\dot\theta_1^2$
- link 2: $\tfrac12 B(\dot\theta_1^2 + \dot\theta_2^2)$ — the axes are perpendicular, so the rates add in
  quadrature; the centre of mass being on $O_1$ kills the translational term.
- link 3: $\tfrac12 m_3|v_P|^2 + \tfrac12 C(\dot\theta_1^2+\dot\theta_2^2)$ with
  $|v_P|^2 = \dot b_3^2 + b_3^2(\dot\theta_2^2 + \sin^2\theta_2\, \dot\theta_1^2)$.

The $\sin^2\theta_2$ is the physics: when the base spins, $P$ circles the axis on a radius of
$b_3\sin\theta_2$ — zero when the arm lies along the axis, so a vertical arm costs nothing to spin.

**Potential energy:** only $P$ changes height, $h = b_3\cos\theta_2$, so $V = m_3gb_3\cos\theta_2$.
(Any constant offset to the shoulder is a constant and never survives the derivative — that is why an
arbitrary frame-1 height $d_1$ changes nothing.)

**Result** ($\sin 2\theta_2 \equiv 2\sin\theta_2\cos\theta_2$)

$$\tau_1 = (A+B+C+m_3b_3^2\sin^2\theta_2)\ddot\theta_1 + 2m_3b_3\dot b_3\sin^2\theta_2\,\dot\theta_1 + m_3b_3^2\sin 2\theta_2\,\dot\theta_1\dot\theta_2$$

$$\tau_2 = (B+C+m_3b_3^2)\ddot\theta_2 + 2m_3b_3\dot b_3\dot\theta_2 - m_3b_3^2\sin\theta_2\cos\theta_2\,\dot\theta_1^2 - m_3gb_3\sin\theta_2$$

$$f_3 = m_3\ddot b_3 - m_3b_3\dot\theta_2^2 - m_3b_3\sin^2\theta_2\,\dot\theta_1^2 + m_3g\cos\theta_2$$

$$D = \mathrm{diag}(A+B+C+m_3b_3^2\sin^2\theta_2,\ B+C+m_3b_3^2,\ m_3), \qquad G = (0,\ m_3gb_3\sin\theta_2,\ -m_3g\cos\theta_2)$$

Read the structure back to the user: $\tau_1$ has **no** gravity entry (a vertical axis cannot be torqued
by gravity); $m_3b_3^2\sin^2\theta_2$ is the arm's moment of inertia about the base axis; the
$-m_3b_3^2\sin\theta_2\cos\theta_2\dot\theta_1^2$ term is the centrifugal action standing the arm up; the
$2m_3b_3\dot b_3$ terms are Coriolis (length changing while rotating).

**Static checks** (each is a ten-second hand-check, not algebra)

- $\theta_2 = 0$, arm along the axis: $f_3 = +m_3g$ (push out to stop gravity retracting it), $\tau_2 = 0$.
- $\theta_2 = 90°$: $f_3 = 0$ (gravity acts across the slide), $\tau_2 = -m_3gb_3$ (must pull against the
  arm's weight).
- Drop link 3 and hold $b_3$ fixed: reduces to the 2-link inertial pattern of the lecture's one-DOF example
  $I\ddot q + mgL_c\cos q = \tau$.

**DH table for reference** (same axes-cross-at-$O_1$ fact that makes the centres of mass static gives
$a_1 = a_2 = 0$):

| $i$ | $\theta$ | $d$ | $a$ | $\alpha$ |
|---|---|---|---|---|
| 1 | $\theta_1$ | $d_1$ (constant, often 0) | 0 | −90° |
| 2 | $\theta_2$ | 0 | 0 | +90° |
| 3 | 0 | $b_3$ (variable) | 0 | 0° |
| 4 (tool) | 0 | 0 | 0 | 0° |

## Base axis perpendicular to gravity — the case the *data* selects

**Run this test first: does the problem state where $\hat g$ points?** Because $x_i \perp z_{i-1}$ holds for every DH row, a statement that gravity is along a frame $x$-axis ("重力方向与 $X_1$ 相同", or a figure drawing $X_1$ along the gravity arrow) **implies a horizontal base joint axis** — the base joint swings the arm in a vertical plane rather than turning it like a turntable. That makes this a *determined* reading: solve it as the main answer, not as the vertical-base result plus a caveat.

A figure whose $X_1$ is drawn along the gravity arrow has a **horizontal** base joint axis (that is what
$x_i \perp z_{i-1}$ forces), so the base axis becomes the pole and the arm is not along it at $\theta_2=0$.
The tip height then comes from $\hat u \cdot \hat g$, giving $V = -m_3gb_3\cos\theta_1\sin\theta_2$: gravity
now enters the $\theta_1$ row as $-\partial V/\partial\theta_1$, and the $\theta_2$ row's gravity term changes
from $\sin\theta_2$ to $\cos\theta_1\cos\theta_2$. **The inertial terms in $D$ are identical either way** —
say that, because it tells the user the ambiguity cannot corrupt most of the answer.

**The assembled answer for this reading** (with $\theta_1 = 0$ at the pose where the arm hangs lowest, and $\theta_2$ measured from the base axis to the arm; verified symbolically by the energy route and re-derived by Euler–Lagrange):

$$\tau_1=[A+B+C+m_3b_3^2\sin^2\theta_2]\ddot\theta_1+2m_3b_3\sin^2\theta_2\,\dot b_3\dot\theta_1+m_3b_3^2\sin2\theta_2\,\dot\theta_1\dot\theta_2+m_3gb_3\sin\theta_2\sin\theta_1$$

$$\tau_2=[B+C+m_3b_3^2]\ddot\theta_2+2m_3b_3\dot b_3\dot\theta_2-m_3b_3^2\sin\theta_2\cos\theta_2\,\dot\theta_1^2-m_3gb_3\cos\theta_2\cos\theta_1$$

$$f_3=m_3\ddot b_3-m_3b_3\dot\theta_2^2-m_3b_3\sin^2\theta_2\,\dot\theta_1^2-m_3g\sin\theta_2\cos\theta_1$$

$$G=(m_3gb_3\sin\theta_2\sin\theta_1,\ -m_3gb_3\cos\theta_2\cos\theta_1,\ -m_3g\sin\theta_2\cos\theta_1)^T$$

$$C=\begin{bmatrix} m_3b_3^2\sin\theta_2\cos\theta_2\dot\theta_2+m_3b_3\sin^2\theta_2\dot b_3 & m_3b_3^2\sin\theta_2\cos\theta_2\dot\theta_1 & m_3b_3\sin^2\theta_2\dot\theta_1\\ -m_3b_3^2\sin\theta_2\cos\theta_2\dot\theta_1 & m_3b_3\dot b_3 & m_3b_3\dot\theta_2\\ -m_3b_3\sin^2\theta_2\dot\theta_1 & -m_3b_3\dot\theta_2 & 0\end{bmatrix}$$

$D$ is the same diagonal matrix as the vertical-base case. **Static checks for this reading** (same ten-second tests, different expected signs): $\theta_1 = 0,\ \theta_2 = 90°$ — the arm hanging straight down along the gravity line — gives $\tau_1 = \tau_2 = 0$ and $f_3 = -m_3g$, i.e. the actuator must *retract* to hold it, because gravity stretches the slide rather than levering it. At $\theta_1 = 90°$ the arm sweeps a horizontal plane, every $G$ entry dies with $\cos\theta_1$, and $\tau_2$ gets its maximum gravity moment $m_3gb_3$ at $\theta_1 = 0,\ \theta_2 = 0°$.

**Translating to the marker's convention is a substitution, not a re-derivation:** these equations are pure functions of $\theta_2$ together with $\dot\theta_2,\ddot\theta_2$, so re-zeroing the elevation from the downward vertical ($\varphi_2 = \theta_2 - 90°$) means $\sin\theta_2 \to \cos\varphi_2$ and $\cos\theta_2 \to -\sin\varphi_2$ everywhere, rates unchanged. Offer that mapping instead of solving twice.

Delivery shape: give this reading whole when the data selects it — full $D$, $C$, $G$ and the three scalar equations — and keep the other reading to one comparison line ($D$ identical, $G$ rotated). Do not hedge
term by term.

## Reading the figure: measurement vs interpretation

When the schematic itself has to be decoded (low-quality screenshot, hand-drawn, no text layer):

- **Label positions are measurable; directions and typography are not.** Component analysis on the
  threshold mask gives real label box centres to the pixel. Which label belongs to which arrow, and which
  way that arrow points, is where vision contradicts itself from call to call.
- Enforce a **budget**: two independent attempts. If they disagree about a direction, stop, take the
  standard convention for that arm, state it in the assumptions line, and flag the single open item in the
  closing caveat. Never keep cropping — it stays ambiguous for as long as you keep going.
- Ask the vision tool for **short bounded answers** ("4 short numbered lines, under 400 characters, no
  preamble") and **one fact per call** (yes/no, or a direction). Multi-part asks come back partially
  contradictory.
- Filter every reading through the algebra: the frame identities ($x_i$ along the drawn link, origin of the
  last frame at the marked point, joint axes as 3rd columns), then $x_i \perp z_{i-1}$. A reading that
  violates an identity is a wrong reading, not a difficult one.
- **The printed problem text is the contract; arbitration goes to the TEXT, not to the figure.** When a
  read of the schematic implies geometry the data never supplies — an offset between the base housing and
  the shoulder point, a link length, a tool offset — re-crop the *text block* on its own (2× is enough) and
  ask one narrow question: "does the text state any length or distance other than <the variable>?" A model
  whose answer would have to contain an undimensioned length is the wrong model — an offset that is never
  given is zero by construction of the problem. Vision will happily describe an S-bend or an off-axis boss
  between two frames that the data places at the same point, and a "the axis does not pass through $O_1$"
  claim is exactly that failure mode.
- **Coincident frame origins in the drawing are a positive check, not an error.** For a spherical arm every
  $a_i = 0$ and $d_1 = d_2 = 0$, so $O_0 = O_1 = O_2$ is precisely what the standard table predicts — seeing
  $X_1, X_2, X_3$ drawn at one marked point confirms that the axes cross there, and it is worth one line in
  the answer as corroboration of the $a$ and $d$ columns.
