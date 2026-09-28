"""Barebones SVD-based image compression on a grayscale matrix."""

import numpy as np


def _svd_rank_k(matrix, k):
    """Return a rank-k reconstruction of a 2-D matrix and its singular values."""
    left, singular_values, right = np.linalg.svd(matrix, full_matrices=False)
    k = min(k, singular_values.shape[0])
    reconstruction = (left[:, :k] * singular_values[:k]) @ right[:k, :]
    return reconstruction, singular_values


def svd_compress(image, k):
    """Compress a grayscale image with truncated SVD keeping the top k singular values.

    The pipeline expects a single 2-D grayscale matrix, i.e. an array produced by
    ``image_utils.to_grayscale``. SVD is computed once on that matrix and a rank-k
    approximation is returned.

    Args:
        image: 2-D float array (H, W) with values in [0, 1].
        k: number of singular values to retain.

    Returns:
        compressed: rank-k reconstruction of ``image``, clipped to [0, 1].
        singular_values: singular values of ``image`` (for analysis).
    """
    compressed, singular_values = _svd_rank_k(image, k)
    return np.clip(compressed, 0.0, 1.0), singular_values
