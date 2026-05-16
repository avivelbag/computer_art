# 240 — Orbital Memory: N-Body Gravity in Slow Time

Newtonian N-body simulation with gravitational inverse-square law and color-coded fading orbital trails. Each body accumulates a 300-position trail that decays from opaque at the head to transparent at the tail, making the arcing paths the visual centerpiece.

## Integrator

**Leapfrog (kick-drift-kick / velocity Verlet)** with `dt = 0.05` simulation time units per frame and `SUBS = 4` sub-steps (`dt_sub = 0.0125`). Leapfrog is a **symplectic** integrator — it conserves a slightly perturbed Hamiltonian exactly, preventing the secular energy drift that causes plain Euler integrations to spiral outward. Each sub-step:

```
v += (dt/2) · a(x)     # half-kick
x += dt · v            # drift
v += (dt/2) · a(x)     # half-kick with updated positions
```

## Softening

The force law uses a **softened** inverse-square potential to prevent singularities at close approach:

```
a_i = G · Σ_{j≠i} m_j · (r_j − r_i) / (|r_j − r_i|² + ε²)^(3/2)
```

Softening parameter **ε = 0.01 simulation units ≈ 1.6 pixels** in screen coordinates (satisfying ε ≥ 1 pixel). This smoothly suppresses the divergence as r → 0 while leaving forces at r ≫ ε essentially Newtonian.

## Initial configurations

### Solar system (default)

Five bodies: a dominant central body (M_sun = 3, `#f4a261`) plus four planets in circular Keplerian orbits:

| Planet | Radius | Mass | Period (frames @60fps) |
|--------|--------|------|------------------------|
| 1 | 0.60 | 0.005 | ~34 |
| 2 | 0.90 | 0.004 | ~62 |
| 3 | 1.20 | 0.003 | ~96 |
| 4 | 1.50 | 0.002 | ~138 |

Planet masses are ≤ 0.2% of M_sun, so planet-planet perturbations are orders of magnitude below solar gravity. Inner-planet angular frequency ω ≈ 3.7 rad/sim with r = 0.6 gives ω · dt_sub ≈ 0.047 rad per sub-step — well within the leapfrog's stable zone — so all orbits remain bounded for 30+ s.

Each planet's speed is set to the Keplerian circular velocity `v = √(G · M_sun / r)`. The sun's velocity is adjusted to zero the total momentum, keeping the center of mass fixed.

### Figure-8 (button)

The **Chenciner–Montgomery choreographic figure-8** (2000) — three equal masses (`m = 1`, `G = 1`) sharing a single figure-8 curve, each displaced T/3 in time. Exact initial conditions from the original paper; net momentum is near-zero. Period ≈ 6.33 simulation time units.

Because the softened force law is not exactly Newtonian, the figure-8 is not a periodic orbit of this system. Integration errors grow exponentially (positive Lyapunov exponent), so the choreography breaks down after several seconds and the system resets to a new random configuration — which is itself visually striking.

### Random (4–6 bodies)

N bodies (4–6) placed on a jittered ring with tangential velocities set to 75% of the Keplerian circular speed, then momentum-zeroed. Produces a variety of near-stable dances before the system escapes or collapses and resets automatically after ≤ 30 s.

## Palette

Bodies are ranked by mass and assigned colors from warmest (heaviest) to coolest (lightest):

| Rank | Color | Hex |
|------|-------|-----|
| 0 (heaviest) | Warm amber | `#f4a261` |
| 1 | Rose-orange | `#e76f51` |
| 2 | Pale gold | `#e9c46a` |
| 3 | Cool teal | `#52b3c8` |
| 4 | Light blue | `#a8dadc` |
| 5 | Violet | `#9b5de5` |

Background: `#0a0a14`.

## Files

| File | Purpose |
|------|---------|
| `index.html` | Self-contained animation — no external dependencies |
| `generate_thumbnail.py` | Deterministic 400×400 PNG thumbnail (stdlib only) |
| `thumbnail.png` | Pre-generated thumbnail showing solar-system trails at 400 frames |
