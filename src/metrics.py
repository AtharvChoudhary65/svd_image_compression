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


def retained_energy(singular_values, k):
    """Return the fraction of total energy retained by the top k singular values.

    Retained energy = sum(sigma_i^2 for i in 1..k) / sum(sigma_i^2 for all i).

    This gives a measure of how much information is preserved by a rank-k
    approximation of the SVD, independent of image dimensions.

    Args:
        singular_values: 1-D array of singular values (typically s from ``np.linalg.svd``).
        k: number of top singular values retained (must be positive and
            not exceed ``len(singular_values)``).

    Returns:
        Float in [0, 1] representing the fraction of total energy retained.
    """
    singular_values = np.asarray(singular_values, dtype=np.float64)
    total = singular_values.shape[-1]
    if k <= 0:
        raise ValueError(f"k must be a positive integer, got {k}.")
    if k > total:
        raise ValueError(f"k ({k}) exceeds the number of singular values ({total}).")
    squared = singular_values ** 2
    return float(np.sum(squared[..., :k]) / np.sum(squared))


def analysis_table(image, ranks, singular_values=None):
    """Compute compression-analysis metrics for each rank.

    Args:
        image: 2-D grayscale or 3-D RGB float array in [0, 1].
        ranks: iterable of positive rank values (already validated).
        singular_values: Optional pre-computed singular values from SVD.
            When provided, these are reused for the retained-energy calculation
            and the rank-k reconstruction is still computed via svd_compress.

    Returns:
        List of dicts with keys ``rank``, ``compression_ratio``, ``mse``,
        ``psnr``, ``retained_energy``, one per rank, preserving order.
    """
    from src.svd_compression import svd_compress

    height, width = image.shape[:2]
    channels = image.shape[2] if image.ndim == 3 else 1

    # Compute singular values once if not provided
    if singular_values is None:
        _, singular_values = svd_compress(image, max(ranks))

    results = []
    for k in ranks:
        compressed, _ = svd_compress(image, k)
        results.append(
            {
                "rank": k,
                "compression_ratio": compression_ratio(height, width, channels, k),
                "mse": mean_squared_error(image, compressed),
                "psnr": peak_signal_noise_ratio(image, compressed),
                "retained_energy": retained_energy(singular_values, k),
            }
        )
    return results
