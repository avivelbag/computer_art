# Piece 224 — The Butterfly Effect: Lorenz Attractor in 3D

An interactive WebGL visualization of the Lorenz strange attractor — the canonical image of chaos theory. Over 50 000 trajectory points are rendered as a glowing line strip coloured deep-violet (oldest) → electric-cyan (newest) via additive blending. A "Nudge" button spawns a second trajectory starting just 0.001 units away, making the exponential divergence visceral and immediate.

## The ODE system

The Lorenz equations model Rayleigh–Bénard convection — a thin horizontal fluid layer heated from below, the same physics driving thunderstorms and oceanic circulation:

```
dx/dt = σ(y − x)
dy/dt = x(ρ − z) − y
dz/dt = xy − βz
```

| Variable | Physical meaning |
|----------|-----------------|
| x | Angular velocity of the convection roll |
| y | Horizontal temperature contrast between rising and sinking fluid |
| z | Vertical temperature deviation from the linear background profile |

## Parameters

| Parameter | Default | Physical interpretation |
|-----------|---------|------------------------|
| σ (sigma) | 10 | Prandtl number: ratio of kinematic viscosity to thermal diffusivity |
| ρ (rho)   | 28 | Rayleigh number: normalized heating rate; chaos onset near ρ ≈ 24.7 |
| β (beta)  | 8/3 | Geometric aspect-ratio factor (twice-as-wide-as-tall convection cell) |

## Lorenz's 1963 paper

Edward Lorenz published "Deterministic Nonperiodic Flow" in *Journal of Atmospheric Sciences* (1963) after noticing that re-running a weather simulation from its midpoint produced a completely different forecast — caused by printing only three decimal places of the state vector. He named the phenomenon in a 1972 lecture: "Does the Flap of a Butterfly's Wings in Brazil Set Off a Tornado in Texas?" The attractor was among the first examples of a mathematical object now called a **strange attractor**: bounded, aperiodic, and fractal (dimension ≈ 2.06).

## Numerical integration

Both trajectories use **fourth-order Runge-Kutta (RK4)** at `dt = 0.005`:

```
k1 = f(y)
k2 = f(y + dt/2 · k1)
k3 = f(y + dt/2 · k2)
k4 = f(y + dt · k3)
y_next = y + (dt/6)(k1 + 2k2 + 2k3 + k4)
```

RK4 achieves fifth-order local error (∝ dt⁵) versus first-order for Euler, keeping orbits faithful to the true attractor many times longer. The initial transient (first 2 000 steps) is discarded before recording so the displayed trail lies entirely on the attractor.

## Chaos and the butterfly effect

The Lorenz attractor's largest Lyapunov exponent is λ₁ ≈ 0.9 nats/time-unit. An initial separation δ₀ grows as δ(t) ≈ δ₀ · e^(λ₁ t). Starting just ε = 0.001 apart, the two trajectories reach macroscopic separation in roughly t ≈ 8 time units — about 1 600 RK4 steps. Press "Nudge ε" to see this unfold in real time.

## Rendering

A ring buffer of 50 001 `vec3` positions is maintained per trajectory. Each frame, 200 new RK4 steps are computed and the buffer is reordered (oldest → newest) for GPU upload. The WebGL 2 vertex shader uses `gl_VertexID` to compute per-vertex age without a separate attribute, mixing colours from deep-violet (oldest, near-transparent) to electric-cyan (newest, fully opaque). Additive blending (`ONE + SRC_ALPHA`) makes overlapping trail segments accumulate into a luminous glow, similar to a long-exposure photograph.

## Controls

| Control | Action |
|---------|--------|
| Drag canvas | Orbit in 3D (yaw + pitch) |
| σ / ρ / β sliders | Reshape the attractor live; resets trajectories |
| Nudge ε | Spawn a second trajectory at (x + 0.001, y, z) in warm coral |
| Reset | Restart from a fresh warm-up initial condition |
| About | Toggle the educational info drawer |
