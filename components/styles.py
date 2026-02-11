"""Card-first UI styles for a clean finance dashboard."""

import streamlit as st


def inject_css():
    """Inject modern card-based styling — white cards, no borders, shadow only."""
    st.markdown(
        """<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #f3f5f9;
    --card: #ffffff;
    --text: #0f172a;
    --muted: #64748b;
    --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.04), 0 1px 5px rgba(15, 23, 42, 0.03);
    --shadow-md: 0 2px 8px rgba(15, 23, 42, 0.05), 0 4px 20px rgba(15, 23, 42, 0.04);
    --radius-lg: 16px;
    --radius-md: 12px;
    --radius-sm: 10px;
}

/* ── Typography ── */
html, body, [class*="css"] {
    font-family: "Plus Jakarta Sans", -apple-system, BlinkMacSystemFont,
                 "Hiragino Kaku Gothic ProN", "Yu Gothic", sans-serif;
}

.stApp {
    background:
        radial-gradient(ellipse 1100px 400px at 92% -8%, rgba(37, 99, 235, 0.06), transparent 60%),
        radial-gradient(ellipse 900px 300px at -5% 4%, rgba(5, 150, 105, 0.04), transparent 55%),
        var(--bg);
    color: var(--text);
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2.5rem;
    max-width: 1120px;
}

h1 { font-size: 1.65rem; font-weight: 800; letter-spacing: -0.03em; margin-bottom: 0.3rem; }
h2 { font-size: 1.2rem; font-weight: 700; letter-spacing: -0.02em; }
h3 { font-size: 1.0rem; font-weight: 700; letter-spacing: -0.01em; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    border-right: 1px solid rgba(231, 236, 244, 0.7) !important;
}
[data-testid="stSidebar"] .block-container {
    padding-top: 1.1rem;
}

/* ══════════════════════════════════════════════════════════════
   BORDER REMOVAL — config.toml sets borderColor=transparent
   globally. These rules add card styling (bg + shadow + radius)
   and fix any remaining border via correct selectors.
   ══════════════════════════════════════════════════════════════ */

/* Belt-and-suspenders: also kill borders on the correct element */
div[data-testid="stVerticalBlock"],
div[data-testid="stMetric"],
div[data-testid="stExpander"],
div[data-testid="stForm"] {
    border: none !important;
    border-color: transparent !important;
}

/* ── Top-level cards: white + shadow ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--card);
    border-radius: var(--radius-lg);
    padding: 1rem 1.15rem;
    box-shadow: var(--shadow-md);
    margin-bottom: 0.3rem;
}

/* Nested cards: subtle elevation, no outer shadow */
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--card);
    border-radius: var(--radius-md);
    padding: 0.75rem 0.9rem;
    box-shadow: none;
}

[data-testid="stVerticalBlockBorderWrapper"] hr {
    margin: 0.4rem 0;
    border-color: #eef1f6;
    opacity: 0.7;
}

/* ── Metrics ── */
/* Standalone metric */
[data-testid="stMetric"] {
    background: var(--card);
    border-radius: var(--radius-md);
    padding: 0.75rem 0.85rem;
    box-shadow: var(--shadow-sm);
}

/* Metrics inside cards → flush, no double-card */
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMetric"] {
    background: transparent !important;
    border-radius: 0 !important;
    padding: 0.4rem 0.15rem !important;
    box-shadow: none !important;
}

[data-testid="stMetricLabel"] p {
    color: var(--muted);
    font-size: 0.66rem;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    font-weight: 700;
}

[data-testid="stMetricValue"] > div {
    font-size: 1.35rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    line-height: 1.2;
}

[data-testid="stMetricDelta"] {
    font-size: 0.72rem;
}

/* ── Expanders ── */
[data-testid="stExpander"] {
    border-radius: var(--radius-md);
    background: var(--card);
    box-shadow: var(--shadow-sm);
}

details summary {
    font-size: 0.84rem;
    font-weight: 700;
    color: #334155;
}

/* ── Tabs → pill ── */
[data-testid="stTabs"] [role="tablist"] {
    gap: 0.4rem;
}
[data-testid="stTabs"] [role="tab"] {
    background: var(--card);
    border: 1px solid #dfe5ef !important;
    border-radius: 9999px;
    padding: 0.32rem 0.75rem;
    font-size: 0.82rem;
    font-weight: 600;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    border-color: #bfdbfe !important;
    background: #eff6ff;
    color: #1d4ed8;
}

/* ── Dialogs ── */
[data-testid="stDialog"] {
    min-width: 760px;
    border-radius: 20px;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: var(--radius-sm);
    border: 1px solid #dce3ee !important;
    background: var(--card);
    color: var(--text);
    font-weight: 600;
    font-size: 0.84rem;
    padding: 0.4rem 1rem;
    transition: all 0.15s ease;
}
.stButton > button:hover {
    border-color: #c4d0e3 !important;
    box-shadow: 0 3px 12px rgba(37, 99, 235, 0.1);
    transform: translateY(-1px);
}
.stButton > button:active {
    transform: translateY(0);
    box-shadow: var(--shadow-sm);
}

/* ── DataFrames ── */
[data-testid="stDataFrame"] {
    border-radius: var(--radius-md);
    overflow: hidden;
    box-shadow: var(--shadow-sm);
}

/* ── Alert boxes ── */
[data-testid="stAlert"] {
    border-radius: var(--radius-sm);
    font-size: 0.84rem;
}

/* ── Progress bars ── */
[data-testid="stProgress"] > div > div {
    border-radius: 6px;
    height: 6px;
}

/* ── Radio / toggle group ── */
[data-testid="stRadio"] > div {
    gap: 0.4rem;
}

/* ── Captions ── */
[data-testid="stCaptionContainer"] {
    font-size: 0.76rem;
    color: #94a3b8;
}

/* ── Dialog-only helper classes (Tier 3) ── */
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
.c-neg { color: #e11d48; }
</style>""",
        unsafe_allow_html=True,
    )
