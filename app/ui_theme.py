"""Visual system for the SVD Image Compressor Streamlit app.

A deep-teal page, liquid-glass panels, Space Grotesk + DM Mono type, and a
System / Light / Dark switch. All colors, type and spacing live here as CSS
tokens. No image-processing or SVD code belongs in this module.
"""

import matplotlib
import streamlit as st

# ---- Design tokens ---------------------------------------------------------
# Change TEAL here (and the matching --teal token in CSS) to retune the page.
TEAL = "#0d4a4a"

COLORS = {
    "bg": TEAL,
    "surface": "#072B2D",
    "text": "#f4f6ff",
    "muted": "#9da4be",
    "faint": "#5b6280",
    "accent": "#6C7DFF",
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
  --teal: #0d4a4a;
  --accent: #6C7DFF;
  --ink: #f4f6ff;
  --muted: rgba(244,246,255,.68);
  --line: rgba(255,255,255,.18);
  --glass: rgba(255,255,255,.075);
  --panel: rgba(3,32,34,.72);
  --panel-strong: rgba(255,255,255,.08);
  --accent-box: rgba(108,125,255,.16);
  --o-text: #f4f6ff;
  --o-muted: rgba(244,246,255,.68);
  --o-faint: #9da4be;
  --o-border: rgba(255,255,255,.12);
  --radius: 14px;
  --mono: 'DM Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
  --sans: 'Space Grotesk', system-ui, -apple-system, 'Segoe UI', sans-serif;
}

/* ---- Page shell ---- */
html, body, [class*="css"] { font-family: var(--sans); }
.stApp {
  background: var(--teal);
  color: var(--o-text);
  font-family: var(--sans);
}
[data-testid="stAppViewContainer"], [data-testid="stHeader"] { background: transparent !important; }
[data-testid="stMain"] { position: relative; z-index: 1; background: transparent; }
#MainMenu, footer, [data-testid="stDecoration"], [data-testid="stStatusWidget"] { display: none !important; }
.block-container { max-width: 1100px; padding: 1rem 24px 4rem; }
h1, h2, h3, h4 { font-family: var(--sans); }

/* ---- Top bar ---- */
.topbar-label { font: 11px var(--mono); letter-spacing: .03em; color: var(--o-faint); }
.topbar-rule { height: 1px; background: var(--o-border); margin: .6rem 0 0; }
[data-testid="stButtonGroup"] { gap: 4px; }
[data-testid="stButtonGroup"] button {
  font: 11px var(--mono) !important; letter-spacing: .03em;
  background: transparent !important; border: 0 !important; border-radius: 7px !important;
  color: var(--o-faint) !important; padding: 6px 10px !important; box-shadow: none !important;
}
[data-testid="stButtonGroup"] button *  { font: 11px var(--mono) !important; color: inherit !important; }
[data-testid="stButtonGroup"] button:hover { background: rgba(255,255,255,.12) !important; color: #fff !important; }
[data-testid="stButtonGroup"] button[aria-checked="true"],
[data-testid="stButtonGroup"] button[aria-pressed="true"] { background: rgba(255,255,255,.12) !important; color: #fff !important; }
a.gh-link, a.gh-link:visited {
  display: inline-flex; align-items: center; gap: 8px; float: right;
  color: var(--o-text) !important; text-decoration: none !important;
  font: 11px var(--mono); padding: 8px 10px; border-radius: 7px; transition: background-color .2s;
}
a.gh-link:hover { background: rgba(255,255,255,.12); }
a.gh-link svg { width: 15px; height: 15px; fill: currentColor; }
.topbar-right { display: block; }

/* ---- Hero ---- */
.hero { padding: 96px 0 24px; max-width: 800px; text-align: left; }
.eyebrow, .overline {
  font: 10px var(--mono); letter-spacing: .14em; text-transform: uppercase; color: var(--o-faint);
}
.eyebrow-dot {
  display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: var(--accent);
  box-shadow: 0 0 12px #6c7dff; margin-right: 9px; vertical-align: middle;
}
.hero h1 {
  font-size: clamp(50px, 9vw, 105px); letter-spacing: -.08em; line-height: .85;
  margin: 22px 0 24px; padding: 0; font-weight: 700; color: var(--o-text);
}
.hero h1 em { font-style: normal; color: var(--accent); }

/* ---- Section headings ---- */
.section-heading { display: flex; gap: 19px; margin: 110px 0 28px; align-items: flex-start; }
.section-number { font: 12px var(--mono); color: var(--accent); padding-top: 6px; }
.section-heading h2 { font-size: 28px; letter-spacing: -.04em; margin: 0 0 8px; padding: 0; color: var(--o-text); }
.section-heading p { margin: 0; color: var(--o-muted); font-size: 16px; }

/* ---- Glass panels ---- */
:is([data-testid="stVerticalBlockBorderWrapper"], [class*="st-key-box_"]) {
  background: var(--panel);
  border: 1px solid var(--line) !important;
  border-radius: var(--radius) !important;
  backdrop-filter: blur(24px) saturate(150%);
  -webkit-backdrop-filter: blur(24px) saturate(150%);
  box-shadow: 0 20px 60px rgba(0,0,0,.2), inset 0 1px 0 rgba(255,255,255,.1);
}
[class*="st-key-box_"] { padding: 22px 24px; }

/* ---- Upload ---- */
[data-testid="stFileUploader"] label { display: none; }
[data-testid="stFileUploaderDropzone"] {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 24px;
  backdrop-filter: blur(24px) saturate(150%);
  -webkit-backdrop-filter: blur(24px) saturate(150%);
  box-shadow: 0 20px 60px rgba(0,0,0,.2), inset 0 1px 0 rgba(255,255,255,.1);
  transition: transform .2s, border-color .2s;
}
[data-testid="stFileUploaderDropzone"]:hover { transform: translateY(-2px); border-color: var(--accent); }
[data-testid="stFileUploaderDropzone"] button {
  background: var(--accent-box); color: var(--accent); border: 0; border-radius: 7px; font: 11px var(--mono);
}
[data-testid="stFileUploaderDropzone"] button:hover { background: rgba(108,125,255,.28); color: #fff; }
[data-testid="stFileUploaderFile"] { background: var(--panel); border-radius: 10px; }

/* ---- Rank control ---- */
.rank-readout { line-height: 1; }
.rank-readout .caption { font: 10px var(--mono); letter-spacing: .1em; color: var(--o-faint); text-transform: uppercase; }
.rank-readout .value { font-size: 31px; font-weight: 700; letter-spacing: -.07em; margin: 6px 0 4px; color: #f4f6ff; }
.rank-readout .value span { color: var(--accent); }
.rank-readout .of { font: 10px var(--mono); color: var(--o-faint); }
.hint { font: 11px var(--mono); color: #9da4be; margin-top: .5rem; }
[data-testid="stSlider"] { padding-top: .4rem; }
[data-testid="stSliderThumbValue"] { font-family: var(--mono); color: var(--accent); }

/* ---- Image cards ---- */
.img-head { display: flex; justify-content: space-between; align-items: center; font: 10px var(--mono); color: #9da4be; margin-bottom: .6rem; }
.img-head .tag { letter-spacing: .1em; text-transform: uppercase; }
.img-head .tag b { color: var(--accent); font-weight: 500; }
.img-head .size { color: #f4f6ff; }
[data-testid="stImage"] img { border-radius: 8px; }

/* ---- Metrics (all tiles share one style) ---- */
.stat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.stat {
  background: var(--panel); border: 1px solid var(--line); border-radius: var(--radius);
  padding: 20px; backdrop-filter: blur(24px) saturate(150%); -webkit-backdrop-filter: blur(24px) saturate(150%);
  box-shadow: 0 20px 60px rgba(0,0,0,.2), inset 0 1px 0 rgba(255,255,255,.1);
}
.stat .k { font: 10px var(--mono); letter-spacing: .1em; color: #9da4be; text-transform: uppercase; }
.stat .v { font-size: 31px; font-weight: 500; letter-spacing: -.06em; margin: 16px 0 5px; color: #f4f6ff; }
.stat .v small { font: 11px var(--mono); letter-spacing: 0; color: #9da4be; margin-left: 6px; }
.footnote { color: var(--o-faint); font: 10px var(--mono); line-height: 1.6; margin-top: 14px; }

/* ---- Rank -> information -> quality chain ---- */
.chain { display: grid; grid-template-columns: 1fr; gap: 10px; }
.chain .node {
  background: var(--panel); border: 1px solid var(--line); border-radius: var(--radius); padding: 16px 18px;
  backdrop-filter: blur(24px) saturate(150%); -webkit-backdrop-filter: blur(24px) saturate(150%);
}
.chain .node .k { font: 10px var(--mono); letter-spacing: .1em; color: #9da4be; text-transform: uppercase; }
.chain .node .v { font-size: 24px; font-weight: 500; letter-spacing: -.05em; margin-top: 6px; color: #f4f6ff; }
.chain .node .bar { height: 4px; background: rgba(255,255,255,.12); border-radius: 4px; margin-top: 12px; overflow: hidden; }
.chain .node .bar > i { display: block; height: 100%; background: var(--accent); border-radius: 4px; }
.chain .arrow { color: var(--accent); font-size: 18px; text-align: center; }

/* ---- Math panel ---- */
.math-eq { font-family: var(--sans); font-size: clamp(1.2rem, 3vw, 1.9rem); text-align: center; letter-spacing: -.02em; color: #f4f6ff; }
.math-eq .dim { color: #9da4be; }
.math-eq .acc { color: var(--accent); }
.math-note { text-align: center; color: #9da4be; font-size: 14px; margin-top: .6rem; }
.svg-wrap svg { width: 100%; height: auto; display: block; }

/* ---- How it works ---- */
.steps { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.step {
  background: var(--panel); border: 1px solid var(--line); border-radius: var(--radius); padding: 20px; min-height: 180px;
  backdrop-filter: blur(24px) saturate(150%); -webkit-backdrop-filter: blur(24px) saturate(150%);
  box-shadow: 0 20px 60px rgba(0,0,0,.2), inset 0 1px 0 rgba(255,255,255,.1);
}
.step .n { font: 10px var(--mono); color: var(--accent); letter-spacing: .1em; }
.step h4 { margin: 32px 0 8px; padding: 0; font-size: 17px; font-weight: 600; color: #f4f6ff; }
.step p { color: #9da4be; font-size: 12px; margin: 0; line-height: 1.5; }
.step .math { font: 11px var(--mono); color: #f4f6ff; margin-top: 12px; }

/* ---- Buttons ---- */
.stDownloadButton button, .stButton button {
  border-radius: 7px; font: 11px var(--mono); padding: 13px 17px;
  transition: transform .2s, background-color .2s;
}
.stDownloadButton button[kind="primary"], .stButton button[kind="primary"] {
  background: var(--accent); border: 0; color: #fff; box-shadow: none;
}
.stDownloadButton button[kind="primary"]:hover, .stButton button[kind="primary"]:hover { background: #8090ff; transform: translateY(-2px); }
.stDownloadButton button[kind="secondary"], .stButton button[kind="secondary"] {
  background: transparent; border: 1px solid var(--line); color: #f4f6ff;
}
.stDownloadButton button[kind="secondary"]:hover { border-color: var(--accent); }
.ready { font-size: 23px; font-weight: 600; letter-spacing: -.03em; margin: 8px 0 4px; color: #f4f6ff; }
.ready-sub { font-size: 13px; color: #9da4be; margin: 0 0 1rem; }

/* ---- Tabs / expanders / tables / inputs ---- */
[data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid var(--line); }
[data-baseweb="tab"] { font: 11px var(--mono); letter-spacing: .03em; }
[data-testid="stExpander"] {
  border: 1px solid var(--line); border-radius: var(--radius); background: var(--panel);
  backdrop-filter: blur(24px) saturate(150%); -webkit-backdrop-filter: blur(24px) saturate(150%);
}
[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 10px; }
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input {
  background: var(--panel-strong); border-radius: 8px; font-family: var(--mono);
}

/* ---- Footer ---- */
.site-footer {
  display: flex; justify-content: space-between; gap: 20px; flex-wrap: wrap;
  border-top: 1px solid var(--o-border); margin-top: 110px; padding: 23px 0 10px;
  font: 9px var(--mono); color: var(--o-faint);
}
.site-footer a { color: inherit !important; text-decoration: none; }

/* ---- Small screens ---- */
@media (max-width: 700px) {
  .block-container { padding: .6rem 14px 3rem; }
  .hero { padding: 64px 0 48px; }
  .hero h1 { font-size: 56px; }
  .section-heading { margin-top: 80px; }
  .stat-grid { grid-template-columns: 1fr 1fr; }
  .steps { grid-template-columns: 1fr 1fr; }
  [data-testid="stFileUploaderDropzone"] { padding: 16px; }
}
</style>
"""

# Light mode: white page, dark teal glass boxes. Only text/borders outside boxes flip.
LIGHT_RULES = """
:root {
  --o-text: #101226; --o-muted: #656a7c; --o-faint: #8a8d9b; --o-border: rgba(20,24,55,.1);
  --panel: #072B2D; --panel-strong: #0E3A3C;
}
.stApp { background: #FFFFFF !important; }
.stApp [data-testid="stSpinner"], .stApp [data-testid="stSpinner"] * { color: var(--o-text); }
.stApp [data-testid="stCaptionContainer"] { color: var(--o-muted); }
.stApp :is([data-testid="stVerticalBlockBorderWrapper"], [class*="st-key-box_"]) [data-testid="stCaptionContainer"] { color: #9da4be; }
.stApp [data-testid="stFileUploaderDropzone"] { background: #072B2D; }
.stApp .stDownloadButton button, .stApp .stButton button { color: #f4f6ff; }
.stApp button[kind="primary"], .stApp button[kind="primary"] * { color: #fff !important; }
.stApp [data-testid="stButtonGroup"] button { color: #777b8b !important; }
.stApp [data-testid="stButtonGroup"] button:hover,
.stApp [data-testid="stButtonGroup"] button[aria-checked="true"],
.stApp [data-testid="stButtonGroup"] button[aria-pressed="true"] { background: #e9eaf1 !important; color: #12152c !important; }
.stApp a.gh-link:hover { background: #e9eaf1; }

/* Reconstruction error map: the expander is a dark box, so all of its text
   (header, caption, any markdown) must be white in light mode. */
.stApp [data-testid="stExpander"] :is(summary, summary *, p, span, label, li,
  [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] *,
  [data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] *) {
  color: #ffffff !important;
}
.stApp [data-testid="stExpander"] svg { fill: #ffffff; color: #ffffff; }
"""

THEME_OPTIONS = ["System", "Light", "Dark"]


def theme_css(mode):
    """Extra CSS for the chosen appearance: 'System', 'Light' or 'Dark'."""
    if mode == "Light":
        return f"<style>{LIGHT_RULES}</style>"
    if mode == "System":
        return f"<style>@media (prefers-color-scheme: light) {{{LIGHT_RULES}}}</style>"
    return ""


def inject_css(mode="System"):
    """Inject the global stylesheet and the selected appearance."""
    st.markdown(CSS + theme_css(mode), unsafe_allow_html=True)
    apply_matplotlib_theme()


GITHUB_URL = "https://github.com/AtharvChoudhary65"
GITHUB_LINK = (
    f'<div class="topbar-right"><a class="gh-link" href="{GITHUB_URL}" target="_blank" '
    'rel="noopener noreferrer" aria-label="GitHub profile">'
    '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 '
    '5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94'
    '-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87'
    '.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 '
    '2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12'
    '.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 '
    '.21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>GitHub ↗</a></div>'
)


def apply_matplotlib_theme():
    """Transparent, light-on-dark matplotlib defaults so charts sit on the glass."""
    c = COLORS
    matplotlib.rcParams.update(
        {
            "figure.facecolor": "none",
            "axes.facecolor": "none",
            "savefig.facecolor": "none",
            "axes.edgecolor": c["faint"],
            "axes.labelcolor": c["muted"],
            "axes.titlecolor": c["text"],
            "text.color": c["text"],
            "xtick.color": c["muted"],
            "ytick.color": c["muted"],
            "grid.color": "#ffffff",
            "grid.alpha": 0.10,
            "legend.facecolor": c["surface"],
            "legend.edgecolor": c["faint"],
            "font.size": 9,
        }
    )


def section(index, title, description=""):
    """Render a numbered section heading with an optional one-line description."""
    desc = f"<p>{description}</p>" if description else ""
    st.markdown(
        f'<div class="section-heading"><div class="section-number">{index:02d}</div>'
        f"<div><h2>{title}</h2>{desc}</div></div>",
        unsafe_allow_html=True,
    )


def stat_card(label, value, unit="", highlight=False):
    """Return the HTML for one metric tile.

    ``highlight`` is accepted for backward compatibility but ignored: every
    tile now uses the same style.
    """
    unit_html = f"<small>{unit}</small>" if unit else ""
    return f'<div class="stat"><div class="k">{label}</div><div class="v">{value}{unit_html}</div></div>'