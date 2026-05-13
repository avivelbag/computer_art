# IFS: The Fern That Was Always Equations

An Iterated Function System (IFS) generates a fractal by repeatedly applying one of several affine transforms to a single point, chosen at random according to fixed probabilities — the "chaos game." The Barnsley fern encodes a botanically convincing fern shape in just four transforms: one collapses all points toward the stem, one maps the whole fern onto its largest leaflet (creating self-similarity), and two produce the left and right sub-leaflets. After two million points the fern emerges fully, each transform contributing its own color — emerald, lime, gold, and pearl — weighted by density.

The piece morphs continuously between three presets (fern, tree, spiral) over a 12-second cycle using linear interpolation of all twelve transform coefficients, with slow alpha-decay of the hit-count buffer so the old shape dissolves as the new one accumulates.
