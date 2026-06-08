# Interference Star — Maurer Rose

A Maurer rose is formed by connecting 360 evenly-stepped points on a rhodonea curve r = sin(n·θ), where each step advances θ by d degrees. Two integers — n (petal count) and d (step size) — unlock thousands of distinct star-burst interference patterns from a single two-line formula.

The piece cycles through eight visually rich (n, d) pairs such as (5, 97), (7, 71), and (3, 113). Between forms, both parameters lerp continuously toward the target values at a rate of ~0.012 per frame; fractional n and d produce intermediate interference geometries that feel like the rose is dissolving and re-crystallising. Alpha-transparent strokes (opacity 0.15) accumulate during the morph so overlapping lines bloom into luminous nodes, then the canvas hard-clears once the target is reached and the sharp new form holds for ~3 seconds.

Palette: deep navy background (#0a0a12) with gold, cyan, and rose hues on alternating forms. All geometry is pure canvas 2D; no external assets or audio.
