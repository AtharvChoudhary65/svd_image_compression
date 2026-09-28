"""Barebones demo: compress a grayscale sample image at several SVD ranks."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.image_utils import load_image, save_image, to_grayscale
from src.metrics import compression_ratio, mean_squared_error, peak_signal_noise_ratio
from src.svd_compression import svd_compress

RANK_VALUES = [5, 20, 50, 100]
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


def main():
    os.makedirs(RESULT_DIR, exist_ok=True)
    image, source_name = get_sample_image()
    image = to_grayscale(image)

    height, width = image.shape[:2]
    channels = 1

    save_image(image, os.path.join(RESULT_DIR, "sample_original.png"))

    print(f"Source:      {source_name}")
    print(f"Image shape: {image.shape}")
    print(f"{'Rank':>6} | {'MSE':>10} | {'PSNR(dB)':>10} | {'Ratio':>8}")
    print("-" * 50)
    for k in RANK_VALUES:
        compressed, _ = svd_compress(image, k)
        mse = mean_squared_error(image, compressed)
        psnr = peak_signal_noise_ratio(image, compressed)
        ratio = compression_ratio(height, width, channels, k)
        save_image(compressed, os.path.join(RESULT_DIR, f"reconstructed_k{k}.png"))
        print(f"{k:>6} | {mse:>10.4f} | {psnr:>10.2f} | {ratio:>8.1f}x")

    print(f"\nReconstructions written to {RESULT_DIR}/")


if __name__ == "__main__":
    main()
