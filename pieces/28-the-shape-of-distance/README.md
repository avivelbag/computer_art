# The Shape of Distance

Ray marching traces a ray from each pixel until it hits a surface defined by a **signed-distance field** (SDF) — a function returning the shortest distance from any point to the nearest surface. The scene blends a slowly rotating `sdTorus` with a morphing `sdSphere` via `opSmoothUnion`, adds a dark-slate ground plane, a small `sdBox`, and a chrome sphere whose colour is resolved by launching a second reflected ray march. Each fragment also runs a 5-sample ambient-occlusion march and a 24-step soft-shadow trace against a single warm point light, with a camera that orbits the scene driven by `uTime`.

**Palette:** deep teal/slate background (`#050d14`), warm gold → coral main form (`vec3(0.93,0.72,0.22)` → `vec3(0.90,0.35,0.20)`), chrome reflective sphere, dark checker ground.
