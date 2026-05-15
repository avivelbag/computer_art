# Piece 150 — Halftone Riso Print: Two-Color Screen Simulation

A simulation of risograph printing using two overlapping halftone dot screens on an off-white
canvas. The piece reproduces the warmth and imperfection of physical Riso printing in pure canvas.

## What is Risograph?

Risograph is a stencil duplicator that prints one colour at a time. Because each colour pass
is registered separately — and because paper shifts slightly between passes — the colours never
align perfectly. That small misalignment, called **misregistration**, is not a flaw; it is the
aesthetic. The slightly offset halos around where two colours overlap are immediately legible as
handmade, tactile, alive.

The overlap areas where two Riso inks land on top of each other mix subtractively, producing a
third colour neither ink alone could make. Fluorescent pink + teal yields a deep burnt-magenta
in the overlay zones. The `multiply` blend mode on canvas reproduces this subtractive mixing
faithfully.

## Technique

Two independent halftone dot grids are drawn with `ctx.globalCompositeOperation = 'multiply'`:

| Screen | Ink colour | Grid angle | Dot tone field |
|--------|-----------|------------|----------------|
| A      | `#FF4880` (fluorescent pink) | 45° | `0.5 + 0.42·sin(r/28)` |
| B      | `#00A99D` (teal)             | 75° | same function, 4 px offset |

The grid angles 45° and 75° are the classic halftone screen angles chosen to minimise Moiré
interference between the two screens (the 30° difference between them is the standard separation
used in two-colour offset and screen printing).

### Tone field

Dot radius = `BASE_R × tone(x, y)`, where:

```
tone(x, y) = 0.5 + 0.42 · sin(‖(x,y) − centre‖ / 28)
```

The concentric sine rings produce a tonal gradient that radiates outward, making dots larger or
smaller as the sine oscillates. This creates visible rings of density — lighter at the troughs,
denser at the peaks.

### Misregistration

Screen B is offset from screen A by a slow sinusoidal drift:

```
offsetX = 4 · sin(frame × 0.003)   (max ±4 px)
offsetY = 0.6 × offsetX
```

The animation drifts over roughly 35 seconds per cycle. At rest the screens are offset by ~4 px
(realistic for Riso); the drift exaggerates and then relaxes the misregistration, showing both
the tight-aligned and loosely-misregistered states over time.

## Parameters

| Name   | Value        | Notes                                         |
|--------|-------------|-----------------------------------------------|
| GRID   | 13 px       | dot centre-to-centre spacing                  |
| BASE_R | 6 px        | maximum dot radius (= 46 % of grid — no merge) |
| Angle A | 45°        | pink screen angle                             |
| Angle B | 75°        | teal screen angle (30° separation)            |
| Drift  | ±4 px       | peak misregistration offset                   |
| Period | ~2100 frames | one full drift cycle at 60 fps               |
| Paper  | `#F5F0E8`   | cream / off-white                             |

## Files

- `index.html` — self-contained canvas animation, no external dependencies
- `thumbnail.svg` — static SVG showing the two-screen dot pattern at rest
- `README.md` — this file
