# Piece 207 — Lorenz Attractor & Chaos Butterfly

Two trajectories trace the iconic double-wing shape discovered by Edward Lorenz in 1963. The amber path and the teal path start only ε = 10⁻⁴ apart — watch them diverge into entirely different regions of phase space, illustrating deterministic chaos.

## The equations

    dx/dt = σ(y − x)
    dy/dt = x(ρ − z) − y
    dz/dt = xy − βz

Classic chaotic parameters: **σ = 10** (Prandtl number), **ρ = 28** (Rayleigh number), **β = 8/3** (geometric factor). The three sliders let you tune each in real time; the pair of trajectories restart from nearby perturbed initial conditions so the butterfly effect is immediately visible.

## RK4 integration

Both trajectories are integrated using **fourth-order Runge-Kutta** at dt = 0.005. RK4 evaluates the Lorenz derivative four times per step (at the start, two midpoints, and the end) then combines them with 1:2:2:1 weights:

    k1 = f(t, y)
    k2 = f(t + dt/2, y + dt/2·k1)
    k3 = f(t + dt/2, y + dt/2·k2)
    k4 = f(t + dt, y + dt·k3)
    y_next = y + (dt/6)(k1 + 2k2 + 2k3 + k4)

This gives fourth-order accuracy (error ∝ dt⁵ per step) and keeps trajectories on the attractor far longer than Euler integration.

## Chaos and sensitive dependence

The Lorenz system's largest Lyapunov exponent is λ₁ ≈ 0.9 nats/time-unit. An initial separation δ₀ grows as δ(t) ≈ δ₀ · eˡ¹ᵗ. With δ₀ = 10⁻⁴ the two paths diverge to order-1 separation in only ≈ 10 time units (2 000 RK4 steps). The attractor is strange: it has fractal dimension ≈ 2.06 and is topologically mixing — every open region is eventually visited — yet no orbit ever repeats.

## Rendering

The 3D orbit (x, y, z) is projected to 2D with a fixed rotation matrix (30° yaw, 29° pitch) giving the classic butterfly view. Each frame:

1. The canvas is alpha-blended with the navy background (opacity 3 %) so old segments fade to a luminous ghost trail.
2. The 15 newest segments for each trajectory are drawn at increasing opacity (newest brightest) so the leading tip is always vivid.

## Controls

| Slider | Range | Default | Effect |
|--------|-------|---------|--------|
| σ (sigma) | 1–20 | 10 | Prandtl number — governs convective momentum diffusion |
| ρ (rho) | 1–50 | 28 | Rayleigh number — driving force; chaos onset near ρ ≈ 24.7 |
| β (beta) | 0.1–8 | 8/3 ≈ 2.67 | Geometric damping; chaos lost at very small values |

Changing any slider immediately restarts both trajectories with a fresh ε-offset pair so the divergence is visible from the start.
