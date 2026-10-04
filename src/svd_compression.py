"""SVD-based compression for grayscale and RGB images."""

import numpy as np


def _svd_rank_k(matrix, k):
    """Return a rank-k reconstruction of a 2-D matrix and its singular values."""
    left, singular_values, right = np.linalg.svd(matrix, full_matrices=False)
    k = min(k, singular_values.shape[0])
    reconstruction = (left[:, :k] * singular_values[:k]) @ right[:k, :]
    return reconstruction, singular_values


def svd_compress(image, k):
    """Compress an image with truncated SVD keeping the top k singular values.

    Grayscale images are decomposed as one matrix. RGB images are decomposed
    independently per channel, using the same rank for each channel.

    Args:
        image: 2-D grayscale or 3-D RGB float array with values in [0, 1].
        k: number of singular values to retain.

    Returns:
        compressed: rank-k reconstruction matching ``image``, clipped to [0, 1].
        singular_values: singular values for each channel (a 1-D array for
            grayscale images or a (channels, components) array for RGB images).
    """
    image = np.asarray(image, dtype=np.float64)
    if image.ndim == 2:
        compressed, singular_values = _svd_rank_k(image, k)
    elif image.ndim == 3 and image.shape[2] == 3:
        channels = [
            _svd_rank_k(image[:, :, channel], k)
            for channel in range(image.shape[2])
        ]
        compressed = np.stack([result[0] for result in channels], axis=2)
        singular_values = np.stack([result[1] for result in channels], axis=0)
    else:
        raise ValueError(
            "image must be a 2-D grayscale array or a 3-D RGB array."
        )
    return np.clip(compressed, 0.0, 1.0), singular_values
