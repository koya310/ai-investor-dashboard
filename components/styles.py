"""Dashboard styles — bulletproof card-first design for Streamlit Cloud."""

import streamlit as st


def inject_css():
    """Inject styles that RELIABLY render cards on Streamlit Cloud.

    Design principles (from reference analysis):
    1. White cards on gray background — CLEAR separation
    2. Minimal color — white base, 1-2 accents only
    3. Visual hierarchy — size & weight, not color
    4. Strategic whitespace — breathing room between elements
    5. Consistent card system — all content lives in cards
    """
    st.markdown(
        """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ══════════════════════════════════════════════
   GLOBAL
   ══════════════════════════════════════════════ */

html, body, [class*="css"] {
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
   ══════════════════════════════════════════════ */

[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    padding: 1.5rem 1.75rem !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06),
                0 1px 2px rgba(0,0,0,0.03) !important;
    margin-bottom: 1rem !important;
}

/* Nested cards — subtle differentiation */
[data-testid="stVerticalBlockBorderWrapper"]
  [data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #f8fafc !important;
    border: 1px solid #f1f5f9 !important;
    border-radius: 8px !important;
    padding: 1rem !important;
    box-shadow: none !important;
    margin-bottom: 0 !important;
}

/* ══════════════════════════════════════════════
   TYPOGRAPHY
   ══════════════════════════════════════════════ */

/* L1: Page title */
h1 {
    font-size: 1.35rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
    color: #0f172a !important;
    margin-bottom: 1rem !important;
    padding-bottom: 0 !important;
}

h2, h3 {
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    color: #0f172a !important;
}

/* Section header within cards (bold markdown) */
.stMarkdown p strong {
    letter-spacing: -0.01em;
}

/* Tabular nums for financial data */
[data-testid="stMetricValue"] > div,
.hero-value,
.tabular-nums {
    font-variant-numeric: tabular-nums !important;
}

/* ══════════════════════════════════════════════
   METRICS
   ══════════════════════════════════════════════ */

[data-testid="stMetric"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0.35rem 0 !important;
}

[data-testid="stMetricLabel"] p {
    color: #64748b !important;
    font-size: 0.68rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    font-weight: 600 !important;
    margin-bottom: 0.15rem !important;
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
   DIVIDERS — barely visible separation
   ══════════════════════════════════════════════ */

hr {
    margin: 0.75rem 0 !important;
    border: none !important;
    border-top: 1px solid #f1f5f9 !important;
}

/* ══════════════════════════════════════════════
   CAPTIONS — muted helper text
   ══════════════════════════════════════════════ */

[data-testid="stCaptionContainer"] p {
    font-size: 0.72rem !important;
    line-height: 1.5 !important;
    color: #94a3b8 !important;
}

/* ══════════════════════════════════════════════
   ALERTS — st.success / st.warning / st.error / st.info
   ══════════════════════════════════════════════ */

[data-testid="stAlert"] {
    border-radius: 8px !important;
    padding: 0.6rem 0.85rem !important;
    font-size: 0.82rem !important;
    margin-top: 0.25rem !important;
    margin-bottom: 0.25rem !important;
}

/* ══════════════════════════════════════════════
   PROGRESS BARS
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

[data-testid="stSidebar"] .block-container {
    padding: 1.5rem 1rem !important;
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
    border-radius: 12px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
    margin-bottom: 1rem !important;
}

details summary {
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    color: #334155 !important;
    padding: 0.65rem 0 !important;
}

/* ══════════════════════════════════════════════
   TABS
   ══════════════════════════════════════════════ */

[data-testid="stTabs"] [role="tablist"] {
    gap: 0.35rem !important;
    margin-bottom: 0.5rem !important;
}

[data-testid="stTabs"] [role="tab"] {
    background: #ffffff !important;
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
    padding: 0.4rem 0.8rem !important;
    transition: all 0.15s ease !important;
}

.stButton > button:hover {
    border-color: #cbd5e1 !important;
    background: #f8fafc !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
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
   RADIO / SELECTBOX
   ══════════════════════════════════════════════ */

[data-testid="stRadio"] label {
    font-size: 0.82rem !important;
    font-weight: 500 !important;
}

/* ══════════════════════════════════════════════
   DIALOGS
   ══════════════════════════════════════════════ */

[data-testid="stDialog"] {
    min-width: 760px !important;
    border-radius: 12px !important;
}

/* ══════════════════════════════════════════════
   CUSTOM COMPONENTS
   ══════════════════════════════════════════════ */

/* Card title */
.card-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.85rem;
}

.card-title-text {
    font-size: 0.92rem;
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
    padding: 0.15rem 0.5rem;
    margin-left: auto;
}

/* Hero value (portfolio total) */
.hero-value {
    font-size: 2rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -1px;
    line-height: 1.1;
    margin: 0.25rem 0 0.4rem;
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

/* Section label (inside cards) */
.section-label {
    font-size: 0.75rem;
    font-weight: 700;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin: 0.5rem 0 0.4rem;
}

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

.dlg-insight {
    background: #fffbeb;
    border-left: 3px solid #d97706;
    border-radius: 8px;
    padding: 0.6rem 0.8rem;
    margin: 0.5rem 0;
    font-size: 0.8rem;
    color: #92400e;
}

.c-pos { color: #059669; font-weight: 600; }
.c-neg { color: #dc2626; font-weight: 600; }

/* ══════════════════════════════════════════════
   HIDE STREAMLIT CHROME
   ══════════════════════════════════════════════ */

/* Remove default top padding from main area */
.stMainBlockContainer {
    padding-top: 1.5rem !important;
}

/* ══════════════════════════════════════════════
   RESPONSIVE
   ══════════════════════════════════════════════ */

@media (max-width: 768px) {
    .block-container {
        padding: 1rem 0.75rem 2rem !important;
    }

    .hero-value {
        font-size: 1.6rem !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        padding: 1rem 1.25rem !important;
        border-radius: 10px !important;
    }
}

@media (max-width: 480px) {
    .block-container {
        padding: 0.75rem 0.5rem 1.5rem !important;
    }

    .hero-value {
        font-size: 1.35rem !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        padding: 0.85rem 1rem !important;
        border-radius: 8px !important;
    }

    [data-testid="stMetricValue"] > div {
        font-size: 1rem !important;
    }
}
</style>""",
        unsafe_allow_html=True,
    )
