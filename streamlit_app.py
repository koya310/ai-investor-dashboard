"""AI Investor Dashboard — メインアプリ"""

import logging
from datetime import datetime

import dashboard_data as _dm
import streamlit as st

from components.styles import inject_css

logger = logging.getLogger(__name__)

# ── ページ設定 ──
st.set_page_config(
    page_title="AI Investor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 最小限のCSS注入
inject_css()

# ── ナビゲーション ──
home_page = st.Page("pages/home.py", title="ポートフォリオ", icon="📊", default=True)
pipeline_page = st.Page("pages/pipeline.py", title="パイプライン", icon="⚙️")
date_detail_page = st.Page("pages/date_detail.py", title="日付詳細", icon="📅")
reference_page = st.Page("pages/reference.py", title="システム仕様", icon="📋")

nav = st.navigation(
    [home_page, pipeline_page, date_detail_page, reference_page],
    position="sidebar",
)

# ── サイドバー ──
with st.sidebar:
    st.markdown(
        '<div style="font-size:1.1rem;font-weight:800;letter-spacing:-0.02em;'
        'color:#1a1d26;margin-bottom:0.1rem">AI Investor</div>',
        unsafe_allow_html=True,
    )
    st.caption("Phase 3 ペーパートレード監視")

    st.divider()

    # Go/No-Go カウントダウン
    deadline_dt = datetime.strptime(_dm.GONOGO_DEADLINE, "%Y-%m-%d")
    days_left = max((deadline_dt - datetime.now()).days, 0)
    st.metric(
        "Go/No-Go 判定まで",
        f"{days_left}日",
        delta=f"期限: {_dm.GONOGO_DEADLINE}",
        delta_color="off",
    )

    # システム状態
    last_run = _dm.get_last_system_run()
    if last_run:
        status = last_run["status"]
        if status == "completed":
            st.success(f"正常稼働  {last_run['started_at'][:16]}")
        elif status == "running":
            st.warning(f"実行中  {last_run['started_at'][:16]}")
        else:
            st.error(f"異常  {last_run['started_at'][:16]}")
            if last_run["error_message"]:
                st.caption(last_run["error_message"][:100])
    else:
        st.info("実行記録なし")

    st.divider()

    if st.button("データを再読込", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

nav.run()
