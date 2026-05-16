# Piece 227 — Charge Canvas: Electric Fields and Equipotentials

An interactive 2D canvas simulation of electric field lines and equipotential contours for an arbitrary arrangement of up to eight point charges. Drag any charge to reshape the field in real time; click empty canvas to add a new charge (sign alternates +/−); click an existing charge to remove it.

## Physics

### Coulomb's Law

The electric field **E** at position **r** due to a point charge q at position **r₀** is:

```
E(r) = k · q · (r − r₀) / |r − r₀|³
```

where k ≈ 8.99 × 10⁹ N·m²/C². This simulation uses a dimensionless scaled constant K = 1×10⁵ (canvas pixels, not SI metres).

### Superposition Principle

For N charges the total field is the vector sum:

```
E_total(r) = Σᵢ k·qᵢ · (r − rᵢ) / |r − rᵢ|³
```

The scalar potential is likewise additive:

```
V(r) = Σᵢ k·qᵢ / |r − rᵢ|
```

Both `getField(x,y)` and `getPotential(x,y)` implement this loop directly.

## Streamline-Tracing Algorithm

Field lines are traced by **Euler forward integration** along the electric field direction:

1. From each **positive** charge, launch **N_LINES = 16** streamlines at equal angular spacing (every 22.5°).
2. Each trace starts a few pixels outside the charge radius to avoid the r = 0 singularity. A soft core (+1 px² added to r²) provides additional numerical safety.
3. At each step, call `getField(x, y)` to obtain **(Ex, Ey)**, normalise the vector, and advance **LINE_STEP = 2 px** in that direction.
4. The trace terminates when:
   - The point enters within **5 px** of a negative charge (line "lands" on the charge).
   - The point exits the canvas boundary.
   - **MAX_STEPS = 2000** Euler steps have elapsed (safety cutoff for orphaned lines when there is no negative charge nearby).

A step size of 2 px balances smoothness against per-frame computation: the total per-frame cost is O(P · N · S) where P is the number of positive charges (≤ 8), N = 16 lines each, and S ≤ 2000 steps per line, with the inner loop dominated by the O(C) Coulomb sum over all C charges.

## Potential Grid and Marching-Squares Contouring

### Grid evaluation

`buildPotentialGrid()` evaluates V on an **80×80** coarse grid spanning the full canvas. Per-frame cost is O(G² · C) with G = 80 and C the number of charges (≤ 8).

### Iso-level selection

The **10th–90th percentile** range of grid values is used as the contour band, discarding the extreme tails near charge centres. **N_CONTOURS = 10** evenly-spaced levels are selected across this band.

### Marching squares

`marchingSquares(grid, V0)` traces the iso-contour V = V₀ via the classic marching-squares algorithm:

1. Visit each 2×2 cell of the grid.
2. Assign each corner a binary flag (1 if the corner value exceeds V₀, 0 otherwise). The four flags form a **4-bit index** (0–15).
3. A lookup table (`switch` statement on the index) specifies which pair of cell edges the contour crosses. The intersection position on each edge is found by **linear interpolation**:
   ```
   t = (V0 − a) / (b − a)   where a,b are the two corner values
   ```
4. Each crossing pair becomes one line segment; all segments together approximate the full V = V₀ contour.
5. **Ambiguous saddle-point cases** (index 5 = 0101 and index 10 = 1010) are resolved by comparing the cell average to V₀: if the average exceeds V₀ the saddle opens on the inside, otherwise on the outside.

## Rendering

| Element | Colour | Style |
|---------|--------|-------|
| Background | `#0a0a14` | solid fill |
| Positive charges | `#e04040` (rim `#ff8080`) | filled circle + label |
| Negative charges | `#4080e0` (rim `#80b0ff`) | filled circle + label |
| Field lines | `#d4a030` (warm gold) | lineWidth 1, opacity 0.85 |
| Equipotentials | `#208888` (cool teal) | lineWidth 0.8, opacity 0.45, dashed |

Rendering is triggered by a `dirty` flag — any charge modification sets `dirty = true`. The `requestAnimationFrame` loop redraws only when dirty **and** at least 16 ms have elapsed since the previous frame, capping throughput at ~60 fps.

## Controls

| Interaction | Effect |
|-------------|--------|
| Click empty canvas | Add a charge (sign alternates +/−) |
| Click a charge | Remove it |
| Drag a charge | Move it; field lines and equipotentials update live |
| Clear charges | Remove all charges |
| Reset | Restore the two default charges (one +, one −) |
| About | Toggle the educational info panel |
