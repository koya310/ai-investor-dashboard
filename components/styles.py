"""Card-first UI styles for a clean finance dashboard."""

import streamlit as st


def inject_css():
    """Inject modern card-based styling — white cards only, no grey borders."""
    st.markdown(
        """<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #f3f5f9;
    --card: #ffffff;
    --text: #0f172a;
    --muted: #64748b;
    --shadow-sm: 0 1px 3px rgba(15, 23, 42, 0.05);
    --shadow-md: 0 4px 20px rgba(15, 23, 42, 0.06);
}

html, body, [class*="css"] {
    font-family: "Plus Jakarta Sans", "Hiragino Kaku Gothic ProN", "Yu Gothic", sans-serif;
}

.stApp {
    background:
        radial-gradient(1000px 360px at 95% -10%, rgba(37, 99, 235, 0.08), transparent 55%),
        radial-gradient(900px 280px at -10% 0%, rgba(5, 150, 105, 0.05), transparent 50%),
        var(--bg);
    color: var(--text);
}

.block-container {
    padding-top: 1.25rem;
    padding-bottom: 2rem;
}

h1, h2, h3 {
    letter-spacing: -0.02em;
    font-weight: 700;
}

[data-testid="stSidebar"] {
    border-right: 1px solid rgba(231, 236, 244, 0.9);
}

[data-testid="stSidebar"] .block-container {
    padding-top: 1.1rem;
}

/* ══════════════════════════════════════════════════════════════
   NUCLEAR BORDER REMOVAL
   Streamlit puts borders on CHILD divs via inline styles.
   We must target both the wrapper AND its > div child.
   ══════════════════════════════════════════════════════════════ */

/* ── Container cards: white card with shadow ── */
[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: var(--card) !important;
    border: none !important;
    border-radius: 16px !important;
    box-shadow: var(--shadow-md) !important;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    padding: 0.9rem 1rem !important;
}

/* Nested cards: no shadow, no border */
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlockBorderWrapper"] > div {
    border: none !important;
    box-shadow: none !important;
    border-radius: 12px !important;
}

[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlockBorderWrapper"] {
    padding: 0.7rem 0.85rem !important;
}

[data-testid="stVerticalBlockBorderWrapper"] hr {
    margin: 0.4rem 0;
    border-color: #f0f3f8;
}

/* ── Metrics ── */
/* Standalone metric → white card */
[data-testid="stMetric"],
[data-testid="stMetric"] > div {
    background: var(--card) !important;
    border: none !important;
    border-radius: 14px !important;
    box-shadow: var(--shadow-sm) !important;
}

[data-testid="stMetric"] {
    padding: 0.85rem 0.95rem !important;
}

/* Metrics inside cards → flush (no double card) */
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMetric"],
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMetric"] > div,
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMetric"] *,
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMetricLabel"],
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMetricValue"],
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMetricDelta"] {
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    outline: none !important;
}

[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMetric"] {
    padding: 0.4rem 0.2rem !important;
}

[data-testid="stMetricLabel"] p {
    color: var(--muted);
    font-size: 0.67rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 700;
}

[data-testid="stMetricValue"] > div {
    font-size: 1.38rem;
    font-weight: 800;
    letter-spacing: -0.02em;
}

[data-testid="stMetricDelta"] {
    font-size: 0.74rem;
}

/* ── Expanders → white card, no border ── */
[data-testid="stExpander"],
[data-testid="stExpander"] > div {
    border: none !important;
    border-radius: 14px !important;
    background: var(--card) !important;
    box-shadow: var(--shadow-sm) !important;
}

details summary {
    font-size: 0.84rem;
    font-weight: 700;
    color: #334155;
}

/* ── Tabs → pill style (border is intentional here for tab shape) ── */
[data-testid="stTabs"] [role="tablist"] {
    gap: 0.45rem;
}

[data-testid="stTabs"] [role="tab"] {
    background: var(--card);
    border: 1px solid #e7ecf4;
    border-radius: 9999px;
    padding: 0.35rem 0.8rem;
}

[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    border-color: #bfdbfe;
    background: #eff6ff;
}

/* ── Dialogs ── */
[data-testid="stDialog"] {
    min-width: 760px;
    border-radius: 18px;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 10px;
    border: 1px solid #d8e1ee;
    background: var(--card);
    color: var(--text);
    font-weight: 600;
    transition: all 0.15s ease;
}

.stButton > button:hover {
    border-color: #bfd0e8;
    box-shadow: 0 5px 14px rgba(37, 99, 235, 0.14);
    transform: translateY(-1px);
}

/* ── DataFrames ── */
[data-testid="stDataFrame"] {
    border: none;
    border-radius: 14px;
    overflow: hidden;
    box-shadow: var(--shadow-sm);
}

/* ── Dialog-only classes (Tier 3) ── */
.dlg-section {
    font-size: 0.82rem;
    font-weight: 700;
    color: var(--text);
    border-bottom: 2px solid #e7ecf4;
    padding-bottom: 0.3rem;
    margin: 1rem 0 0.5rem;
}

.dlg-row {
    display: flex;
    justify-content: space-between;
    padding: 0.25rem 0;
    font-size: 0.8rem;
    border-bottom: 1px solid #f0f3f8;
}

.dlg-key { color: var(--muted); }

.dlg-val {
    font-weight: 600;
    color: var(--text);
}

.dlg-insight {
    background: #fff7ed;
    border-left: 3px solid #f59e0b;
    border-radius: 8px;
    padding: 0.6rem 0.8rem;
    margin: 0.5rem 0;
    font-size: 0.78rem;
    color: #92400e;
}

.c-pos { color: #059669; }
.c-neg { color: #e11d48; }
</style>""",
        unsafe_allow_html=True,
    )
