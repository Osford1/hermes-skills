# Applications outside robotics (and outside their coursework)

**How to use this file.** Pick **one**, give the one-line "it's the same maths", and stop. The goal is
surprise + a new mental hook, not a catalogue dump. Prefer a domain they have real-world context in
(CAD, EVs, energy, manufacturing) or one they have never touched (medicine, chemistry, protein biology).
Never present the list as the answer.

`✓` = verified live with a source; unmarked = standard textbook fact.

---

## Configuration space / C-obstacle — "a pose is a dot"

- **Protein folding and drug docking.** A molecule's shape is set by its rotatable bonds, and each bond
  angle is a joint. The space of conformations *is* a configuration space; a misfolded protein is a
  local minimum in an energy landscape; docking a drug is a collision/overlap check between two rigid
  bodies. Same objects, different units.
- **Reaction pathways — nudged elastic band (NEB).** Computational chemistry finds the lowest-energy
  path over a reaction barrier by discretizing the path into "images" and relaxing each, chained to its
  neighbours. Structurally identical to CO-DOSP's Nx task-point subproblems.
- **Radiotherapy gantry collision.** A linear accelerator is a 6-DOF arm swinging around a patient on a
  moving couch, in a room full of equipment. Avoiding a gantry/couch/patient collision is a C-space
  problem, in a hospital.
- **Games and animation.** Physics engines wrap nonconvex character and prop meshes in **convex
  decompositions** (V-HACD → Bullet/PhysX); crowd pathfinding and ragdoll control are C-space searches.

## Convexification / sequential convex programming (the same trick, other industries)

- **Rocket landing — G-FOLD** ✓ (JPL; Açıkmeşe & Blackmore). Powered-descent guidance via *lossless
  convexification*: a nonconvex minimum-fuel landing problem relaxed to a convex (SOCP) one with a proof
  that the relaxation is tight. Flight-tested on the ADAPT / Xombie VTVL rocket, ~100 ms on a 1.4 GHz
  processor, meter-level accuracy. **The original implementation was in MATLAB.** Not yet flown on a
  planetary mission ("readying the way for adoption by future missions").
- **Radiotherapy treatment planning — VMAT** ✓ (Memorial Sloan Kettering, 2023). The VMAT optimisation is
  "highly non-convex"; the ECHO-VMAT system replaced a commercial treatment-planning optimisation engine
  with a **sequential convex programming** algorithm and runs in daily clinical routine across 60
  patients. Same shape: solve a chain of convex approximations, then correct for model error.
- **Structural design / generative design in CAD** ✓. SCP with the method of moving asymptotes
  (Svanberg 1987) is the standard engine for FE-based structural optimisation — i.e. the mathematics
  inside generative-design tools. This is "convexification" they have already used without knowing it.
- **Power grid** — SDP / convex relaxations of AC optimal power flow; the classic "relax, then check
  whether the relaxation was tight" pattern.

## Duality — the multiplier is literally a price

- **Electricity spot prices.** In DC optimal power flow the **locational marginal price is the dual
  variable** — the λ on a binding transmission constraint is what appears on the settlement bill. It is
  the identical object to the "price of the ball" in CO-DOSP's dual search. Same maths: one is a robot,
  the other is the national grid.
- Also: congestion pricing, ad auctions, airline revenue management — all dual-variable pricing.

## Null space — the redundancy you got for free

- **Torque vectoring in a four-motor EV.** More motors than the commanded yaw moment needs → the
  distribution of torque among the wheels has a null space. Spend it on efficiency, tyre temperature, or
  brake wear without changing the car's yaw. Their EV interest, straight from the same algebra.
- **Aircraft control allocation.** Redundant control surfaces: keep the commanded moment, use the null
  space to trim drag or hold a surface in its efficient range.
- **Neuroscience — the uncontrolled-manifold hypothesis.** The brain stabilises the task-relevant
  variables and lets the rest (the null space) vary freely, using it to absorb error. Redundancy
  resolution in wetware. (Brain 1 has a neuroscience domain — use only if the link is real.)
- **Biomechanics (OpenSim-style static optimisation).** Muscles are hugely redundant: the inverse
  problem is solved with the joint torque as a hard constraint and effort minimised in the null space.

## Batch vs online, and "stopping is a trajectory"

- **Radiotherapy with breathing motion** — case (b) in a hospital: the plan is computed offline, then the
  patient breathes. Solved by gating (irradiate only inside a window) or real-time tracking.
- **Power markets.** Day-ahead auction = offline batch planning; real-time balancing = the seconds-scale
  layer; **spinning reserve is the braking layer**. The three-tier architecture, already regulated.
- **Cellular schedulers.** Network-wide optimisation runs offline; the scheduler decides every ~1 ms.
  The timescale gap forces exactly the tiering CO-DOSP's authors propose for robotics.
- **Emergency braking (AEB) and railway protection.** "Stopping is itself a trajectory": jerk-limited
  braking curves are computed to guarantee a collision-free stop — the safe-stop problem, solved daily in
  transport engineering.
