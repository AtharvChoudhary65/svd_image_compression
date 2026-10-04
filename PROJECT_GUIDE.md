# Project Guide — SVD Image Compression

This guide explains the implementation, how to run it, and how to extend it.

## 1. Background

Any matrix `A` (here, a grayscale image or one RGB color channel) can be decomposed via SVD as `A = U Σ Vᵀ`. For color images, this decomposition is performed independently on each RGB channel. A rank-`k` approximation keeps the `k` largest singular values per channel and discards the rest:

```
A_k = U[:, :k] * s[:k] @ Vt[:k, :]
```

Grayscale images use one 2-D matrix; RGB images use three 2-D matrices and recombine their reconstructions as a color image. Smaller `k` gives stronger compression with more loss; larger `k` gives higher fidelity.

## 2. Setup

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## 3. Architecture

| Path | Purpose |
| --- | --- |
| `src/image_utils.py` | `load_image`, `save_image` — image I/O helpers (PIL + numpy). |
| `src/svd_compression.py` | `svd_compress(image, k)` — truncated SVD for grayscale images or RGB channels. |
| `src/metrics.py` | `mean_squared_error`, `peak_signal_noise_ratio`, `compression_ratio`, `retained_energy`, `analysis_table`. |
| `src/visualization.py` | Plotting helpers: comparison figures, metric curves, singular value spectrum, error visualization. |
| `experiments/run_demo.py` | CLI demo: grayscale and RGB pipeline, multiple ranks, metrics, outputs. |
| `app/streamlit_app.py` | Streamlit web interface with three modes. |
| `data/sample_images/` | Place input images here. |
| `results/reconstructed/` | Output images and charts. |
| `notebooks/` | For exploratory analysis. |

## 4. Running the application

### Streamlit interface

```bash
streamlit run app/streamlit_app.py
```

Three modes are available:

1. **Single Reconstruction** — upload an image, choose one rank `k`, view original vs. reconstructed with MSE / PSNR / compression ratio / retained energy / reconstruction error.
2. **Compare Ranks** — upload an image, enter multiple comma-separated ranks, view all reconstructions with a metrics table.
3. **Compression Analysis** — upload an image, sweep a rank range (start/end/step), view the analysis table, singular value spectrum, rank-vs-quality charts, error visualization, and trade-off summary.

### CLI demo

```bash
python experiments/run_demo.py --image path/to/image.jpg --ranks 10 25 50
```

Without `--image`, the demo searches `data/sample_images/` for an image, then falls back to a synthetic gradient-noise image:

```bash
python experiments/run_demo.py              # default ranks: 5 20 50 100
python experiments/run_demo.py --ranks 10 30 80
```

Validations:
- `--image` path must exist and be a loadable image.
- Each rank must be a positive integer not exceeding `min(height, width)`.
- In Compression Analysis: start rank ≤ end rank ≤ maximum valid rank.

## 5. Metrics

| Metric | Formula / Definition |
| --- | --- |
| **MSE** | `mean((original - reconstructed)²)` |
| **PSNR** | `20 × log10(peak / sqrt(MSE))` |
| **Compression Ratio** | `(H × W × C) / (k × (H + W + 1) × C)` |
| **Retained Energy** | `Σ(σᵢ² for i=1..k) / Σ(σᵢ² for all i)` |

## 6. Choosing rank `k`

- Higher `k` preserves detail but reduces compression. Typical values: 5–50 for strong compression, 100+ for near-lossless.
- The ideal rank depends on the desired trade-off between quality and representation size.

## 7. Extensibility

- Add a notebook in `notebooks/` that analyzes the singular-value spectrum or plots PSNR vs. `k`.
- Extend `src/metrics.py` with new quality or compression metrics.
- Add visualization helpers to `src/visualization.py`.

## 8. Notes / limitations

- NumPy SVD is computed on the full matrix; slow for very large images.
- RGB images are compressed independently by channel; grayscale inputs remain grayscale.
- Compression ratio is a representation-based metric, not a comparison against JPEG/PNG file sizes.
- No automatic optimal-rank selection is provided.
