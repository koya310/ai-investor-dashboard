"""共通定数・データ読み込み・ヘルパー"""

import logging

import dashboard_data as _dm
import streamlit as st

logger = logging.getLogger(__name__)

# ── カラーパレット ──
P = "#2563eb"  # primary blue
W = "#059669"  # win emerald
L = "#e11d48"  # loss rose

# ── 曜日 ──
WEEKDAY_JP = ["月", "火", "水", "木", "金", "土", "日"]

# ── モードラベル ──
MODE_LABELS = {
    "full": "フル実行",
    "medium": "中間実行",
    "light": "軽量実行",
    "news_only": "ニュース収集",
    "news_collect": "ニュース収集",
    "analysis_only": "分析のみ",
    "improvement": "改善サイクル",
}


# ── キャッシュ付きデータ読み込み ──
@st.cache_data(ttl=600, show_spinner="読み込み中...")
def load_daily(sd):
    return _dm.build_daily_portfolio(sd)


@st.cache_data(ttl=600, show_spinner=False)
def load_spy(sd):
    return _dm.get_spy_benchmark(sd)


@st.cache_data(ttl=120, show_spinner=False)
def load_alpaca_portfolio():
    return _dm.get_alpaca_portfolio()


@st.cache_data(ttl=120, show_spinner=False)
def load_alpaca_positions():
    return _dm.get_alpaca_positions()


@st.cache_data(ttl=120, show_spinner=False)
def load_positions_from_trades():
    return _dm.get_open_positions_from_trades()


@st.cache_data(ttl=120, show_spinner=False)
def load_pipeline_status():
    return _dm.get_todays_pipeline_status()


@st.cache_data(ttl=600, show_spinner=False)
def load_runs_timeline():
    return _dm.get_recent_runs_timeline(14)


@st.cache_data(ttl=600, show_spinner=False)
def load_health_metrics():
    return _dm.get_pipeline_health_metrics(7)


def load_common_data():
    """全ページ共通のデータをまとめて読み込む"""
    start = _dm.PHASE3_START
    daily = load_daily(start)
    spy = load_spy(start)
    trades = _dm.get_trades(start)
    kpi = _dm.get_kpi_summary(start)
    verdict = _dm.get_go_nogo_verdict(kpi)
    last_run = _dm.get_last_system_run()
    manual_holdings = _dm.get_manual_holdings()
    capital = _dm.INITIAL_CAPITAL

    alpaca_pf = load_alpaca_portfolio()
    alpaca_positions = load_alpaca_positions()
    if not alpaca_positions:
        alpaca_positions = load_positions_from_trades()

    return {
        "start": start,
        "daily": daily,
        "spy": spy,
        "trades": trades,
        "kpi": kpi,
        "verdict": verdict,
        "last_run": last_run,
        "manual_holdings": manual_holdings,
        "capital": capital,
        "alpaca_pf": alpaca_pf,
        "alpaca_positions": alpaca_positions,
    }
