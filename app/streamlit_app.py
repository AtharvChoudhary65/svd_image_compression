"""Streamlit app for SVD image compression — basic Phase 5A-style interface.

Run with:
    streamlit run app/streamlit_app.py

Reuses the existing src/ modules for all image processing, SVD, metrics,
and visualization logic.
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import streamlit as st

from src.image_utils import load_image, save_image, to_grayscale
from src.svd_compression import svd_compress
from src.metrics import analysis_table
from src.visualization import plot_comparison, plot_metric_curves, plot_analysis, plot_singular_values

RESULT_DIR = os.path.join("results", "reconstructed")

st.set_page_config(page_title="SVD Image Compression", layout="wide")

# Reusable explanation block shown near rank controls
RANK_EXPLANATION = (
    "*Rank k is the number of singular components retained in the "
    "low-rank approximation.*"
)


def upload_image():
    """Return a grayscale float64 array from a Streamlit upload, or None."""
    uploaded = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded is None:
        return None
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp.write(uploaded.getbuffer())
        tmp_path = tmp.name
    try:
        image = load_image(tmp_path)
    finally:
        os.unlink(tmp_path)
    return to_grayscale(image)


def mode_single(image):
    """Mode 1: Single rank reconstruction."""
    max_k = min(image.shape)
    st.markdown(RANK_EXPLANATION)
    st.markdown(f"*Maximum valid rank: {max_k}*")
    st.markdown("The image matrix **A** is approximated as **A ≈ Uₖ Σₖ Vₖᵀ**, "
                "using only the first k singular components.")
    k = st.number_input("Rank k", min_value=1, max_value=max_k, value=20)
    if st.button("Run Reconstruction", type="primary"):
        compressed, _ = svd_compress(image, k)
        results = analysis_table(image, [k])[0]

        st.image(
            [image, compressed],
            caption=["ORIGINAL", f"RECONSTRUCTED · RANK {k}"],
            clamp=True,
        )

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("MSE", f"{results['mse']:.4f}")
        col2.metric("PSNR (dB)", f"{results['psnr']:.2f}")
        col3.metric("Compression Ratio", f"{results['compression_ratio']:.1f}x")
        col4.metric("Retained Energy", f"{results['retained_energy']*100:.1f}%")

        save_image(image, os.path.join(RESULT_DIR, "sample_original.png"))
        save_image(compressed, os.path.join(RESULT_DIR, f"reconstructed_k{k}.png"))


def mode_compare(image):
    """Mode 2: Compare multiple ranks."""
    max_rank = min(image.shape)
    st.markdown(RANK_EXPLANATION)
    st.markdown(f"*Maximum valid rank: {max_rank}*")
    st.markdown("Each reconstruction uses **A ≈ Uₖ Σₖ Vₖᵀ** with k singular components.")
    ranks_str = st.text_input("Ranks (comma-separated)", value="10, 25, 50, 100")
    ranks = sorted(
        [int(r.strip()) for r in ranks_str.split(",") if r.strip().isdigit()]
    )
    if not ranks:
        st.warning("Enter at least one valid rank.")
        return
    if any(k > max_rank for k in ranks):
        st.error(f"Rank(s) exceed maximum valid rank {max_rank} for this image.")
        return
    if any(k <= 0 for k in ranks):
        st.error("All ranks must be positive integers.")
        return

    if st.button("Run Comparison", type="primary"):
        results = analysis_table(image, ranks)
        reconstructions = [svd_compress(image, k)[0] for k in ranks]

        os.makedirs(RESULT_DIR, exist_ok=True)
        for k, rec in zip(ranks, reconstructions):
            save_image(rec, os.path.join(RESULT_DIR, f"reconstructed_k{k}.png"))
        save_image(image, os.path.join(RESULT_DIR, "sample_original.png"))

        cols = st.columns(len(ranks))
        for i, (k, rec, r) in enumerate(zip(ranks, reconstructions, results)):
            with cols[i]:
                st.markdown(f"**RANK {k}**")
                st.image(rec, clamp=True, use_container_width=True)
                st.caption(f"MSE: {r['mse']:.4f}")
                st.caption(f"PSNR: {r['psnr']:.2f} dB")
                st.caption(f"Ratio: {r['compression_ratio']:.1f}×")
                st.caption(f"Energy: {r['retained_energy']*100:.1f}%")

        st.markdown("### Metrics")
        st.table(results)

        fig_path = os.path.join(RESULT_DIR, "comparison.png")
        plot_comparison(image, reconstructions, ranks, fig_path)
        st.image(fig_path, caption="Side-by-side comparison")


def mode_analysis(image):
    """Mode 3: Compression analysis over a rank range."""
    max_rank = min(image.shape)
    st.markdown(RANK_EXPLANATION)
    st.markdown(f"*Maximum valid rank: {max_rank}*")
    st.markdown("The image matrix **A** is approximated as **A ≈ Uₖ Σₖ Vₖᵀ**, "
                "retaining only the first k singular components from the full SVD "
                "**A = U Σ Vᵀ**.")
    start_k = st.number_input("Start Rank", min_value=1, max_value=max_rank, value=5, step=1)
    end_k = st.number_input("End Rank", min_value=1, max_value=max_rank, value=min(100, max_rank), step=1)
    step = st.number_input("Step", min_value=1, max_value=max_rank, value=5, step=1)

    if start_k > end_k:
        st.error(f"Start rank ({start_k}) must be less than or equal to end rank ({end_k}).")
        return

    if end_k > max_rank:
        st.error(
            f"End rank ({end_k}) exceeds the maximum valid rank "
            f"({max_rank}) for this image."
        )
        return

    ranks = list(range(start_k, end_k + 1, step))
    if not ranks:
        st.warning("No valid ranks in the selected range.")
        return

    if st.button("Run Analysis", type="primary"):
        # Compute singular values once; reuse for both metrics and plot
        max_k_for_svd = max(ranks)
        _, singular_values = svd_compress(image, max_k_for_svd)
        results = analysis_table(image, ranks, singular_values)

        os.makedirs(RESULT_DIR, exist_ok=True)
        ratios = [r["compression_ratio"] for r in results]
        mses = [r["mse"] for r in results]
        psnrs = [r["psnr"] for r in results]
        fig_path = os.path.join(RESULT_DIR, "analysis.png")
        plot_analysis(ranks, ratios, mses, psnrs, fig_path)
        plot_metric_curves(ranks, mses, psnrs, os.path.join(RESULT_DIR, "metric_curves.png"))
        sv_path = os.path.join(RESULT_DIR, "singular_values.png")
        plot_singular_values(singular_values, sv_path)

        st.markdown("### Singular Value Spectrum")
        st.markdown(
            "<small>Singular values are ordered from largest to smallest. "
            "Large values indicate components that contribute more strongly to the image "
            "representation. Keeping only the first k components uses the largest singular "
            "values and discards the remaining components. Retained energy measures the "
            "fraction of total squared singular-value energy captured by the first k "
            "components.</small>",
            unsafe_allow_html=True,
        )
        st.image(sv_path, caption="Singular value spectrum")

        st.markdown("### Analysis Table")
        st.dataframe(results, use_container_width=True, hide_index=True)

        st.markdown("### Rank vs MSE / PSNR / Compression Ratio")
        st.image(fig_path, caption="Compression analysis figure")

        st.markdown(
            "<small>Increasing k retains more singular components, which generally "
            "improves reconstruction quality and retained energy, while reducing the "
            "compression ratio.</small>",
            unsafe_allow_html=True,
        )


def main():
    st.title("SVD Image Compression")
    st.markdown("Upload an image and explore low-rank SVD reconstruction.")

    image = upload_image()
    if image is None:
        st.info("Upload an image to get started.")
        return

    mode = st.selectbox(
        "Select mode",
        ["Single Reconstruction", "Compare Ranks", "Compression Analysis"],
    )

    if mode == "Single Reconstruction":
        mode_single(image)
    elif mode == "Compare Ranks":
        mode_compare(image)
    else:
        mode_analysis(image)


if __name__ == "__main__":
    main()
