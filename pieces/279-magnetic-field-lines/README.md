# Piece 279 — Polarity: Magnetic Dipole Field Lines

Two magnetic dipoles animate on a charcoal canvas. 3,000 iron-filing segments align to the local **B**-field each frame; optional RK4 streamlines trace the closed loops connecting north pole to south pole, demonstrating ∇·B = 0.

## Physics

### Magnetic Dipole Formula

A point dipole with moment **m** at position **p** produces a field at **r**:

```
B(r) = (μ₀/4π) · [3(m·r̂)r̂ − m] / |r−p|³
```

where **r̂** = (r−p)/|r−p|. This simulation uses a dimensionless constant K = 10⁵ (canvas-pixel units) and adds a soft-core term r₀² = 900 px² to the denominator to prevent the singularity at the dipole centre:

```
r_eff² = |r−p|² + r₀²
```

The total field is the vector sum of contributions from both dipoles (superposition principle).

### Key Field Properties

**Along the dipole axis** (r̂ ∥ **m**):

```
B_axis = 2μ₀m / 4π r³   (parallel to m, pointing outward from north)
```

**At the equatorial plane** (r̂ ⊥ **m**):

```
B_equator = −μ₀m / 4π r³   (anti-parallel to m)
```

The ratio is 2:1 — the axial field is twice as strong as the equatorial field at the same distance.

### ∇·B = 0

Unlike electric monopoles (point charges), magnetic monopoles do not exist. The divergence theorem applied to ∇·B = 0 guarantees that every field line must form a **closed loop**: any line that exits a north pole must return to a south pole. There are no sources or sinks.

## Iron-Filing Texture

3,000 point positions are generated at random when the canvas is resized and stay fixed thereafter. Each frame:

1. Evaluate **B** at every filing position.
2. Normalise to get the local field direction.
3. Draw a short line segment (±FILING_LEN = 7 px) centred on the point, aligned to the field direction.
4. Colour the segment by |**B**| through a log-scale palette from amber to gold.

Because the positions are stable between frames, the pattern evolves smoothly as the dipoles move rather than flickering.

## RK4 Streamline Tracing

Full streamlines are available via the "Streamlines" button (off by default for performance). Each streamline:

1. Seeds at one of N_SEEDS = 20 equal angular positions around a dipole centre (just outside POLE_RAD).
2. Advances with fourth-order Runge-Kutta along **B**/|**B**| at STEP = 2 px per step.
3. Terminates when:
   - The point exits the canvas boundary.
   - The point enters within POLE_RAD of any dipole centre (line has completed its loop).
   - MAX_STEPS = 600 steps have elapsed (safety cutoff).

### Why RK4 over Euler?

Euler integration introduces tangential drift that causes streamlines to spiral outward rather than close cleanly. RK4 keeps the local truncation error O(h⁵) per step, which is sufficient for closed-loop fidelity at STEP = 2 px.

## Animation

Both dipoles rotate their moment vectors and drift on sinusoidal orbits:

```
angle₀ = t·0.14 + 0.45·sin(t·0.28)
angle₁ = t·0.14 + π + 0.45·sin(t·0.22 + 1.1)

x₀ = W/2 + cos(t·0.07)·W·0.14
y₀ = H/2 + sin(t·0.10)·H·0.08
```

The Lissajous-like orbit prevents periodicity so the configuration never exactly repeats.

## Colour Palette

| Element        | Colour              | Notes                              |
|----------------|---------------------|------------------------------------|
| Background     | `#0e0e12`           | Charcoal                           |
| Weak field     | `#c8871a` (amber)   | Filing segments far from poles     |
| Strong field   | `#f5d060` (gold)    | Filing segments near poles         |
| North pole     | `#c8871a` with gold rim | Where **B** exits               |
| South pole     | `#2a1804` with amber rim | Where **B** enters             |

The colour interpolation uses a log scale so the transition spans a comfortable visual range despite the 1/r³ field falloff.

## Controls

| Button          | Effect                                          |
|-----------------|-------------------------------------------------|
| About           | Toggle the info panel                           |
| Pause / Resume  | Freeze / unfreeze the animation                 |
| Streamlines     | Toggle full RK4 field-line streamlines          |
| Hide Filings    | Toggle the 3,000 iron-filing segments           |
