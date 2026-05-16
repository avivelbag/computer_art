# Ising Model — The Temperature of Order

A live Metropolis–Hastings Monte Carlo simulation of the 2D ferromagnetic Ising model on a 200×200 toroidal lattice. Drag the temperature slider through the critical point and watch magnetic order emerge or dissolve in real time.

## How it works

Each cell holds a spin s ∈ {+1, −1} representing a magnetic dipole. Spins interact only with their four nearest neighbours; the Hamiltonian is:

```
H = −J Σ sᵢ sⱼ   (sum over adjacent pairs, J = k = 1)
```

**Metropolis–Hastings algorithm:** each animation frame attempts N² random spin flips. A flip at site (i,j) is accepted immediately if it lowers energy (ΔE ≤ 0). If it raises energy by ΔE the flip is accepted with Boltzmann probability `exp(−ΔE / kT)`. Because the neighbour sum can only be −4, −2, 0, 2, or 4, only two positive ΔE values exist (4J and 8J), so only two lookup values (`exp(−4/T)` and `exp(−8/T)`) need to be recomputed when T changes.

**Boundary conditions:** the grid wraps toroidally — left/right and top/bottom edges are neighbours — eliminating surface effects.

**Colours:** spin +1 renders as warm linen (#f5ead8); spin −1 renders as deep indigo (#1a1040). The 200×200 pixel ImageData is scaled to fill the canvas.

## The Curie temperature

The 2D square-lattice Ising model has an exactly known critical temperature (Onsager 1944):

```
Tc = 2J / (k · ln(1 + √2)) ≈ 2.2692  (in units J/k = 1)
```

Below Tc large ferromagnetic domains dominate and the net magnetisation |M| approaches 1.  
Above Tc thermal fluctuations overwhelm exchange coupling, domains dissolve, and |M| → 0.  
Right at Tc the system is scale-free: domains of every size coexist — "critical opalescence."

## Controls

| Control | Description |
|---------|-------------|
| Temperature slider | T from 0.5 (ordered ferromagnet) through Tc ≈ 2.27 (critical point, marked) to 4.0 (disordered paramagnet) |
| Reset | Reinitialise lattice with uniform random spins |
| Click any cell | Flip that spin (defect injection) |
| Info | Open the physics explanation pane |

## What to notice

- **Below Tc:** large same-colour domains grow and coarsen. Defects injected into a domain heal quickly.
- **At Tc:** fractal domain boundaries appear at every scale; the sparkline of |M| fluctuates wildly.
- **Above Tc:** no persistent domains; injected defects spread immediately; sparkline sits near zero.
- **Phase transition:** dragging the slider through Tc causes the sparkline to abruptly collapse or recover — a sharp, not gradual, change.
- **Critical slowing down:** equilibration near Tc is much slower than away from it (correlation length diverges as ξ ~ |T − Tc|^(−1)).

## Onsager's exact solution

Lars Onsager (1944) derived the exact free energy of the 2D Ising model in zero external field — one of the great achievements of twentieth-century mathematical physics. The spontaneous magnetisation below Tc obeys:

```
M = (1 − sinh⁻⁴(2J/kT))^(1/8)
```

The heat capacity diverges logarithmically at Tc with critical exponent α = 0. No closed-form solution exists in 3D; the 3D critical temperature is found numerically (Tc ≈ 4.511 J/k for the simple cubic lattice).

## References

- L. Onsager, "Crystal Statistics I," *Phys. Rev.* **65**, 117 (1944).
- N. Metropolis et al., "Equation of State Calculations by Fast Computing Machines," *J. Chem. Phys.* **21**, 1087 (1953).
- K. Huang, *Statistical Mechanics*, 2nd ed., Wiley (1987).
