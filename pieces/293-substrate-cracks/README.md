# Ancient Glaze

Substrate crack simulation growing crystalline fault lines across aged parchment,
implementing Jared Tarbell's substrate algorithm.

Six seeds scatter across the 800×800 canvas at random positions and angles. Each
extends one pixel per animation frame along its heading, with the angle biased by
±3° per step from a precomputed 64×64 value-noise grain field (bilinearly
interpolated) to produce organic waviness. On contact with an existing crack pixel,
the arriving tip dies and spawns a perpendicular offspring (±5° jitter) at the
contact point. Growth continues until no seeds remain alive.

The result resembles cracked ceramic glaze, dry clay, or ice fissures — organic
yet geometric.

**Technique:** Substrate algorithm / 2D value noise / Canvas 2D  
**Palette:** Aged parchment `#e8dfc8` · Deep umber `#3d2b1a`  
**Year:** 2026
