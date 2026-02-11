"""Finazch-inspired card UI styles — flat background + white card system."""

import streamlit as st


def inject_css():
    """Inject clean card-based styling inspired by modern finance dashboards."""
    st.markdown(
        """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #f8f9fc;
    --card: #ffffff;
    --text: #1a1d26;
    --text-secondary: #6b7280;
    --text-muted: #9ca3af;
    --shadow-card: 0 1px 3px rgba(0,0,0,0.04), 0 2px 12px rgba(0,0,0,0.03);
    --shadow-card-hover: 0 4px 16px rgba(0,0,0,0.06);
    --radius: 14px;
    --radius-sm: 10px;
}

/* ── Base ── */
html, body, [class*="css"] {
    font-family: "Inter", -apple-system, BlinkMacSystemFont,
                 "Hiragino Kaku Gothic ProN", "Yu Gothic", sans-serif;
    -webkit-font-smoothing: antialiased;
}

.stApp {
    background: var(--bg);
    color: var(--text);
}

.block-container {
    padding: 2rem 2rem 3rem;
    max-width: 1100px;
}

/* ── Typography ── */
h1 {
    font-size: 1.55rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: var(--text);
    margin-bottom: 0.15rem;
}
h2 { font-size: 1.15rem; font-weight: 700; letter-spacing: -0.02em; }
h3 { font-size: 0.95rem; font-weight: 700; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--card) !important;
    border-right: none !important;
    box-shadow: 1px 0 8px rgba(0,0,0,0.03);
}
[data-testid="stSidebar"] .block-container {
    padding-top: 1.25rem;
}

/* ══════════════════════════════════════════════════════════════
   CARD SYSTEM — config.toml borderColor=transparent kills all
   Streamlit borders. CSS adds card styling (bg + shadow).
   Also target stVerticalBlock for belt-and-suspenders.
   ══════════════════════════════════════════════════════════════ */

div[data-testid="stVerticalBlock"],
div[data-testid="stMetric"],
div[data-testid="stExpander"],
div[data-testid="stForm"] {
    border: none !important;
    border-color: transparent !important;
}

/* ── Cards (st.container border=True) ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--card);
    border-radius: var(--radius);
    padding: 1.1rem 1.25rem;
    box-shadow: var(--shadow-card);
    margin-bottom: 0.5rem;
    transition: box-shadow 0.2s ease;
}

/* Nested cards — flat, no shadow, just a bit of spacing */
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--card);
    border-radius: var(--radius-sm);
    padding: 0.8rem 1rem;
    box-shadow: none;
    margin-bottom: 0.25rem;
}

[data-testid="stVerticalBlockBorderWrapper"] hr {
    margin: 0.5rem 0;
    border-color: #f0f1f5;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: var(--card);
    border-radius: var(--radius-sm);
    padding: 0.8rem 0.9rem;
    box-shadow: var(--shadow-card);
}

/* Metrics inside cards — no card effect, just clean text */
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMetric"] {
    background: transparent !important;
    border-radius: 0 !important;
    padding: 0.35rem 0.1rem !important;
    box-shadow: none !important;
}

[data-testid="stMetricLabel"] p {
    color: var(--text-secondary);
    font-size: 0.72rem;
    font-weight: 500;
    text-transform: none;
    letter-spacing: 0;
}

[data-testid="stMetricValue"] > div {
    font-size: 1.4rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    line-height: 1.25;
    color: var(--text);
}

[data-testid="stMetricDelta"] {
    font-size: 0.72rem;
    font-weight: 500;
}

/* ── Expanders ── */
[data-testid="stExpander"] {
    border-radius: var(--radius-sm);
    background: var(--card);
    box-shadow: var(--shadow-card);
}
details summary {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text);
}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tablist"] {
    gap: 0.35rem;
    border-bottom: none;
}
[data-testid="stTabs"] [role="tab"] {
    background: transparent;
    border: none !important;
    border-radius: 8px;
    padding: 0.4rem 0.85rem;
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--text-secondary);
    transition: all 0.15s ease;
}
[data-testid="stTabs"] [role="tab"]:hover {
    background: #f0f1f5;
    color: var(--text);
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    background: #eef2ff;
    color: #4f46e5;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: var(--radius-sm);
    border: 1px solid #e5e7eb !important;
    background: var(--card);
    color: var(--text);
    font-weight: 600;
    font-size: 0.84rem;
    padding: 0.45rem 1.1rem;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    transition: all 0.15s ease;
}
.stButton > button:hover {
    border-color: #d1d5db !important;
    box-shadow: var(--shadow-card-hover);
    transform: translateY(-1px);
}
.stButton > button:active {
    transform: translateY(0);
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}

/* ── DataFrames ── */
[data-testid="stDataFrame"] {
    border-radius: var(--radius-sm);
    overflow: hidden;
    box-shadow: var(--shadow-card);
}

/* ── Dialogs ── */
[data-testid="stDialog"] {
    min-width: 760px;
    border-radius: 16px;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    border-radius: var(--radius-sm);
    font-size: 0.84rem;
    border-left-width: 3px;
}

/* ── Progress bars ── */
[data-testid="stProgress"] > div > div {
    border-radius: 8px;
    height: 6px;
}

/* ── Captions ── */
[data-testid="stCaptionContainer"] {
    font-size: 0.76rem;
    color: var(--text-muted);
}

/* ── Page links ── */
[data-testid="stPageLink"] a {
    color: var(--text-secondary) !important;
    font-size: 0.82rem;
    font-weight: 500;
}
[data-testid="stPageLink"] a:hover {
    color: var(--text) !important;
}

/* ── Dialog-only helper classes ── */
.dlg-section {
    font-size: 0.82rem;
    font-weight: 700;
    color: var(--text);
    border-bottom: 2px solid #f0f1f5;
    padding-bottom: 0.3rem;
    margin: 1rem 0 0.5rem;
}
.dlg-row {
    display: flex;
    justify-content: space-between;
    padding: 0.25rem 0;
    font-size: 0.8rem;
    border-bottom: 1px solid #f7f8fa;
}
.dlg-key { color: var(--text-secondary); }
.dlg-val { font-weight: 600; color: var(--text); }
.dlg-insight {
    background: #fffbeb;
    border-left: 3px solid #f59e0b;
    border-radius: 8px;
    padding: 0.6rem 0.8rem;
    margin: 0.5rem 0;
    font-size: 0.78rem;
    color: #92400e;
}
.c-pos { color: #059669; }
.c-neg { color: #ef4444; }
</style>""",
        unsafe_allow_html=True,
    )
