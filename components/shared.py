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


# ── フォーマットヘルパー ──


def fmt_currency(val: float, show_sign: bool = False) -> str:
    """通貨フォーマット: $1,234 or +$1,234"""
    if show_sign:
        sign = "+" if val > 0 else ("-" if val < 0 else "")
        return f"{sign}${abs(val):,.0f}"
    return f"${val:,.0f}"


def fmt_pct(val: float, show_sign: bool = False, decimals: int = 1) -> str:
    """パーセントフォーマット: 12.3% or +12.3%"""
    if show_sign:
        sign = "+" if val > 0 else ("-" if val < 0 else "")
        return f"{sign}{abs(val):.{decimals}f}%"
    return f"{val:.{decimals}f}%"


def fmt_delta(val: float, is_pct: bool = False) -> str:
    """st.metric用のdelta文字列"""
    if is_pct:
        return fmt_pct(val, show_sign=True)
    return fmt_currency(val, show_sign=True)


def color_for_value(val: float) -> str:
    """正負で色を返す"""
    return W if val >= 0 else L


def color_for_status(status: str) -> str:
    """ステータス文字列から色を返す"""
    status_colors = {
        "completed": W,
        "running": "#f59e0b",
        "failed": L,
        "ok": W,
        "warn": "#f59e0b",
        "ng": L,
    }
    return status_colors.get(status, "#94a3b8")


def section_header(title: str, color: str = P, subtitle: str = "") -> None:
    """Section header with clean spacing and modern accent."""
    subtitle_html = (
        f'<span style="font-size:0.7rem;font-weight:600;color:#475569;'
        f'background:#e8edf5;border:1px solid #d4dce8;border-radius:9999px;'
        f'padding:0.2rem 0.55rem">{subtitle}</span>'
        if subtitle
        else ""
    )
    st.markdown(
        f'<div style="display:flex;align-items:center;justify-content:space-between;'
        f'gap:0.8rem;margin:1.35rem 0 0.65rem">'
        f'<div style="display:flex;align-items:center;gap:0.55rem">'
        f'<span style="width:10px;height:10px;border-radius:9999px;'
        f'background:{color};box-shadow:0 0 0 4px {color}22"></span>'
        f'<span style="font-size:1.0rem;font-weight:760;color:#0f172a;'
        f'letter-spacing:-0.02em">{title}</span>'
        f"</div>"
        f"{subtitle_html}"
        f"</div>",
        unsafe_allow_html=True,
    )


def render_pill(label: str, color: str = P) -> str:
    """インライン小バッジ（HTML文字列を返す）"""
    return (
        f'<span style="display:inline-flex;align-items:center;gap:0.28rem;'
        f'font-size:0.64rem;font-weight:700;color:{color};'
        f'background:{color}14;border:1px solid {color}30;'
        f'padding:0.16rem 0.5rem;border-radius:9999px;vertical-align:middle">'
        f'<span style="width:5px;height:5px;border-radius:9999px;'
        f'background:{color};display:inline-block"></span>{label}</span>'
    )


def nav_back(label: str, page: str) -> None:
    """ページ上部の戻るボタン"""
    if st.button(label):
        st.switch_page(page)


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
