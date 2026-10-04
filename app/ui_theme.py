"""Visual system for the SVD Image Compressor Streamlit app.

All colors, type, spacing and component styles live here as CSS tokens so the
look can be changed without touching application logic. No image-processing
or SVD code belongs in this module.
"""

import matplotlib
import streamlit as st

# ---- Design tokens ---------------------------------------------------------
COLORS = {
    "bg": "#08090D",
    "surface": "#0D0F15",
    "text": "#E9ECF4",
    "muted": "#8B93A7",
    "faint": "#4A5062",
    "accent": "#6C7DFF",
    "accent_soft": "rgba(108,125,255,0.16)",
    "border": "rgba(255,255,255,0.09)",
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  --bg: #08090D;
  --surface: #0D0F15;
  --panel: rgba(255,255,255,0.035);
  --panel-strong: rgba(255,255,255,0.06);
  --border: rgba(255,255,255,0.09);
  --text: #E9ECF4;
  --muted: #8B93A7;
  --faint: #4A5062;
  --accent: #6C7DFF;
  --accent-soft: rgba(108,125,255,0.16);
  --radius: 14px;
  --gap: 24px;
  --mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
  --sans: 'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif;
}

/* ---- Page shell ---- */
.stApp {
  background:
    radial-gradient(900px 420px at 50% -8%, rgba(108,125,255,0.10), transparent 65%),
    var(--bg);
  font-family: var(--sans);
  color: var(--text);
}
html, body, [class*="css"] { font-family: var(--sans); }
#MainMenu, footer, [data-testid="stDecoration"], [data-testid="stStatusWidget"] { display: none !important; }
[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 1180px; padding: 2.5rem 1.5rem 5rem; }
h1, h2, h3, h4 { font-family: var(--sans); letter-spacing: -0.01em; }

/* ---- Hero ---- */
.hero { text-align: center; padding: 1.5rem 0 2rem; }
.hero .eyebrow {
  font-family: var(--mono); font-size: 0.72rem; letter-spacing: 0.28em;
  color: var(--accent); text-transform: uppercase; margin-bottom: 0.9rem;
}
.hero h1 {
  font-size: clamp(2rem, 5vw, 3.4rem); font-weight: 700; margin: 0;
  letter-spacing: 0.02em; line-height: 1.1; padding: 0;
}
.hero p { color: var(--muted); font-size: 1.05rem; margin: 0.9rem 0 0; }
.hero .formula {
  font-family: var(--mono); color: var(--faint); font-size: 0.85rem; margin-top: 1.4rem;
}

/* ---- Section headings ---- */
.section-label {
  font-family: var(--mono); font-size: 0.72rem; letter-spacing: 0.22em;
  color: var(--muted); text-transform: uppercase; margin: 3rem 0 1rem;
  display: flex; align-items: center; gap: 0.9rem;
}
.section-label::after { content: ""; flex: 1; height: 1px; background: var(--border); }
.section-label .idx { color: var(--accent); }

/* ---- Glass panels ---- */
.glass {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  box-shadow: 0 10px 40px rgba(0,0,0,0.35);
  padding: 1.4rem 1.5rem;
}
[data-testid="stVerticalBlockBorderWrapper"] {
  background: var(--panel);
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  box-shadow: 0 10px 40px rgba(0,0,0,0.35);
}

/* ---- Upload ---- */
[data-testid="stFileUploader"] label { display: none; }
[data-testid="stFileUploaderDropzone"] {
  background: var(--panel);
  border: 1.5px dashed rgba(108,125,255,0.45);
  border-radius: var(--radius);
  padding: 3.2rem 1.5rem;
  justify-content: center;
  transition: border-color .2s ease, background .2s ease, box-shadow .2s ease;
}
[data-testid="stFileUploaderDropzone"]:hover {
  border-color: var(--accent);
  background: var(--accent-soft);
  box-shadow: 0 0 0 4px rgba(108,125,255,0.08);
}
[data-testid="stFileUploaderDropzone"] button {
  background: transparent; color: var(--text);
  border: 1px solid var(--border); border-radius: 8px;
}
[data-testid="stFileUploaderDropzone"] button:hover { border-color: var(--accent); color: var(--accent); }
[data-testid="stFileUploaderFile"] { background: var(--panel); border-radius: 10px; }

/* ---- Rank readout ---- */
.rank-readout { font-family: var(--mono); line-height: 1; }
.rank-readout .caption { font-size: 0.7rem; letter-spacing: 0.22em; color: var(--muted); text-transform: uppercase; }
.rank-readout .value { font-size: clamp(2.6rem, 6vw, 4rem); font-weight: 600; color: var(--text); margin-top: 0.5rem; }
.rank-readout .value span { color: var(--accent); }
.rank-readout .of { font-size: 0.8rem; color: var(--faint); margin-top: 0.5rem; }
.hint { color: var(--muted); font-size: 0.92rem; margin-top: 0.4rem; }

/* ---- Slider ---- */
[data-testid="stSlider"] { padding-top: 0.4rem; }
[data-testid="stSlider"] [data-baseweb="slider"] > div > div { height: 6px; border-radius: 6px; }
[data-testid="stSliderThumbValue"] { font-family: var(--mono); color: var(--accent); }

/* ---- Image cards ---- */
.img-head { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.7rem; }
.img-head .tag { font-family: var(--mono); font-size: 0.72rem; letter-spacing: 0.2em; color: var(--muted); text-transform: uppercase; }
.img-head .tag b { color: var(--accent); font-weight: 600; }
.img-head .size { font-family: var(--mono); font-size: 0.9rem; color: var(--text); }
[data-testid="stImage"] img { border-radius: 10px; }

/* ---- Stats ---- */
.stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 14px; }
.stat {
  background: var(--panel); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 1.1rem 1.2rem; backdrop-filter: blur(14px);
}
.stat .k { font-family: var(--mono); font-size: 0.68rem; letter-spacing: 0.18em; color: var(--muted); text-transform: uppercase; }
.stat .v { font-family: var(--mono); font-size: 1.7rem; font-weight: 500; margin-top: 0.55rem; color: var(--text); }
.stat .v small { font-size: 0.85rem; color: var(--muted); margin-left: 0.25rem; }
.stat.hi { border-color: rgba(108,125,255,0.45); background: var(--accent-soft); }
.stat.hi .v { color: var(--accent); }
.footnote { color: var(--faint); font-size: 0.8rem; margin-top: 0.9rem; }

/* ---- Rank -> information -> quality chain ---- */
.chain { display: grid; grid-template-columns: 1fr auto 1fr auto 1fr; align-items: center; gap: 12px; }
.chain .node { background: var(--panel); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem 1.1rem; }
.chain .node .k { font-family: var(--mono); font-size: 0.66rem; letter-spacing: 0.18em; color: var(--muted); text-transform: uppercase; }
.chain .node .v { font-family: var(--mono); font-size: 1.5rem; margin-top: 0.4rem; }
.chain .node .bar { height: 4px; background: var(--border); border-radius: 4px; margin-top: 0.7rem; overflow: hidden; }
.chain .node .bar > i { display: block; height: 100%; background: var(--accent); border-radius: 4px; }
.chain .arrow { color: var(--accent); font-family: var(--mono); font-size: 1.3rem; }
@media (max-width: 720px) {
  .chain { grid-template-columns: 1fr; }
  .chain .arrow { transform: rotate(90deg); justify-self: center; }
}

/* ---- Math panel ---- */
.math-eq { font-family: var(--mono); font-size: clamp(1.1rem, 3vw, 1.7rem); text-align: center; letter-spacing: 0.04em; }
.math-eq .dim { color: var(--faint); }
.math-eq .acc { color: var(--accent); }
.math-note { text-align: center; color: var(--muted); font-size: 0.92rem; margin-top: 0.6rem; }
.svg-wrap svg { width: 100%; height: auto; display: block; }

/* ---- How it works ---- */
.steps { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; }
.step { background: var(--panel); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.3rem; }
.step .n { font-family: var(--mono); font-size: 0.7rem; color: var(--accent); letter-spacing: 0.2em; }
.step h4 { margin: 0.6rem 0 0.4rem; font-size: 1.02rem; font-weight: 600; }
.step p { color: var(--muted); font-size: 0.88rem; margin: 0; line-height: 1.5; }
.step .math { font-family: var(--mono); color: var(--text); font-size: 0.85rem; margin-top: 0.7rem; }

/* ---- Buttons ---- */
.stDownloadButton button, .stButton button {
  border-radius: 10px; font-weight: 600; padding: 0.7rem 1.4rem;
  transition: transform .15s ease, box-shadow .2s ease;
}
.stDownloadButton button[kind="primary"], .stButton button[kind="primary"] {
  background: var(--accent); border: none; color: #fff;
  box-shadow: 0 8px 28px rgba(108,125,255,0.35);
}
.stDownloadButton button:hover, .stButton button:hover { transform: translateY(-1px); }
.stDownloadButton button[kind="secondary"] { background: transparent; border: 1px solid var(--border); color: var(--text); }
.ready { font-size: 1.5rem; font-weight: 600; margin: 0; }
.ready-sub { color: var(--muted); margin: 0.3rem 0 1rem; }

/* ---- Tabs / expanders / tables ---- */
[data-baseweb="tab-list"] { gap: 0.4rem; border-bottom: 1px solid var(--border); }
[data-baseweb="tab"] { font-family: var(--mono); font-size: 0.8rem; letter-spacing: 0.08em; }
[data-testid="stExpander"] { border: 1px solid var(--border); border-radius: var(--radius); background: var(--panel); }
[data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: 10px; }
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input {
  background: var(--panel-strong); border-radius: 8px; font-family: var(--mono);
}

/* ---- Empty state ---- */
.steps-mini { display: flex; justify-content: center; gap: 2.2rem; flex-wrap: wrap; margin-top: 2.2rem; }
.steps-mini div { font-family: var(--mono); font-size: 0.78rem; letter-spacing: 0.14em; color: var(--faint); text-transform: uppercase; }
.steps-mini b { color: var(--accent); margin-right: 0.5rem; font-weight: 600; }

/* ---- Small screens ---- */
@media (max-width: 640px) {
  .block-container { padding: 1.25rem 1rem 3rem; }
  [data-testid="stFileUploaderDropzone"] { padding: 2rem 1rem; }
  .section-label { margin-top: 2.2rem; }
}
</style>
"""


def inject_css():
    """Inject the global stylesheet and align matplotlib with the dark theme."""
    st.markdown(CSS, unsafe_allow_html=True)
    apply_matplotlib_theme()


def apply_matplotlib_theme():
    """Dark matplotlib defaults so existing plot helpers match the UI."""
    c = COLORS
    matplotlib.rcParams.update(
        {
            "figure.facecolor": c["surface"],
            "axes.facecolor": c["surface"],
            "savefig.facecolor": c["surface"],
            "axes.edgecolor": c["faint"],
            "axes.labelcolor": c["muted"],
            "axes.titlecolor": c["text"],
            "text.color": c["text"],
            "xtick.color": c["muted"],
            "ytick.color": c["muted"],
            "grid.color": "#ffffff",
            "grid.alpha": 0.08,
            "legend.facecolor": c["surface"],
            "legend.edgecolor": c["faint"],
            "font.size": 9,
        }
    )


def section(index, title):
    """Render a numbered section label."""
    st.markdown(
        f'<div class="section-label"><span class="idx">{index:02d}</span>{title}</div>',
        unsafe_allow_html=True,
    )


def stat_card(label, value, unit="", highlight=False):
    """Return the HTML for one metric tile."""
    cls = "stat hi" if highlight else "stat"
    unit_html = f"<small>{unit}</small>" if unit else ""
    return f'<div class="{cls}"><div class="k">{label}</div><div class="v">{value}{unit_html}</div></div>'
