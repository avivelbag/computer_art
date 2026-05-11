# The Surface Speaks

A rippling sine–cosine product surface rendered as animated ASCII art on a deep navy background with amber phosphor text.

Each frame samples an 80 × 40 character grid: for every cell the normalised coordinates (x, y) in [−π, π] are fed into z = sin(x · 3 + t) · cos(y · 3 + t · 0.7), which acts as a top-down projection of a mathematically infinite 3 D wave onto the 2 D plane. The two different time multipliers (1.0 and 0.7) cause the wave crest to travel diagonally so the animation never looks purely left-right. The resulting z ∈ [−1, 1] is then mapped linearly onto the nine-character brightness ramp ` .:-=+*#@` — spaces for valleys, `@` for peaks — and written into a monospace `<pre>` element at up to 60 fps.

**Technique:** HTML5 `<pre>` ASCII art, sine–cosine product surface, brightness-to-character ramp  
**Year:** 2026
