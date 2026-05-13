# The Signal Disagrees With Itself

**Technique:** canvas / ImageData / glitch art / scanline displacement / chromatic aberration / block copy

## What is glitch art?

Glitch art treats digital corruption as a medium. Where most generative art aims for mathematical precision, glitch art deliberately introduces errors — misread memory, misaligned buffers, out-of-sync signals — and elevates them into aesthetic form. The corruptions are not random noise; they are *structured failures* that reveal how the underlying format encodes information.

## Techniques used here

**Scanline row displacement** — each horizontal row of pixels is shifted sideways by an independent random offset. Most rows stay in place; roughly one in ten jumps by up to 80 pixels. This mimics a CRT's horizontal sync losing lock on individual scan lines: the image tears in discrete horizontal bands rather than smearing uniformly.

**Chromatic aberration (RGB channel split)** — the red, green, and blue color channels are read from slightly different horizontal positions. Red shifts left, blue shifts right, green stays centered. This replicates the lateral color fringing produced by imperfect lenses or analog signal crosstalk. Where colors separate, unexpected secondary hues appear at the fringe edges.

**Block copy** — with low probability, a horizontal strip of the image (2–20 rows) is copied from a random source position to a random destination. This simulates a corrupt video frame buffer that re-uses old memory rather than writing new content — the visual signature of a driver writing to the wrong region of VRAM.

## Why a pulse rather than pure chaos?

Constant maximum corruption would make the base image unrecognizable within seconds, reducing the piece to visual noise. The glitch intensity follows sin³(t) over a 7-second cycle — slow and nearly clean at the extremes, peaking in the middle. This ensures the base geometry (concentric rectangles in six saturated colors) is always legible through the distortion. The viewer can track *what is being destroyed* and anticipate its recovery — the glitch becomes dramatic rather than merely chaotic.

## Base image

Ten concentric rectangles in a six-color palette (`#e63946`, `#457b9d`, `#f4a261`, `#2a9d8f`, `#e9c46a`, `#264653`) with a horizontal stripe overlay that amplifies scanline-shift artifacts. The bold, high-contrast geometry ensures the structure reads clearly at all glitch intensities.
