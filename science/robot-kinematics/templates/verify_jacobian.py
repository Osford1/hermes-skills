"""Numeric verification of an analytic manipulator Jacobian (template).

Copy into the task's Working/ directory, then edit:
  * DH_ROWS   -- the DH table of the arm you are working on (standard convention),
                 rows in frame order, joint variables written as "th1".."th6" / "d3";
  * PRISMATIC -- 1-based indexes of the prismatic joints;
  * Q         -- the configuration to test;
  * CLAIMED   -- optionally paste a claimed Jacobian evaluated at Q to check a
                 textbook/paper/derivation answer directly.

Run:  python verify_jacobian.py

The numeric route uses central differences on the FK matrix and needs no axis or
index reasoning, so a mismatch localises to specific columns.
Expected agreement: ~1e-9..1e-11 (float64, h=1e-6). Larger -> an axis, index or
sign error, not rounding.
"""

import numpy as np

# ---------------------------------------------------------------------------
# DH table: T_i = Rz(theta) Tz(d) Tx(a) Rx(alpha), standard convention.
D2 = 0.1      # table constant (base-to-shoulder offset)  [Stanford arm example]
D6 = 0.0      # tool offset; 0 -> tool point == wrist centre

DH_ROWS = [
    ("th1", 0.0,  0.0, -np.pi / 2),
    ("th2", D2,   0.0,  np.pi / 2),
    (0.0,   "d3", 0.0,  0.0),          # prismatic joint
    ("th4", 0.0,  0.0, -np.pi / 2),
    ("th5", 0.0,  0.0,  np.pi / 2),
    ("th6", D6,   0.0,  0.0),
]
PRISMATIC = {3}                        # 1-based joint indexes

Q = np.array([0.3, -0.4, 0.25, 0.6, -0.5, 0.2])   # configuration to test


def dh_row(theta, d, a, alpha):
    ct, st = np.cos(theta), np.sin(theta)
    ca, sa = np.cos(alpha), np.sin(alpha)
    return np.array([[ct, -st * ca,  st * sa, a * ct],
                     [st,  ct * ca, -ct * sa, a * st],
                     [0.0,     sa,      ca,    d],
                     [0.0, 0.0, 0.0, 1.0]])


def subs(value, q):
    """Resolve a DH entry: 'th1'/'d3' -> that joint variable, else the constant."""
    if isinstance(value, str):
        name = value
        if name.startswith("th"):
            return float(q[int(name[2:]) - 1])
        if name.startswith("d"):
            return float(q[int(name[1:]) - 1])
        raise ValueError(f"unknown joint variable {name!r}")
    return float(value)


def fk_frames(q):
    """Ts[i] = 4x4 base -> frame i (Ts[0] = identity base frame)."""
    Ts = [np.eye(4)]
    for row in DH_ROWS:
        Ts.append(Ts[-1] @ dh_row(*[subs(v, q) for v in row]))
    return Ts


def geo_jac(q, prismatic=PRISMATIC):
    """Vector-product construction: joint i's axis and point are z_{i-1}, p_{i-1}."""
    Ts = fk_frames(q)
    pe = Ts[-1][:3, 3]
    J = np.zeros((6, len(DH_ROWS)))
    for i in range(1, len(DH_ROWS) + 1):
        z, p = Ts[i - 1][:3, 2], Ts[i - 1][:3, 3]
        if i in prismatic:
            J[:3, i - 1] = z
        else:
            J[:3, i - 1] = np.cross(z, pe - p)
            J[3:, i - 1] = z
    return J


def num_jac(q, h=1e-6):
    """Central differences: linear = dp/dq, angular = vee((dR/dq) R^T)."""
    T0 = fk_frames(q)[-1]
    J = np.zeros((6, len(DH_ROWS)))
    for i in range(len(DH_ROWS)):
        qp, qm = q.copy(), q.copy()
        qp[i] += h
        qm[i] -= h
        Tp, Tm = fk_frames(qp)[-1], fk_frames(qm)[-1]
        J[:3, i] = (Tp[:3, 3] - Tm[:3, 3]) / (2 * h)
        W = ((Tp[:3, :3] - Tm[:3, :3]) / (2 * h)) @ T0[:3, :3].T
        J[3:, i] = [W[2, 1], W[0, 2], W[1, 0]]
    return J


def report(name, A, B):
    err = np.abs(A - B)
    print(f"{name}: max |diff| = {err.max():.3e}")
    print("  per column:", " ".join(
        f"{i + 1}:{err[:, i].max():.1e}" for i in range(err.shape[1])))
    np.set_printoptions(precision=4, suppress=True)
    print(A)


if __name__ == "__main__":
    T = fk_frames(Q)[-1]
    print("position at the test configuration:", np.round(T[:3, 3], 6))
    report("geo(mine) vs numeric", geo_jac(Q), num_jac(Q))
    # Optional: check a claimed Jacobian (same shape, evaluated at Q).
    # CLAIMED = np.array([[...]])
    # report("claimed vs numeric", CLAIMED, num_jac(Q))
