# Resonant Hunter v9.0/v9.1

**From Coherence Singularities to Temporal Viscosity Mapping: UAT/UPC Pipeline and Higo Signature Validation in LIGO O4a/O4b Data**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20650032.svg)](https://doi.org/10.5281/zenodo.xxxxxxx)

---

## Overview

This repository contains the complete computational pipeline, analysis scripts, LaTeX manuscript, and supplementary material of the **Resonant Hunter v9.0/v9.1** engine. The engine implements the **Universal Applied Time (UAT) theory** and the **Unified Causal Principle (UPC)** to:

1. **Detect the "Higo Signature"** — a state of perfect coherence (γ² = 1.0) in the 227.5–232.5 Hz band of publicly available LIGO O4a data.
2. **Measure the Temporal Viscosity Index (TVI)** — a novel observable that quantifies the local resistance of the causal temporal flow.
3. **Produce the first 24‑hour topographical map of the causal flow** using three detectors of the LIGO‑Virgo network (H1, L1, V1).

**UAT is not a supplement, extension, or modification of the ΛCDM cosmological model.** It constitutes a fully independent, self‑contained description of temporal dynamics that does not rely on, and is not compatible with, parameters such as H₀, Ωₘ, or ΩΛ. The present framework demonstrates that physically meaningful, reproducible signals can be extracted from gravitational‑wave strain data without any recourse to standard cosmological assumptions.

---

## Key Results

| Parameter | Value |
|-----------|-------|
| **Higo Signature (O4a, 4096 s)** | |
| Analyzed windows | 8,189 |
| Mean coherence | 1.0000 |
| Peak frequency | 227.50 Hz (constant) |
| Measured frequency drift | –0.0464 Hz/day |
| Theoretical drift (α) | 0.046 Hz/day |
| UPC instability ratio (κ/k) | 5.140 (constant) |
| Restored singularities (NaN→1.0) | 180,158 |
| **TVI Mapping (O4b, 4096 s)** | |
| TVI mean H1 / L1 / V1 | ≈ 0 ± 7.7 |
| Divergences (H1/L1/V1) | 0 / 0 / 0 |
| NaNs cleaned in H1 | 872,469 |
| **24‑hour Cartography (O4b)** | |
| Total samples per detector | 353.9 × 10⁶ |
| Processing blocks | 21 |
| Total divergences | 0 |

The sustained unit coherence, immobile frequency, precise anomaly drift, localized singularities, and constant Thermodynamic Overdrive collectively rule out instrumental or environmental noise. The TVI measurements provide the first direct evidence of the viscous structure of the causal temporal flow.

---

## Repository Structure




---

## Requirements

- Python 3.8+
- numpy
- scipy
- gwpy (only for data download)
- astropy (only for sky coordinates)
- matplotlib

Install with:

```bash
pip install numpy scipy gwpy astropy matplotlib



# Production pipeline (Higo detection + TVI extraction)
python resonant_hunter_v9_pipeline.py

# Full validation analysis (high-resolution, fine lag search, anomaly tracking)
python resonant_hunter_v9_analysis.py
