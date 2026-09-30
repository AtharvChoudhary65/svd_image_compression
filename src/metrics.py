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


def analysis_table(image, ranks):
    """Compute compression-analysis metrics for each rank.

    Args:
        image: 2-D grayscale float array in [0, 1].
        ranks: iterable of positive rank values (already validated).

    Returns:
        List of dicts with keys ``rank``, ``compression_ratio``, ``mse``,
        ``psnr``, one per rank, preserving order.
    """
    from src.svd_compression import svd_compress

    height, width = image.shape[:2]
    channels = 1
    results = []
    for k in ranks:
        compressed, _ = svd_compress(image, k)
        results.append(
            {
                "rank": k,
                "compression_ratio": compression_ratio(height, width, channels, k),
                "mse": mean_squared_error(image, compressed),
                "psnr": peak_signal_noise_ratio(image, compressed),
            }
        )
    return results
