# SDF Kaleidoscope — Mirror Lattice

Raymarching (sphere-tracing) fires one ray per pixel from a virtual camera into a 3D scene described entirely by a signed-distance function (SDF): each step along the ray advances by the safe minimum distance to any surface, so the ray never overshoots, and convergence to an intersection typically takes 20–80 tiny steps instead of exhaustive sampling.

The SDF scene uses a **kaleidoscopic octahedral domain fold** — `abs(p)` collapses all eight octants into one, and sorting the components (`if x<y swap`) further collapses the six ordering permutations, achieving 48-fold mirror symmetry before the `mod()` tiling fills infinite space. Inside each tile a **sphere** is blended with a **rounded box** via the polynomial `smin` (smooth-minimum) operator, whose blend radius oscillates with time to morph the shapes continuously.

Primitives: `sdSphere`, `sdRoundBox`. Domain operators: `abs`-mirror fold + component sort (octahedral IFS), `mod`-repeat. Lighting: single directional Phong diffuse/specular, five-tap ambient occlusion, electric-cyan rim light, depth fog. Palette: neon crimson (`#e6123a`) surfaces fading to near-black teal void. Camera orbits on a 25-second period with a slow vertical bob.
