# Whorled

A Kleinian group limit set rendered by iterated circle inversions.

Three mutually-tangent generating circles form a Schottky group. Every pixel on
the canvas is mapped to a point in the complex plane and repeatedly inverted
through whichever generating circle contains it. When the point escapes all
three circles it has landed on the limit set; it is coloured by the index of
the last circle that reflected it — rose, gold, teal, or violet.

The result is a fractal foam of interlocking curved arcs, infinitely nested,
with bilateral symmetry arising from the symmetric placement of the three
circles. The whole configuration rotates imperceptibly slowly (~35 minutes per
full turn), so the geometry itself is the payoff.

**Technique:** HTML5 Canvas, Möbius / circle inversion math, Schottky group, iterated inversion  
**Year:** 2026
