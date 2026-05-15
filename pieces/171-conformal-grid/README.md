# Conformal Grid — The Grid That Knows Where It Lives

A rectangular grid drawn in the complex plane is fed through a conformal map — a holomorphic function that locally preserves the angle at which any two curves cross. What you see are two grids at once: faint straight lines marking where the coordinates began, and bold rose and sky-blue curves showing where the map sends them.

## Angle preservation

A conformal map f: ℂ → ℂ stretches and bends the plane, but wherever two curves cross at a right angle in the original grid, their images cross at a right angle too. That is what "conformal" means: shape-preserving in the small, even as the large-scale geometry distorts dramatically. Circles are sent to circles (or lines, which are circles of infinite radius), and the delicate web of coordinate curves retains its perpendicular crossings throughout the deformation.

## The three maps

**Joukowski transform** z → z + λ/z was invented by Nikolai Joukowski in 1910 to map a circle to an airfoil profile. At λ = 0 the transform is the identity; as λ rises to 1 the grid lines bend into the characteristic teardrop curves that define aeroplane wing cross-sections. The function has a pole at z = 0, so lines that pass close to the origin are bent outward violently, producing the gap near the centre. The unit circle under this map collapses exactly onto the real interval [−2, 2] — the airfoil's chord line — revealing why Joukowski's construction turned an abstract theorem in complex analysis into a practical tool for aerodynamics.

**Square map** z → z² folds the plane in half: every output point is hit by two pre-images (z and −z), so the grid doubles back on itself. Horizontal lines (constant imaginary part) become upward-opening parabolas; vertical lines (constant real part) become downward-opening parabolas. The two families remain perpendicular wherever they meet, which is the conformal property made visible.

**Möbius transform** (z − 1)/(z + 1) sends circles and lines to circles and lines, rearranging the entire plane around two fixed points (z = 1 maps to 0; z = −1 is a pole). It is the simplest non-trivial rational conformal map and has been central to hyperbolic geometry, signal processing (bilinear transform), and complex analysis for over a century.

## What the animation does

Each map is introduced gradually: the morphing parameter λ rises smoothly from 0 to 1 and falls back to 0 over eight seconds, so the grid breathes in and out of distortion. At λ = 0 both grids coincide and the canvas shows only straight lines; at λ = 1 the bold conformal curves reach their most distorted state. After eight seconds the cycle hands off to the next map.

Rose and coral lines follow curves of constant imaginary part (horizontal coordinate lines in the original grid). Sky-blue lines follow curves of constant real part (vertical coordinate lines). Because the compositing mode is additive, intersections of the two colour families bloom brighter, tracing the conformal image of the grid's crossing points.
