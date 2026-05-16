# Halftone Tides — Interference Wave Dot Grid

## Distinction from other halftone pieces in the gallery

Piece 150 (*Halftone Riso*) is a two-screen offset-litho simulation: two dot grids at fixed rotation angles drift apart via slow misregistration, modulated by a single concentric sine field. Piece 22 (*Dot by Dot*) drives a single-screen coral grid with one outward ripple emanating from the canvas centre.

**Halftone Tides** uses neither a rotated screen nor a single-source ripple. The modulation is a true multi-wave *spatial interference pattern* — four independent traveling plane waves, each with a distinct wave-vector direction, spatial frequency, temporal frequency, and phase offset. Their superposition drives dot radius at every grid point, generating traveling moiré-like interference fringes that cannot arise from any single-wave driver. The palette (deep indigo background, warm gold dots) also differs entirely from the existing halftone pieces.

## Algorithm

A 40 × 40 grid of dot centres is fixed at sub-pixel intervals across a 600 × 600 canvas. On every frame, each dot's radius is computed as:

```
v  = (1/N) Σᵢ sin(kxᵢ·x + kyᵢ·y + freqᵢ·t + phaseᵢ)
r  = maxR × clamp(v/2 + 0.5, 0.10, 0.90)
```

where (kxᵢ, kyᵢ) is the wave-vector of wave i, freqᵢ is its temporal frequency (rad/s), and N = 4. The clamp to [0.10, 0.90] ensures dots never fully disappear nor overlap neighbours (maxR = 0.45 × cell size, so 90% fills 90% of half the grid spacing without touching adjacent cells).

## Wave parameters

| Wave | kx      | ky      | freq | phase |
|------|---------|---------|------|-------|
| 1    |  0.08   |  0.06   | 1.1  | 0.00  |
| 2    | −0.05   |  0.10   | 0.7  | 1.20  |
| 3    |  0.12   | −0.04   | 1.5  | 2.40  |
| 4    | −0.07   | −0.09   | 0.9  | 3.70  |

The four wave-vector directions span all four quadrants. The temporal frequencies (1.1, 0.7, 1.5, 0.9) are pairwise incommensurate, so the pattern never exactly repeats — yet because all components are bounded sinusoids the visual impression is a seamless, perpetually undulating tide.

## Palette

| Role       | Colour      | Hex       |
|------------|-------------|-----------|
| Background | Deep indigo | `#1a0a2e` |
| Dot        | Warm gold   | `#f7c95b` |

Chosen to avoid all palettes already in the gallery: riso-halftone (cream / pink / teal) and dot-by-dot (warm cream / coral).

## Performance

Animation is capped at 60 fps via a timestamp comparison gate inside `requestAnimationFrame`. All 1 600 dots per frame are batched into a single canvas path and filled in one call, keeping CPU cost low.
