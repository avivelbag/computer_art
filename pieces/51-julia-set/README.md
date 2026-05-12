# Julia Set — Orbit-Trap Coloring

For each pixel the shader iterates **z → z² + c** up to 256 times and records the minimum distance the orbit reaches from the origin. This *orbit trap* value — a single continuous scalar — drives a three-stop palette (deep indigo → amber → ivory) through `smoothstep`, producing smooth jewel-like bands instead of the staircase banding that comes from counting raw escape iterations. Because the minimum-distance measurement varies continuously between neighbouring pixels, colour boundaries are perfectly smooth.

The parameter **c** follows `c = 0.7885 · (cos t, sin t)` with t advancing at 0.25 rad/s, tracing the "dancing dragon" circle that keeps the Julia set connected throughout the ~25-second seamless loop.

Built with pure WebGL 1.0, no external libraries.
