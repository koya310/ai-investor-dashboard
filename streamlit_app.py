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
    st.markdown("### AI Investor")
    st.caption("Phase 3 ペーパートレード運用ダッシュボード")

    # Go/No-Go カウントダウン
    deadline_dt = datetime.strptime(_dm.GONOGO_DEADLINE, "%Y-%m-%d")
    days_left = max((deadline_dt - datetime.now()).days, 0)
    st.metric(
        "Go/No-Go 判定まで",
        f"{days_left}日",
        delta=f"期限: {_dm.GONOGO_DEADLINE}",
        delta_color="off",
    )

    if st.button("データを再読込", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

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

    with st.expander("使い方", expanded=False):
        st.markdown(
            """
            1. `ポートフォリオ` で Go/No-Go 判定と資産推移を確認
            2. `パイプライン` で本日の実行ステップと異常有無を確認
            3. `日付詳細` で特定日のニュース〜取引まで追跡
            4. `システム仕様` で計算式・判定条件を参照
            """
        )

    st.divider()
    st.caption(f"Phase 3 開始: {_dm.PHASE3_START}")
    st.caption(f"初期資本: ${_dm.INITIAL_CAPITAL:,.0f}")

nav.run()
