# Double-Slit Diffraction — Light as a Wave

The double-slit experiment is the most celebrated demonstration in all of physics. It shows that light
is a wave, produces a strikingly beautiful interference pattern, and — in its quantum incarnation —
reveals that particles pass through both slits simultaneously as probability amplitudes.

## How it Works

The canvas is split into two regions. The left 60% shows a **top-down view** of the physical setup: a
plane wave (incident from the left) hits a barrier with N slit openings. Circular wavefronts radiate
outward from each slit, and their superposition creates the interference pattern — bright where crests
meet, dark where a crest meets a trough.

The right 40% is the **detector screen**, showing the intensity pattern computed analytically for the
current slider values. Each pixel row maps to an observation angle θ; brightness encodes I(θ). A white
profile curve traces the intensity as a function of angle.

## The Intensity Formula

For N identical slits of width a, separated center-to-center by d, the Fraunhofer diffraction
intensity at angle θ is:

```
I(θ) = sinc²(β) × [sin(Nδ) / (N·sinδ)]²
  β = π·a·sinθ/λ
  δ = π·d·sinθ/λ
  sinc(x) = sin(x)/x
```

Special cases:

**Single slit (N = 1):**
```
I(θ) = sinc²(π·a·sinθ/λ)
```

**Double slit (N = 2):**
```
I(θ) = cos²(π·d·sinθ/λ) × sinc²(π·a·sinθ/λ)
```

The cos² factor creates the two-slit interference fringes; the sinc² envelope from the finite slit
width modulates (and can suppress) individual fringes.

## Fringe Positions

Bright fringes for a double slit appear where:
```
d · sinθ = m · λ,   m = 0, ±1, ±2, …
```

For a screen at distance L (small-angle approximation):
```
y_m = m · λ · L / d
```

Fringe spacing Δy = λL/d. Wider slit separation → closer fringes. Longer wavelength → wider fringes.

## Controls

| Control | Range | Effect |
|---------|-------|--------|
| **d** (slit separation) | 0.5λ – 5λ | Changes fringe spacing on the screen |
| **a** (slit width) | 0.1λ – 2λ | Changes single-slit envelope; narrows as a increases |
| **λ** (wavelength) | 380 – 700 nm | Shifts fringe spacing and changes display color |
| **Slits** (1 / 2 / 5) | — | Switches between single slit, double slit, diffraction grating |
| **ⓘ** | — | Opens the educational side panel |

## Huygens-Fresnel Principle

Every point on a wavefront acts as a source of secondary spherical wavelets. The total field anywhere
downstream is the superposition of all these wavelets. This principle explains both diffraction (the
spreading of waves through a narrow opening) and interference (the pattern produced by multiple
coherent sources).

## Young's Experiment and Quantum Mechanics

Thomas Young performed this experiment in 1801, measuring the wavelength of visible light for the
first time. The quantum version — firing single particles (electrons, neutrons, even C₆₀ molecules)
one at a time — produces the identical pattern: each particle passes through both slits simultaneously
as a probability amplitude ψ, and the Born rule |ψ|² gives exactly the formula above.

The de Broglie wavelength λ = h/p lets any particle with momentum p behave as a wave. An electron
accelerated through 50 V has λ ≈ 0.17 nm — comparable to atomic spacings, which is why electron
diffraction maps crystal structures.

## Diffraction Grating (5 Slits)

With 5 slits, the grating factor [sin(Nδ)/(N·sinδ)]² creates sharp principal maxima with N−2 = 3
secondary maxima between them. As N grows, the principal maxima sharpen toward delta functions —
exactly how a spectrometer resolves closely-spaced spectral lines.
