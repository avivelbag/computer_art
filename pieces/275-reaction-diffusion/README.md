# Piece 275 — The Labyrinth Writes Itself

A Gray-Scott reaction-diffusion simulation running entirely on the GPU via WebGL2 ping-pong
framebuffers at 60 fps, tuned to the **maze regime** where the activator self-organises into
an endlessly branching network of labyrinthine corridors.

**Prior pieces in this gallery:**
[Piece 17 — Where Life Begins](../17-where-life-begins/) and
[Piece 96 — Mitosis in Amber](../96-gray-scott/) both use the *coral regime*
(F=0.0545, K=0.062) on a CPU canvas double-buffer with charcoal/cream and amber/ivory palettes.
[Piece 180 — Chemical Dreams](../180-gray-scott/) uses the *mitosis regime*
(F=0.0367, K=0.0649) on CPU canvas with an indigo/cyan palette.
This piece uses the **maze regime** (F=0.029, K=0.057) running on the **GPU** (two RGBA32F
WebGL framebuffers), with an earthy near-black → dark-sienna → warm-parchment palette.
The three differ in morphological class, rendering architecture, and colour family.

## Gray-Scott Model

Two chemical species, U (substrate) and V (activator), evolve according to:

```
dU/dt = Du·∇²U  −  U·V²  +  F·(1−U)
dV/dt = Dv·∇²V  +  U·V²  −  (F+K)·V
```

U is continuously replenished at feed rate F.  V autocatalytically converts U into more V
at rate U·V², and decays at rate (F+K)·V.  The balance between diffusion, autocatalysis,
and decay produces self-organising spatial patterns whose morphology depends entirely on F and K.

## Parameters

| Parameter | Value  | Role                                        |
|-----------|--------|---------------------------------------------|
| F         | 0.029  | Feed rate — replenishes U from the boundary |
| K         | 0.057  | Kill rate — drains V beyond the feed        |
| Du        | 0.2097 | Diffusion coefficient for U                 |
| Dv        | 0.1050 | Diffusion coefficient for V (Du / 2)        |

At F=0.029, K=0.057 the system lies in the **maze** region of the Gray-Scott parameter space.
Neither the coral regime (spots / branching trees) nor the mitosis regime (self-replicating
blobs) applies here: instead, V forms a connected, space-filling network of narrow corridors
that resembles a hand-drawn labyrinth.  The network is stable once formed; it neither grows
nor shrinks but may drift and reconnect very slowly.

## GPU Implementation

Two RGBA32F textures are allocated as WebGL2 framebuffer colour attachments.  Each animation
frame runs a GLSL fragment shader that reads from the *ping* texture, advances one Gray-Scott
step per pixel, and writes the updated (U, V) pair to the *pong* texture.  After each step
the ping and pong references are swapped, so the next step automatically reads the freshly
computed state.  The textures use `GL_REPEAT` wrapping, which provides toroidal (wrap-around)
boundary conditions for free — no conditional modulo arithmetic is needed in the shader.

The Laplacian uses a 9-point isotropic stencil that weights axis-aligned neighbours at 0.20
and diagonal neighbours at 0.05 (kernel sums to zero):

```
∇²U[i] = 0.05·(NW + NE + SW + SE) + 0.20·(N + S + W + E) − U[i]
```

Twenty simulation steps run per rendered frame for the first 500 frames (≈10 000 steps total)
so the labyrinthine pattern develops quickly on first load.  After stabilisation the rate drops
to two steps per frame, which keeps the pattern gently animated without disrupting its structure.

Five seeds — one near the centre and one near each quadrant corner — are jittered with random
noise before the first frame so that multiple growth fronts collide and weave a uniform network
across the full canvas rather than a single patch expanding from one point.

## Colour Palette

Three stops map V concentration to colour:

| Stop | V   | Colour        | Hex      |
|------|-----|---------------|----------|
| 0    | 0.0 | Near-black    | #0e0b08  |
| 1    | 0.5 | Dark sienna   | #7b3f00  |
| 2    | 1.0 | Warm parchment| #f0e8d0  |

Channels (V ≈ 0) appear near-black.  Maze walls (V ≈ 1) glow warm parchment.  The sienna
midpoint gives wall edges a deep ochre halo, evoking carved stone or scorched earth.

## What to Notice

- The first few seconds show the pattern crystallising rapidly (20 GPU steps per display frame)
- Once stable the corridors form a connected graph: every region of dark background is enclosed
  by the wall network, with no isolated loops and no dead ends visible at large scale
- The pattern never fully freezes — very slow drift and occasional reconnection events are
  a consequence of the finite diffusion still propagating through the stabilised state

## Files

- `index.html` — self-contained WebGL2 animation, no external dependencies
- `thumbnail.svg` — SVG approximation of the maze pattern in the sienna/parchment palette
- `README.md` — this file
