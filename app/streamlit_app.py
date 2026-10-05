"""SVD Image Compressor — Streamlit interface.

Run with:
    streamlit run app/streamlit_app.py

UI only. All image processing, SVD and metrics come from the ``src`` package;
styling lives in ``ui_theme.py`` and presentation-only charts in ``ui_charts.py``.
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import streamlit as st
from PIL import Image

from src.image_utils import load_image, save_image
from src.metrics import (
    analysis_table,
    compression_ratio,
    mean_squared_error,
    peak_signal_noise_ratio,
    retained_energy,
)
from src.svd_compression import svd_compress
from src.visualization import (
    plot_analysis,
    plot_comparison,
    plot_error,
    plot_metric_curves,
    plot_rank_vs_quality,
    plot_singular_values,
)

from ui_charts import decomposition_svg, spectrum_figure
from ui_theme import GITHUB_LINK, THEME_OPTIONS, inject_css, section, stat_card

RESULT_DIR = os.path.join("results", "reconstructed")
# Longest side used for the interactive session. Each new rank costs one SVD per
# channel, so very large uploads are downscaled to keep the slider responsive.
MAX_SIDE = 1280

st.set_page_config(page_title="SVD Image Compressor", page_icon="◰", layout="wide")


# --------------------------------------------------------------------------- #
# Helpers (UI plumbing only; the maths is in src/)
# --------------------------------------------------------------------------- #
def fmt_bytes(n):
    """Human-readable file size."""
    n = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024


def box(key, parent=st):
    """Bordered glass container. The key gives CSS a stable hook across versions."""
    try:
        return parent.container(border=True, key=f"box_{key}")
    except TypeError:  # older Streamlit without container keys
        return parent.container(border=True)


def show_image(data, **kwargs):
    """st.image stretched to its container, across Streamlit versions."""
    try:
        st.image(data, width="stretch", clamp=True, **kwargs)
    except TypeError:
        st.image(data, use_container_width=True, clamp=True, **kwargs)


@st.cache_data(show_spinner=False, max_entries=6)
def cached_compress(_image, key, k):
    """Cached wrapper around the existing ``svd_compress``."""
    return svd_compress(_image, k)


@st.cache_data(show_spinner=False, max_entries=4)
def cached_spectrum(_image, key):
    """Singular values for every channel (full SVD, computed once per upload)."""
    return svd_compress(_image, 1)[1]


@st.cache_data(show_spinner=False, max_entries=12)
def encode_image(_array, key, k, ext):
    """Encode an array as PNG/JPEG bytes using the existing ``save_image``."""
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        path = tmp.name
    try:
        save_image(_array, path)
        with open(path, "rb") as handle:
            return handle.read()
    finally:
        os.unlink(path)


def read_upload(uploaded):
    """Load an upload via the existing ``load_image``; return (array, note)."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp.write(uploaded.getbuffer())
        path = tmp.name
    try:
        image = load_image(path)
    finally:
        os.unlink(path)

    note = None
    height, width = image.shape[:2]
    if max(height, width) > MAX_SIDE:
        scale = MAX_SIDE / max(height, width)
        new_size = (max(1, round(width * scale)), max(1, round(height * scale)))
        resized = Image.fromarray((np.clip(image, 0, 1) * 255).round().astype(np.uint8))
        resized = resized.resize(new_size, Image.LANCZOS)
        image = np.asarray(resized, dtype=np.float64) / 255.0
        note = (
            f"Working resolution {new_size[0]}×{new_size[1]} "
            f"(downscaled from {width}×{height}) to keep the slider responsive."
        )
    return image, note


def measure(image, compressed, singular_values, k):
    """Metrics for one rank, using the existing metric functions."""
    height, width = image.shape[:2]
    channels = image.shape[2] if image.ndim == 3 else 1
    return {
        "mse": mean_squared_error(image, compressed),
        "psnr": peak_signal_noise_ratio(image, compressed),
        "ratio": compression_ratio(height, width, channels, k),
        "energy": retained_energy(singular_values, k),
    }


# --------------------------------------------------------------------------- #
# Sections
# --------------------------------------------------------------------------- #
def render_header():
    st.markdown(
        """<div class="hero">
<div class="eyebrow">Linear algebra · Image processing</div>
<h1>SVD IMAGE COMPRESSOR</h1>
<p>Compress images. Explore the mathematics.</p>
<div class="formula">A = U Σ Vᵀ</div>
</div>""",
        unsafe_allow_html=True,
    )


def render_topbar():
    """Top-right controls: appearance switch and GitHub link. Returns the mode."""
    _, theme_col, github_col = st.columns([6.5, 2.6, 1.4], vertical_alignment="center")
    with theme_col:
        if hasattr(st, "segmented_control"):
            mode = st.segmented_control(
                "Appearance", THEME_OPTIONS, default="System",
                key="appearance", label_visibility="collapsed",
            )
        else:  # older Streamlit
            mode = st.radio(
                "Appearance", THEME_OPTIONS, horizontal=True,
                key="appearance", label_visibility="collapsed",
            )
    github_col.markdown(GITHUB_LINK, unsafe_allow_html=True)
    return mode or "System"


def render_rank_panel(max_rank, file_key):
    """Primary interaction. Returns the selected rank."""
    with box("rank"):
        left, right = st.columns([1, 2.6], vertical_alignment="center")
        slider_slot = right.empty()
        k = slider_slot.slider(
            "RANK",
            min_value=1,
            max_value=max_rank,
            value=min(20, max_rank),
            step=1,
            key=f"rank_{file_key}",
            label_visibility="collapsed",
            help="Number of singular values and vectors retained (k).",
        )
        left.markdown(
            f"""<div class="rank-readout">
<div class="caption">Rank</div>
<div class="value"><span>k</span> = {k}</div>
<div class="of">of {max_rank} possible</div>
</div>""",
            unsafe_allow_html=True,
        )
        right.markdown(
            '<div class="hint">Lower rank = smaller representation, but lower '
            "reconstruction quality.</div>",
            unsafe_allow_html=True,
        )
    return k


def render_comparison(image, compressed, k, original_bytes, compressed_bytes):
    left, right = st.columns(2, gap="medium")
    with box("orig", left):
        st.markdown(
            f'<div class="img-head"><span class="tag">Original</span>'
            f'<span class="size">{fmt_bytes(original_bytes)}</span></div>',
            unsafe_allow_html=True,
        )
        show_image(image)
    with box("comp", right):
        st.markdown(
            f'<div class="img-head"><span class="tag">Compressed · rank <b>{k}</b></span>'
            f'<span class="size">{fmt_bytes(compressed_bytes)}</span></div>',
            unsafe_allow_html=True,
        )
        show_image(compressed)


def render_svd_visual(singular_values, k, max_rank, m):
    section(2, "The mathematics")
    with box("math"):
        st.markdown(
            '<div class="math-eq"><span class="dim">A</span> = U Σ Vᵀ'
            '<span class="dim">  →  </span>'
            '<span class="acc">A<sub>k</sub> ≈ U<sub>k</sub> Σ<sub>k</sub> V<sub>k</sub>ᵀ</span></div>'
            f'<div class="math-note">Only the <b>{k}</b> largest singular values and their '
            "vectors are retained; the rest are discarded.</div>",
            unsafe_allow_html=True,
        )
        st.markdown(decomposition_svg(k, max_rank), unsafe_allow_html=True)

    st.write("")
    chart_col, info_col = st.columns([1.7, 1], gap="medium")
    with box("spectrum", chart_col):
        st.markdown('<div class="img-head"><span class="tag">Singular value spectrum</span></div>',
                    unsafe_allow_html=True)
        fig = spectrum_figure(singular_values, k)
        st.pyplot(fig, clear_figure=True)
    with info_col:
        energy_pct = m["energy"] * 100
        st.markdown(
            f"""<div class="chain" style="grid-template-columns:1fr;">
<div class="node"><div class="k">1 · Rank retained</div><div class="v">{k} <small style="color:#8B93A7;font-size:.8rem">/ {max_rank}</small></div>
<div class="bar"><i style="width:{k / max_rank * 100:.2f}%"></i></div></div>
<div class="arrow" style="text-align:center;transform:rotate(90deg);">→</div>
<div class="node"><div class="k">2 · Retained information</div><div class="v">{energy_pct:.2f}%</div>
<div class="bar"><i style="width:{energy_pct:.2f}%"></i></div></div>
<div class="arrow" style="text-align:center;transform:rotate(90deg);">→</div>
<div class="node"><div class="k">3 · Reconstruction quality</div><div class="v">{m['psnr']:.2f} dB</div>
<div class="bar"><i style="width:{min(m['psnr'], 50) / 50 * 100:.1f}%"></i></div></div>
</div>""",
            unsafe_allow_html=True,
        )
    st.markdown(
        '<div class="footnote">Retained information is Σσᵢ² (top k) ÷ Σσᵢ² (all) averaged '
        "over the colour channels' singular values. It is a mathematical measure, not a "
        "perceptual quality score.</div>",
        unsafe_allow_html=True,
    )


def render_metrics(original_bytes, compressed_bytes, m):
    section(3, "Metrics")
    cards = [
        stat_card("Original size", fmt_bytes(original_bytes)),
        stat_card("Compressed size", fmt_bytes(compressed_bytes)),
        stat_card("Compression ratio", f"{m['ratio']:.1f}", "×", highlight=True),
        stat_card("PSNR", f"{m['psnr']:.2f}", "dB", highlight=True),
        stat_card("MSE", f"{m['mse']:.4f}"),
        stat_card("Retained energy", f"{m['energy'] * 100:.1f}", "%"),
    ]
    st.markdown(f'<div class="stat-grid">{"".join(cards)}</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="footnote">Sizes are file sizes, with the reconstruction encoded in the '
        "same format as your upload. Compression ratio counts the numbers stored in Uₖ, Σₖ and Vₖ "
        "versus the full pixel matrix, so it is not a comparison with JPEG/PNG bytes.</div>",
        unsafe_allow_html=True,
    )


def render_explainer():
    section(4, "How SVD compresses")
    st.markdown(
        """<div class="steps">
<div class="step"><div class="n">01 · IMAGE</div><h4>Pixels become a matrix</h4>
<p>Each colour channel is a grid of brightness values.</p><div class="math">A  (H × W)</div></div>
<div class="step"><div class="n">02 · SVD</div><h4>Split into components</h4>
<p>SVD factors A into ranked layers of structure, strongest first.</p><div class="math">A = U Σ Vᵀ</div></div>
<div class="step"><div class="n">03 · TRUNCATE</div><h4>Keep the top k</h4>
<p>Small singular values add little detail, so they are dropped.</p><div class="math">σ₁ ≥ σ₂ ≥ … ≥ σₖ</div></div>
<div class="step"><div class="n">04 · RECONSTRUCT</div><h4>Rebuild the image</h4>
<p>Multiplying the kept parts gives a close, cheaper approximation.</p><div class="math">Aₖ = Uₖ Σₖ Vₖᵀ</div></div>
</div>""",
        unsafe_allow_html=True,
    )


def render_download(compressed, k, file_key, name, compressed_bytes, size_ext):
    section(5, "Download")
    stem = os.path.splitext(name)[0]
    with box("download"):
        st.markdown(
            '<p class="ready">Your compressed image is ready.</p>'
            f'<p class="ready-sub">Rank {k} reconstruction · {size_ext[1:].upper()} {fmt_bytes(compressed_bytes)}</p>',
            unsafe_allow_html=True,
        )
        png_col, jpg_col, _ = st.columns([1, 1, 2])
        png_col.download_button(
            "Download PNG",
            data=encode_image(compressed, file_key, k, ".png"),
            file_name=f"{stem}_rank{k}.png",
            mime="image/png",
            type="primary",
            key="dl_png",
        )
        jpg_col.download_button(
            "Download JPEG",
            data=encode_image(compressed, file_key, k, ".jpg"),
            file_name=f"{stem}_rank{k}.jpg",
            mime="image/jpeg",
            key="dl_jpg",
        )


# --------------------------------------------------------------------------- #
# Additional experiments (previous Compare Ranks / Compression Analysis modes)
# --------------------------------------------------------------------------- #
def tab_compare(image, max_rank, file_key):
    ranks_str = st.text_input("Ranks (comma-separated)", value="10, 25, 50, 100", key="cmp_ranks")
    ranks = sorted(int(r.strip()) for r in ranks_str.split(",") if r.strip().isdigit())
    if not ranks:
        st.warning("Enter at least one valid rank.")
        return
    if any(k <= 0 for k in ranks):
        st.error("All ranks must be positive integers.")
        return
    if any(k > max_rank for k in ranks):
        st.error(f"Rank(s) exceed the maximum valid rank {max_rank} for this image.")
        return

    if st.button("Run comparison", type="primary", key="cmp_run"):
        with st.spinner("Reconstructing…"):
            results = analysis_table(image, ranks, cached_spectrum(image, file_key))
            reconstructions = [cached_compress(image, file_key, k)[0] for k in ranks]
            os.makedirs(RESULT_DIR, exist_ok=True)
            for k, rec in zip(ranks, reconstructions):
                save_image(rec, os.path.join(RESULT_DIR, f"reconstructed_k{k}.png"))
            save_image(image, os.path.join(RESULT_DIR, "sample_original.png"))
            fig_path = os.path.join(RESULT_DIR, "comparison.png")
            plot_comparison(image, reconstructions, ranks, fig_path)

        cols = st.columns(min(len(ranks), 4))
        for i, (k, rec, r) in enumerate(zip(ranks, reconstructions, results)):
            with cols[i % len(cols)]:
                st.markdown(f'<div class="img-head"><span class="tag">Rank <b>{k}</b></span></div>',
                            unsafe_allow_html=True)
                show_image(rec)
                st.caption(
                    f"MSE {r['mse']:.4f} · PSNR {r['psnr']:.2f} dB · "
                    f"{r['compression_ratio']:.1f}× · energy {r['retained_energy'] * 100:.1f}%"
                )
        st.dataframe(results, hide_index=True)
        show_image(fig_path, caption="Side-by-side comparison")


def tab_analysis(image, max_rank, file_key):
    c1, c2, c3 = st.columns(3)
    start_k = c1.number_input("Start rank", 1, max_rank, 5, 1, key="an_start")
    end_k = c2.number_input("End rank", 1, max_rank, min(100, max_rank), 1, key="an_end")
    step = c3.number_input("Step", 1, max_rank, 5, 1, key="an_step")
    if start_k > end_k:
        st.error(f"Start rank ({start_k}) must be less than or equal to end rank ({end_k}).")
        return
    ranks = list(range(int(start_k), int(end_k) + 1, int(step)))
    if not ranks:
        st.warning("No valid ranks in the selected range.")
        return

    if st.button("Run analysis", type="primary", key="an_run"):
        with st.spinner("Sweeping ranks…"):
            singular_values = cached_spectrum(image, file_key)
            results = analysis_table(image, ranks, singular_values)
            os.makedirs(RESULT_DIR, exist_ok=True)
            ratios = [r["compression_ratio"] for r in results]
            mses = [r["mse"] for r in results]
            psnrs = [r["psnr"] for r in results]
            energies = [r["retained_energy"] for r in results]
            paths = {
                "analysis": os.path.join(RESULT_DIR, "analysis.png"),
                "curves": os.path.join(RESULT_DIR, "metric_curves.png"),
                "sv": os.path.join(RESULT_DIR, "singular_values.png"),
                "rq": os.path.join(RESULT_DIR, "rank_vs_quality.png"),
            }
            plot_analysis(ranks, ratios, mses, psnrs, paths["analysis"])
            plot_metric_curves(ranks, mses, psnrs, paths["curves"])
            plot_singular_values(singular_values, paths["sv"])
            plot_rank_vs_quality(ranks, mses, psnrs, energies, ratios, paths["rq"])

        st.markdown("**Analysis table**")
        st.dataframe(results, hide_index=True)
        st.markdown("**Singular value spectrum**")
        show_image(paths["sv"])
        st.markdown("**Rank vs MSE / PSNR / compression ratio**")
        show_image(paths["analysis"])
        st.markdown("**Rank vs quality**")
        show_image(paths["rq"])
        st.caption(
            "As k increases, reconstruction error generally falls while PSNR and retained "
            "energy rise and the compression ratio drops. These are observed relationships "
            "for this image, not guarantees for every image."
        )


def render_experiments(image, max_rank, file_key):
    section(6, "More experiments")
    with box("experiments"):
        tab_cmp, tab_an = st.tabs(["Compare ranks", "Compression analysis"])
        with tab_cmp:
            tab_compare(image, max_rank, file_key)
        with tab_an:
            tab_analysis(image, max_rank, file_key)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main():
    inject_css(render_topbar())
    render_header()

    uploaded = st.file_uploader(
        "Upload an image",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
        help="JPG or PNG",
    )
    if uploaded is None:
        return

    file_key = f"{uploaded.name}-{uploaded.size}"
    try:
        with st.spinner("Reading image…"):
            image, note = read_upload(uploaded)
    except Exception:
        st.error("That file couldn't be read as an image. Please upload a valid JPG or PNG.")
        return

    max_rank = min(image.shape[:2])

    section(1, "Experiment")
    k = render_rank_panel(max_rank, file_key)
    st.write("")

    with st.spinner(f"Computing rank-{k} reconstruction…"):
        compressed, _ = cached_compress(image, file_key, k)
        singular_values = cached_spectrum(image, file_key)
        metrics = measure(image, compressed, singular_values, k)
        size_ext = ".jpg" if uploaded.name.lower().endswith((".jpg", ".jpeg")) else ".png"
        compressed_bytes = len(encode_image(compressed, file_key, k, size_ext))

    # Keep the saved outputs the previous app wrote on each run.
    os.makedirs(RESULT_DIR, exist_ok=True)
    save_image(image, os.path.join(RESULT_DIR, "sample_original.png"))
    save_image(compressed, os.path.join(RESULT_DIR, f"reconstructed_k{k}.png"))

    render_comparison(image, compressed, k, uploaded.size, compressed_bytes)
    if note:
        st.caption(note)

    with st.expander("Reconstruction error map"):
        error_path = os.path.join(RESULT_DIR, f"error_k{k}.png")
        plot_error(image, compressed, error_path)
        show_image(error_path, caption="Absolute pixel difference |original − reconstructed|")

    render_svd_visual(singular_values, k, max_rank, metrics)
    render_metrics(uploaded.size, compressed_bytes, metrics)
    render_explainer()
    render_download(compressed, k, file_key, uploaded.name, compressed_bytes, size_ext)
    render_experiments(image, max_rank, file_key)


if __name__ == "__main__":
    main()
