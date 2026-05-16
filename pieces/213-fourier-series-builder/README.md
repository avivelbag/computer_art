# Fourier Series Builder — Harmonics Summoned One by One

Any periodic signal — no matter how jagged or complex — is secretly a sum of pure sine waves. This builder lets you watch that truth unfold in real time: add harmonics one by one and see the familiar square, sawtooth, and triangle waves emerge from spinning arrows.

## How it Works

The canvas is split into two panels. On the left, each active harmonic is drawn as a **rotating phasor**: an arrow whose length equals the harmonic's amplitude and whose rotation speed equals its frequency. The phasors chain tip-to-tail; the tip of the final arrow traces the output signal.

On the right, that tip position is recorded continuously, scrolling from left to right, forming the time-domain waveform.

## Controls

| Control | Effect |
|---------|--------|
| **H1 – H10** | Toggle individual harmonics on or off |
| **Square** | Load odd harmonics 1,3,5,7,9 with amplitudes 1/n |
| **Sawtooth** | Load all 10 harmonics with amplitudes 1/n, alternating sign |
| **Triangle** | Load odd harmonics with amplitudes 1/n², alternating sign |
| **Reset** | Return to fundamental only (H1) |
| **Speed** | Control the animation rate |
| **ⓘ** | Open the educational side-panel |

## The Three Classic Waveforms

**Square wave** — only odd harmonics with amplitude 1/n:

```
f(x) = 4/π · Σ sin((2k−1)x) / (2k−1),  k = 1, 2, 3, …
```

Only odd harmonics appear because the square wave has half-wave symmetry: f(x+π) = −f(x). Even harmonics would violate that symmetry.

**Sawtooth wave** — all harmonics with amplitude 1/n, alternating signs:

```
f(x) = 2/π · Σ (−1)^(k+1) · sin(kx) / k,  k = 1, 2, 3, …
```

**Triangle wave** — odd harmonics only, amplitudes fall as 1/n²:

```
f(x) = 8/π² · Σ (−1)^k · sin((2k+1)x) / (2k+1)²,  k = 0, 1, 2, …
```

The faster 1/n² decay is why the triangle wave looks smooth compared to the square wave — the higher harmonics barely contribute.

## Gibbs Phenomenon

Try loading the Square preset and toggling harmonics off one by one. Notice the ringing overshoot (~9%) near each vertical edge. That overshoot never disappears — it only narrows as more harmonics are added. This is the **Gibbs phenomenon**: a consequence of approximating a discontinuous function with a finite sum of continuous (sine) functions.

## Why Phasors?

Each harmonic sin(nθ) can be visualized as the imaginary part of a complex exponential e^(inθ) — a point rotating on a unit circle at frequency n. Chaining these rotating vectors (phasors) makes the summation geometrically tangible: the composite waveform is literally drawn by the tip of the last arrow in the chain.

This visualization, used by 3Blue1Brown and countless physics courses, makes Fourier analysis intuitive in a way that algebraic formulas alone cannot.

## Real-World Relevance

Fourier decomposition underlies audio equalization, JPEG and MP3 compression, MRI scanning, radio signal separation, and countless other technologies. The ability to move between a time-domain signal and its frequency-domain representation is one of the most useful skills in signal processing and physics.
