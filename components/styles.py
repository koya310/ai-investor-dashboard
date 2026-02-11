"""Dashboard styles — bulletproof card-first design for Streamlit Cloud.

CRITICAL: Font loading is separated from CSS to prevent @import failures
from breaking the entire style block. This is the #1 cause of card
rendering failures on Streamlit Cloud.
"""

import streamlit as st


def inject_css():
    """Inject styles in TWO steps: font link + CSS rules.

    Step 1: <link> for Google Fonts (non-blocking, fails gracefully)
    Step 2: <style> for all CSS rules (guaranteed to load)
    """
    # ── Step 1: Font — separate from CSS so failures don't cascade ──
    st.markdown(
        '<link href="https://fonts.googleapis.com/css2?'
        'family=Inter:wght@400;500;600;700;800&display=swap" '
        'rel="stylesheet">',
        unsafe_allow_html=True,
    )

    # ── Step 2: All CSS — no @import, guaranteed to parse ──
    st.markdown(
        """<style>
/* ══════════════════════════════════════════════
   GLOBAL
   ══════════════════════════════════════════════ */

html, body, [class*="css"], [class*="st-"] {
    font-family: "Inter", -apple-system, BlinkMacSystemFont,
                 "Hiragino Kaku Gothic ProN", "Yu Gothic", sans-serif !important;
    -webkit-font-smoothing: antialiased !important;
}

.stApp {
    background-color: #f1f5f9 !important;
}

.block-container {
    padding: 2rem 2rem 3rem !important;
    max-width: 1080px !important;
}

/* ══════════════════════════════════════════════
   CARDS — st.container(border=True)
   Multi-selector targeting for Streamlit Cloud.
   ══════════════════════════════════════════════ */

/* Wrapper element */
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 14px !important;
    padding: 1.5rem 1.75rem !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06),
                0 1px 2px rgba(0,0,0,0.03) !important;
    margin-bottom: 1rem !important;
    overflow: visible !important;
}

/* Inner div (Streamlit places border here in some versions) */
[data-testid="stVerticalBlockBorderWrapper"] > div:first-child {
    background-color: #ffffff !important;
    border: none !important;
    border-radius: 14px !important;
    box-shadow: none !important;
}

/* Nested cards — subtle flat bg */
[data-testid="stVerticalBlockBorderWrapper"]
  [data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #f8fafc !important;
    border: 1px solid #f1f5f9 !important;
    border-radius: 10px !important;
    padding: 1rem 1.25rem !important;
    box-shadow: none !important;
    margin-bottom: 0.5rem !important;
}

[data-testid="stVerticalBlockBorderWrapper"]
  [data-testid="stVerticalBlockBorderWrapper"] > div:first-child {
    background-color: #f8fafc !important;
    border: none !important;
}

/* ══════════════════════════════════════════════
   TYPOGRAPHY
   ══════════════════════════════════════════════ */

h1 {
    font-size: 1.3rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
    color: #0f172a !important;
    margin-bottom: 0.5rem !important;
    padding-bottom: 0 !important;
}

h2, h3 {
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    color: #0f172a !important;
}

/* Tabular nums for financial data */
[data-testid="stMetricValue"] > div,
.hero-value,
.tabular-nums {
    font-variant-numeric: tabular-nums !important;
}

/* ══════════════════════════════════════════════
   METRICS — transparent on card bg
   ══════════════════════════════════════════════ */

[data-testid="stMetric"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0.25rem 0 !important;
}

[data-testid="stMetricLabel"] p {
    color: #64748b !important;
    font-size: 0.68rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    font-weight: 600 !important;
    margin-bottom: 0.1rem !important;
}

[data-testid="stMetricValue"] > div {
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    color: #0f172a !important;
    line-height: 1.3 !important;
}

[data-testid="stMetricDelta"] {
    font-size: 0.7rem !important;
}

/* ══════════════════════════════════════════════
   DIVIDERS
   ══════════════════════════════════════════════ */

hr {
    margin: 0.6rem 0 !important;
    border: none !important;
    border-top: 1px solid #f1f5f9 !important;
}

/* ══════════════════════════════════════════════
   CAPTIONS
   ══════════════════════════════════════════════ */

[data-testid="stCaptionContainer"] p {
    font-size: 0.72rem !important;
    line-height: 1.5 !important;
    color: #94a3b8 !important;
}

/* ══════════════════════════════════════════════
   ALERTS
   ══════════════════════════════════════════════ */

[data-testid="stAlert"] {
    border-radius: 10px !important;
    padding: 0.6rem 0.85rem !important;
    font-size: 0.82rem !important;
    margin: 0.3rem 0 !important;
}

/* ══════════════════════════════════════════════
   PROGRESS
   ══════════════════════════════════════════════ */

[data-testid="stProgress"] > div > div {
    height: 6px !important;
    border-radius: 3px !important;
}

/* ══════════════════════════════════════════════
   SIDEBAR
   ══════════════════════════════════════════════ */

[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
}

[data-testid="stSidebar"] [data-testid="stMetricValue"] > div {
    font-size: 1.5rem !important;
}

/* ══════════════════════════════════════════════
   EXPANDERS
   ══════════════════════════════════════════════ */

[data-testid="stExpander"] {
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 14px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
    margin-bottom: 1rem !important;
}

details summary {
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    color: #334155 !important;
}

/* ══════════════════════════════════════════════
   TABS
   ══════════════════════════════════════════════ */

[data-testid="stTabs"] [role="tablist"] {
    gap: 0.35rem !important;
    margin-bottom: 0.5rem !important;
}

[data-testid="stTabs"] [role="tab"] {
    background: #f8fafc !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 9999px !important;
    padding: 0.35rem 0.75rem !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
}

[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    border-color: #bfdbfe !important;
    background: #eff6ff !important;
    color: #2563eb !important;
}

/* ══════════════════════════════════════════════
   BUTTONS
   ══════════════════════════════════════════════ */

.stButton > button {
    border-radius: 8px !important;
    border: 1px solid #e2e8f0 !important;
    background: #ffffff !important;
    color: #334155 !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
    transition: all 0.15s ease !important;
}

.stButton > button:hover {
    border-color: #cbd5e1 !important;
    background: #f8fafc !important;
}

/* ══════════════════════════════════════════════
   DATAFRAMES
   ══════════════════════════════════════════════ */

[data-testid="stDataFrame"] {
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}

/* ══════════════════════════════════════════════
   DIALOGS
   ══════════════════════════════════════════════ */

[data-testid="stDialog"] {
    min-width: 760px !important;
    border-radius: 14px !important;
}

/* ══════════════════════════════════════════════
   CUSTOM COMPONENTS
   ══════════════════════════════════════════════ */

.card-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
}

.card-title-text {
    font-size: 0.88rem;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.01em;
}

.card-title .accent-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
}

.card-subtitle {
    font-size: 0.68rem;
    font-weight: 600;
    color: #64748b;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 9999px;
    padding: 0.12rem 0.5rem;
    margin-left: auto;
}

/* Hero value */
.hero-value {
    font-size: 2.2rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -1.5px;
    line-height: 1.05;
    margin: 0.15rem 0 0.35rem;
}

/* Section label (uppercase) */
.section-label {
    font-size: 0.72rem;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 0.4rem 0 0.35rem;
}

/* Status dots */
.status-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    vertical-align: middle;
}
.status-dot--ok     { background: #059669; box-shadow: 0 0 0 2px rgba(5,150,105,0.15); }
.status-dot--warn   { background: #d97706; box-shadow: 0 0 0 2px rgba(217,119,6,0.15); }
.status-dot--fail   { background: #dc2626; box-shadow: 0 0 0 2px rgba(220,38,38,0.15); }
.status-dot--none   { background: #e2e8f0; }
.status-dot--active { background: #2563eb; box-shadow: 0 0 0 2px rgba(37,99,235,0.15); }

/* Dialog helpers */
.dlg-section {
    font-size: 0.85rem;
    font-weight: 700;
    color: #0f172a;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 0.3rem;
    margin: 1rem 0 0.5rem;
}

.dlg-row {
    display: flex;
    justify-content: space-between;
    padding: 0.25rem 0;
    font-size: 0.82rem;
    border-bottom: 1px solid #f8fafc;
}

.dlg-key { color: #64748b; }
.dlg-val { font-weight: 600; color: #0f172a; font-variant-numeric: tabular-nums; }

.c-pos { color: #059669; font-weight: 600; }
.c-neg { color: #dc2626; font-weight: 600; }

/* ══════════════════════════════════════════════
   RESPONSIVE
   ══════════════════════════════════════════════ */

@media (max-width: 768px) {
    .block-container {
        padding: 1rem 0.75rem 2rem !important;
    }
    .hero-value { font-size: 1.6rem !important; }
    [data-testid="stVerticalBlockBorderWrapper"] {
        padding: 1rem 1.25rem !important;
    }
}

@media (max-width: 480px) {
    .hero-value { font-size: 1.3rem !important; }
    [data-testid="stMetricValue"] > div { font-size: 1rem !important; }
}
</style>""",
        unsafe_allow_html=True,
    )
