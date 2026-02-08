"""
AI Investor ダッシュボード — マルチページ版

起動:
    streamlit run streamlit_app.py --server.port 8514
"""

import logging
from datetime import datetime

import dashboard_data as _dm
import streamlit as st

from components.shared import P, L, load_common_data
from components.styles import get_global_css

logger = logging.getLogger(__name__)

st.set_page_config(page_title="AI Investor", layout="wide")
st.markdown(get_global_css(), unsafe_allow_html=True)

# ── 共通データ読み込み ──
data = load_common_data()

# ── サイドバー（全ページ共通） ──
with st.sidebar:
    st.markdown("#### AI Investor")

    deadline = datetime.strptime(_dm.GONOGO_DEADLINE, "%Y-%m-%d")
    days_left = max((deadline - datetime.now()).days, 0)
    cd_color = P if days_left > 14 else ("#d97706" if days_left > 7 else L)

    urgency = ""
    if days_left <= 7:
        urgency = f'<div class="urgency-text" style="color:{L}">要注意</div>'
    elif days_left <= 14:
        urgency = f'<div class="urgency-text" style="color:#d97706">残りわずか</div>'

    st.markdown(
        f"""<div style="padding:0.6rem 0 0.8rem">
            <div class="cd-num" style="color:{cd_color}">{days_left}<span style="font-size:0.9rem; font-weight:600">日</span></div>
            <div class="cd-label">判定まで</div>
            {urgency}
        </div>""",
        unsafe_allow_html=True,
    )

    if st.button("更新", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    last_run = data["last_run"]
    if last_run:
        run_time = last_run["started_at"][:16].replace("T", " ")
        run_status = last_run["status"]
        if run_status == "completed":
            st.markdown(
                f'<div style="font-size:0.78rem; color:#64748b; margin-top:0.5rem">'
                f'<span class="status-dot status-dot-ok"></span>'
                f'<span class="c-pos" style="font-weight:600">正常稼働</span>'
                f"<br>{run_time}</div>",
                unsafe_allow_html=True,
            )
        elif run_status == "running":
            st.markdown(
                f'<div style="font-size:0.78rem; color:#64748b; margin-top:0.5rem">'
                f'<span class="status-dot status-dot-warn"></span>'
                f'<span style="color:#d97706; font-weight:600">実行中</span>'
                f"<br>{run_time}</div>",
                unsafe_allow_html=True,
            )
        else:
            err = (
                last_run["error_message"][:40]
                if last_run["error_message"]
                else run_status
            )
            st.markdown(
                f'<div style="font-size:0.78rem; color:#64748b; margin-top:0.5rem">'
                f'<span class="status-dot status-dot-ng"></span>'
                f'<span class="c-neg" style="font-weight:600">異常あり</span>'
                f"<br>{err}</div>",
                unsafe_allow_html=True,
            )

    manual_holdings = data["manual_holdings"]
    if manual_holdings:
        st.markdown("---")
        st.markdown(
            '<div style="font-size:0.68rem; color:#94a3b8; letter-spacing:0.06em; '
            'font-weight:600; margin-bottom:0.3rem">実保有（参考）</div>',
            unsafe_allow_html=True,
        )
        for h in manual_holdings:
            st.markdown(
                f'<div style="font-size:0.8rem; color:#64748b">'
                f'{h["ticker"]} {h["shares"]}株 @${h["average_price"]:.0f}</div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.markdown(
        f'<div style="font-size:0.73rem; color:#94a3b8">'
        f"開始 {data['start']}<br>判定 {_dm.GONOGO_DEADLINE}</div>",
        unsafe_allow_html=True,
    )

# ── ページナビゲーション ──
pages = {
    "Dashboard": [
        st.Page("pages/home.py", title="Home", icon=":material/home:"),
        st.Page("pages/pipeline.py", title="Pipeline", icon=":material/sync:"),
    ],
    "Detail": [
        st.Page("pages/date_detail.py", title="Date Detail", icon=":material/calendar_today:"),
    ],
    "System": [
        st.Page("pages/reference.py", title="Reference", icon=":material/menu_book:"),
    ],
}

pg = st.navigation(pages)
pg.run()
