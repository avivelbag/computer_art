"""
Generate thumbnail.png for Piece 70 — The Signal Disagrees With Itself.

Replicates the JavaScript glitch logic in Python/Pillow/numpy:
1. Draw the concentric-rectangle base image.
2. Apply scanline row displacement at a fixed glitch intensity of 0.7.
3. Apply RGB channel split (chromatic aberration).
4. Apply one block-copy strip for visual interest.
5. Save as 400×400 PNG.
"""

import random
import numpy as np
from PIL import Image, ImageDraw

W, H = 400, 400
INTENSITY = 0.7

COLORS = [
    (230, 57,  70),   # #e63946
    (69,  123, 157),  # #457b9d
    (244, 162, 97),   # #f4a261
    (42,  157, 143),  # #2a9d8f
    (233, 196, 106),  # #e9c46a
    (38,  70,  83),   # #264653
]


def draw_base(w: int, h: int) -> np.ndarray:
    """Return an (H, W, 3) uint8 array with the concentric-rectangle base."""
    img = Image.new("RGB", (w, h), (10, 10, 10))
    draw = ImageDraw.Draw(img)
    rings = 10
    for i in range(rings + 1):
        margin = int((i / rings) * (min(w, h) * 0.48))
        x0, y0 = margin, margin
        x1, y1 = w - margin - 1, h - margin - 1
        color = COLORS[i % len(COLORS)]
        draw.rectangle([x0, y0, x1, y1], fill=color)
    # Horizontal stripe overlay
    for y in range(0, h, 24):
        overlay = Image.new("RGBA", (w, 8), (0, 0, 0, 64))
        img.paste(overlay, (0, y), overlay)
    return np.array(img, dtype=np.uint8)


def apply_glitch(src: np.ndarray, intensity: float, seed: int = 42) -> np.ndarray:
    """
    Apply glitch techniques to src and return the distorted array.

    Parameters
    ----------
    src:       (H, W, 3) uint8 base image.
    intensity: glitch strength in [0, 1].
    seed:      random seed for deterministic thumbnail output.
    """
    rng = random.Random(seed)
    h, w = src.shape[:2]
    dst = np.empty_like(src)

    max_shift = round(intensity * 80)
    chroma = round(intensity * 18)

    # Pre-compute per-row offsets
    row_offsets = np.zeros(h, dtype=np.int32)
    for y in range(h):
        if rng.random() < 0.10 * intensity:
            row_offsets[y] = rng.randint(-max_shift, max_shift)

    # Scanline shift + chromatic aberration
    xs = np.arange(w)
    for y in range(h):
        shift = int(row_offsets[y])
        # Red
        rx = np.clip(xs - chroma - shift, 0, w - 1)
        dst[y, :, 0] = src[y, rx, 0]
        # Green
        gx = np.clip(xs - shift, 0, w - 1)
        dst[y, :, 1] = src[y, gx, 1]
        # Blue
        bx = np.clip(xs + chroma - shift, 0, w - 1)
        dst[y, :, 2] = src[y, bx, 2]

    # Block copy
    src_row  = rng.randint(0, h)
    dest_row = rng.randint(0, h)
    strip_h  = rng.randint(2, 20)
    for dy in range(strip_h):
        sy = min(src_row  + dy, h - 1)
        ry = min(dest_row + dy, h - 1)
        dst[ry] = src[sy]

    return dst


def main():
    base = draw_base(W, H)
    glitched = apply_glitch(base, INTENSITY, seed=42)
    Image.fromarray(glitched).save("thumbnail.png")
    print("Saved thumbnail.png")


if __name__ == "__main__":
    main()
