"""Demo: compress a grayscale image at one or more SVD ranks from the CLI.

Usage:
    python experiments/run_demo.py --image path/to/image.jpg --ranks 10 25 50

Without --image, the demo falls back to a sample image in data/sample_images/
and finally to a synthetic gradient-noise image when the folder is empty.
"""

import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.image_utils import load_image, save_image, to_grayscale
from src.metrics import compression_ratio, mean_squared_error, peak_signal_noise_ratio
from src.svd_compression import svd_compress
from src.visualization import plot_comparison, plot_metric_curves

DEFAULT_RANKS = [5, 20, 50, 100]
SAMPLE_DIR = os.path.join("data", "sample_images")
RESULT_DIR = os.path.join("results", "reconstructed")


def get_sample_image():
    """Return a float64 image array and a label describing its source."""
    if os.path.isdir(SAMPLE_DIR):
        for name in sorted(os.listdir(SAMPLE_DIR)):
            if name.lower().endswith((".png", ".jpg", ".jpeg")):
                return load_image(os.path.join(SAMPLE_DIR, name)), name
    gradient = np.tile(np.linspace(0.0, 1.0, 160), (120, 1))
    noise = np.random.default_rng(0).random((120, 160))
    synthetic = noise * 0.4 + gradient * 0.6
    return np.clip(synthetic, 0.0, 1.0), "synthetic_sample.png"


def parse_args():
    parser = argparse.ArgumentParser(
        description="SVD image compression demo with CLI rank control."
    )
    parser.add_argument(
        "--image",
        type=str,
        default=None,
        help="Path to a real image file to compress. If omitted, falls back to a sample or synthetic image.",
    )
    parser.add_argument(
        "--ranks",
        type=int,
        nargs="+",
        default=DEFAULT_RANKS,
        help="One or more SVD ranks (positive integers) to test. Default: 5 20 50 100.",
    )
    return parser.parse_args()


def validate_ranks(ranks, max_rank):
    valid = []
    for k in ranks:
        if k <= 0:
            raise ValueError(f"Rank must be a positive integer, got {k}.")
        if k > max_rank:
            raise ValueError(
                f"Rank {k} exceeds the maximum valid rank {max_rank} for this image."
            )
        valid.append(k)
    return valid


def main():
    args = parse_args()
    os.makedirs(RESULT_DIR, exist_ok=True)

    if args.image:
        if not os.path.isfile(args.image):
            raise FileNotFoundError(f"Image path does not exist: {args.image}")
        source_name = os.path.basename(args.image)
        image = load_image(args.image)
    else:
        image, source_name = get_sample_image()

    image = to_grayscale(image)
    height, width = image.shape[:2]
    max_rank = min(height, width)
    ranks = validate_ranks(args.ranks, max_rank)
    channels = 1

    save_image(image, os.path.join(RESULT_DIR, "sample_original.png"))

    print(f"Source:      {source_name}")
    print(f"Image shape: {image.shape}")
    print(f"{'Rank':>6} | {'MSE':>10} | {'PSNR(dB)':>10} | {'Ratio':>8}")
    print("-" * 50)

    reconstructions = []
    mses = []
    psnrs = []
    for k in ranks:
        compressed, _ = svd_compress(image, k)
        mse = mean_squared_error(image, compressed)
        psnr = peak_signal_noise_ratio(image, compressed)
        ratio = compression_ratio(height, width, channels, k)
        save_image(compressed, os.path.join(RESULT_DIR, f"reconstructed_k{k}.png"))
        print(f"{k:>6} | {mse:>10.4f} | {psnr:>10.2f} | {ratio:>8.1f}x")
        reconstructions.append(compressed)
        mses.append(mse)
        psnrs.append(psnr)

    plot_comparison(
        image,
        reconstructions,
        ranks,
        os.path.join(RESULT_DIR, "comparison.png"),
    )
    plot_metric_curves(
        ranks,
        mses,
        psnrs,
        os.path.join(RESULT_DIR, "metric_curves.png"),
    )

    print(f"\nReconstructions written to {RESULT_DIR}/")
    print(f"Comparison figure: {os.path.join(RESULT_DIR, 'comparison.png')}")
    print(f"Metric curves:     {os.path.join(RESULT_DIR, 'metric_curves.png')}")


if __name__ == "__main__":
    main()
