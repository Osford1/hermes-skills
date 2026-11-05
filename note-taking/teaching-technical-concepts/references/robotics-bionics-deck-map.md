# Deck map: 机器人与仿生学 (robotics and bionics)

Use when the user asks a question about this course and wants pointing at the slides, or when a
course concept needs the deck's own wording. Both decks sit in
`Brain 1/raw/机器人与仿生学/Lecture notes/`. Page numbers are PDF pages; on these decks they match the
printed slide numbers.

## 机器人控制.pdf (Lecture 5, the lecturer, 62 pages)

| page | title | what is there |
|---|---|---|
| p9 | 机器人控制理论 | Jacobian refresher: `p = [h1,h2,h3]`, `Y = h(q)`, `Ydot = J qdot`, `J = dh/dq` |
| p10 | 机器人的运动学建模 | planar 2-link arm position from the joint angles, using **full** l1 and l2 (the tip), plus J |
| p11 | 操作臂动力学回顾 | `L = K - V` (K 系统总动能, V 系统总势能), Euler-Lagrange, and the standard form `D(q)qdd + H(q,qd)qd + C(q) = tau` labelled 惯性矩阵 / 科氏矩阵 / 重力矩 / 关节力矩 |
| p15-19 | framing | why control structure follows the model |
| p20-29 | single-joint PID | gain meaning, one joint at a time |
| p32, p38 | gain choice | importable vs non-importable parameters, pole placement |
| p34-38 | computed torque | the law and its block diagram |
| p42 | coupling | how joint 1's motion reaches joint 2 |
| p46+ | force control | impedance vs admittance, hybrid force/position |

Presenter-flagged discrepancies: p47 carries an extra `F_d`; p55 says 30 N where p57 says -50 N.

## 动力学.pdf (第四讲 轨迹规划、静力学与动力学)

| page | title | what is there |
|---|---|---|
| p34, p35 | rod inertia | about one end `I = ML^2/3`, and about the centre (平行轴定理) |
| p43 | 求平面双关节机器人动力学 | planar two-link arm with centre-of-mass distances `l_c1`, `l_c2` and `omega_i`, `alpha_i`. The closest deck analogue of a 2R assignment arm |
| p44 | 前向递推 | centre-of-mass linear accelerations, carrying the `l1 qd1^2 cos q2` cross terms |
| p49 | 单个杆件的质心位置 | `r_0^i = T_0^1 ... T_{i-1}^i r_i^i = r_0^i(q)`: a fixed point in the link frame, mapped to the base |
| p50 | 单个杆件的线速度和角速度 | `V_i = dr_i/dq * qd`, `omega_i = dphi_i/dq * qd`, and `K = sum(0.5 m_i V_i' V_i + 0.5 I_i omega_i' omega_i)` |
| p52 | typical Lagrangian form | same `D/H/C` shape as control deck p11 |
| p53, p54 | worked RP example | centres given by `l1` and `d2`, then K, then P, then Lagrange |
| p56, p57 | 1-DOF example | uniform rod versus mass concentrated at the rod end |

## Pointing the user at slides

- **Render the page and read it as an image.** The text layer of these decks scrambles every equation, so
  a text grep returns confident nonsense that reads like real formulas.
  `fitz` `page.get_pixmap(dpi=140)` to JPEG, and stack two pages in one image to halve the vision calls.
- **Cite the deck's own Chinese title beside the number** (`p49 单个杆件的质心位置`). He revises from the
  deck and navigates by title, not by page number.
- **Name the deck, not just a number** (`动力学 第四讲 p49`). A bare `slide 49` is ambiguous across courses.
- **Copy the crops into the assignment's `Reference/slide-crops/`** so the pointers survive a temp cleanup,
  and attach them so he can read the slide while following the explanation.

## Notation collision to state every time a derivation is walked

An assignment solution written here uses `M(q)` for the inertia matrix and `h(q,qd)` for Coriolis plus
centrifugal, with gravity dropped. The decks write `D(q)`, `H(q,qd)`, `C(q)` where `C` is the gravity
torque. Say the collision out loud, or he reads the sheet's `h` as `H` and `C` at once.

## The control assignment's arm (anchor values)

Planar 2R: `l1 = 0.3 m`, `l2 = 0.2 m`, `m1 = 2 kg`, `m2 = 1 kg`, masses as point masses at the link
centres, gravity and friction neglected; `theta1` from the horizontal, `theta2` from the extension of link
1. Because the mass sits at the centre, `l_c = l/2` and the inertia carries `1/4`, not `1/3` (deck p34) and
not `1` (deck p57). Walk-through procedure: `references/walking-assignment-solutions.md`.
