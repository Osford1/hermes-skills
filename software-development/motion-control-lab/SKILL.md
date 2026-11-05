---
name: motion-control-lab
description: Use for control-system sim labs and learned feedforward.
---

# Motion Control Simulation Labs

Class: Python control-system experiments that mirror the user's Masters research direction (learning-based feedforward for precision motion, my supervisor's group). The user is a mechatronics grad learning the ML side — always connect ML mechanics back to control theory they already know.

## The existing lab

`C:\Users\<you>\dev\motion-ff-lab` — a verified, working learning-feedforward demo. Full detail in `references/motion-ff-lab.md` (file map, verified numbers, environment specs). Run order:

```bash
cd C:\Users\<you>\dev\motion-ff-lab
.venv\Scripts\activate
python run_baseline.py   # feedback-only vs model-FF: shows the problem
python collect_data.py   # log true friction as training data
python train_ff.py       # train MLP friction model, close the loop, compare
```

Venv has torch 2.13+cu126 (RTX 3050 6GB, CUDA confirmed), numpy, matplotlib. Separate from the user's miniconda doc toolchain — do not mix.

## Architecture conventions (keep when extending)

- **plant.py / controllers.py split**: the simulator knows the true friction; controllers never do. Learned controllers get any object with `.predict(features) -> float`, so MLP → GRU swaps don't touch the loop.
- **Three-controller comparison is the narrative**: feedback-only (reactive baseline) → model-FF (hand-derived, deliberately incomplete) → learned-FF (closes the gap). Every new experiment should report all three RMS/peak errors.
- **Perfect-FF oracle as diagnostic ceiling**: a controller that cheats by reading the plant's true friction. If learned-FF can't approach oracle performance, the model/features are the bottleneck; if it matches the oracle but tracking is still poor, the feedback loop or trajectory is. Build one for any new plant — it's the fastest way to localize a failure.

## Pitfalls (learned the hard way)

- **Trajectory choice decides which physics dominates.** The original fast multi-sine trajectory let viscous friction dominate torque, so the viscous-only model-FF looked fine and the dry-friction effect the demo exists to show was invisible — model-FF even looked *worse* than feedback-only. The fix was a slow, dwelling trajectory with frequent velocity zero-crossings (Stribeck/hysteresis regime). When a simulation result contradicts the expected physics, check the excitation regime BEFORE trusting or "fixing" anything else.
- **Gain vs. integrator stability**: semi-implicit Euler at 1 kHz blows up around kp≈400 for the default plant (J=0.01). Gains kp=80/kd=6 are the stable working point; sweep gains only with the integrator's stability limit in mind.
- **Counterintuitive results are usually regime bugs, not physics.** The debugging path that worked: frictionless plant → gain sweep → error-vs-velocity-regime split → oracle comparison. Decompose conditions before concluding.

## Extending: Stage 3 (GRU) recipe

The user's stated next step: replace the MLP in `train_ff.py` with a GRU over a window of past (vel, accel) samples. Rationale to explain: friction hysteresis (the plant's `z` state) has memory — a stateless MLP has an irreducible ceiling, a recurrent net can infer the hidden state. This mirrors why my supervisor's group uses GRUs for inverse dynamics. Data collection needs windowing (sequence samples, not i.i.d. rows); everything else in the loop stays.

## Explaining to this user

Their learning style (see user profile): they restate concepts in their own casual words and want corrections tailored to *their* summary, tied to the source paper. In this domain, anchor every ML concept to a control analogue they own: autograd = "you never write a gradient by hand," network = "the same role as your hand-derived friction equation, but fit to data," learned FF vs ILC = "learning the plant vs. learning one playback."

## Files

- `references/motion-ff-lab.md` — lab file map, verified results, environment specs, debugging transcript, GRU stage notes.
