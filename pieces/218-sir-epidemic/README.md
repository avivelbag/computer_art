# Piece 218 — SIR Epidemic: The Curve We Tried to Flatten

300 colour-coded particles bounce around a box infecting their neighbours on contact. A live chart on the right records the Susceptible, Infected, and Recovered populations over time, producing the characteristic bell-shaped infected curve of the SIR epidemic model.

## The SIR Model

The SIR model partitions a population N into three compartments:

- **S** — Susceptible: healthy individuals who can catch the disease
- **I** — Infected: currently sick and contagious
- **R** — Recovered: immune (includes vaccinated individuals)

The compartment sizes evolve according to:

```
dS/dt = −β · S · I / N
dI/dt =  β · S · I / N − γ · I
dR/dt =  γ · I
```

β (beta) is the transmission rate and γ (gamma) is the recovery rate. The sum S + I + R = N is conserved at all times.

## Reproduction Number R₀

```
R₀ = β / γ
```

R₀ is the average number of secondary infections caused by a single infected individual in a fully susceptible population. When **R₀ < 1** each case generates less than one new case — the epidemic declines and dies out. When R₀ > 1 it grows.

## How it works

**Particle simulation (left panel):** Each of the 300 dots moves at constant speed and bounces off the walls. When an infected dot (red) comes within contact distance of a susceptible dot (blue), infection is transmitted with probability proportional to β. Each infected dot recovers each frame with probability proportional to γ, becoming a green recovered dot immune to further infection.

**S/I/R chart (right panel):** Every frame the counts of Susceptible, Infected, and Recovered particles are appended to a rolling history buffer. The three lines are drawn as polylines scaled to the canvas, giving a live view of the epidemic's progress.

**Sliders:**
- β (0.1–1.0): higher β spreads the disease faster
- γ (0.05–0.5): higher γ recovers infected individuals faster
- Initial infected: how many particles start as infected
- Vaccination %: fraction that start already recovered (immune)

## What to notice

- The bell-shaped red peak is the "curve" public health officials tried to flatten during COVID-19.
- Reducing β lowers and broadens the peak — the same total infections spread over more time.
- Raising vaccination % shrinks the susceptible pool; once enough are vaccinated the epidemic cannot grow even with a high β (herd immunity).
- Watch the R₀ display: when it turns green (R₀ < 1) the infected count in the chart will be falling.
