# Mandelbrot + Julia — Interactive Explorer

A dual-panel WebGL fractal explorer that makes the link between the Mandelbrot set and Julia sets tangible: hover anywhere on the Mandelbrot canvas and the corresponding Julia set appears instantly in the panel on the right. An orbit-trace overlay shows the iteration path for the hovered point, revealing why it escapes or stays.

## How it works

### The Mandelbrot set

For each complex number `c = a + bi`, repeatedly apply the map:

```
z → z² + c,   starting from z = 0
```

If the orbit `{0, c, c²+c, …}` remains bounded (|z| ≤ 2 for all iterations), `c` belongs to the Mandelbrot set and is coloured black. If |z| exceeds the bailout radius the orbit escapes; `c` is coloured by how quickly it escapes.

### Smooth escape-time colouring

Integer iteration counts produce discrete visible bands. Smooth colouring removes them using the continuous escape count:

```
smooth_n = n − log₂( log₂(|z|) )
```

where `n` is the integer iteration at which |z| first exceeds the large bailout radius 256 (chosen large so the log formula is accurate). The resulting real value maps to a hue via a full-range HSL sweep (hue = fract(smooth_n / 40) × 360°), producing a gradient with no banding.

### Julia sets

For every fixed `c` there is a Julia set `J_c`: the set of starting points `z₀` whose orbits under `z → z² + c` remain bounded. The same GLSL shader handles both sets — in Julia mode the pixel coordinate supplies `z₀` and `c` is a shader uniform updated each frame from the mouse position.

**Mandelbrot ↔ Julia correspondence:** points deep inside the Mandelbrot set produce connected, richly structured Julia sets; points outside produce Cantor dust (totally disconnected). Points near the Mandelbrot boundary produce Julia sets with intricate, fractal boundaries.

### Orbit trace overlay

A transparent 2D canvas sits on top of the Mandelbrot WebGL canvas (`pointer-events: none`). On each mouse-move event, JavaScript iterates `z → z² + c` for the hovered `c` (up to 128 steps) and draws the resulting orbit as step-coloured circles connected by lines. Early-orbit points are purple, late-orbit points are gold.

## Controls

| Action | Effect |
|--------|--------|
| Hover mouse over Mandelbrot | Julia set updates to match hovered `c`; orbit trace appears |
| Click-drag | Pan the Mandelbrot view |
| Scroll wheel | Zoom in/out (centred on cursor) |
| Double-click | Re-centre view on cursor position |
| Max-iterations slider (64–2048) | Trade off detail vs render speed |
| Reset button | Restore default centre (−0.5, 0) and scale |

## Technical notes

- Both canvases run independent WebGL contexts with the same GLSL fragment shader. The `u_julia` uniform switches between Mandelbrot and Julia modes.
- A high bailout radius of 256 (rather than the minimal 2) is used so the log-based smooth-colouring formula is numerically accurate.
- The GLSL `for` loop is bounded at 2048 (maximum allowed uniform) with an early `break` at `u_maxIter`, which the GLSL compiler can fold into a single loop.
- No external dependencies; WebGL unavailability is caught and a fallback message is displayed.

## References

- B. Mandelbrot, *The Fractal Geometry of Nature* (1982).
- G. Julia, "Mémoire sur l'itération des fonctions rationnelles," *J. Math. Pures Appl.* 8 (1918).
- Linas Vepstas, "Smooth Iteration Count for the Mandelbrot Set" (2002).
