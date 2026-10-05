"""Presentation-only visuals for the SVD explorer.

Everything here draws from values that the existing ``src`` modules already
computed (singular values, retained energy). Nothing re-implements the SVD.
"""

import sys
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.metrics import retained_energy

from ui_theme import COLORS


def _mean_spectrum(singular_values):
    """Average per-channel singular values into one 1-D curve for display."""
    sv = np.asarray(singular_values, dtype=np.float64)
    return sv if sv.ndim == 1 else sv.mean(axis=0)


def spectrum_figure(singular_values, k):
    """Singular-value spectrum with the retained range highlighted.

    Left axis: singular values (log). Right axis: retained energy, sampled
    with the existing ``retained_energy`` function.
    """
    spectrum = _mean_spectrum(singular_values)
    n = len(spectrum)
    k = min(k, n)
    x = np.arange(1, n + 1)

    fig, ax = plt.subplots(figsize=(8, 3.6))
    ax.set_yscale("log")
    ax.plot(x, spectrum, color=COLORS["muted"], linewidth=1.4, zorder=2)
    ax.fill_between(x[:k], spectrum[:k], spectrum.min() * 0.6,
                    color=COLORS["accent"], alpha=0.35, zorder=1)
    ax.plot(x[:k], spectrum[:k], color=COLORS["accent"], linewidth=2.2, zorder=3)
    ax.axvline(k, color=COLORS["accent"], linestyle="--", linewidth=1, alpha=0.9)
    ax.scatter([k], [spectrum[k - 1]], color="#ffffff", s=36, zorder=4,
               edgecolor=COLORS["accent"], linewidth=2)
    ax.annotate(f"k = {k}", (k, spectrum[k - 1]), xytext=(10, 12),
                textcoords="offset points", color=COLORS["text"], fontsize=10,
                family="monospace")
    ax.set_xlabel("Singular value index")
    ax.set_ylabel("Singular value (log)")
    ax.set_xlim(1, n)
    ax.grid(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)

    # Retained energy, reusing the project's own metric on a sampled grid.
    sample = np.unique(np.clip(np.geomspace(1, n, 60).astype(int), 1, n))
    energy = [retained_energy(singular_values, int(i)) * 100 for i in sample]
    ax2 = ax.twinx()
    ax2.plot(sample, energy, color="#ffffff", linewidth=1, alpha=0.45, linestyle=":")
    ax2.set_ylim(0, 102)
    ax2.set_ylabel("Retained energy (%)")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_color(COLORS["faint"])
    fig.tight_layout()
    return fig


def decomposition_svg(k, max_k):
    """Inline SVG of A = U S V^T with the retained k components highlighted."""
    frac = max(0.0, min(1.0, k / max_k))
    acc, dim = COLORS["accent"], "rgba(255,255,255,0.07)"
    edge = "rgba(255,255,255,0.18)"

    # Geometry (viewBox 760 x 190)
    s = 130          # block height
    top = 30
    uw, sw, vw = 96, 130, 260   # widths for U, Sigma, V^T
    xa, xu, xs, xv = 10, 250, 400, 560

    ret_u = max(5, uw * frac)
    ret_s = max(5, sw * frac)
    ret_vt = max(5, s * frac)

    parts = []

    def label(x, w, text, y=top + s + 24):
        parts.append(
            f'<text x="{x + w / 2}" y="{y}" fill="{COLORS["muted"]}" '
            f'font-family="DM Mono, monospace" font-size="13" text-anchor="middle">{text}</text>'
        )

    def op(x, text):
        parts.append(
            f'<text x="{x}" y="{top + s / 2 + 8}" fill="{COLORS["faint"]}" '
            f'font-family="DM Mono, monospace" font-size="24" text-anchor="middle">{text}</text>'
        )

    # A (full image matrix)
    parts.append(f'<rect x="{xa}" y="{top}" width="{s}" height="{s}" rx="6" fill="{dim}" stroke="{edge}"/>')
    label(xa, s, "A  (image)")
    op(xa + s + 55 / 2 + 5, "=")

    # U: tall; leftmost k columns retained
    parts.append(f'<rect x="{xu}" y="{top}" width="{uw}" height="{s}" rx="6" fill="{dim}" stroke="{edge}"/>')
    parts.append(f'<rect x="{xu}" y="{top}" width="{ret_u}" height="{s}" rx="6" fill="{acc}" opacity="0.85"/>')
    label(xu, uw, "U")

    # Sigma: diagonal; first k entries retained
    parts.append(f'<rect x="{xs}" y="{top}" width="{sw}" height="{s}" rx="6" fill="{dim}" stroke="{edge}"/>')
    parts.append(f'<rect x="{xs}" y="{top}" width="{ret_s}" height="{ret_s * s / sw}" rx="4" fill="{acc}" opacity="0.18"/>')
    steps = 12
    for i in range(steps):
        d = i * (sw / steps)
        on = d < ret_s
        parts.append(
            f'<rect x="{xs + d + 3}" y="{top + d * s / sw + 3}" width="{sw / steps - 4}" '
            f'height="{s / steps - 4}" rx="2" fill="{acc if on else "rgba(255,255,255,0.22)"}"/>'
        )
    label(xs, sw, "Σ")

    # V^T: wide; top k rows retained
    vh = s
    parts.append(f'<rect x="{xv}" y="{top + (s - vh) / 2}" width="{vw}" height="{vh}" rx="6" fill="{dim}" stroke="{edge}"/>')
    parts.append(f'<rect x="{xv}" y="{top}" width="{vw}" height="{ret_vt}" rx="6" fill="{acc}" opacity="0.85"/>')
    label(xv, vw, "Vᵀ")

    svg = (
        '<div class="svg-wrap"><svg viewBox="0 0 840 190" xmlns="http://www.w3.org/2000/svg" role="img" '
        'aria-label="Decomposition of A into U, Sigma and V transpose with the top k components highlighted">'
        + "".join(parts)
        + "</svg></div>"
    )
    return svg
