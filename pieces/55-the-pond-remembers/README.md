# Wave Interference — The Pond Remembers Every Stone

Five point wave sources emit coherent circular wavefronts. At each pixel the canvas evaluates the superposition of all five waves and maps the signed sum through a 256-step palette: deep indigo/violet for negative amplitude, near-black at the zero crossing, warm gold/amber for positive amplitude.

Each source drifts along a Lissajous orbit — `x = cx + rx·sin(ax·t + φx)`, `y = cy + ry·sin(ay·t + φy)` — with incommensurable frequency ratios so the path never closes into a fixed loop. As the sources drift, hyperbolic interference fringes sweep and rotate, continuously reshaping the pattern without ever repeating.

The wave amplitude at pixel `(x, y)` from source `i` is `sin(K·d_i − ω·t + φ_i)` where `d_i` is the Euclidean distance to that source, `K = 0.08 rad/px` (fringe spacing ≈ 78 px in the offscreen buffer), and `ω = 1.2 rad/s`. The summed amplitude passes through `tanh` to compress the range, then indexes the precomputed palette. One `putImageData` call per frame updates a 400×300 offscreen canvas which is upscaled to fill the window.

Built with plain Canvas 2D API, no external libraries. Target: 60 fps via `requestAnimationFrame`.
