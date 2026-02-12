"""Dashboard styles — Dark-theme financial dashboard (Design System v2.0).

Based on: Bloomberg Terminal, TradingView, shadcn/ui (Zinc scale).
Font loading via <link> tag to prevent @import CSS block failures.
"""

import streamlit as st


def inject_css():
    """Inject styles: font <link> + dark-theme <style>."""

    # ── Step 1: Font (separate, non-blocking) ──
    st.markdown(
        '<link href="https://fonts.googleapis.com/css2?'
        'family=Inter:wght@400;500;600;700;800&display=swap" '
        'rel="stylesheet">',
        unsafe_allow_html=True,
    )

    # ── Step 2: All CSS ──
    st.markdown(
        """<style>
/* ═══════ GLOBAL ═══════ */

html, body, [class*="css"], [class*="st-"] {
    font-family: "Inter", -apple-system, BlinkMacSystemFont,
                 "Hiragino Kaku Gothic ProN", "Yu Gothic", sans-serif !important;
    -webkit-font-smoothing: antialiased !important;
}

section.stMain .block-container {
    padding: 1.5rem 2rem 3rem !important;
    max-width: 100% !important;
}

header[data-testid="stHeader"] {
    background-color: #09090b !important;
}

/* ═══════ CARDS — st.container(border=True) ═══════ */

[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #18181b !important;
    border: 1px solid #27272a !important;
    border-radius: 12px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.3),
                0 1px 2px rgba(0,0,0,0.2) !important;
    margin-bottom: 1rem !important;
    overflow: visible !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: #3f3f46 !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4) !important;
}

[data-testid="stVerticalBlockBorderWrapper"] > div:first-child {
    background-color: #18181b !important;
    border: none !important;
    border-radius: 12px !important;
    box-shadow: none !important;
}

/* Nested cards */
[data-testid="stVerticalBlockBorderWrapper"]
  [data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #27272a !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 10px !important;
    box-shadow: none !important;
    margin-bottom: 0.5rem !important;
}

[data-testid="stVerticalBlockBorderWrapper"]
  [data-testid="stVerticalBlockBorderWrapper"] > div:first-child {
    background-color: #27272a !important;
}

/* ═══════ TYPOGRAPHY ═══════ */

h1 {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    color: #fafafa !important;
}

h2, h3 {
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    color: #fafafa !important;
}

[data-testid="stMetricValue"] > div,
.hero-value,
.tabular-nums {
    font-variant-numeric: tabular-nums !important;
}

/* ═══════ METRICS ═══════ */

div[data-testid="metric-container"] {
    background-color: #18181b !important;
    border: 1px solid #27272a !important;
    border-radius: 12px !important;
    padding: 14px 18px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.2) !important;
    transition: border-color 0.2s ease !important;
}

div[data-testid="metric-container"]:hover {
    border-color: #3f3f46 !important;
}

[data-testid="stMetricLabel"] p {
    color: #a1a1aa !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    font-weight: 600 !important;
}

[data-testid="stMetricValue"] > div {
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.01em !important;
    color: #fafafa !important;
    line-height: 1.3 !important;
}

[data-testid="stMetricDelta"] {
    font-size: 0.75rem !important;
}

/* ═══════ DIVIDERS ═══════ */

hr {
    margin: 0.75rem 0 !important;
    border: none !important;
    border-top: 1px solid #27272a !important;
}

/* ═══════ CAPTIONS ═══════ */

[data-testid="stCaptionContainer"] p {
    font-size: 0.75rem !important;
    line-height: 1.5 !important;
    color: #71717a !important;
}

/* ═══════ ALERTS ═══════ */

[data-testid="stAlert"] {
    border-radius: 10px !important;
    padding: 0.6rem 0.85rem !important;
    font-size: 0.82rem !important;
    margin: 0.3rem 0 !important;
}

/* ═══════ PROGRESS ═══════ */

[data-testid="stProgress"] > div > div {
    height: 6px !important;
    border-radius: 3px !important;
}

/* ═══════ SIDEBAR ═══════ */

section[data-testid="stSidebar"] {
    background-color: #0f0f12 !important;
    border-right: 1px solid #27272a !important;
}

section[data-testid="stSidebar"] [data-testid="stMetricValue"] > div {
    font-size: 1.5rem !important;
}

/* ═══════ EXPANDERS ═══════ */

[data-testid="stExpander"] {
    background-color: #18181b !important;
    border: 1px solid #27272a !important;
    border-radius: 12px !important;
    box-shadow: none !important;
    margin-bottom: 1rem !important;
}

details summary {
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    color: #a1a1aa !important;
}

/* ═══════ TABS ═══════ */

.stTabs [data-baseweb="tab-list"] {
    gap: 4px !important;
    background-color: transparent !important;
    border-bottom: 1px solid #27272a !important;
}

.stTabs [data-baseweb="tab"] {
    background-color: transparent !important;
    border: none !important;
    border-radius: 8px 8px 0 0 !important;
    color: #a1a1aa !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    padding: 8px 20px !important;
    transition: all 0.2s ease !important;
}

.stTabs [data-baseweb="tab"]:hover {
    background-color: rgba(99,102,241,0.06) !important;
    color: #fafafa !important;
}

.stTabs [aria-selected="true"] {
    background-color: rgba(99,102,241,0.1) !important;
    color: #6366f1 !important;
    font-weight: 600 !important;
}

.stTabs [data-baseweb="tab-highlight"] {
    background-color: #6366f1 !important;
}

/* ═══════ BUTTONS ═══════ */

.stButton > button {
    border-radius: 8px !important;
    border: 1px solid #27272a !important;
    background: #18181b !important;
    color: #fafafa !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    transition: all 0.15s ease !important;
}

.stButton > button:hover {
    border-color: #3f3f46 !important;
    background: #27272a !important;
}

/* ═══════ DATAFRAMES ═══════ */

[data-testid="stDataFrame"] {
    border: 1px solid #27272a !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}

/* ═══════ DIALOGS ═══════ */

[data-testid="stDialog"] {
    min-width: 760px !important;
    border-radius: 14px !important;
}

/* ═══════ CUSTOM COMPONENTS ═══════ */

.card-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
}

.card-title-text {
    font-size: 0.875rem;
    font-weight: 700;
    color: #fafafa;
}

.card-title .accent-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
}

.card-subtitle {
    font-size: 0.7rem;
    font-weight: 600;
    color: #a1a1aa;
    background: #27272a;
    border: 1px solid #3f3f46;
    border-radius: 9999px;
    padding: 0.12rem 0.5rem;
    margin-left: auto;
}

.hero-value {
    font-size: 2.25rem;
    font-weight: 800;
    color: #fafafa;
    letter-spacing: -0.03em;
    line-height: 1.05;
    margin: 0.15rem 0 0.35rem;
}

.section-label {
    font-size: 0.75rem;
    font-weight: 600;
    color: #a1a1aa;
    text-transform: uppercase;
    letter-spacing: 0.05em;
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
.status-dot--ok     { background: #22c55e; box-shadow: 0 0 0 2px rgba(34,197,94,0.3); }
.status-dot--warn   { background: #f59e0b; box-shadow: 0 0 0 2px rgba(245,158,11,0.3); }
.status-dot--fail   { background: #ef4444; box-shadow: 0 0 0 2px rgba(239,68,68,0.3); }
.status-dot--none   { background: #71717a; }
.status-dot--active { background: #6366f1; box-shadow: 0 0 0 2px rgba(99,102,241,0.3); }

/* Dialog helpers */
.dlg-section {
    font-size: 0.85rem;
    font-weight: 700;
    color: #fafafa;
    border-bottom: 2px solid #27272a;
    padding-bottom: 0.3rem;
    margin: 1rem 0 0.5rem;
}

.dlg-row {
    display: flex;
    justify-content: space-between;
    padding: 0.25rem 0;
    font-size: 0.82rem;
    border-bottom: 1px solid #27272a;
}

.dlg-key { color: #a1a1aa; }
.dlg-val { font-weight: 600; color: #fafafa; font-variant-numeric: tabular-nums; }

.c-pos { color: #22c55e; font-weight: 600; }
.c-neg { color: #ef4444; font-weight: 600; }

/* ═══════ SCROLLBAR ═══════ */

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #09090b; }
::-webkit-scrollbar-thumb { background: #3f3f46; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #52525b; }

/* ═══════ HIDE BRANDING ═══════ */

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* ═══════ RESPONSIVE ═══════ */

@media (max-width: 768px) {
    section.stMain .block-container {
        padding: 1rem 0.75rem 2rem !important;
    }
    .hero-value { font-size: 1.6rem !important; }
}

@media (max-width: 480px) {
    .hero-value { font-size: 1.3rem !important; }
    [data-testid="stMetricValue"] > div { font-size: 1.2rem !important; }
}
</style>""",
        unsafe_allow_html=True,
    )
