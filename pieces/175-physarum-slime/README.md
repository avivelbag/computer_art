# Piece 175 — The Mold That Finds the Train Schedule: Physarum

*Physarum polycephalum* — slime mold — is a single-celled organism without a nervous system that nonetheless solves network-optimization problems. When presented with food sources at Tokyo's rail stations, it built a transport network matching the human-engineered subway system, discovered independently over a few days (Nakagaki, Yamada, Tóth, 2000; Jones, 2010).

## The three rules

Each of 12 000 agents carries a position and a heading. Every frame:

1. **Deposit** — drop `DEPOSIT` units of chemical trail onto the grid cell beneath the agent.
2. **Diffuse + decay** — the entire trail grid is convolved with a 3×3 box blur, then multiplied by `DECAY = 0.96`. Trail spreads to neighbors and fades over time.
3. **Chemotax** — each agent samples trail intensity at three sensor points: straight ahead, 30° left, and 30° right, at a distance of 9 px. It steers toward whichever sensor reads the highest concentration. Ties are broken with random jitter.

From these three rules alone, a vein network self-organises: paths used by many agents accumulate more trail, attracting more agents, reinforcing themselves into bright corridors while unused paths decay away.

## Parameters

| Parameter | Value | Role |
|-----------|-------|------|
| N | 12 000 | Number of agents |
| sensorAngle | 30° (π/6) | Angular offset of left/right sensors |
| sensorDist | 9 px | Sensing distance ahead |
| stepSize | 1.5 px | Distance moved per frame |
| decayFactor | 0.96 | Per-frame trail decay after diffusion |
| deposit | 5.0 | Trail units deposited per agent per frame |

## Initial condition

Agents are placed on a ring of radius 28 % of canvas height, facing outward. The ring expands and its agents sense each other's deposited trails, causing positive feedback that locks high-traffic corridors into bright veins.

## Palette

Trail intensity is mapped through a smoothstep to a three-stop gradient:

- **0.0** — deep violet `#120028` (empty space)
- **0.5** — electric teal `#00e6c8` (light trail)
- **1.0** — warm white `#fff8eb` (dense vein)

## Technical

- `Float32Array` trail buffer and agent array — avoids GC pressure in the hot loop.
- Double-buffering: diffusion writes to a secondary array, then the two pointers are swapped.
- `ImageData` writes every frame for per-pixel palette mapping, using bitwise `<< 2` indexing.
- Toroidal wrap on a 800 × 500 canvas; agents and sensors wrap at all four edges.
- Runs indefinitely at 60 fps via `requestAnimationFrame`; no external dependencies.

## Files

- `index.html` — self-contained canvas simulation
- `thumbnail.svg` — static SVG snapshot suggesting the vein network
- `README.md` — this file
