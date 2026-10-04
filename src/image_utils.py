"""Utilities for loading and saving images as numpy arrays."""

import numpy as np
from PIL import Image


def load_image(path):
    """Load an image file into a float64 array scaled to [0, 1].

    Grayscale images are returned as (H, W); color images are converted to RGB
    and returned as (H, W, 3).
    """
    image = Image.open(path)
    if image.mode in ("1", "L", "I", "F", "I;16"):
        image = image.convert("L")
    else:
        image = image.convert("RGB")
    return np.asarray(image, dtype=np.float64) / 255.0


def save_image(array, path):
    """Save a float array in [0, 1] as an image file."""
    clipped = np.clip(array, 0.0, 1.0)
    scaled = (clipped * 255.0).round().astype(np.uint8)
    Image.fromarray(scaled).save(path)


def to_grayscale(image):
    """Convert an RGB image (H, W, 3) to a grayscale (H, W) array via luminance."""
    if image.ndim == 2:
        return image
    weights = np.array([0.2989, 0.5870, 0.1140], dtype=np.float64)
    return np.tensordot(image, weights, axes=([2], [0]))
