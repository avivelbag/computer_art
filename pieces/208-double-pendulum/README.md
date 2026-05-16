# Double Pendulum — Chaos Made Visible

Two rigid arms pivoting in series: the second bob hangs from the tip of the first. The **Lagrangian** L = T − V yields two coupled nonlinear ODEs integrated via **4th-order Runge-Kutta (RK4)** at dt = 0.012 s — no small-angle approximation.

## Controls

| Control | Effect |
|---------|--------|
| **θ₁ slider** | Initial angle of arm 1; resets simulation immediately |
| **θ₂ slider** | Initial angle of arm 2 |
| **m₂/m₁** | Mass ratio; alters inertia coupling and chaotic onset |
| **Trail** | Trail length (frames) |
| **Reset** | Restart from current slider values |
| **Click pivot** | Also resets (click within ~28 px of the central dot) |

## Twin trajectory

A second pendulum, offset by **0.001° in θ₁** (the teal trail), runs alongside the gold trajectory. Both start with zero angular velocity. The two trails diverge exponentially — the **Lyapunov exponent** for the double pendulum is λ ≈ 3–7 s⁻¹ depending on initial conditions.

## Physics

The Lagrangian equations of motion are solved exactly as:

```
θ₁'' = [−g(2m₁+m₂)sin θ₁ − m₂g sin(θ₁−2θ₂) − 2m₂ sin(θ₁−θ₂)(ω₂²L₂ + ω₁²L₁ cos(θ₁−θ₂))]
         / [L₁(2m₁ + m₂ − m₂ cos(2θ₁−2θ₂))]

θ₂'' = [2 sin(θ₁−θ₂)(ω₁²L₁(m₁+m₂) + g(m₁+m₂)cos θ₁ + ω₂²L₂m₂ cos(θ₁−θ₂))]
         / [L₂(2m₁ + m₂ − m₂ cos(2θ₁−2θ₂))]
```

RK4 combines derivatives at four sub-points (weights ⅙, ⅓, ⅓, ⅙) for O(dt⁴) global accuracy.

## Canvas details

- Trail color encodes **time**: recent segments are bright, older segments fade quadratically.
- Gold/amber trail = pendulum 1; teal trail = twin (0.001° offset).
- Canvas annotations show live θ₁/θ₂ readouts on the arm midpoints.
- 60 fps via `requestAnimationFrame`; physics pauses when the tab is hidden (`visibilitychange`).
- Palette: deep navy `#06061a`, copper-gold `#c8a96e`, electric teal `#4ecdc4`.
