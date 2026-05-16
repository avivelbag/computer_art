# Double Pendulum: Painting Chaos

Seven identical double pendulums start with θ₁ values offset by 0.002 rad between neighbors. Each traces a colored trail (spectral palette: red, orange, yellow-green, green, cyan, blue, violet) on a dark canvas. Their trails overlap initially and diverge exponentially, painting deterministic chaos as layered ink art.

## Controls

| Control | Effect |
|---------|--------|
| **θ₁** | Initial angle of arm 1 for the center pendulum; each of the 7 pendulums is offset ±0.002, ±0.004, ±0.006 rad from this |
| **g** | Gravitational acceleration (m/s²); lower g gives slower, more regular motion |
| **l₁** | Length of arm 1; affects swing period and chaos onset |
| **l₂** | Length of arm 2; unequal arm lengths shift the non-integrable coupling |
| **Reset** | Restart all 7 pendulums from the current slider values |

Any slider change resets and replays the simulation.

## Physics

The Lagrangian L = T − V for a double pendulum (masses m₁ = m₂ = 1) gives two coupled nonlinear ODEs via the Euler-Lagrange equation d/dt(∂L/∂θ̇ᵢ) − ∂L/∂θᵢ = 0:

```
θ₁′′ = [−g(2m₁+m₂)sinθ₁ − m₂g·sin(θ₁−2θ₂) − 2sin(δ)·m₂(ω₂²l₂ + ω₁²l₁cos(δ))]
         / [l₁(2m₁+m₂−m₂cos(2δ))]

θ₂′′ = [2sin(δ)·(ω₁²l₁(m₁+m₂) + g(m₁+m₂)cosθ₁ + ω₂²l₂m₂cos(δ))]
         / [l₂(2m₁+m₂−m₂cos(2δ))]

where δ = θ₁ − θ₂
```

Integration uses **4th-order Runge-Kutta (RK4)** with dt = 0.012 s and 4 sub-steps per animation frame (≈ 20 ms physics interval at 60 fps). RK4 uses derivative estimates at four sub-points with weights 1/6, 1/3, 1/3, 1/6, giving O(dt⁴) accuracy and far better energy conservation than Euler integration over the thousands of steps needed to reveal chaotic behavior.

## Sensitive dependence and Lyapunov exponents

The **Lyapunov exponent** λ quantifies how fast nearby trajectories separate: if two orbits start at distance ε, after time t they are roughly ε·e^(λt) apart. For the double pendulum λ ≈ 3–7 s⁻¹ depending on initial conditions.

The **Chaos Meter** overlay tracks max|θ₂[i] − θ₂[center]| across the 7 pendulums in real time. The bar fills as divergence grows and saturates near π rad (full de-correlation). Near-vertical (θ₁ ≈ 0°) or very short arms give smaller λ; large initial angles and mismatched arm lengths tend to maximize it.

## Trail rendering

Each pendulum's second-bob position is recorded in a ring buffer capped at 500 points. Trails are rendered with 16 alpha-opacity buckets — oldest segments appear faint and dim, newest glow full saturation. All 7 trails are drawn before the pendulum rods and bobs, which are drawn in the foreground.

## Implementation details

- **Canvas**: full-viewport `requestAnimationFrame` loop; pauses via `visibilitychange`
- **Scale**: adapts to arm lengths so max reach occupies ~35% of the shorter canvas dimension
- **Pivot**: fixed at (W/2, 0.28·H); pendulum hangs into the lower two-thirds
- **Background**: `#08080e` (near-black)
- **Trail palette**: HSL hues at 0°, 40°, 75°, 130°, 185°, 230°, 280°
