# Cloth: What Falls Together

A 32×32 spring-mass cloth simulation rendered in real time on an HTML5 Canvas. The cloth hangs from evenly spaced pin points along its top edge and falls under gravity while a continuous sinusoidal wind ripples through it. Each of the 961 visible quadrilaterals is shaded by a proxy surface normal so the fabric reads as a physical material rather than a flat mesh.

## Verlet Integration

Each particle stores its current position `(x, y)` and its previous position `(px, py)`. The implicit velocity `v = current − previous` is scaled by a damping factor and used to advance the simulation one frame:

```
vx = (x - px) * damp
vy = (y - py) * damp
px = x;  py = y
x += vx + wind_force
y += vy + gravity
```

Verlet integration is preferred over explicit Euler + spring forces for cloth because **constraint projection can be applied directly to positions** without accumulating force errors. Explicit spring forces become stiff at short time steps and require small `dt` for stability; Verlet with iterative constraint projection remains stable at interactive frame rates even with large spring constants.

## Constraint Projection

Each spring is a constraint `(a, b, restLength)`. After the Verlet integration step, constraints are enforced by moving particle positions:

```
dx = b.x - a.x;  dy = b.y - a.y
dist = sqrt(dx² + dy²)
correction = (dist - restLength) / dist × 0.5
if !a.pinned:  a += (dx, dy) × correction
if !b.pinned:  b -= (dx, dy) × correction
```

Running this 5 times per frame is enough to make the cloth behave stiffly. The cloth has three spring types:

- **Structural** — horizontal and vertical neighbours at rest length `REST`
- **Shear** — diagonal neighbours at rest length `REST × √2`, preventing angular collapse

## Wind and Looping

The horizontal wind force per particle is:

```
Fx = A × sin(t × ω + x × k)
```

where `t` is the frame counter, `ω = 0.0015 rad/frame`, `x` is the particle's current horizontal position, and `k = 0.055` is a spatial wavenumber. This creates a travelling wave across the cloth that repeats every `2π/ω ≈ 4200` frames, ensuring the animation never settles to a static rest state.

## Shading

For each quad `(A, B, C, D)`, the z-component of the cross product of the two diagonals gives a proxy surface normal:

```
d1 = C − A;  d2 = D − B
nz = (d1.x × d2.y − d1.y × d2.x) / (2 × REST²)
```

`nz ≈ 1` for a flat quad facing the viewer, `nz ≈ 0` for a twisted or foreshortened quad, and `nz < 0` for back-facing (inverted) quads. Brightness is mapped to `[0.4, 1.4] × base_colour` using a pre-built 256-entry LUT, giving the cloth a sense of depth without a full 3D renderer.

## Palette

Deep burgundy (`#8b1a3a`) on near-black (`#080810`). The warm-dark combination reads as heavy fabric lit by a single overhead source.
