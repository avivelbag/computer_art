# Piece 113 — Murmuration: Three Rules and a Sky

Three local rules — *separation*, *alignment*, *cohesion* — applied independently to each of 300 agents produce the global pattern of a murmuration: a single fluid swarm that splits, wheels, and re-coheres without any central coordinator. The algorithm is Craig Reynolds' Boids model (1986).

## The three rules

Each boid perceives neighbors within a radius of 60 px. On every frame:

1. **Separation** — steer away from neighbors closer than 20 px, weighted by inverse distance, preventing collisions.
2. **Alignment** — steer toward the average velocity of nearby boids, so the flock tends to fly together.
3. **Cohesion** — steer toward the center of mass of nearby boids, keeping the swarm from dispersing.

The weighted sum of these three forces is added to the boid's velocity each frame, then speed is clamped to the range [0.8, 2.5] px/frame.

## Toroidal wrapping

Position wraps at all four canvas edges, so a boid flying off the right edge re-enters from the left. Inter-boid distance is measured toroidally so the perception radius crosses the wrap boundary correctly.

## Visual design

300 near-white boids (RGBA 220, 230, 255, 85%) on a deep midnight-blue background (`#060614`) with subtle motion trails from a semi-transparent fill (alpha 0.25 per frame). Each boid is a small filled triangle pointed in its direction of travel.

## Animation

Runs at 60 fps via `requestAnimationFrame`. The flock self-organises from random initial conditions within a few seconds and produces complex collective motion indefinitely — no interaction required.

## Files

- `index.html` — self-contained canvas animation, no external dependencies
- `generate_thumbnail.py` — pure-stdlib Python that writes `thumbnail.svg`
- `thumbnail.svg` — static SVG snapshot with 100 boid glyphs at fixed seed 42
- `README.md` — this file
