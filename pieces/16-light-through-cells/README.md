# Light Through Cells

A Voronoi diagram rendered on a `<canvas>` element — 25 seed points drift slowly across the frame, and their Voronoi cells shift continuously, creating the impression of light filtering through a stained-glass window whose lead came is always gently settling.

## Voronoi construction

The diagram is computed via **brute-force pixel coloring**: an internal 150 × 150 grid is evaluated every frame. For every pixel the algorithm iterates over all 25 seeds and records the index of the nearest one by squared Euclidean distance. The result fills a flat `Int32Array` (`nearest[]`). This approach avoids the complexity of Fortune's sweep-line algorithm while remaining fast enough for real-time rendering because the 150 × 150 resolution is scaled up 4× to the 600 × 600 display canvas with `imageSmoothingEnabled = false`, giving crisp pixelated cell edges rather than blurred ones.

After the nearest-seed pass, a second pass checks each pixel's four axis-aligned neighbours: if any neighbour belongs to a different cell the pixel is painted with the lead-came colour `#1a1a1a`, otherwise it receives its seed's palette colour.

## Why drifting seeds

Static seeds would produce a fixed diagram that conveys geometry but not life. Drifting seeds give the piece an organic, breathing quality — cell boundaries migrate the way real glass deforms imperceptibly over centuries. Each seed moves at a constant velocity between 0.2 and 0.5 px/frame (at the internal resolution) and bounces elastically off the canvas walls, so the animation loops without ever resetting.

## Palette

Six warm colours drawn from amber, sienna, cream, dark brown, deep teal, and sage green: `#f5c07a`, `#c97d4e`, `#e8dcc8`, `#6b4c3b`, `#2e5c6e`, `#a8c5b5`. Seeds are assigned palette indices round-robin so adjacent cells tend to contrast.

**Technique:** canvas / Voronoi diagram / brute-force pixel coloring  
**Year:** 2026
