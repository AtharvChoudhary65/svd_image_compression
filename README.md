# SVD Image Compression

A minimal Python project that compresses images using **truncated Singular Value
Decomposition (SVD)**. The image is converted to grayscale and the top-`k` singular
values of the resulting 2-D matrix are kept, yielding a compact approximation that
trades file size against reconstruction quality.

## Project structure

```
data/
  sample_images/        # drop input images here
src/
  __init__.py
  image_utils.py        # load / save / grayscale conversion
  svd_compression.py    # truncated-SVD core (operates on a grayscale matrix)
  metrics.py            # MSE, PSNR, compression ratio, retained energy
experiments/
  run_demo.py           # grayscale demo: compress at several ranks
notebooks/              # Jupyter notebooks (add here)
results/
  reconstructed/        # compressed output images
app/                    # optional front-end (placeholder)
README.md
PROJECT_GUIDE.md
requirements.txt
.gitignore
```

## Requirements

- Python 3.9+
- numpy, pillow

```bash
pip install -r requirements.txt
```

## Usage

From the project root:

```bash
python experiments/run_demo.py
```

This loads an image from `data/sample_images/` (or a small synthetic image when the
folder is empty), converts it to grayscale, compresses it at several rank values,
writes reconstructions to `results/reconstructed/`, and prints MSE / PSNR /
compression ratio / retained energy metrics.

**Retained energy** is the fraction of the total singular-value energy (sum of σ²)
preserved by keeping the top-k singular values. It quantifies how much of the image's
information survives the rank-k truncation, complementing the MSE and PSNR quality
metrics and the compression ratio.

## Notes

This is a barebones educational implementation. It converts the image to grayscale and
applies `numpy.linalg.svd` to the single 2-D matrix; it is not optimized for speed or
memory on large images.
