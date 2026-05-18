# Pursuit Curves — The Spider and the Fly

## What are pursuit curves?

A pursuit curve is the path traced by a pursuer that always moves directly toward a moving target. The classic *n-agent* version places *n* points at the vertices of a regular *n*-gon; each point chases the next one clockwise at constant speed. Because all agents are arranged symmetrically and all move simultaneously, the *n*-fold rotational symmetry is preserved at every step — the whole constellation contracts while rotating.

### The update rule

Each frame, every agent moves a fixed fraction `s` of the way toward its target:

```
agents[i].x += s * (agents[(i+1) % n].x - agents[i].x)
agents[i].y += s * (agents[(i+1) % n].y - agents[i].y)
```

Positions are updated **simultaneously** (all new coordinates are computed before any are written back) so no agent sees a partially-updated neighbour.

## The logarithmic spiral

The path of each agent is a **logarithmic spiral**. This emerges from the linear algebra of the update: in the complex-number representation, the map is multiplication by the constant `(1−s) + s·e^{i·2π/n}`, which contracts the magnitude by a fixed ratio and rotates by a fixed angle every step. Iterating a contraction-rotation produces a logarithmic spiral by definition.

The contraction ratio per step is `|(1−s) + s·e^{i·2π/n}|`, and the rotation angle is `arg((1−s) + s·e^{i·2π/n})`. For the parameters used here (`s = 0.015`):

| n | contraction/step | rotation/step |
|---|---|---|
| 3 | 0.9775 | 0.744° |
| 4 | 0.9858 | 0.859° |
| 5 | 0.9896 | 0.817° |
| 6 | 0.9919 | 0.748° |
| 7 | 0.9934 | 0.668° |
| 8 | 0.9944 | 0.592° |

Smaller *n* converges faster because the polygon edges are relatively longer compared to the diagonal, giving each agent more "sideways pull" per step.

## Composition choices

Six swarms — triangles through octagons — run concurrently, each at a radius inversely proportional to *n* so that the individual spirals occupy similar visual areas despite their different angular densities. All six are centred on the same canvas centre, which means their spiral envelopes overlap and interfere, producing a composite mandala-like form.

### Palette

Each *n* receives a single committed hue that spans the full visible spectrum without clustering:

| n | shape | hue |
|---|---|---|
| 3 | triangle | amber (42°) |
| 4 | square | teal (192°) |
| 5 | pentagon | rose (330°) |
| 6 | hexagon | lime (95°) |
| 7 | heptagon | violet (270°) |
| 8 | octagon | coral (18°) |

Hues are chosen so that no two adjacent *n* values share a similar colour region, preventing visual merging when swarms overlap. Saturation and lightness are held constant (≈75%, ≈60%) across all swarms so brightness equality ensures no single swarm dominates.

### Trail fade and depth

Each frame a near-black rectangle is painted at 1.2% opacity over the entire canvas. This exponentially decays old marks: a trail pixel reaches 50% brightness after roughly 57 frames (~0.95 s) and fades to near-invisible in about 300 frames (~5 s). Because each swarm's spiral completes in 230–280 frames, you see roughly one full spiral cycle of accumulation before it ghosts away — creating a hazy, layered depth without explicit z-ordering.

### Perpetual respawn

When all agents of a swarm converge within 3 px of the centre, the swarm is respawned at the same radius but with its initial angle offset by `π/n` radians (half an edge arc). This places the new spiral exactly between the traces of the previous one, gradually filling the space with a dense mandala pattern rather than endlessly re-tracing the same lines.
