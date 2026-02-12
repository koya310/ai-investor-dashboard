"""共通定数・データ読み込み・ヘルパー"""

import logging

import dashboard_data as _dm
import streamlit as st

logger = logging.getLogger(__name__)

# ── カラーパレット (Design System v2.0 — Dark Theme) ──
P = "#6366f1"  # primary indigo (accent)
W = "#22c55e"  # win green (profit/success)
L = "#ef4444"  # loss red (negative/error)
WARN = "#f59e0b"  # warning amber
INFO = "#3b82f6"  # info blue
TEXT_MUTED = "#71717a"  # muted text (Zinc-500)
TEXT_SECONDARY = "#a1a1aa"  # secondary text (Zinc-400)

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
        "running": WARN,
        "failed": L,
        "ok": W,
        "warn": WARN,
        "ng": L,
    }
    return status_colors.get(status, TEXT_MUTED)


# ── UI コンポーネント ──


def card_title(title: str, color: str = P, subtitle: str = "") -> None:
    """Card title — MUST be called INSIDE st.container(border=True)."""
    subtitle_html = (
        f'<span class="card-subtitle">{subtitle}</span>' if subtitle else ""
    )
    st.markdown(
        f'<div class="card-title">'
        f'<span class="accent-dot" style="background:{color}"></span>'
        f'<span class="card-title-text">{title}</span>'
        f"{subtitle_html}"
        f"</div>",
        unsafe_allow_html=True,
    )


def section_header(title: str, color: str = P, subtitle: str = "") -> None:
    """Legacy section header — kept for backward compat but prefer card_title."""
    subtitle_html = (
        f'<span style="font-size:0.7rem;font-weight:600;color:{TEXT_SECONDARY};'
        f'background:#27272a;border:1px solid #3f3f46;border-radius:9999px;'
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
        f'<span style="font-size:1.0rem;font-weight:760;color:#fafafa;'
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
        f'font-size:0.72rem;font-weight:600;color:{color};'
        f'background:{color}14;border:1px solid {color}30;'
        f'padding:0.15rem 0.55rem;border-radius:9999px;vertical-align:middle">'
        f'<span style="width:6px;height:6px;border-radius:9999px;'
        f'background:{color};display:inline-block"></span>{label}</span>'
    )


def status_dot_html(status: str) -> str:
    """CSS status dot (Linear-style). Returns raw HTML."""
    css_class = {
        "completed": "status-dot--ok",
        "ok": "status-dot--ok",
        "failed": "status-dot--fail",
        "error": "status-dot--fail",
        "warn": "status-dot--warn",
        "skipped": "status-dot--warn",
        "interrupted": "status-dot--warn",
        "running": "status-dot--active",
        "pending": "status-dot--none",
    }.get(status, "status-dot--none")
    return f'<span class="status-dot {css_class}"></span>'


def status_badge(label: str, status: str) -> str:
    """Status badge (dot + label pill). Returns raw HTML. Dark theme."""
    # (text_color, bg_tint, border_color)
    configs = {
        "completed": ("#4ade80", "#052e16", "#166534"),
        "ok":        ("#4ade80", "#052e16", "#166534"),
        "failed":    ("#f87171", "#450a0a", "#991b1b"),
        "error":     ("#f87171", "#450a0a", "#991b1b"),
        "skipped":   ("#fbbf24", "#451a03", "#92400e"),
        "interrupted": ("#fbbf24", "#451a03", "#92400e"),
        "warn":      ("#fbbf24", "#451a03", "#92400e"),
        "pending":   ("#a1a1aa", "#27272a", "#3f3f46"),
        "running":   ("#818cf8", "#1e1b4b", "#3730a3"),
    }
    text_c, bg_c, border_c = configs.get(status, configs["pending"])
    return (
        f'<span style="display:inline-flex;align-items:center;gap:0.3rem;'
        f'font-size:0.72rem;font-weight:600;color:{text_c};'
        f'background:{bg_c};border:1px solid {border_c};'
        f'padding:0.15rem 0.55rem;border-radius:9999px">'
        f'{status_dot_html(status)} {label}</span>'
    )


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
