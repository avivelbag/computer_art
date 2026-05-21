#!/usr/bin/env python3
"""Generate thumbnail.svg for Piece 267 — Differential Growth: Coral Maze.

Computes a sinusoidally-perturbed closed curve that approximates the mature
state of the differential-growth simulation and writes it as a static SVG.
Uses only the Python standard library.
"""
import math
import pathlib

W, H = 400, 400
CX, CY = W // 2, H // 2


def make_path(n_pts: int = 200) -> str:
    """Return SVG path data for a crinkled closed curve.

    Layers four sinusoidal perturbations at incommensurable frequencies to
    approximate the dense, coral-like folds produced by the simulation.

    Args:
        n_pts: Number of polygon vertices (higher = smoother curve).

    Returns:
        SVG path data string beginning with 'M' and ending with 'Z'.
    """
    parts = []
    R = 140
    for i in range(n_pts):
        t = 2 * math.pi * i / n_pts
        r = (R
             + 28 * math.sin(5  * t + 0.30)
             + 16 * math.sin(9  * t + 1.10)
             + 9  * math.sin(14 * t + 2.40)
             + 5  * math.sin(21 * t + 0.70))
        x = CX + r * math.cos(t)
        y = CY + r * math.sin(t)
        cmd = 'M' if i == 0 else 'L'
        parts.append(f'{cmd}{x:.2f},{y:.2f}')
    parts.append('Z')
    return ' '.join(parts)


def make_svg() -> str:
    """Assemble and return the full SVG markup for the thumbnail."""
    path_d = make_path()
    return f"""<svg width="400" height="400" viewBox="0 0 400 400"
     xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="bg" cx="50%" cy="50%" r="65%">
      <stop offset="0%"   stop-color="#0a1a24"/>
      <stop offset="100%" stop-color="#050d14"/>
    </radialGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="2.5" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <rect width="400" height="400" fill="url(#bg)"/>

  <path d="{path_d}"
        fill="rgba(0,80,60,0.18)"
        stroke="#00d4aa"
        stroke-width="4"
        stroke-opacity="0.22"
        filter="url(#glow)"/>

  <path d="{path_d}"
        fill="rgba(0,75,60,0.25)"
        stroke="#00c8a0"
        stroke-width="1.3"/>
</svg>"""


if __name__ == '__main__':
    out = pathlib.Path(__file__).parent / 'thumbnail.svg'
    out.write_text(make_svg())
    print(f'Written {out}')
