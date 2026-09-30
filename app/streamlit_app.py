"""Streamlit app for SVD image compression — basic Phase 5A UI.

Run with:
    streamlit run app/streamlit_app.py

Reuses the existing src/ modules for all image processing, SVD, metrics,
and visualization logic.
"""

import os
import sys
import tempfile

# Make src/ importable when running from app/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import streamlit as st
from PIL import Image

from src.image_utils import load_image, to_grayscale
from src.svd_compression import svd_compress
from src.metrics import analysis_table
from src.visualization import plot_comparison, plot_metric_curves, plot_analysis

RESULT_DIR = os.path.join("results", "reconstructed")


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
    k = st.number_input("Rank k", min_value=1, max_value=min(image.shape), value=20)
    if st.button("Run"):
        compressed, _ = svd_compress(image, k)
        results = analysis_table(image, [k])[0]
        st.image([image, compressed], caption=["Original", f"Reconstructed (k={k})"], clamp=True)
        col1, col2 = st.columns(2)
        col1.metric("MSE", f"{results['mse']:.4f}")
        col2.metric("PSNR (dB)", f"{results['psnr']:.2f}")
        st.metric("Compression Ratio", f"{results['compression_ratio']:.1f}x")


def mode_compare(image):
    """Mode 2: Compare multiple ranks."""
    ranks_str = st.text_input("Ranks (comma-separated)", value="10, 25, 50, 100")
    ranks = sorted([int(r.strip()) for r in ranks_str.split(",") if r.strip().isdigit()])
    max_rank = min(image.shape)
    if any(k > max_rank for k in ranks):
        st.error(f"Rank(s) exceed maximum valid rank {max_rank} for this image.")
        return
    if st.button("Run"):
        results = analysis_table(image, ranks)
        reconstructions = []
        for k in ranks:
            compressed, _ = svd_compress(image, k)
            reconstructions.append(compressed)

        os.makedirs(RESULT_DIR, exist_ok=True)
        for k, rec in zip(ranks, reconstructions):
            path = os.path.join(RESULT_DIR, f"reconstructed_k{k}.png")
            from src.image_utils import save_image
            save_image(rec, path)

        st.image(reconstructions, caption=[f"rank={k}" for k in ranks], clamp=True)
        st.markdown("### Metrics")
        st.table(results)
        fig_path = os.path.join(RESULT_DIR, "comparison.png")
        plot_comparison(image, reconstructions, ranks, fig_path)
        st.image(fig_path, caption="Comparison figure")


def mode_analysis(image):
    """Mode 3: Compression analysis over a rank range."""
    max_rank = min(image.shape)
    end_k = st.slider("Max rank", min_value=5, max_value=max_rank, value=min(100, max_rank))
    start_k = st.slider("Min rank", min_value=1, max_value=end_k, value=5)
    step = st.number_input("Step", min_value=1, max_value=end_k, value=5)
    ranks = list(range(start_k, end_k + 1, step))
    if st.button("Run"):
        results = analysis_table(image, ranks)
        st.markdown("### Analysis Table")
        st.table(results)

        os.makedirs(RESULT_DIR, exist_ok=True)
        ratios = [r["compression_ratio"] for r in results]
        mses = [r["mse"] for r in results]
        psnrs = [r["psnr"] for r in results]
        plot_analysis(ranks, ratios, mses, psnrs, os.path.join(RESULT_DIR, "analysis.png"))
        st.image(os.path.join(RESULT_DIR, "analysis.png"), caption="Compression analysis")


def main():
    st.set_page_config(page_title="SVD Image Compression", layout="wide")
    st.title("SVD Image Compression")
    st.markdown("Upload a grayscale or RGB image and explore low-rank SVD reconstruction.")

    image = upload_image()
    if image is None:
        st.info("Upload an image to get started.")
        return

    st.success(f"Image loaded: shape {image.shape}")

    mode = st.selectbox(
        "Mode",
        ["1. Single Reconstruction", "2. Compare Ranks", "3. Compression Analysis"],
    )

    if mode.startswith("1"):
        mode_single(image)
    elif mode.startswith("2"):
        mode_compare(image)
    else:
        mode_analysis(image)


if __name__ == "__main__":
    main()
