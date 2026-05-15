# Piece 137 — Lorenz Attractor: The Butterfly That Never Lands

A 3D strange attractor discovered by Edward Lorenz in 1963 while modelling atmospheric convection. The trajectory traces the shape of a butterfly indefinitely without ever repeating.

## The equations

    dx/dt = σ(y − x)
    dy/dt = x(ρ − z) − y
    dz/dt = xy − βz

The classic parameters are **σ = 10** (Prandtl number), **ρ = 28** (Rayleigh number), and **β = 8/3** (geometric factor). At these values the system is chaotic: two trajectories starting arbitrarily close together diverge exponentially, and the orbit never settles into a periodic cycle.

## RK4 integration

The system is integrated using the **fourth-order Runge-Kutta** method at dt = 0.005. RK4 evaluates the Lorenz derivative at four points within each time step (beginning, two midpoints, end) and combines them with weights 1, 2, 2, 1:

    k1 = f(t, y)
    k2 = f(t + dt/2, y + dt/2 · k1)
    k3 = f(t + dt/2, y + dt/2 · k2)
    k4 = f(t + dt,   y + dt · k3)
    y_next = y + (dt/6)(k1 + 2k2 + 2k3 + k4)

This achieves fourth-order accuracy (error ∝ dt⁵ per step) and dramatically reduces numerical drift compared to Euler integration, keeping the trajectory on the attractor far longer before floating-point errors accumulate.

## Why the attractor never repeats

The Lorenz system is **chaotic**: its largest Lyapunov exponent is positive (λ₁ ≈ 0.9), meaning an infinitesimal perturbation δ grows to order 1 in roughly log(1/|δ|)/λ₁ time units. The attractor is **topologically mixing** — every open region of phase space is eventually visited — but no periodic orbit of finite length closes the figure. The butterfly shape is the limit set of all trajectories from a large basin of initial conditions, asymptotically dense yet nowhere self-intersecting.

## Rendering

200 000 trajectory points are held in a ring buffer. Each animation frame:

1. The 200 000 3D points are projected to 2D by rotating the XY plane at a slowly increasing camera angle (0.002 rad/frame): `u = x·cos θ − y·sin θ`, `v = z`.
2. Projected coordinates are binned into a 800×800 density grid.
3. Each pixel is tone-mapped via `log(density + 1)` to compress the wide dynamic range.
4. The normalised value indexes a 256-entry colour LUT: deep indigo (background) → luminous cyan → warm gold.

A full camera revolution takes roughly 50 seconds, revealing the 3D butterfly structure from every azimuth.
