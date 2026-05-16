# Wave Harmonics Synthesizer

An interactive Fourier synthesis workbench: eight sine-wave harmonics are drawn individually in the upper panel (each in a distinct hue), and their weighted sum appears live in the lower panel as a bright white waveform. Sliders control the amplitude and phase of each harmonic so you can build square, sawtooth, and triangle waves from scratch, or load a preset and watch the Convergence animation add one harmonic at a time until the familiar Gibbs overshoot appears near every sharp corner.

## How it works

The sum at sample point `i` across `N = 800` points is computed as:

```
sum[i] = Σ  amp_n · sin(2π · n · i/N  −  2π · n · t  +  phase_n)
          n
```

where `t` is a global time offset incremented each animation frame when Ripple mode is active, causing the assembled wave to scroll as if it were a traveling wave.

## What to notice

- **Gibbs overshoot:** load Square then press ▶ Converge — watch the ~9 % spike appear at the step edge and sharpen (but never vanish) as harmonics accumulate.
- **Waveform symmetry:** Triangle wave uses only odd harmonics with alternating signs; its corners are smooth because the coefficients fall as 1/n² instead of 1/n.
- **Pure sine:** zero out harmonics 2–8 to isolate the fundamental — the sum panel becomes identical to the upper-panel H1 wave.
- **Ripple vs. standing wave:** with Ripple off the wave is stationary (a standing pattern); with Ripple on each harmonic scrolls at a speed proportional to its frequency (dispersionless traveling wave).
