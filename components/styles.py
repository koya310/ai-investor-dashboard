"""Professional dashboard styles — Stripe/Linear-inspired clean finance UI."""

import streamlit as st


def inject_css():
    """Inject clean, professional styling. Stripe-level subtlety."""
    st.markdown(
        """<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
    /* ── Backgrounds ── */
    --bg: #f3f5f9;
    --card: #ffffff;
    --card-hover: #fafbfd;
    --border: #e7ecf4;
    --border-light: #f1f4f9;

    /* ── Semantic text (5 levels) ── */
    --text: #0f172a;
    --text-secondary: #334155;
    --text-sub: #475569;
    --text-muted: #94a3b8;
    --text-faint: #cbd5e1;

    /* ── Shadows (Stripe-level subtlety) ── */
    --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.03);
    --shadow-md: 0 1px 3px rgba(15, 23, 42, 0.04),
                 0 4px 12px rgba(15, 23, 42, 0.03);

    /* ── Radii ── */
    --radius-md: 12px;
    --radius-lg: 16px;

    /* ── Semantic data colors ── */
    --positive: #059669;
    --positive-bg: #ecfdf5;
    --positive-border: #a7f3d0;
    --negative: #dc2626;
    --negative-bg: #fef2f2;
    --negative-border: #fca5a5;
    --warning: #d97706;
    --warning-bg: #fffbeb;
    --warning-border: #fde68a;

    /* ── Accent (interactive only) ── */
    --blue: #2563eb;
    --blue-hover: #1d4ed8;
    --blue-bg: #eff6ff;
    --blue-border: #bfdbfe;

    /* ── Legacy aliases ── */
    --emerald: var(--positive);
    --rose: var(--negative);
    --amber: var(--warning);
}

html, body, [class*="css"] {
    font-family: "Plus Jakarta Sans", "Hiragino Kaku Gothic ProN",
                 "Yu Gothic", sans-serif;
}

/* ══════════════════════════════════════════════
   GLOBAL
   ══════════════════════════════════════════════ */

.stApp {
    background: var(--bg);
    color: var(--text);
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 1.5rem;
    max-width: 1200px;
}

/* ══════════════════════════════════════════════
   TYPOGRAPHY — Consolidated 5-level scale
   ══════════════════════════════════════════════ */

/* L1: Page title — 24px */
h1 {
    font-size: 1.5rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em;
}

h2, h3 {
    font-weight: 700;
    letter-spacing: -0.02em;
}

/* ── Tabular numbers for ALL financial data ── */
[data-testid="stMetricValue"] > div,
.hero-value,
.dlg-val,
.tabular-nums {
    font-variant-numeric: tabular-nums;
    font-feature-settings: "tnum";
}

/* ══════════════════════════════════════════════
   SIDEBAR
   ══════════════════════════════════════════════ */

[data-testid="stSidebar"] {
    border-right: 1px solid var(--border);
    background: #fafbfd;
}

[data-testid="stSidebar"] .block-container {
    padding-top: 1rem;
}

/* ══════════════════════════════════════════════
   CARDS — st.container(border=True)
   ══════════════════════════════════════════════ */

[data-testid="stVerticalBlock"]
  > [data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1rem 1.1rem;
    box-shadow: var(--shadow-md);
}

/* Nested containers: subtle, no heavy borders */
[data-testid="stVerticalBlockBorderWrapper"]
  [data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--card-hover);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    padding: 0.75rem 0.85rem;
    box-shadow: none;
}

/* ══════════════════════════════════════════════
   METRICS — transparent inside cards
   ══════════════════════════════════════════════ */

[data-testid="stMetric"] {
    background: transparent;
    border: none;
    border-radius: 0;
    padding: 0.3rem 0;
    box-shadow: none;
}

/* L4: Metric labels — 11.5px */
[data-testid="stMetricLabel"] p {
    color: var(--text-muted);
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600;
}

/* L3: Metric values — 19px */
[data-testid="stMetricValue"] > div {
    font-size: 1.2rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: var(--text);
}

[data-testid="stMetricDelta"] {
    font-size: 0.72rem;
    font-weight: 500;
}

/* ══════════════════════════════════════════════
   DIVIDERS — tighter
   ══════════════════════════════════════════════ */

[data-testid="stVerticalBlockBorderWrapper"] hr {
    margin: 0.35rem 0;
    border-color: var(--border-light);
    opacity: 0.7;
}

/* ══════════════════════════════════════════════
   EXPANDERS
   ══════════════════════════════════════════════ */

[data-testid="stExpander"] {
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    background: var(--card);
    box-shadow: var(--shadow-sm);
}

details summary {
    font-size: 0.82rem;
    font-weight: 700;
    color: #334155;
}

/* ══════════════════════════════════════════════
   TABS — pill style
   ══════════════════════════════════════════════ */

[data-testid="stTabs"] [role="tablist"] {
    gap: 0.4rem;
}

[data-testid="stTabs"] [role="tab"] {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 9999px;
    padding: 0.32rem 0.75rem;
    font-size: 0.82rem;
    font-weight: 600;
}

[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    border-color: var(--blue-border);
    background: var(--blue-bg);
    color: var(--blue);
}

/* ══════════════════════════════════════════════
   DIALOGS
   ══════════════════════════════════════════════ */

[data-testid="stDialog"] {
    min-width: 760px;
    border-radius: var(--radius-lg);
}

/* ══════════════════════════════════════════════
   BUTTONS
   ══════════════════════════════════════════════ */

.stButton > button {
    border-radius: 8px;
    border: 1px solid #d8e1ee;
    background: var(--card);
    color: var(--text);
    font-weight: 600;
    font-size: 0.82rem;
    transition: all 0.15s ease;
}

.stButton > button:hover {
    border-color: #bfcfe8;
    box-shadow: 0 2px 8px rgba(37, 99, 235, 0.1);
    transform: translateY(-1px);
}

/* Primary button override */
.stButton > button[kind="primary"] {
    background: var(--blue);
    color: #fff;
    border: none;
}

.stButton > button[kind="primary"]:hover {
    background: var(--blue-hover);
    box-shadow: 0 2px 8px rgba(37, 99, 235, 0.25);
}

/* ══════════════════════════════════════════════
   DATAFRAMES
   ══════════════════════════════════════════════ */

[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    overflow: hidden;
    box-shadow: var(--shadow-sm);
}

/* ══════════════════════════════════════════════
   CHARTS — seamless integration
   ══════════════════════════════════════════════ */

[data-testid="stPlotlyChart"] {
    margin: -0.15rem -0.3rem;
}

/* ══════════════════════════════════════════════
   UTILITY CLASSES
   ══════════════════════════════════════════════ */

/* ── Card title ── */
.card-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
}

.card-title-text {
    font-size: 0.94rem;
    font-weight: 700;
    color: var(--text);
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
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--text-muted);
    background: #f8fafc;
    border: 1px solid #e8edf5;
    border-radius: 9999px;
    padding: 0.15rem 0.5rem;
    margin-left: auto;
}

/* ── Hero value (portfolio total) ── */
.hero-value {
    font-size: 2rem;
    font-weight: 800;
    color: var(--text);
    letter-spacing: -1px;
    line-height: 1.15;
    margin: 0.15rem 0 0.3rem;
}

/* ── Subtle in-card divider ── */
.card-divider {
    height: 1px;
    background: var(--border-light);
    margin: 0.5rem 0;
}

/* ── Status dots (Linear-style) ── */
.status-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    vertical-align: middle;
}
.status-dot--ok     { background: var(--positive); box-shadow: 0 0 0 2px rgba(5,150,105,0.15); }
.status-dot--warn   { background: var(--warning);  box-shadow: 0 0 0 2px rgba(217,119,6,0.15); }
.status-dot--fail   { background: var(--negative); box-shadow: 0 0 0 2px rgba(220,38,38,0.15); }
.status-dot--none   { background: #e2e8f0; }
.status-dot--active { background: var(--blue);     box-shadow: 0 0 0 2px rgba(37,99,235,0.15); }

/* ── Data colors ── */
.c-pos { color: var(--positive); font-weight: 600; }
.c-neg { color: var(--negative); font-weight: 600; }

/* ── Dialog helpers ── */
.dlg-section {
    font-size: 0.82rem;
    font-weight: 700;
    color: var(--text);
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

.dlg-key { color: var(--text-muted); }
.dlg-val { font-weight: 600; color: var(--text); }

.dlg-insight {
    background: var(--warning-bg);
    border-left: 3px solid var(--warning);
    border-radius: 8px;
    padding: 0.6rem 0.8rem;
    margin: 0.5rem 0;
    font-size: 0.78rem;
    color: #92400e;
}

/* ══════════════════════════════════════════════
   RESPONSIVE
   ══════════════════════════════════════════════ */

@media (max-width: 768px) {
    .hero-value {
        font-size: 1.6rem;
    }

    [data-testid="stVerticalBlock"]
      > [data-testid="stVerticalBlockBorderWrapper"] {
        padding: 0.85rem 0.9rem;
    }
}

@media (max-width: 480px) {
    .hero-value {
        font-size: 1.4rem;
    }

    [data-testid="stVerticalBlock"]
      > [data-testid="stVerticalBlockBorderWrapper"] {
        padding: 0.75rem 0.85rem;
    }
}
</style>""",
        unsafe_allow_html=True,
    )
