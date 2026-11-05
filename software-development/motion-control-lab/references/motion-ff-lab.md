# motion-ff-lab — session detail (built 2026-08-31)

Location: `C:\Users\<you>\dev\motion-ff-lab`

## Environment

- Venv: `.venv` (Python 3.11, created with `uv venv`)
- torch 2.13.0+cu126 — CUDA verified on NVIDIA GeForce RTX 3050 6GB Laptop GPU (driver 576.02)
- numpy 2.4.6, matplotlib 3.11.1
- Install command used: `uv pip install --python .venv/Scripts/python.exe torch --index-url https://download.pytorch.org/whl/cu126`
- Separate from miniconda doc toolchain (`C:\Users\<you>\miniconda3\python`) and the cad venv — do not cross-install.

## File map

| file | role |
|---|---|
| `plant.py` | 1-DOF motor sim. `PlantParams` (J=0.01, coulomb=0.6, stribeck=1.0, v_s=0.05, viscous=0.02, hysteresis_k=0.25, dt=1ms). Friction = Coulomb + Stribeck + viscous + presliding hysteresis (stateful `z`). `reference_trajectory()` = slow dwelling multi-sine (0.15/0.8 Hz, amplitudes 0.3/0.05). |
| `controllers.py` | `NoFFController` (PD only), `ModelFFController` (J·a + viscous-only FF — deliberate blind spot), `LearnedFFController` (J·a + NN friction + PD). Gains kp=80, kd=6. |
| `run_baseline.py` | FB-only vs model-FF, prints RMS/peak, saves `baseline_comparison.png` |
| `collect_data.py` | logs 30k samples of (vel_ref, acc_ref, sign(vel_ref)) → true friction; saves `friction_data.npz` |
| `train_ff.py` | 3-64-64-1 tanh MLP, Adam lr=1e-3, 300 epochs, explicit training loop; saves `friction_mlp.pt` + `learned_ff_comparison.png` |

## Verified results (current plant + trajectory)

```
controller                RMS err [rad]   peak err [rad]
feedback only               0.00620          0.01003
model FF + feedback         0.00616          0.00998   (1.0x — viscous model blind here)
learned FF + feedback       0.00113          0.00259   (5.4x vs model FF)
```

Perfect-FF oracle (cheats, reads true friction): rms=0.000247 — the ceiling learned-FF should chase.

## Debugging transcript (why the trajectory changed)

Original trajectory: fast multi-sine (0.5/1.7 Hz, amplitude 1.0/0.3). Result: model-FF rms 0.00316 vs FB-only 0.00211 — FF looked WORSE, contradicting the demo's point.

Diagnosis path:
1. Frictionless plant test — model-FF still worse → not friction-model error.
2. Gain sweep (kp 80→800) — mild improvement to kp=120, instability blowup at kp=400 (1 kHz semi-implicit Euler limit).
3. Error split by |vel_ref| regime — worst errors at velocity zero-crossings, but only ~7% of time at low speed; fast segments dominated RMS where viscous friction (modeled) is the main term.
4. Slow trajectory + stronger dry friction (coulomb 0.35→0.6, stribeck 0.6→1.0, hysteresis_k 0.15→0.25) — controllers separated correctly.

Lesson: with dry friction, the demonstration only works in the low-speed/dwelling regime. Fast motion lets viscous terms mask everything.

## Stage 3 notes (GRU swap — user's next step, not yet done)

- MLP features are instantaneous (vel, accel, sign(vel)) — cannot observe the hysteresis state `z`, so ~irreducible residual.
- GRU input: window of past (vel, accel) pairs (e.g. 32–64 samples @ 1 kHz); hidden state learns to track `z` implicitly.
- Data: `collect_data.py` emits i.i.d. rows; needs sequence batching (sliding windows over a continuous run) for recurrent training.
- Success metric: beat MLP's 0.00113 RMS, approach oracle 0.000247.
- Physical extension path mentioned to user: their open-loop robot arm as testbed — sim-first always.

## PyTorch install note

torch cu126 wheel is ~2.4 GB; download ~5 min on the user's connection, install ~25 s. Run as background process with notify, scaffold project files while it downloads.
