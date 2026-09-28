"""Image quality and compression metrics for SVD compression."""

import numpy as np


def mean_squared_error(original, compressed):
    """Return the pixel-wise mean squared error between two images."""
    return float(np.mean((original - compressed) ** 2))


def peak_signal_noise_ratio(original, compressed, peak=1.0):
    """Return the PSNR in decibels between two images scaled to ``peak``."""
    mse = mean_squared_error(original, compressed)
    if mse <= 0.0:
        return float("inf")
    return float(20.0 * np.log10(peak / np.sqrt(mse)))


def compression_ratio(height, width, channels, k):
    """Return the storage ratio of a truncated-SVD image versus the original."""
    original = height * width * channels
    compressed = k * (height + width + 1) * channels
    return original / compressed
