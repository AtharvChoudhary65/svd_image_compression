"""Plotting helpers for SVD image compression comparison."""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


def plot_comparison(original, reconstructions, ranks, path):
    """Save a side-by-side figure comparing the original to rank-k reconstructions.

    Args:
        original: 2-D float array in [0, 1] (grayscale image).
        reconstructions: list of 2-D float arrays matching ``original``.
        ranks: list of rank labels (one per reconstruction).
        path: output file path for the figure.
    """
    n = len(reconstructions) + 1
    fig, axes = plt.subplots(1, n, figsize=(2.5 * n, 3))
    if n == 1:
        axes = [axes]

    axes[0].imshow(original, cmap="gray", vmin=0, vmax=1)
    axes[0].set_title("Original")
    axes[0].axis("off")

    for i, (img, k) in enumerate(zip(reconstructions, ranks)):
        axes[i + 1].imshow(img, cmap="gray", vmin=0, vmax=1)
        axes[i + 1].set_title(f"rank = {k}")
        axes[i + 1].axis("off")

    fig.tight_layout()
    fig.savefig(path, dpi=100)
    plt.close(fig)


def plot_metric_curves(ranks, mses, psnrs, path):
    """Save a two-panel plot: rank vs MSE and rank vs PSNR.

    Args:
        ranks: list of rank values.
        mses: list of MSE values (one per rank).
        psnrs: list of PSNR values (one per rank).
        path: output file path for the figure.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.5))

    ax1.plot(ranks, mses, "o-", color="tab:blue")
    ax1.set_xlabel("Rank")
    ax1.set_ylabel("MSE")
    ax1.set_title("Rank vs MSE")
    ax1.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(path, dpi=100)
    plt.close(fig)


def plot_analysis(ranks, ratios, mses, psnrs, path):
    """Save a three-panel analysis figure: rank vs ratio, rank vs PSNR, rank vs MSE.

    Args:
        ranks: list of rank values.
        ratios: list of compression-ratio values (one per rank).
        mses: list of MSE values (one per rank).
        psnrs: list of PSNR values (one per rank).
        path: output file path for the figure.
    """
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(12, 3.5))

    ax1.plot(ranks, ratios, "o-", color="tab:green")
    ax1.set_xlabel("Rank")
    ax1.set_ylabel("Compression Ratio")
    ax1.set_title("Rank vs Compression Ratio")
    ax1.grid(True, alpha=0.3)

    ax2.plot(ranks, psnrs, "o-", color="tab:orange")
    ax2.set_xlabel("Rank")
    ax2.set_ylabel("PSNR (dB)")
    ax2.set_title("Rank vs PSNR")
    ax2.grid(True, alpha=0.3)

    ax3.plot(ranks, mses, "o-", color="tab:blue")
    ax3.set_xlabel("Rank")
    ax3.set_ylabel("MSE")
    ax3.set_title("Rank vs MSE")
    ax3.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(path, dpi=100)
    plt.close(fig)


def plot_singular_values(singular_values, path):
    """Save a plot of the singular-value spectrum.

    Args:
        singular_values: 1-D array of singular values (descending order).
        path: output file path for the figure.
    """
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.plot(
        range(1, len(singular_values) + 1),
        singular_values,
        "o-",
        markersize=2,
        color="tab:blue",
    )
    ax.set_xlabel("Singular Component")
    ax.set_ylabel("Singular Value")
    ax.set_title("Singular Value Spectrum")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=100)
    plt.close(fig)


def plot_rank_vs_quality(ranks, mses, psnrs, energies, ratios, path):
    """Save a four-panel figure: rank vs MSE, PSNR, retained energy, and ratio.

    Args:
        ranks: list of rank values.
        mses: list of MSE values (one per rank).
        psnrs: list of PSNR values (one per rank).
        energies: list of retained-energy fractions in [0, 1] (one per rank).
        ratios: list of compression-ratio values (one per rank).
        path: output file path for the figure.
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(10, 7))

    ax1.plot(ranks, mses, "o-", color="tab:blue")
    ax1.set_xlabel("Rank")
    ax1.set_ylabel("MSE")
    ax1.set_title("Rank vs MSE")
    ax1.grid(True, alpha=0.3)

    ax2.plot(ranks, psnrs, "o-", color="tab:orange")
    ax2.set_xlabel("Rank")
    ax2.set_ylabel("PSNR (dB)")
    ax2.set_title("Rank vs PSNR")
    ax2.grid(True, alpha=0.3)

    ax3.plot(ranks, [e * 100 for e in energies], "o-", color="tab:green")
    ax3.set_xlabel("Rank")
    ax3.set_ylabel("Retained Energy (%)")
    ax3.set_title("Rank vs Retained Energy")
    ax3.grid(True, alpha=0.3)

    ax4.plot(ranks, ratios, "o-", color="tab:red")
    ax4.set_xlabel("Rank")
    ax4.set_ylabel("Compression Ratio")
    ax4.set_title("Rank vs Compression Ratio")
    ax4.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(path, dpi=100)
    plt.close(fig)


def plot_error(original, reconstructed, path):
    """Save an absolute pixel-difference visualization between two images.

    The pixel-wise absolute difference is normalized to [0, 1] and saved as a
    heatmap where brighter regions indicate larger reconstruction error.

    Args:
        original: 2-D float array in [0, 1] (grayscale image).
        reconstructed: 2-D float array matching ``original``.
        path: output file path for the figure.
    """
    error = np.abs(original - reconstructed)
    max_err = error.max()
    if max_err > 0:
        normalized = error / max_err
    else:
        normalized = error

    fig, ax = plt.subplots(figsize=(6, 4))
    im = ax.imshow(normalized, cmap="hot", vmin=0, vmax=1)
    ax.set_title("Reconstruction Error (|original - reconstructed|)")
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")
    fig.colorbar(im, ax=ax, label="Normalized error")
    fig.tight_layout()
    fig.savefig(path, dpi=100)
    plt.close(fig)


def plot_reconstruction_comparison(original, reconstructions, ranks, path):
    """Save a side-by-side figure comparing the original to rank-k reconstructions.

    Args:
        original: 2-D float array in [0, 1] (grayscale image).
        reconstructions: list of 2-D float arrays matching ``original``.
        ranks: list of rank labels (one per reconstruction).
        path: output file path for the figure.
    """
    n = len(reconstructions) + 1
    fig, axes = plt.subplots(1, n, figsize=(2.5 * n, 3))
    if n == 1:
        axes = [axes]

    axes[0].imshow(original, cmap="gray", vmin=0, vmax=1)
    axes[0].set_title("Original")
    axes[0].axis("off")

    for i, (img, k) in enumerate(zip(reconstructions, ranks)):
        axes[i + 1].imshow(img, cmap="gray", vmin=0, vmax=1)
        axes[i + 1].set_title(f"rank = {k}")
        axes[i + 1].axis("off")

    fig.tight_layout()
    fig.savefig(path, dpi=100)
    plt.close(fig)
