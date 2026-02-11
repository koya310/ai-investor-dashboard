"""Card-first UI styles for a clean finance dashboard."""

import streamlit as st


def inject_css():
    """Inject modern card-based styling."""
    st.markdown(
        """<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #f3f5f9;
    --bg-accent: #edf2ff;
    --card: #ffffff;
    --border: #e7ecf4;
    --text: #0f172a;
    --muted: #64748b;
    --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.06);
    --shadow-md: 0 10px 28px rgba(15, 23, 42, 0.07);
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

[data-testid="stMetric"] {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 0.85rem 0.95rem;
    box-shadow: var(--shadow-sm);
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

[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1rem 1.05rem;
    box-shadow: var(--shadow-md);
}

[data-testid="stVerticalBlockBorderWrapper"] hr {
    margin: 0.4rem 0;
    border-color: #f1f4f9;
}

[data-testid="stExpander"] {
    border: 1px solid var(--border);
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.75);
    box-shadow: var(--shadow-sm);
}

details summary {
    font-size: 0.84rem;
    font-weight: 700;
    color: #334155;
}

[data-testid="stTabs"] [role="tablist"] {
    gap: 0.45rem;
}

[data-testid="stTabs"] [role="tab"] {
    background: #ffffff;
    border: 1px solid var(--border);
    border-radius: 9999px;
    padding: 0.35rem 0.8rem;
}

[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    border-color: #bfdbfe;
    background: #eff6ff;
}

[data-testid="stDialog"] {
    min-width: 760px;
    border-radius: 18px;
}

.stButton > button {
    border-radius: 10px;
    border: 1px solid #d8e1ee;
    background: #ffffff;
    color: #0f172a;
    font-weight: 600;
    transition: all 0.15s ease;
}

.stButton > button:hover {
    border-color: #bfd0e8;
    box-shadow: 0 5px 14px rgba(37, 99, 235, 0.14);
    transform: translateY(-1px);
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 14px;
    overflow: hidden;
    box-shadow: var(--shadow-sm);
}

.dlg-section {
    font-size: 0.82rem;
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
    font-size: 0.8rem;
    border-bottom: 1px solid #f8fafc;
}

.dlg-key {
    color: #64748b;
}

.dlg-val {
    font-weight: 600;
    color: #0f172a;
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
