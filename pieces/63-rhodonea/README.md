# Rhodonea — The Petal Count Is Always a Surprise

A rhodonea (rose) curve is the polar equation *r = cos(k·θ)*. When *k = n/d* is rational in lowest terms, the curve closes after a finite sweep of θ and produces exactly *n* petals if *n* is odd, or *2n* petals if *n* is even — a fact that means even the smallest change in *k* can double or halve the petal count instantly, making the morphing animation feel like watching a living thing decide how many limbs it wants.

## Technique

The animation sweeps *k* from 1 to 6 and back over 30 seconds using a sin-based oscillator for seamless looping. Each frame three concentric roses are drawn — at radii 1, 0.72, and 0.44 of the full radius, with *k* offsets of ±0.05 — so the near-resonance between the three parameter values creates moiré-like petal beating independent of the overall morphing. Motion-blur ghosting is produced by painting the background at 4% opacity each frame rather than clearing it fully, letting recent curves glow while older strokes decay.

## Mathematical note

The petal count rule: for *k = n/d* in lowest terms, the rose has *n* petals when *n* is odd and *2n* petals when *n* is even. Irrational *k* produces a curve that never closes, filling the disc densely over infinite time — the animation catches only the transient, still-open arcs, which look like petal buds mid-bloom.
