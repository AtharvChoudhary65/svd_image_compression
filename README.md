# Image Compression and Reconstruction via Low-Rank SVD Approximation

A Python project that demonstrates how **Singular Value Decomposition (SVD)** can compress a grayscale image by retaining only its most important components. The application reconstructs the image at various ranks, allowing you to explore the trade-off between compression and reconstruction quality.

## Features

- **Grayscale SVD compression** using NumPy's `numpy.linalg.svd`
- **Streamlit web interface** with three interactive modes
- **CLI demo** for batch experimentation
- **Quality metrics**: MSE, PSNR, compression ratio, retained energy
- **Visualizations**: reconstruction comparison, singular value spectrum, rank-vs-quality analysis, error visualization

## How It Works

```
Input Image
    ↓
Grayscale Conversion
    ↓
Image → Matrix
    ↓
Singular Value Decomposition (A = UΣVᵀ)
    ↓
Select Rank k
    ↓
Low-Rank Approximation (Aₖ ≈ UₖΣₖVₖᵀ)
    ↓
Reconstructed Image
    ↓
Quality + Compression Metrics
```

### Mathematical background

A grayscale image is represented as a 2-D matrix **A**. SVD decomposes it into:

```
A = U Σ Vᵀ
```

where **U** and **V** contain the left and right singular vectors, and **Σ** is a diagonal matrix of singular values (ordered from largest to smallest).

A rank-`k` approximation keeps only the top `k` singular values and their corresponding vectors:

```
Aₖ ≈ Uₖ Σₖ Vₖᵀ
```

The parameter `k` controls the trade-off: smaller `k` gives stronger compression but more information loss; larger `k` preserves more detail but provides less compression.

## Why SVD Works for Image Compression

- **Singular values are ordered by importance**: the largest singular values capture the strongest structure in the image.
- **Low-rank approximation** discards smaller singular values, reducing storage while incurring minimal perceptual loss.
- **Compact representation**: a rank-`k` matrix can be stored using only `k × (height + width + 1)` values instead of `height × width`.

No single rank is universally optimal — the appropriate choice depends on your quality and compression requirements.

## Metrics

| Metric | Meaning | Interpretation |
| --- | --- | --- |
| **MSE** | Mean Squared Error | Lower generally means less reconstruction error |
| **PSNR** | Peak Signal-to-Noise Ratio (dB) | Higher generally indicates lower reconstruction error |
| **Compression Ratio** | Representation size comparison | Higher means more compression under this project's model |
| **Retained Energy** | Fraction of total singular-value energy (Σσ²) preserved | Higher means more SVD energy is retained |

**Retained Energy:**

```
Retained Energy = Σ(σᵢ² for i=1..k) / Σ(σᵢ² for all i)
```

This measures how much of the image's mathematical information (as defined by the singular values) is preserved by a rank-`k` approximation. It is not a perceptual quality score.

## Streamlit Application

The application provides three workflows. Launch with:

```bash
streamlit run app/streamlit_app.py
```

### Single Reconstruction

Upload an image, choose one rank `k`, and inspect the original vs. reconstructed image along with MSE, PSNR, compression ratio, retained energy, and reconstruction error.

### Compare Ranks

Upload an image and enter multiple comma-separated ranks (e.g., `10, 25, 50`). View all reconstructions side-by-side with their metrics.

### Compression Analysis

Upload an image and sweep a range of ranks (start, end, step). View:

- Analysis table with all metrics
- Singular value spectrum
- Rank-vs-quality charts (MSE, PSNR, retained energy, compression ratio)
- Reconstruction error visualization
- Trade-off summary

## CLI Demo

Run the command-line demo:

```bash
python experiments/run_demo.py --image data/sample_images/your_image.jpg --ranks 10 25 50
```

Without `--image`, the demo falls back to a synthetic gradient image if no image is placed in `data/sample_images/`.

Reconstructed images and charts are saved to `results/reconstructed/`.

## Installation

```bash
git clone <repository-url>
cd svd_image_compression

python -m venv .venv
```

### Linux / macOS

```bash
source .venv/bin/activate
```

### Windows

```bash
.venv\Scripts\activate
```

Then install dependencies:

```bash
pip install -r requirements.txt
```

## Project Structure

```
svd_image_compression/
├── app/
│   └── streamlit_app.py      # Web interface (Streamlit)
├── data/
│   └── sample_images/        # Place your input images here
├── experiments/
│   └── run_demo.py           # CLI demonstration
├── notebooks/                # Exploratory analysis (add here)
├── results/
│   └── reconstructed/        # Output images and charts
├── src/
│   ├── image_utils.py        # Image loading, saving, grayscale conversion
│   ├── svd_compression.py    # Truncated SVD core
│   ├── metrics.py            # MSE, PSNR, compression ratio, retained energy
│   └── visualization.py      # Matplotlib plotting helpers
├── requirements.txt
├── PROJECT_GUIDE.md
└── README.md
```

## Technical Implementation

- **NumPy**: `numpy.linalg.svd` for the singular value decomposition
- **Pillow (PIL)**: image loading and saving
- **Matplotlib**: chart and figure generation (singular value spectrum, rank-vs-quality plots, reconstruction comparisons)
- **Streamlit**: web interface for interactive exploration

The project is organized into clear modules under `src/`, keeping image handling, compression logic, metrics, and visualization separate from the application layer.

## Example Interpretation

| Rank | Effect |
| --- | --- |
| **Low k** | Fewer singular components → stronger compression → generally more reconstruction error |
| **High k** | More singular components → weaker compression → generally better reconstruction fidelity |

The appropriate rank depends on the desired trade-off between image quality and storage efficiency.

## Limitations

- The current implementation operates on grayscale images (color images are reduced to luminance).
- Pure NumPy SVD is computed on the full matrix; this can be slow for very large images.
- The compression ratio is a representation-based metric (storage of `Uₖ`, `Σₖ`, `Vₖᵀ`), not a comparison against JPEG/PNG file sizes.
- No automatic optimal-rank selection is provided.
- This is an educational project, not a production image codec.

## License

This project is released for educational purposes. See the repository for license details.
