# Stadium Billiard: The Orbit That Never Closes

A point particle bouncing elastically inside a boundary is called a dynamical billiard. The shape of that boundary determines everything about the long-run behaviour of the orbit.

## The square: integrable motion

In a square table every trajectory is governed by two conserved quantities — the angles of reflection off the horizontal walls and the vertical walls never change independently. Particles launched at rational angles (e.g. 45°) trace closed, repeating polygons; those at irrational angles fill a two-dimensional strip in the phase space but never fill the entire surface. The motion is called **integrable**: it is constrained to a low-dimensional torus in phase space, and the orbit organises itself into structured, repeating patterns. You can see this visually — the square side of the animation builds star-like or diagonal-band patterns that stay predictable no matter how long you run it.

## The Bunimovich stadium: ergodic chaos

The stadium is a rectangle capped at each end with a semicircle. Leonid Bunimovich proved in 1979 that this simple modification destroys integrability completely. The curved ends mix the two angle components of motion, exponentially amplifying any tiny difference in initial direction. Two particles launched from identical positions at angles that differ by a millionth of a radian will, after enough bounces, be travelling in entirely unrelated directions.

This behaviour is **ergodic**: over time the orbit visits every region of the phase space with equal frequency. A single trajectory, run long enough, fills the interior uniformly. There are no conserved quantities that could restrict the orbit to a sub-region. The stadium also satisfies the stronger **mixing** property — correlations between the particle's position at time 0 and its position at time T decay to zero as T grows.

## The reflection law

At each collision the velocity vector is reflected through the surface normal at the impact point. For the flat top and bottom walls the normal is simply the vertical unit vector. For the curved caps, the normal at a point P on a semicircle centred at C is the radial vector (P − C) / |P − C|. This gives the elastic reflection formula:

    v_out = v_in − 2 (v_in · n) n

No energy is lost; the speed stays constant throughout.

## Technique

HTML5 Canvas, dynamical billiards simulation, elastic reflection, Bunimovich stadium geometry, integrable vs. ergodic motion, HSL colour palette by launch angle, trail accumulation with alpha fade.

**Year:** 2026
