# The Gyroid Unfolds — Triply Periodic Minimal Surface

The gyroid is a triply periodic minimal surface — a surface with zero mean curvature that repeats in all three spatial directions. It appears in butterfly wing nanostructure, block copolymer self-assembly, and cell membrane architectures. Its implicit equation is f(x,y,z) = sin(x)cos(y) + sin(y)cos(z) + sin(z)cos(x) = 0.

This piece takes a continuously animated slice through the gyroid at z = z(t), rendering the 2D cross-section of the surface pixel-by-pixel in a WebGL fragment shader. As z sweeps from −π to π over ~20 seconds, the topology of the level-set curve evolves: connected sheets split apart, holes open and close, and labyrinthine channels form and reconnect in patterns reminiscent of the Schwarz P and D surfaces that share the same crystallographic symmetry group.

The slice plane rocks gently ±10° around the vertical axis so the surface is never seen perfectly flat, hinting at the three-dimensional structure beneath the 2D projection. A warm gold isocurve marks the primary level set f = 0; two cooler blue bands at f = ±0.5 provide topographic depth. The gold drifts toward orange as z approaches ±π, making the period of the animation perceptible by color as well as shape.

Technique: WebGL fragment shader / GLSL implicit surface / level-set cross-section / triply periodic minimal surface
