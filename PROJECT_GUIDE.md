# Project Guide — SVD Image Compression

This guide explains the barebones implementation, how to run it, and how to extend it.

## 1. Background

Any matrix `A` (here, a grayscale image) can be decomposed via SVD as `A = U S V^T`. A
rank-`k` approximation keeps the `k` largest singular values and discards the rest:

```
A_k = U[:, :k] * s[:k] @ Vt[:k, :]
```

The image is first converted to grayscale (L = 0.299R + 0.587G + 0.114B), so SVD is
computed once on a single 2-D matrix. Smaller `k` gives stronger compression with more
loss; larger `k` gives higher fidelity.

## 2. Setup

```bash
pip install -r requirements.txt
```

## 3. Layout

| Path | Purpose |
| --- | --- |
| `src/image_utils.py` | `load_image`, `save_image`, `to_grayscale` — I/O helpers (PIL + numpy). |
| `src/svd_compression.py` | `svd_compress(image, k)` — truncated SVD on a grayscale matrix. |
| `src/metrics.py` | `mean_squared_error`, `peak_signal_noise_ratio`, `compression_ratio`, `analysis_table`. |
| `src/visualization.py` | `plot_comparison`, `plot_metric_curves`, `plot_analysis` — Matplotlib figure helpers. |
| `experiments/run_demo.py` | End-to-end demo: grayscale pipeline, multiple ranks, metrics, outputs. |
| `data/sample_images/` | Place input images here. |
| `results/reconstructed/` | Demo output reconstructions. |
| `notebooks/` | For exploratory analysis. |
| `app/` | Placeholder for a future front-end. |

## 4. Running the demo

### Using a real image

```bash
python experiments/run_demo.py --image path/to/image.jpg --ranks 10 25 50
```

This loads the image, converts it to grayscale, computes the SVD, and reconstructs it at
each requested rank. Reconstructed PNGs are written to `results/reconstructed/` alongside
a metrics table (rank, MSE, PSNR, compression ratio) and three Matplotlib figures:

- `comparison.png` — side-by-side original and reconstructions with rank labels.
- `metric_curves.png` — rank vs MSE and rank vs PSNR.
- `analysis.png` — three panels: rank vs compression ratio, rank vs PSNR, rank vs MSE.

### Defaults / fallback

Omitting `--image` makes the demo search `data/sample_images/` for an image, then falls
back to a synthetic gradient-noise image:

```bash
python experiments/run_demo.py              # default ranks: 5 20 50 100
python experiments/run_demo.py --ranks 10 30 80
```

Validations performed:
- `--image` path must exist and be a loadable image.
- Each rank must be a positive integer not exceeding `min(height, width)`.

Expected output: a table of rank vs. MSE / PSNR / compression ratio, plus reconstructed
PNG files in `results/reconstructed/`.

### Choosing rank `k`

- Higher `k` preserves detail but increases size. Typical values: 5–50 for strong
  compression, 100+ for near-lossless.

## 5. Extending

- `matplotlib>=3.7.0` for the comparison and metric-curve figures.
- Add a notebook in `notebooks/` that plots the singular-value spectrum and PSNR vs. `k`.
- Try a per-channel RGB variant by skipping the grayscale conversion.
- Add a front-end under `app/` behind an explicit, opt-in choice of framework.

## 6. Notes / limitations

- Pure-numpy truncated SVD; fine for small/medium images, slow for large ones.
- Operates on a single grayscale matrix (color is reduced to luminance).
- Pure-numpy SVD; for very large images a reduced-rank solver (e.g. `scipy.sparse.svds`)
  would speed things up, but none is added yet.
- The demo falls back to a synthetic image when `data/sample_images/` is empty.
