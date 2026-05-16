# Rössler Attractor — Ensemble Divergence

Seven Rössler systems started 0.01 apart in x₀ trace colored spiral trails that diverge exponentially — showing sensitive dependence on a 3D continuous-time strange attractor first described by Otto Rössler in 1976.

## Controls

| Control | Effect |
|---------|--------|
| **a** | Spiral expansion rate; larger values widen the arms |
| **b** | z-axis reinjection strength |
| **c** | Primary chaos parameter; near 4.0 the system has a stable limit cycle, above ~5 it is chaotic |
| **x₀** | Initial x position for the center trajectory; resets all seven |
| **Reset** | Restart from current slider values |

## Physics

The Rössler system is a 3D autonomous ODE:

```
dx/dt = -(y + z)
dy/dt = x + a·y
dz/dt = b + z·(x - c)
```

With a = b = 0.2, c = 5.7 the orbit spirals outward on the x-y plane, folds over through the z-axis, and returns — a classic strange attractor with topological structure resembling a Möbius band in phase space.

Integration uses 4th-order Runge-Kutta at dt = 0.025 s. The trajectory is projected onto the x-y plane for display.

## Ensemble

Seven trajectories start at x₀ + k·0.01, y₀ = 0, z₀ = 0 for k ∈ {−3,−2,−1,0,1,2,3}. Colors follow a spectral palette from red (k = −3) through violet (k = +3). Trails persist for 500 frames and fade; recent segments are bright, older segments dim.

## Chaos Meter

Tracks max Euclidean distance in the x-y projection between the center trajectory (k = 0) and any other. The bar saturates at Δr = 25 units, roughly the attractor diameter. The classic-parameter Lyapunov exponent is λ ≈ 0.07 s⁻¹ — much gentler than the double pendulum — so the spiral structure is visible for many cycles before trajectories fully de-correlate.

## Contrast with Lorenz

The Lorenz attractor (butterfly shape, two lobes, σ=10 b=8/3 ρ=28) has λ ≈ 0.9 s⁻¹ and a figure-8 topology. The Rössler attractor has a single lobe with a spiral-and-fold topology and smaller λ. Rössler deliberately designed his system to be the simplest possible strange attractor, making it analytically more tractable while still exhibiting full chaos.
