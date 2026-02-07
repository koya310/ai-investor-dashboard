"""
AI Investor ダッシュボード

起動:
    cd AI_Investor
    .venv/bin/streamlit run 02_src/11_monitoring/streamlit_dashboard.py
"""

import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

import dashboard_data as _dm
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="AI Investor", layout="wide")

# ============================================================
# カラーパレット（3色 + ニュートラル）
# ============================================================
P = "#2563eb"  # primary blue
W = "#059669"  # win emerald
L = "#e11d48"  # loss rose

st.markdown(
    """
<style>
/* ── Page ── */
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main .block-container { background: #f8fafc; }
[data-testid="stHeader"] { background: #f8fafc; }

/* ── Card ── */
.card {
    background: #fff;
    border-radius: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06);
    padding: 1.4rem 1.5rem;
    margin-bottom: 0.9rem;
}
.card-sm {
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    padding: 0.9rem 1.15rem;
    margin-bottom: 0.55rem;
}

/* ── Section header ── */
.sec-hdr {
    display: flex; align-items: center; gap: 0.6rem;
    margin-top: 1.6rem; margin-bottom: 0.7rem;
}
.sec-hdr .bar {
    width: 4px; height: 1.4rem; border-radius: 2px;
}
.sec-hdr .txt {
    font-size: 0.95rem; font-weight: 700; color: #0f172a;
}
.sec-hdr .sub {
    font-size: 0.73rem; color: #94a3b8; margin-left: 0.3rem; font-weight: 400;
}

/* ── Color utils ── */
.c-pos  { color: #059669; }
.c-neg  { color: #e11d48; }
.c-dim  { color: #94a3b8; }
.c-sub  { color: #64748b; }
.c-pri  { color: #2563eb; }

/* ── Pill ── */
.pill {
    display: inline-block; padding: 0.18rem 0.6rem;
    border-radius: 999px; font-size: 0.72rem; font-weight: 600;
}
.pill-blue  { background: #eff6ff; color: #2563eb; }
.pill-green { background: #ecfdf5; color: #059669; }
.pill-red   { background: #fff1f2; color: #e11d48; }

/* ── Split boxes (equity/cash) ── */
.split-row {
    display: flex; gap: 0.8rem;
    margin-top: 1rem; padding: 0 1.5rem;
}
.split-box {
    flex: 1; border-radius: 12px; padding: 0.7rem 0.8rem;
    text-align: center;
}
.split-val { font-size: 1.15rem; font-weight: 700; line-height: 1.2; }
.split-label { font-size: 0.68rem; margin-top: 0.15rem; }

/* ── Position row (inside hero) ── */
.pos-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.5rem 0.4rem;
    border-bottom: 1px solid #f1f5f9;
}
.pos-row:last-child { border-bottom: none; }

/* ── Checklist gauge ── */
.cl-row {
    display: flex; align-items: center; gap: 1rem;
    padding: 0.7rem 0; border-bottom: 1px solid #f1f5f9;
}
.cl-row:last-child { border-bottom: none; }
.cl-label { width: 6rem; flex-shrink: 0; }
.cl-label-txt { font-size: 0.75rem; font-weight: 600; color: #64748b; }
.cl-label-tip { font-size: 0.62rem; color: #94a3b8; margin-top: 0.1rem; }
.cl-bar-wrap { flex: 1; }
.cl-bar-track {
    background: #f1f5f9; border-radius: 6px; height: 10px;
    position: relative; overflow: hidden;
}
.cl-bar-fill { height: 100%; border-radius: 6px; transition: width 0.3s; }
.cl-nums { display: flex; justify-content: space-between; margin-top: 0.2rem; }
.cl-cur { font-size: 0.82rem; font-weight: 700; }
.cl-tgt { font-size: 0.7rem; color: #94a3b8; }
.cl-gap { text-align: right; width: 7rem; flex-shrink: 0; }
.cl-gap-txt { font-size: 0.78rem; font-weight: 600; }
.cl-gap-sub { font-size: 0.62rem; color: #94a3b8; margin-top: 0.1rem; }

/* ── Verdict ── */
.verdict {
    border-radius: 12px; padding: 0.8rem 1.2rem;
    font-size: 0.84rem; margin-top: 0.6rem; line-height: 1.5;
}
.v-go   { background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
.v-cond { background: #fffbeb; color: #92400e; border: 1px solid #fde68a; }
.v-ng   { background: #fff1f2; color: #9f1239; border: 1px solid #fecdd3; }

/* ── Trade card ── */
.tr-card {
    background: #fff; border-radius: 12px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    padding: 0.75rem 1.1rem; margin-bottom: 0.45rem;
    border-left: 4px solid #e2e8f0;
    display: flex; justify-content: space-between; align-items: center;
}
.tr-win  { border-left-color: #059669; }
.tr-loss { border-left-color: #e11d48; }
.tr-open { border-left-color: #2563eb; }
.tr-best { background: #ecfdf5; border-left-color: #059669; }
.tr-worst { background: #fff1f2; border-left-color: #e11d48; }

/* ── Sidebar ── */
[data-testid="stSidebar"] { background: #f8fafc; }
.cd-num { font-size: 2.4rem; font-weight: 800; line-height: 1; text-align: center; }
.cd-label { font-size: 0.72rem; color: #94a3b8; text-align: center; margin-top: 0.15rem; }

/* ── Mini stat ── */
.mini-stat { text-align: center; padding: 0.3rem 0; }
.mini-val { font-size: 1.1rem; font-weight: 700; color: #0f172a; }
.mini-label { font-size: 0.65rem; color: #94a3b8; margin-top: 0.1rem; }

/* ── Dialog styling ── */
.dlg-section {
    font-size: 0.78rem; font-weight: 700; color: #0f172a;
    margin-top: 1rem; margin-bottom: 0.4rem;
    padding-bottom: 0.3rem; border-bottom: 2px solid #f1f5f9;
}
.dlg-row {
    display: flex; justify-content: space-between;
    padding: 0.35rem 0; font-size: 0.82rem;
    border-bottom: 1px solid #f8fafc;
}
.dlg-key { color: #64748b; }
.dlg-val { font-weight: 600; color: #0f172a; }
.dlg-insight {
    background: #fffbeb; border: 1px solid #fde68a; border-radius: 10px;
    padding: 0.7rem 1rem; margin-top: 0.7rem;
    font-size: 0.8rem; color: #92400e; line-height: 1.6;
}

/* ── Workflow stepper (投資プロセス tab) ── */
.wf-intro {
    background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 12px;
    padding: 0.8rem 1.2rem; margin-bottom: 0.8rem;
    font-size: 0.78rem; color: #1e40af; line-height: 1.6;
}
.wf-step {
    display: flex; align-items: center; gap: 0.9rem;
    padding: 0.7rem 1rem;
    border-bottom: 1px solid #f1f5f9;
}
.wf-step:last-child { border-bottom: none; }
.wf-num {
    width: 28px; height: 28px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.72rem; font-weight: 700; flex-shrink: 0;
}
.wf-n-ok   { background: #ecfdf5; color: #059669; border: 2px solid #a7f3d0; }
.wf-n-fail { background: #fff1f2; color: #e11d48; border: 2px solid #fecdd3; }
.wf-n-wait { background: #f8fafc; color: #94a3b8; border: 2px dashed #cbd5e1; }
.wf-body { flex: 1; min-width: 0; }
.wf-name { font-size: 0.88rem; font-weight: 700; color: #0f172a; }
.wf-desc { font-size: 0.72rem; color: #94a3b8; margin-top: 0.1rem; }
.wf-right { text-align: right; flex-shrink: 0; min-width: 65px; }
.wf-val  { font-size: 1.05rem; font-weight: 700; color: #0f172a; }
.wf-ts   { font-size: 0.62rem; color: #94a3b8; margin-top: 0.1rem; }

/* ── Drill-down <details> ── */
.dd-item {
    padding: 0.45rem 0.7rem; border-bottom: 1px solid #f1f5f9;
}
.dd-item:last-child { border-bottom: none; }
.dd-summary {
    cursor: pointer; font-size: 0.82rem; color: #0f172a;
    padding: 0.15rem 0; list-style: none;
}
.dd-summary::-webkit-details-marker { display: none; }
.dd-summary::before {
    content: "\25B8"; margin-right: 0.4rem; color: #94a3b8;
    display: inline-block; transition: transform 0.15s;
}
details[open] > .dd-summary::before { transform: rotate(90deg); }
.dd-detail {
    margin-top: 0.4rem; padding: 0.55rem 0.8rem;
    background: #f8fafc; border-radius: 8px;
    font-size: 0.76rem; color: #475569; line-height: 1.65;
}
.dd-kv { display: flex; gap: 0.5rem; padding: 0.15rem 0; }
.dd-k { color: #94a3b8; min-width: 5rem; flex-shrink: 0; }
.dd-v { color: #0f172a; }

/* ── Timeline (System Ops tab) ── */
.tl-row {
    display: flex; align-items: center; gap: 0.7rem;
    padding: 0.55rem 0.8rem; border-bottom: 1px solid #f1f5f9;
}
.tl-row:last-child { border-bottom: none; }
.tl-date { width: 5.5rem; font-size: 0.78rem; font-weight: 600; color: #64748b; }
.tl-dot { width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0; }
.tl-ok   { background: #059669; }
.tl-warn { background: #f59e0b; }
.tl-fail { background: #e11d48; }
.tl-empty { background: #e2e8f0; }
.tl-info { flex: 1; font-size: 0.78rem; color: #0f172a; }
.tl-sub  { font-size: 0.68rem; color: #94a3b8; margin-left: 0.3rem; }
.tl-nums { font-size: 0.72rem; color: #64748b; text-align: right; white-space: nowrap; }

/* ── Health metric ── */
.health-val { font-size: 1.5rem; font-weight: 800; color: #0f172a; text-align: center; }
.health-label { font-size: 0.65rem; color: #94a3b8; text-align: center; margin-top: 0.1rem; }

/* ── Info tooltip (? icon) ── */
.wf-info {
    display: inline-flex; align-items: center; justify-content: center;
    width: 16px; height: 16px; border-radius: 50%;
    background: #e2e8f0; color: #64748b; font-size: 0.6rem; font-weight: 700;
    cursor: help; margin-left: 0.35rem; position: relative; vertical-align: middle;
    transition: background 0.15s;
}
.wf-info:hover { background: #2563eb; color: #fff; }
.wf-tip {
    visibility: hidden; opacity: 0;
    position: absolute; bottom: calc(100% + 8px); left: 50%;
    transform: translateX(-50%); width: 260px;
    background: #1e293b; color: #f1f5f9; font-size: 0.68rem; font-weight: 400;
    line-height: 1.55; padding: 0.6rem 0.8rem; border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    z-index: 1000; pointer-events: none;
    transition: opacity 0.15s, visibility 0.15s;
}
.wf-tip::after {
    content: ""; position: absolute; top: 100%; left: 50%;
    transform: translateX(-50%);
    border: 5px solid transparent; border-top-color: #1e293b;
}
.wf-info:hover .wf-tip { visibility: visible; opacity: 1; }

/* ── Spec tab ── */
.spec-section {
    margin-bottom: 1.2rem;
}
.spec-title {
    display: flex; align-items: center; gap: 0.5rem;
    font-size: 0.9rem; font-weight: 700; color: #0f172a;
    padding: 0.7rem 1rem; border-bottom: 2px solid #f1f5f9;
}
.spec-icon { font-size: 1rem; }
.spec-grid {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 0.1rem; padding: 0.2rem 0.5rem;
}
@media (max-width: 768px) {
    .spec-grid { grid-template-columns: 1fr; }
    .cl-label { width: auto; min-width: 3.5rem; font-size: 0.7rem; }
    .cl-gap { width: auto; min-width: 4rem; font-size: 0.7rem; }
    .wf-step { flex-direction: column; }
    .wf-right { min-width: auto; text-align: left; margin-top: 0.3rem; }
    .tl-date { width: 4rem; font-size: 0.7rem; }
    .tl-nums { font-size: 0.65rem; }
    .wf-tip { width: 200px; font-size: 0.68rem; left: 0; transform: none; }
    .pos-row { flex-direction: column; gap: 0.2rem; }
    .split-row { flex-direction: column; gap: 0.5rem; }
}
.spec-row {
    display: flex; justify-content: space-between; align-items: baseline;
    padding: 0.4rem 0.5rem; border-bottom: 1px solid #f8fafc;
    font-size: 0.78rem;
}
.spec-row:last-child { border-bottom: none; }
.spec-k { color: #64748b; }
.spec-v { font-weight: 600; color: #0f172a; text-align: right; }
.spec-note {
    font-size: 0.72rem; color: #94a3b8; padding: 0.4rem 1rem 0.6rem;
    line-height: 1.55;
}
.spec-list {
    padding: 0.3rem 1rem 0.5rem; font-size: 0.76rem; color: #475569;
    line-height: 1.7;
}
.spec-list li { margin-bottom: 0.15rem; }
.spec-badge {
    display: inline-block; padding: 0.1rem 0.4rem; border-radius: 4px;
    font-size: 0.65rem; font-weight: 600; margin-right: 0.3rem;
}
.spec-b1 { background: #dbeafe; color: #1d4ed8; }
.spec-b2 { background: #ecfdf5; color: #059669; }
.spec-b3 { background: #f1f5f9; color: #64748b; }
.spec-highlight {
    background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 10px;
    padding: 0.7rem 1rem; margin: 0.5rem 1rem 0.8rem;
    font-size: 0.76rem; color: #1e40af; line-height: 1.6;
}

/* ── News utilization ── */
.nu-flow {
    display: flex; align-items: center; justify-content: center;
    gap: 0; padding: 0.8rem 0; flex-wrap: wrap;
}
.nu-node {
    text-align: center; padding: 0.5rem 0.7rem;
    border-radius: 10px; min-width: 80px;
}
.nu-active { background: #ecfdf5; border: 1.5px solid #a7f3d0; }
.nu-empty  { background: #f8fafc; border: 1.5px dashed #cbd5e1; }
.nu-icon   { font-size: 1rem; }
.nu-label  { font-size: 0.65rem; font-weight: 600; color: #64748b; margin-top: 0.1rem; }
.nu-val    { font-size: 0.95rem; font-weight: 700; color: #0f172a; }
.nu-arrow  { color: #cbd5e1; font-size: 1rem; margin: 0 0.15rem; }
.nu-src-bar {
    display: flex; align-items: center; gap: 0.5rem;
    padding: 0.25rem 0; font-size: 0.75rem;
}
.nu-src-name { width: 7rem; color: #64748b; flex-shrink: 0; text-align: right; }
.nu-src-fill { height: 6px; border-radius: 3px; background: #2563eb; }
.nu-src-cnt  { color: #94a3b8; font-size: 0.68rem; min-width: 2.5rem; }
.nu-theme-card {
    display: inline-flex; align-items: center; gap: 0.4rem;
    padding: 0.3rem 0.6rem; border-radius: 8px;
    background: #fff; border: 1px solid #e2e8f0;
    font-size: 0.72rem; margin: 0.2rem;
}
.nu-score { font-weight: 700; }

/* ── Streamlit overrides ── */
.stMarkdown { margin-bottom: 0; }
div[data-testid="stVerticalBlock"] > div:has(> .stMarkdown) { padding-top: 0; padding-bottom: 0; }
h1, h2, h3, h4 { color: #0f172a; }
div[data-testid="stPlotlyChart"] > div {
    border-radius: 16px; overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06);
}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# 詳細分析ダイアログ
# ============================================================


@st.dialog("パフォーマンス詳細分析", width="large")
def show_analysis_dialog():
    """チェックリストの「なぜ」を深掘りするダイアログ"""
    tr = _dm.get_trades(start)
    summary = _dm.get_trade_summary(tr)
    patterns = _dm.get_trade_patterns(tr)

    # ── 損益の概要 ──
    st.markdown('<div class="dlg-section">損益の全体像</div>', unsafe_allow_html=True)
    rows = [
        ("決済回数", f"{summary['total']}回"),
        ("勝敗", f"{summary['wins']}勝 {summary['losses']}敗"),
        ("勝率", f"{summary['win_rate']}%"),
        ("累積損益", f"${summary['total_pnl']:+,.0f}"),
        ("プロフィットファクター", f"{summary['profit_factor']:.2f}"),
        ("平均利益（勝ち）", f"{summary['avg_profit_pct']:+.2f}%"),
        ("平均損失（負け）", f"{summary['avg_loss_pct']:+.2f}%"),
        ("最大利益", f"{summary['largest_win_pct']:+.2f}%"),
        ("最大損失", f"{summary['largest_loss_pct']:+.2f}%"),
        ("平均保有日数", f"{summary['avg_holding_days']:.1f}日"),
    ]
    html = ""
    for k, v in rows:
        html += f'<div class="dlg-row"><span class="dlg-key">{k}</span><span class="dlg-val">{v}</span></div>'
    st.markdown(html, unsafe_allow_html=True)

    # ── 問題診断 ──
    insights = []
    if summary["total"] > 0:
        if summary["win_rate"] < 50:
            insights.append(
                f"勝率が{summary['win_rate']}%と低い: "
                f"{summary['losses']}回中ほとんどが損失。"
                "シグナル品質（銘柄選定・タイミング）の改善が最優先。"
            )
        if summary["avg_loss_pct"] != 0 and summary["avg_profit_pct"] != 0:
            rr = abs(summary["avg_profit_pct"] / summary["avg_loss_pct"])
            if rr < 1.5:
                insights.append(
                    f"リスクリワード比が{rr:.2f}と不十分 "
                    f"（勝ち平均{summary['avg_profit_pct']:+.2f}% vs 負け平均{summary['avg_loss_pct']:+.2f}%）。"
                    "利確を伸ばすか、損切りを早くする必要あり。"
                )
        if summary["profit_factor"] < 1.0:
            insights.append(
                f"プロフィットファクターが{summary['profit_factor']:.2f}（1.0未満 = 損失 > 利益）。"
                "トータルで負けている状態。"
            )

    if insights:
        items = "".join(
            f"<div style='margin-bottom:0.4rem'>- {i}</div>" for i in insights
        )
        st.markdown(
            f'<div class="dlg-insight"><b>問題点</b>{items}</div>',
            unsafe_allow_html=True,
        )

    # ── 銘柄別パフォーマンス ──
    closed = tr[tr["status"] == "CLOSED"]
    if len(closed) > 0:
        st.markdown(
            '<div class="dlg-section">銘柄別パフォーマンス</div>',
            unsafe_allow_html=True,
        )
        ticker_stats = []
        for ticker, grp in closed.groupby("ticker"):
            wins = len(grp[grp["profit_loss"] > 0])
            ticker_stats.append(
                {
                    "ticker": ticker,
                    "trades": len(grp),
                    "wins": wins,
                    "pnl": grp["profit_loss"].sum(),
                    "avg_pct": grp["profit_loss_pct"].mean(),
                }
            )
        ticker_stats.sort(key=lambda x: x["pnl"])

        html = ""
        for ts in ticker_stats:
            c = "c-pos" if ts["pnl"] >= 0 else "c-neg"
            sign = "+" if ts["pnl"] >= 0 else ""
            html += (
                f'<div class="dlg-row">'
                f'<span class="dlg-key"><b>{ts["ticker"]}</b> '
                f'{ts["wins"]}/{ts["trades"]}勝</span>'
                f'<span class="{c}" style="font-weight:600">'
                f'{sign}${ts["pnl"]:.0f} ({sign}{ts["avg_pct"]:.1f}%)</span></div>'
            )
        st.markdown(html, unsafe_allow_html=True)

    # ── テーマ別 ──
    by_theme = patterns.get("by_theme", {})
    if by_theme:
        st.markdown('<div class="dlg-section">テーマ別</div>', unsafe_allow_html=True)
        html = ""
        for theme, data in sorted(by_theme.items(), key=lambda x: x[1]["total_pnl"]):
            c = "c-pos" if data["total_pnl"] >= 0 else "c-neg"
            sign = "+" if data["total_pnl"] >= 0 else ""
            html += (
                f'<div class="dlg-row">'
                f'<span class="dlg-key">{theme} ({data["trades"]}回, '
                f'勝率{data["win_rate"]}%)</span>'
                f'<span class="{c}" style="font-weight:600">'
                f'{sign}${data["total_pnl"]:.0f}</span></div>'
            )
        st.markdown(html, unsafe_allow_html=True)

    # ── 改善アクション ──
    st.markdown('<div class="dlg-section">改善アクション</div>', unsafe_allow_html=True)
    actions = []
    if summary["win_rate"] < 50:
        actions.append("シグナルのフィルタリング強化（確信度の閾値引き上げ）")
    if summary["avg_loss_pct"] != 0 and abs(summary["avg_loss_pct"]) > abs(
        summary["avg_profit_pct"]
    ):
        actions.append("ストップロスを現在より浅く設定（損切りを早める）")
    if summary["profit_factor"] < 1.0:
        actions.append("利益確定の目標幅を拡大（テイクプロフィットの見直し）")
    if summary["avg_holding_days"] < 1:
        actions.append("保有期間が短すぎる可能性。デイトレ傾向を見直し")
    if not actions:
        actions.append("現在のパラメータを維持しつつデータ蓄積を継続")
    html = ""
    for i, a in enumerate(actions, 1):
        html += f'<div style="padding:0.25rem 0; font-size:0.82rem; color:#0f172a">{i}. {a}</div>'
    st.markdown(html, unsafe_allow_html=True)


# ============================================================
# データ取得
# ============================================================


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

# Alpaca APIが使えない場合、tradesテーブルからポジションを再構築
if not alpaca_positions:
    alpaca_positions = load_positions_from_trades()

# ============================================================
# サイドバー
# ============================================================

with st.sidebar:
    st.markdown("#### AI Investor")

    deadline = datetime.strptime(_dm.GONOGO_DEADLINE, "%Y-%m-%d")
    days_left = max((deadline - datetime.now()).days, 0)
    cd_color = P if days_left > 14 else ("#d97706" if days_left > 7 else L)

    st.markdown(
        f"""<div style="padding:0.6rem 0 0.8rem">
            <div class="cd-num" style="color:{cd_color}">{days_left}<span style="font-size:0.9rem; font-weight:600">日</span></div>
            <div class="cd-label">判定まで</div>
        </div>""",
        unsafe_allow_html=True,
    )

    if st.button("更新", width="stretch"):
        st.cache_data.clear()
        st.rerun()

    if last_run:
        run_time = last_run["started_at"][:16].replace("T", " ")
        if last_run["status"] == "completed":
            st.markdown(
                f'<div style="font-size:0.78rem; color:#64748b; margin-top:0.5rem">'
                f'最終実行 <span class="c-pos" style="font-weight:600">正常</span>'
                f"<br>{run_time}</div>",
                unsafe_allow_html=True,
            )
        else:
            err = (
                last_run["error_message"][:40]
                if last_run["error_message"]
                else last_run["status"]
            )
            st.markdown(
                f'<div style="font-size:0.78rem; color:#64748b; margin-top:0.5rem">'
                f'最終実行 <span class="c-neg" style="font-weight:600">異常</span>'
                f"<br>{err}</div>",
                unsafe_allow_html=True,
            )

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
        f"開始 {start}<br>判定 {_dm.GONOGO_DEADLINE}</div>",
        unsafe_allow_html=True,
    )

# ============================================================
# タブ構造
# ============================================================

tab_overview, tab_ops, tab_spec, tab_log = st.tabs(["Overview", "投資プロセス", "システム仕様", "詳細ログ"])

# ============================================================
# Overview タブ
# ============================================================

with tab_overview:

    # ── 1. ポートフォリオ総額 + 保有銘柄 ──

    if alpaca_pf is not None:
        total_val = alpaca_pf["portfolio_value"]
        cash_val = alpaca_pf["cash"]
        equity_val = total_val - cash_val
    elif len(daily) > 0:
        now = daily.iloc[-1]
        total_val = now["total"]
        cash_val = now["cash"]
        equity_val = now["equity"]
    else:
        total_val = cash_val = equity_val = 0

    if total_val > 0:
        pnl = total_val - capital
        pnl_pct = pnl / capital * 100
        color = W if pnl >= 0 else L
        sign = "+" if pnl >= 0 else ""

        spy_html = ""
        if len(spy) > 0:
            spy_now = spy.iloc[-1]["spy_total"]
            spy_pnl_pct = (spy_now - capital) / capital * 100
            diff = pnl_pct - spy_pnl_pct
            diff_color = W if diff >= 0 else L
            spy_html = (
                f'<div style="font-size:0.78rem; color:#94a3b8; margin-top:0.3rem">'
                f"SPY {spy_pnl_pct:+.2f}%"
                f'<span style="margin:0 0.35rem; color:#e2e8f0">|</span>'
                f'差 <span style="color:{diff_color}; font-weight:600">{diff:+.2f}%</span></div>'
            )

        equity_pct = (equity_val / total_val * 100) if total_val > 0 else 0
        cash_pct = 100 - equity_pct
        source_label = "Alpaca" if alpaca_pf is not None else "推定"

        days_running = kpi.get("days_running", 0)
        total_trades_count = kpi.get("total_trades", 0)

        pos_html = ""
        if alpaca_positions:
            pos_items = ""
            for p in alpaca_positions:
                p_pnl = p["unrealized_pnl"]
                p_pct = p["unrealized_pnl_pct"]
                p_c = "c-pos" if p_pnl >= 0 else "c-neg"
                p_sign = "+" if p_pnl >= 0 else ""
                pos_items += (
                    f'<div class="pos-row">'
                    f"<div>"
                    f'<span style="font-weight:700; color:#0f172a; font-size:0.92rem">{p["ticker"]}</span>'
                    f'<span style="color:#94a3b8; margin-left:0.4rem; font-size:0.78rem">'
                    f'{p["shares"]}株 &times; ${p["current_price"]:.2f}</span>'
                    f'<span style="color:#94a3b8; font-size:0.68rem; margin-left:0.25rem">'
                    f'(取得${p["entry_price"]:.2f})</span>'
                    f"</div>"
                    f"<div>"
                    f'<span class="{p_c}" style="font-weight:700; font-size:0.92rem">'
                    f"{p_sign}${p_pnl:,.0f}</span>"
                    f'<span class="{p_c}" style="font-size:0.78rem; margin-left:0.2rem">'
                    f"({p_sign}{p_pct:.1f}%)</span>"
                    f"</div>"
                    f"</div>"
                )
            pos_html = (
                f'<div style="margin-top:1rem; padding:0 0.5rem">'
                f'<div style="font-size:0.65rem; color:#94a3b8; letter-spacing:0.06em; '
                f'font-weight:600; margin-bottom:0.2rem; padding-left:0.4rem">保有銘柄</div>'
                f'<div style="background:#f8fafc; border-radius:10px; padding:0.3rem 0.6rem">'
                f"{pos_items}</div></div>"
            )
        else:
            pos_html = (
                '<div style="margin-top:1rem; text-align:center; '
                'font-size:0.78rem; color:#94a3b8">ポジションなし</div>'
            )

        st.markdown(
            f"""<div class="card" style="text-align:center; padding:1.8rem 1.5rem 1.4rem">
                <div style="font-size:0.68rem; color:#94a3b8; letter-spacing:0.06em;
                            font-weight:600; margin-bottom:0.5rem">
                    ポートフォリオ総額
                    <span class="pill pill-blue" style="margin-left:0.4rem; font-size:0.6rem;
                            padding:0.1rem 0.45rem">{source_label}</span>
                </div>
                <div style="font-size:3.2rem; font-weight:800; color:#0f172a;
                            letter-spacing:-2px; line-height:1.1">
                    ${total_val:,.0f}
                </div>
                <div style="font-size:1.15rem; color:{color}; font-weight:700; margin-top:0.35rem">
                    {sign}${abs(pnl):,.0f}
                    <span style="font-weight:500; font-size:0.95rem">（{sign}{pnl_pct:.2f}%）</span>
                </div>
                {spy_html}
                <div class="split-row">
                    <div class="split-box" style="background:#eff6ff">
                        <div class="split-val" style="color:#2563eb">${equity_val:,.0f}</div>
                        <div class="split-label" style="color:#64748b">株式 {equity_pct:.1f}%</div>
                    </div>
                    <div class="split-box" style="background:#f1f5f9">
                        <div class="split-val" style="color:#64748b">${cash_val:,.0f}</div>
                        <div class="split-label" style="color:#94a3b8">現金 {cash_pct:.1f}%</div>
                    </div>
                </div>
                {pos_html}
                <div style="display:flex; justify-content:center; gap:2.5rem;
                            margin-top:1.1rem; padding-top:1rem;
                            border-top:1px solid #f1f5f9">
                    <div class="mini-stat">
                        <div class="mini-val">${capital:,.0f}</div>
                        <div class="mini-label">初期資本</div>
                    </div>
                    <div class="mini-stat">
                        <div class="mini-val">{days_running}<span style="font-size:0.75rem; font-weight:500">日</span></div>
                        <div class="mini-label">運用期間</div>
                    </div>
                    <div class="mini-stat">
                        <div class="mini-val">{total_trades_count}<span style="font-size:0.75rem; font-weight:500">回</span></div>
                        <div class="mini-label">決済回数</div>
                    </div>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="card" style="text-align:center; padding:3rem; color:#94a3b8">'
            "まだデータがありません</div>",
            unsafe_allow_html=True,
        )

    # ── 2. 資産推移チャート ──

    st.markdown(
        f'<div class="sec-hdr">'
        f'<div class="bar" style="background:{P}"></div>'
        f'<div class="txt">資産推移</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    if len(daily) > 0:
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=daily["date"],
                y=[capital] * len(daily),
                mode="lines",
                line=dict(width=0),
                showlegend=False,
                hoverinfo="skip",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=daily["date"],
                y=daily["total"],
                fill="tonexty",
                fillcolor="rgba(225,29,72,0.04)",
                mode="none",
                showlegend=False,
                hoverinfo="skip",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=daily["date"],
                y=daily["total"],
                name="ポートフォリオ",
                mode="lines+markers",
                line=dict(color=P, width=2.5),
                marker=dict(size=5, color=P),
                hovertemplate="%{x|%m/%d}  $%{y:,.0f}<extra></extra>",
            )
        )

        if len(spy) > 0:
            fig.add_trace(
                go.Scatter(
                    x=spy["date"],
                    y=spy["spy_total"],
                    name="SPY",
                    mode="lines",
                    line=dict(color="#94a3b8", width=1.5, dash="dash"),
                    hovertemplate="%{x|%m/%d}  SPY $%{y:,.0f}<extra></extra>",
                )
            )

        buy_rows = trades[
            (trades["action"] == "BUY") & trades["entry_timestamp"].notna()
        ].copy()
        if len(buy_rows) > 0:
            buy_rows["entry_date"] = pd.to_datetime(
                buy_rows["entry_timestamp"], format="mixed"
            ).dt.normalize()
            merged = buy_rows.merge(
                daily[["date", "total"]],
                left_on="entry_date",
                right_on="date",
                how="inner",
            )
            if len(merged) > 0:
                fig.add_trace(
                    go.Scatter(
                        x=merged["date"],
                        y=merged["total"],
                        name="買い",
                        mode="markers",
                        marker=dict(
                            symbol="triangle-up",
                            size=12,
                            color=W,
                            line=dict(width=1.5, color="#fff"),
                        ),
                        hovertemplate="%{x|%m/%d} 買い %{text}<extra></extra>",
                        text=merged["ticker"],
                        showlegend=False,
                    )
                )

        sell_rows = trades[
            (trades["status"] == "CLOSED") & trades["exit_timestamp"].notna()
        ].copy()
        if len(sell_rows) > 0:
            sell_rows["exit_date"] = pd.to_datetime(
                sell_rows["exit_timestamp"], format="mixed"
            ).dt.normalize()
            merged = sell_rows.merge(
                daily[["date", "total"]],
                left_on="exit_date",
                right_on="date",
                how="inner",
            )
            if len(merged) > 0:
                fig.add_trace(
                    go.Scatter(
                        x=merged["date"],
                        y=merged["total"],
                        name="売り",
                        mode="markers",
                        marker=dict(
                            symbol="triangle-down",
                            size=12,
                            color=L,
                            line=dict(width=1.5, color="#fff"),
                        ),
                        hovertemplate="%{x|%m/%d} 売り %{text}<extra></extra>",
                        text=merged["ticker"],
                        showlegend=False,
                    )
                )

        fig.add_hline(y=capital, line_dash="dot", line_color="#cbd5e1", line_width=1)
        fig.add_annotation(
            x=daily["date"].iloc[0],
            y=capital,
            text=f"スタート ${capital:,.0f}",
            showarrow=False,
            font=dict(size=10, color="#94a3b8"),
            xanchor="left",
            yshift=10,
        )

        fig.update_layout(
            template="plotly_white",
            height=320,
            margin=dict(t=20, b=28, l=65, r=20),
            xaxis=dict(title="", gridcolor="#f1f5f9", linecolor="#e2e8f0"),
            yaxis=dict(
                title="",
                tickprefix="$",
                tickformat=",",
                gridcolor="#f1f5f9",
                linecolor="#e2e8f0",
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=11),
            ),
            font=dict(
                family="Inter, -apple-system, BlinkMacSystemFont, sans-serif", size=12
            ),
            plot_bgcolor="#fff",
            paper_bgcolor="#fff",
            hoverlabel=dict(
                bgcolor="#0f172a",
                font_color="#fff",
                font_size=12,
                bordercolor="#0f172a",
            ),
        )

        st.plotly_chart(fig, width="stretch")

    # ── 3. 実取引チェックリスト ──

    deadline_dt = datetime.strptime(_dm.GONOGO_DEADLINE, "%Y-%m-%d")
    days_left = max((deadline_dt - datetime.now()).days, 0)
    targets = _dm.KPI_TARGETS

    cl_left, cl_right = st.columns([6, 1])
    with cl_left:
        st.markdown(
            f'<div class="sec-hdr">'
            f'<div class="bar" style="background:#f59e0b"></div>'
            f'<div class="txt">実取引チェックリスト'
            f'<span class="sub">残り{days_left}日で判定</span></div>'
            f"</div>",
            unsafe_allow_html=True,
        )
    with cl_right:
        st.markdown('<div style="height:1.6rem"></div>', unsafe_allow_html=True)
        if st.button("詳細分析", type="secondary", width="stretch"):
            show_analysis_dialog()

    kpi_checks = []

    wr = kpi["win_rate"]
    wr_tgt = targets["win_rate"]
    wr_ok = wr >= wr_tgt
    wr_pct = min(100, max(0, wr / wr_tgt * 100)) if wr_tgt > 0 else 0
    wr_gap = wr_tgt - wr
    kpi_checks.append(
        {
            "label": "勝率",
            "tip": "利益が出た取引の割合",
            "current": f"{wr:.0f}%",
            "target_str": f"{wr_tgt:.0f}%",
            "ok": wr_ok,
            "bar_pct": wr_pct,
            "gap_txt": "達成" if wr_ok else f"あと{wr_gap:.0f}pp",
            "gap_sub": "" if wr_ok else "勝てる銘柄選定が必要",
        }
    )

    ar = kpi["annual_return"]
    ar_tgt = targets["annual_return"]
    ar_ok = ar >= ar_tgt
    ar_pct = min(100, max(0, ar / ar_tgt * 100)) if ar_tgt > 0 and ar > 0 else 0
    ar_gap = ar_tgt - ar
    days_running = kpi.get("days_running", 0)
    ar_note = f"（{days_running}日間データから換算）" if days_running < 30 else ""
    kpi_checks.append(
        {
            "label": "年率リターン",
            "tip": f"今の成績を1年に換算した利回り{ar_note}",
            "current": f"{ar:+.1f}%",
            "target_str": f"{ar_tgt:.0f}%",
            "ok": ar_ok,
            "bar_pct": ar_pct,
            "gap_txt": "達成" if ar_ok else f"あと{ar_gap:.1f}%",
            "gap_sub": (
                ""
                if ar_ok
                else (
                    f"マイナス圏。利確精度の向上が必要{ar_note}"
                    if ar < 0
                    else ar_note
                )
            ),
        }
    )

    dd = kpi["max_drawdown"]
    dd_tgt = targets["max_drawdown"]
    dd_ok = dd <= dd_tgt
    if dd_ok:
        dd_pct = 100
    elif dd_tgt > 0:
        dd_pct = min(100, max(0, dd_tgt / dd * 100))
    else:
        dd_pct = 0
    dd_over = dd - dd_tgt
    kpi_checks.append(
        {
            "label": "最大DD",
            "tip": "資産が最も下がった時の下落幅（小さいほど良い）",
            "current": f"{dd:.1f}%",
            "target_str": f"{dd_tgt:.0f}%以下",
            "ok": dd_ok,
            "bar_pct": dd_pct,
            "gap_txt": "達成" if dd_ok else f"{dd_over:.0f}%超過",
            "gap_sub": "" if dd_ok else "損切りルールの改善が急務",
        }
    )

    up = kpi["uptime"]
    up_tgt = targets["uptime"]
    up_ok = up >= up_tgt
    up_pct = min(100, max(0, up / up_tgt * 100)) if up_tgt > 0 else 0
    up_gap = up_tgt - up
    kpi_checks.append(
        {
            "label": "稼働率",
            "tip": "システムが正常に動いていた割合",
            "current": f"{up:.0f}%",
            "target_str": f"{up_tgt:.0f}%",
            "ok": up_ok,
            "bar_pct": up_pct,
            "gap_txt": "達成" if up_ok else f"あと{up_gap:.0f}pp",
            "gap_sub": "" if up_ok else "システム安定性の改善が必要",
        }
    )

    cl_html = ""
    for item in kpi_checks:
        bar_color = W if item["ok"] else L
        cur_color = W if item["ok"] else "#0f172a"
        gap_color = W if item["ok"] else L
        check_icon = "&#10003;" if item["ok"] else ""

        gap_sub_html = ""
        if item["gap_sub"]:
            gap_sub_html = f'<div class="cl-gap-sub">{item["gap_sub"]}</div>'

        cl_html += f"""
        <div class="cl-row">
            <div class="cl-label">
                <div class="cl-label-txt">{item["label"]}</div>
                <div class="cl-label-tip">{item["tip"]}</div>
            </div>
            <div class="cl-bar-wrap">
                <div class="cl-bar-track">
                    <div class="cl-bar-fill" style="width:{item['bar_pct']:.0f}%;
                         background:{bar_color}"></div>
                </div>
                <div class="cl-nums">
                    <div class="cl-cur" style="color:{cur_color}">{item["current"]}</div>
                    <div class="cl-tgt">目標 {item["target_str"]}</div>
                </div>
            </div>
            <div class="cl-gap">
                <div class="cl-gap-txt" style="color:{gap_color}">
                    {check_icon} {item["gap_txt"]}</div>
                {gap_sub_html}
            </div>
        </div>"""

    st.markdown(
        f'<div class="card" style="padding:0.8rem 1.3rem">{cl_html}</div>',
        unsafe_allow_html=True,
    )

    # 判定バナー
    v = verdict["status"]
    passed = verdict["passed"]
    total = verdict["total"]
    if v == "GO":
        vc = "v-go"
        vt = f"<b>GO</b> — 全{total}項目を達成。Phase 4（実取引）へ移行可能です。"
    elif v == "CONDITIONAL_GO":
        vc = "v-cond"
        recs = " / ".join(verdict["recommendations"][:2])
        vt = (
            f"<b>条件付き</b> — {passed}/{total}項目を達成。"
            f"<br><span style='font-size:0.78rem'>{recs}</span>"
        )
    else:
        vc = "v-ng"
        vt = f"<b>未達</b> — {passed}/{total}項目のみ達成。残り{days_left}日で改善が必要です。"

    st.markdown(
        f'<div class="verdict {vc}">{vt}</div>',
        unsafe_allow_html=True,
    )

    # ── 4. 取引履歴 ──

    st.markdown(
        f'<div class="sec-hdr">'
        f'<div class="bar" style="background:{W}"></div>'
        f'<div class="txt">取引履歴</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    if len(trades) > 0:
        trades_sorted = trades.sort_values("entry_timestamp", ascending=True)

        closed_trades = trades_sorted[trades_sorted["status"] == "CLOSED"]
        best_id = None
        worst_id = None
        if len(closed_trades) > 0:
            best_id = closed_trades.loc[closed_trades["profit_loss"].idxmax(), "id"]
            worst_id = closed_trades.loc[closed_trades["profit_loss"].idxmin(), "id"]

        for _, t in trades_sorted.iterrows():
            ticker = t["ticker"]
            shares = int(t["shares"])

            if t["status"] == "CLOSED":
                pnl_val = t["profit_loss"] or 0
                pct_val = t["profit_loss_pct"] or 0
                c = "c-pos" if pnl_val >= 0 else "c-neg"
                sign_t = "+" if pnl_val >= 0 else ""
                accent = "tr-win" if pnl_val >= 0 else "tr-loss"

                if t["id"] == best_id and pnl_val > 0:
                    accent = "tr-best"
                elif t["id"] == worst_id and pnl_val < 0:
                    accent = "tr-worst"

                hd = t.get("holding_days")
                hd_str = f" &middot; {int(hd)}日保有" if pd.notna(hd) and hd else ""

                result = (
                    f'<span class="{c}" style="font-weight:600">'
                    f"{sign_t}${pnl_val:,.0f}（{sign_t}{pct_val:.1f}%）</span>"
                )

                ed = (
                    t["entry_timestamp"][:10]
                    if pd.notna(t.get("entry_timestamp"))
                    else ""
                )
                xd = (
                    t["exit_timestamp"][:10]
                    if pd.notna(t.get("exit_timestamp"))
                    else ""
                )
                st.markdown(
                    f"""<div class="tr-card {accent}">
                        <div>
                            <span style="font-weight:600; color:#0f172a; margin-right:0.4rem">
                                {ticker}</span>
                            <span style="color:#94a3b8; font-size:0.78rem">
                                {shares}株</span>
                            <span style="color:#cbd5e1; margin:0 0.25rem">&middot;</span>
                            <span style="color:#94a3b8; font-size:0.78rem">
                                ${t['entry_price']:.2f} &rarr; ${t['exit_price']:.2f}</span>
                            <span style="color:#cbd5e1; margin:0 0.25rem">&middot;</span>
                            <span style="color:#94a3b8; font-size:0.72rem">
                                {ed} &rarr; {xd}{hd_str}</span>
                        </div>
                        <div>{result}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

            elif t["status"] == "OPEN":
                accent = "tr-open"
                result = '<span class="pill pill-blue">保有中</span>'
                ed = (
                    t["entry_timestamp"][:10]
                    if pd.notna(t.get("entry_timestamp"))
                    else ""
                )
                st.markdown(
                    f"""<div class="tr-card {accent}">
                        <div>
                            <span style="font-weight:600; color:#0f172a; margin-right:0.4rem">
                                {ticker}</span>
                            <span style="color:#94a3b8; font-size:0.78rem">
                                {shares}株 @ ${t['entry_price']:.2f}</span>
                            <span style="color:#cbd5e1; margin:0 0.25rem">&middot;</span>
                            <span style="color:#94a3b8; font-size:0.72rem">{ed}〜</span>
                        </div>
                        <div>{result}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

        # サマリー
        if len(closed_trades) > 0:
            wins = len(closed_trades[closed_trades["profit_loss"] > 0])
            losses = len(closed_trades) - wins
            total_pnl = closed_trades["profit_loss"].sum()
            pc = "c-pos" if total_pnl >= 0 else "c-neg"
            ps = "+" if total_pnl >= 0 else ""
            avg_pnl = total_pnl / len(closed_trades)
            ac = "c-pos" if avg_pnl >= 0 else "c-neg"
            a_sign = "+" if avg_pnl >= 0 else ""

            st.markdown(
                f"""<div class="card" style="text-align:center; margin-top:0.5rem;
                            padding:0.9rem 1rem">
                    <span style="color:#64748b; font-size:0.82rem">
                        {len(closed_trades)}回決済</span>
                    <span style="color:#e2e8f0; margin:0 0.5rem">|</span>
                    <span class="c-pos" style="font-size:0.82rem; font-weight:600">
                        {wins}勝</span>
                    <span class="c-neg" style="font-size:0.82rem; font-weight:600;
                            margin-left:0.2rem">{losses}敗</span>
                    <span style="color:#e2e8f0; margin:0 0.5rem">|</span>
                    <span class="{pc}" style="font-size:1rem; font-weight:700">
                        {ps}${total_pnl:,.0f}</span>
                    <span style="color:#e2e8f0; margin:0 0.5rem">|</span>
                    <span class="{ac}" style="font-size:0.82rem">
                        平均 {a_sign}${avg_pnl:,.0f}/回</span>
                </div>""",
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<div class="card-sm" style="color:#94a3b8; text-align:center; padding:1.2rem">'
            "まだ取引がありません</div>",
            unsafe_allow_html=True,
        )

# ============================================================
# 投資プロセス タブ
# ============================================================

with tab_ops:

    WEEKDAY_JP = ["月", "火", "水", "木", "金", "土", "日"]
    MODE_LABELS = {
        "full": "定時分析",
        "medium": "中間チェック",
        "light": "モニタリング",
    }

    # ── データ読み込み ──
    pipeline = load_pipeline_status()
    timeline_df = load_runs_timeline()
    health = load_health_metrics()

    # ── タブ説明 ──

    st.markdown(
        '<div class="wf-intro">'
        "<b>投資プロセス — 本日の運用状況</b><br>"
        "このタブでは「今日、システムが何をしたか」をリアルタイムで確認できます。"
        "5つのステップの進行状況・実行結果・詳細データを表示します。"
        "各ステップの<b>仕組みや設定値</b>は「システム仕様」タブを参照してください。"
        "</div>",
        unsafe_allow_html=True,
    )

    # ── 1. 本日の投資プロセス ──

    st.markdown(
        f'<div class="sec-hdr">'
        f'<div class="bar" style="background:{P}"></div>'
        f'<div class="txt">本日の投資プロセス'
        f'<span class="sub">{pipeline["date"]}</span></div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    steps_config = [
        (
            "news",
            "情報収集",
            "市場ニュースを自動取得",
            "Finnhub・Google News RSS・Yahoo Finance等から自動収集。8つ以上の金融メディアRSSを15分間隔で巡回。URLベースで重複排除。",
        ),
        (
            "analysis",
            "AI分析",
            "テーマ・銘柄をAIが評価",
            "Gemini Proが「シニアアナリスト」として6種類の定性分析を実施。テーマ評価・センチメント(CoT推論)・イベント分類・ディープニュース分析・メガトレンド5軸採点・トレード戦略生成。",
        ),
        (
            "signals",
            "売買判断",
            "買い・売りのシグナルを生成",
            "3戦略（押し目買い・トレンド追従・VIX逆張り）のテクニカル指標＋AIニュース分析を統合。最低3カテゴリ一致＆確信度6以上で発出。AIがrejectなら取消。",
        ),
        (
            "trading",
            "注文執行",
            "条件を満たす注文を自動発注",
            "7段階のリスクチェック（価格検証→CB→市場レジーム→重複→決算→マクロ→相関）を全て通過した場合のみAlpaca APIで発注。VIXに応じてSL/TPを動的調整。",
        ),
        (
            "portfolio",
            "資産記録",
            "取引後の資産を記録・更新",
            "取引後にAlpacaからポジション・残高を取得し、DBにスナップショットを記録。日次でパフォーマンスを算出。",
        ),
    ]

    steps_html = ""
    for i, (key, label, desc, tip) in enumerate(steps_config):
        step = pipeline["steps"][key]
        status = step["status"]
        count = step["count"]
        time_str = step["last_at"]

        if status == "completed":
            n_cls = "wf-n-ok"
            icon = "&#10003;"
        elif status == "failed":
            n_cls = "wf-n-fail"
            icon = "&#10007;"
        else:
            n_cls = "wf-n-wait"
            icon = f"{i + 1}"

        # 補足情報（売買判断の内訳など）
        extra = ""
        if key == "signals" and count > 0:
            buy_cnt = step.get("buy", 0)
            sell_cnt = step.get("sell", 0)
            parts = []
            if buy_cnt:
                parts.append(f'<span class="c-pos">買 {buy_cnt}</span>')
            if sell_cnt:
                parts.append(f'<span class="c-neg">売 {sell_cnt}</span>')
            if parts:
                extra = (
                    f' <span style="font-size:0.7rem">（{" / ".join(parts)}）</span>'
                )

        count_str = f"{count}件" if count > 0 else "-"
        val_color = "#0f172a" if count > 0 else "#cbd5e1"

        steps_html += f"""
        <div class="wf-step">
            <div class="wf-num {n_cls}">{icon}</div>
            <div class="wf-body">
                <div class="wf-name">{label}{extra}<span class="wf-info">?<span class="wf-tip">{tip}</span></span></div>
                <div class="wf-desc">{desc}</div>
            </div>
            <div class="wf-right">
                <div class="wf-val" style="color:{val_color}">{count_str}</div>
                <div class="wf-ts">{time_str}</div>
            </div>
        </div>"""

    # 本日の実行情報
    runs_today = pipeline["runs_today"]
    total_errors = pipeline["total_errors"]
    if runs_today:
        mode_labels = sorted(
            {MODE_LABELS.get(r["run_mode"], r["run_mode"]) for r in runs_today}
        )
        run_info = (
            f'<span class="c-sub" style="font-size:0.72rem">'
            f'本日 {len(runs_today)}回実行（{", ".join(mode_labels)}）'
        )
        if total_errors > 0:
            run_info += f' / <span class="c-neg">異常 {total_errors}件</span>'
        run_info += "</span>"
    else:
        run_info = '<span class="c-dim" style="font-size:0.72rem">本日はまだ実行されていません</span>'

    st.markdown(
        f'<div class="card" style="padding:0.5rem 0.3rem">'
        f"{steps_html}"
        f'<div style="text-align:center; padding:0.5rem 0; border-top:1px solid #f1f5f9">{run_info}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    # ── 2. 過去7日間の運用品質 ──

    st.markdown(
        f'<div class="sec-hdr">'
        f'<div class="bar" style="background:{W}"></div>'
        f'<div class="txt">運用品質'
        f'<span class="sub">過去7日間の平均</span></div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    success_rate = max(0.0, 100.0 - health["error_rate"])
    hcols = st.columns(5)
    h_items = [
        (
            "情報収集",
            f"{health['news_per_day']:.0f}",
            "件/日",
            health["news_per_day"] > 0,
        ),
        (
            "AI分析",
            f"{health['analysis_per_day']:.1f}",
            "件/日",
            health["analysis_per_day"] > 0,
        ),
        (
            "売買判断",
            f"{health['signals_per_day']:.1f}",
            "件/日",
            health["signals_per_day"] > 0,
        ),
        ("正常処理率", f"{success_rate:.0f}%", "", success_rate >= 90),
        ("稼働継続率", f"{health['uptime_pct']:.0f}%", "", health["uptime_pct"] >= 95),
    ]

    for col, (label, val, sub, is_ok) in zip(hcols, h_items):
        val_color = W if is_ok else L
        sub_html = (
            f'<span style="font-size:0.6rem; color:#94a3b8; font-weight:400">{sub}</span>'
            if sub
            else ""
        )
        with col:
            st.markdown(
                f'<div class="card-sm" style="text-align:center; padding:0.8rem 0.5rem">'
                f'<div class="health-val" style="color:{val_color}">{val}{sub_html}</div>'
                f'<div class="health-label">{label}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )

    # ── 3. ニュース・分析活用 ──

    st.markdown(
        f'<div class="sec-hdr">'
        f'<div class="bar" style="background:#8b5cf6"></div>'
        f'<div class="txt">ニュース・分析活用'
        f'<span class="sub">直近14日</span></div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    # データ読み込み
    news_trend = _dm.get_news_collection_trend(14)
    news_sources = _dm.get_news_source_breakdown(14)
    news_tickers = _dm.get_news_ticker_coverage(14)
    analysis_trend = _dm.get_analysis_trend(14)
    theme_scores = _dm.get_analysis_theme_scores(7)
    ns_conn = _dm.get_news_signal_connection(14)

    # 3a: フロー概要（ニュース→分析→シグナル）
    total_news = int(news_trend["article_count"].sum()) if len(news_trend) > 0 else 0
    total_analysis = int(analysis_trend["total"].sum()) if len(analysis_trend) > 0 else 0
    total_signals = ns_conn["total_signals"]
    news_influenced = ns_conn["news_influenced_signals"]
    flow_df = ns_conn["flow_df"]

    def _nu_cls(v):
        return "nu-active" if v > 0 else "nu-empty"

    st.markdown(
        f'<div class="card">'
        f'<div style="font-size:0.72rem; color:#64748b; font-weight:600; margin-bottom:0.4rem">データフロー（14日間合計）</div>'
        f'<div class="nu-flow">'
        f'  <div class="nu-node {_nu_cls(total_news)}"><div class="nu-icon">📰</div><div class="nu-val">{total_news:,}</div><div class="nu-label">ニュース収集</div></div>'
        f'  <div class="nu-arrow">→</div>'
        f'  <div class="nu-node {_nu_cls(total_analysis)}"><div class="nu-icon">🧠</div><div class="nu-val">{total_analysis}</div><div class="nu-label">AI分析</div></div>'
        f'  <div class="nu-arrow">→</div>'
        f'  <div class="nu-node {_nu_cls(total_signals)}"><div class="nu-icon">🎯</div><div class="nu-val">{total_signals}</div><div class="nu-label">シグナル</div></div>'
        f'  <div class="nu-arrow">→</div>'
        f'  <div class="nu-node {_nu_cls(news_influenced)}"><div class="nu-icon">📊</div><div class="nu-val">{news_influenced}</div><div class="nu-label">ニュース活用</div></div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # 3b: 日別フローチャート（Plotly）
    if len(flow_df) > 0:
        fig_flow = go.Figure()
        fig_flow.add_trace(go.Bar(
            x=flow_df["date"], y=flow_df["news"],
            name="ニュース", marker_color="#8b5cf6", opacity=0.7,
        ))
        fig_flow.add_trace(go.Bar(
            x=flow_df["date"], y=flow_df["analysis"],
            name="AI分析", marker_color="#2563eb", opacity=0.7,
        ))
        fig_flow.add_trace(go.Scatter(
            x=flow_df["date"], y=flow_df["signals"],
            name="シグナル", mode="lines+markers",
            line=dict(color="#059669", width=2),
            marker=dict(size=6),
        ))
        fig_flow.update_layout(
            height=220, margin=dict(l=0, r=0, t=25, b=0),
            legend=dict(orientation="h", yanchor="top", y=1.15, xanchor="center", x=0.5, font_size=11),
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(showgrid=False, tickfont_size=10),
            yaxis=dict(showgrid=True, gridcolor="#f1f5f9", tickfont_size=10),
            barmode="group", bargap=0.3,
        )
        st.plotly_chart(fig_flow, use_container_width=True)

    # 3c: 詳細（2カラム: ニュースソース / AI分析テーマ）
    nu_col1, nu_col2 = st.columns(2)

    with nu_col1:
        st.markdown(
            '<div class="card-sm">'
            '<div style="font-size:0.72rem; font-weight:600; color:#64748b; margin-bottom:0.4rem">ニュースソース TOP</div>',
            unsafe_allow_html=True,
        )
        if len(news_sources) > 0:
            max_cnt = int(news_sources["cnt"].max())
            src_html = ""
            for _, row in news_sources.head(7).iterrows():
                pct = int(row["cnt"]) / max_cnt * 100 if max_cnt > 0 else 0
                src_html += (
                    f'<div class="nu-src-bar">'
                    f'<div class="nu-src-name">{row["source"]}</div>'
                    f'<div style="flex:1"><div class="nu-src-fill" style="width:{pct:.0f}%"></div></div>'
                    f'<div class="nu-src-cnt">{int(row["cnt"]):,}</div>'
                    f'</div>'
                )
            st.markdown(src_html + '</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                '<div style="color:#94a3b8; font-size:0.78rem; padding:0.5rem 0">データなし</div></div>',
                unsafe_allow_html=True,
            )

        # ティッカー紐付け
        if len(news_tickers) > 0:
            st.markdown(
                '<div class="card-sm">'
                '<div style="font-size:0.72rem; font-weight:600; color:#64748b; margin-bottom:0.3rem">関連銘柄（記事数）</div>',
                unsafe_allow_html=True,
            )
            tk_pills = ""
            for _, row in news_tickers.head(12).iterrows():
                tk_pills += (
                    f'<span class="nu-theme-card">'
                    f'<span style="color:{P}; font-weight:600">{row["ticker"]}</span>'
                    f'<span class="nu-score" style="color:#64748b">{int(row["article_count"])}</span>'
                    f'</span>'
                )
            st.markdown(tk_pills + '</div>', unsafe_allow_html=True)

    with nu_col2:
        st.markdown(
            '<div class="card-sm">'
            '<div style="font-size:0.72rem; font-weight:600; color:#64748b; margin-bottom:0.4rem">AI分析テーマ（最新スコア）</div>',
            unsafe_allow_html=True,
        )
        if len(theme_scores) > 0:
            themes_html = ""
            for _, t in theme_scores.iterrows():
                score = t.get("score", 0) or 0
                direction = t.get("direction", "") or ""
                dir_label = {"bullish": "強気", "bearish": "弱気", "neutral": "中立"}.get(direction, direction)
                dir_color = W if direction == "bullish" else (L if direction == "bearish" else "#64748b")
                rec = t.get("recommendation", "") or ""
                themes_html += (
                    f'<div class="nu-theme-card">'
                    f'<span>{t["theme"]}</span>'
                    f'<span class="nu-score" style="color:{dir_color}">{score:.0f}</span>'
                    f'<span style="font-size:0.6rem; color:{dir_color}">{dir_label}</span>'
                    f'</div>'
                )
            st.markdown(themes_html + '</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                '<div style="color:#94a3b8; font-size:0.78rem; padding:0.5rem 0">データなし</div></div>',
                unsafe_allow_html=True,
            )

        # 分析トレンド: 方向性分布
        if len(analysis_trend) > 0:
            total_b = int(analysis_trend["bullish"].sum())
            total_bear = int(analysis_trend["bearish"].sum())
            total_n = int(analysis_trend["neutral"].sum())
            total_all = total_b + total_bear + total_n
            if total_all > 0:
                b_pct = total_b / total_all * 100
                bear_pct = total_bear / total_all * 100
                n_pct = total_n / total_all * 100
                avg_score = analysis_trend["avg_score"].mean()
                st.markdown(
                    f'<div class="card-sm">'
                    f'<div style="font-size:0.72rem; font-weight:600; color:#64748b; margin-bottom:0.3rem">分析方向性の分布</div>'
                    f'<div style="display:flex; height:10px; border-radius:5px; overflow:hidden; margin-bottom:0.3rem">'
                    f'<div style="width:{b_pct:.0f}%; background:{W}"></div>'
                    f'<div style="width:{n_pct:.0f}%; background:#94a3b8"></div>'
                    f'<div style="width:{bear_pct:.0f}%; background:{L}"></div>'
                    f'</div>'
                    f'<div style="display:flex; justify-content:space-between; font-size:0.68rem; color:#64748b">'
                    f'<span style="color:{W}">強気 {total_b}件 ({b_pct:.0f}%)</span>'
                    f'<span>中立 {total_n}件</span>'
                    f'<span style="color:{L}">弱気 {total_bear}件 ({bear_pct:.0f}%)</span>'
                    f'</div>'
                    f'<div style="text-align:center; margin-top:0.3rem; font-size:0.72rem; color:#64748b">'
                    f'平均スコア: <span style="font-weight:700; color:#0f172a">{avg_score:.0f}</span> / 100'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    # ── 4. 日次運用カレンダー（直近14日） ──

    st.markdown(
        f'<div class="sec-hdr">'
        f'<div class="bar" style="background:#f59e0b"></div>'
        f'<div class="txt">日次運用カレンダー'
        f'<span class="sub">直近14日</span></div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    # 凡例
    st.markdown(
        '<div style="display:flex; gap:1.2rem; margin-bottom:0.5rem; font-size:0.68rem; color:#64748b">'
        '<span><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#059669;margin-right:0.3rem"></span>正常</span>'
        '<span><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#f59e0b;margin-right:0.3rem"></span>一部異常</span>'
        '<span><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#e11d48;margin-right:0.3rem"></span>失敗</span>'
        '<span><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#e2e8f0;margin-right:0.3rem"></span>未実行</span>'
        "</div>",
        unsafe_allow_html=True,
    )

    if len(timeline_df) > 0:
        tl_html = ""
        for _, day in timeline_df.iterrows():
            run_date = day["run_date"]
            try:
                dt_obj = datetime.strptime(run_date, "%Y-%m-%d")
                wd = WEEKDAY_JP[dt_obj.weekday()]
                date_label = f"{run_date[5:]} ({wd})"
            except Exception:
                date_label = run_date[5:] if len(run_date) > 5 else run_date

            failed = int(day["failed"] or 0)
            interrupted = int(day["interrupted"] or 0)
            completed = int(day["completed"] or 0)
            total_runs = int(day["total_runs"] or 0)
            errors = int(day["total_errors"] or 0)
            signals = int(day["total_signals"] or 0)
            t_trades = int(day["total_trades"] or 0)
            modes_raw = day["modes"] or ""

            if failed > 0:
                dot_cls = "tl-fail"
            elif errors > 0 or interrupted > 0:
                dot_cls = "tl-warn"
            elif completed > 0:
                dot_cls = "tl-ok"
            else:
                dot_cls = "tl-empty"

            # ラン種別を業務名に変換
            mode_parts = [
                MODE_LABELS.get(m.strip(), m.strip())
                for m in modes_raw.split(",")
                if m.strip()
            ]
            mode_display = ", ".join(mode_parts) if mode_parts else "-"

            nums_parts = []
            if signals > 0:
                nums_parts.append(f'<span class="c-pri">判断 {signals}件</span>')
            if t_trades > 0:
                nums_parts.append(f'<span class="c-pos">約定 {t_trades}件</span>')
            if errors > 0:
                nums_parts.append(f'<span class="c-neg">異常 {errors}件</span>')
            nums_html = (
                " &middot; ".join(nums_parts)
                if nums_parts
                else '<span class="c-dim">&ndash;</span>'
            )

            tl_html += f"""
            <div class="tl-row">
                <div class="tl-date">{date_label}</div>
                <div class="tl-dot {dot_cls}"></div>
                <div class="tl-info">{mode_display}<span class="tl-sub">{completed}/{total_runs}回 正常完了</span></div>
                <div class="tl-nums">{nums_html}</div>
            </div>"""

        st.markdown(
            f'<div class="card" style="padding:0.5rem 0.3rem">{tl_html}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="card-sm" style="color:#94a3b8; text-align:center; padding:1.2rem">'
            "直近14日間の実行記録なし</div>",
            unsafe_allow_html=True,
        )

    # ── 4. プロセス詳細（ドリルダウン） ──

    st.markdown(
        f'<div class="sec-hdr">'
        f'<div class="bar" style="background:#64748b"></div>'
        f'<div class="txt">プロセス詳細'
        f'<span class="sub">各ステップの中身を確認</span></div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    # 4a: 情報収集
    news_cnt = pipeline["steps"]["news"]["count"]
    with st.expander(f"Step 1. 情報収集 - {news_cnt}件", expanded=False):
        today_news = _dm.get_todays_news()
        if len(today_news) > 0:
            news_html = ""
            for _, n in today_news.iterrows():
                title = n["title"] or ""
                source = n.get("source", "")
                content = n.get("content", "") or ""
                theme = n.get("theme", "") or ""
                tickers_raw = n.get("tickers_json", "") or ""
                sent = n.get("sentiment_score") or 0
                s_color = W if sent > 0 else (L if sent < 0 else "#94a3b8")
                sent_label = (
                    "好材料" if sent > 0.3 else ("悪材料" if sent < -0.3 else "中立")
                )

                # テーマ・ティッカーピル
                pills = ""
                if theme:
                    pills += f'<span class="pill pill-blue" style="font-size:0.58rem; padding:0.05rem 0.3rem; margin-right:0.2rem">{theme}</span>'
                try:
                    import json as _json

                    tickers = _json.loads(tickers_raw) if tickers_raw else []
                    for tk in tickers[:5]:
                        pills += f'<span style="font-size:0.6rem; color:#64748b; margin-right:0.25rem">${tk}</span>'
                except Exception as e:
                    logger.warning(f"ティッカーJSON解析エラー: {e}")

                # 詳細ブロック
                detail_rows = ""
                if content:
                    detail_rows += f'<div class="dd-kv"><span class="dd-k">概要</span><span class="dd-v">{content[:300]}</span></div>'
                if sent:
                    detail_rows += f'<div class="dd-kv"><span class="dd-k">センチメント</span><span class="dd-v" style="color:{s_color}">{sent_label} ({sent:+.2f})</span></div>'
                if pills:
                    detail_rows += f'<div class="dd-kv"><span class="dd-k">関連</span><span class="dd-v">{pills}</span></div>'

                news_html += f"""<div class="dd-item"><details>
                    <summary class="dd-summary">{title}
                    <span style="color:#94a3b8; font-size:0.68rem; margin-left:0.3rem">{source}</span></summary>
                    <div class="dd-detail">{detail_rows}</div>
                    </details></div>"""

            st.markdown(news_html, unsafe_allow_html=True)
        else:
            st.markdown(
                '<span style="color:#94a3b8; font-size:0.82rem">本日の収集ニュースはありません</span>',
                unsafe_allow_html=True,
            )

    # 4b: AI分析
    analysis_cnt = pipeline["steps"]["analysis"]["count"]
    with st.expander(f"Step 2. AI分析 - {analysis_cnt}件", expanded=False):
        today_analysis = _dm.get_todays_analyses()
        if len(today_analysis) > 0:
            ana_html = ""
            for _, a in today_analysis.iterrows():
                theme = a.get("theme", "") or ""
                ticker = a.get("ticker", "") or ""
                a_type = a.get("analysis_type", "") or ""
                score = a.get("score") or 0
                direction = a.get("direction", "") or ""
                summary = a.get("summary", "") or ""
                detailed = a.get("detailed_analysis", "") or ""
                kp_raw = a.get("key_points_json", "") or ""
                recommendation = a.get("recommendation", "") or ""
                model = a.get("model_used", "") or ""
                time_a = str(a.get("analyzed_at", ""))[:16].replace("T", " ")

                dir_label = {
                    "bullish": "強気",
                    "bearish": "弱気",
                    "neutral": "中立",
                }.get(direction, direction)
                dir_color = (
                    W
                    if direction == "bullish"
                    else (L if direction == "bearish" else "#64748b")
                )

                type_label = {
                    "theme_report": "テーマレポート",
                    "ticker_analysis": "銘柄分析",
                    "impact_analysis": "インパクト分析",
                }.get(a_type, a_type)

                # ヘッダー
                header_parts = [f"<b>{theme}</b>"]
                if ticker:
                    header_parts.append(
                        f'<span style="color:{P}; font-weight:600">{ticker}</span>'
                    )
                header_parts.append(
                    f'<span style="color:{dir_color}; font-weight:600">スコア {score:.0f} / {dir_label}</span>'
                )
                header = " - ".join(header_parts)

                # 詳細
                detail_rows = ""
                detail_rows += f'<div class="dd-kv"><span class="dd-k">種別</span><span class="dd-v">{type_label}</span></div>'
                if recommendation:
                    detail_rows += f'<div class="dd-kv"><span class="dd-k">推奨</span><span class="dd-v">{recommendation}</span></div>'
                if summary:
                    detail_rows += f'<div class="dd-kv"><span class="dd-k">要約</span><span class="dd-v">{summary[:500]}</span></div>'

                # キーポイント
                try:
                    import json as _json

                    kps = _json.loads(kp_raw) if kp_raw else []
                    if kps:
                        kp_list = "".join(f"<li>{kp}</li>" for kp in kps[:5])
                        detail_rows += f'<div class="dd-kv"><span class="dd-k">注目点</span><span class="dd-v"><ul style="margin:0; padding-left:1.2rem">{kp_list}</ul></span></div>'
                except Exception as e:
                    logger.warning(f"注目点JSON解析エラー: {e}")

                if detailed:
                    detail_rows += (
                        f'<div style="margin-top:0.4rem; padding-top:0.4rem; border-top:1px solid #e2e8f0">'
                        f'<span class="dd-k">詳細分析</span>'
                        f'<div style="margin-top:0.2rem; white-space:pre-wrap">{detailed[:800]}</div></div>'
                    )

                if model:
                    detail_rows += f'<div class="dd-kv" style="margin-top:0.3rem"><span class="dd-k">モデル</span><span class="dd-v">{model} / {time_a}</span></div>'

                ana_html += f"""<div class="dd-item"><details>
                    <summary class="dd-summary">{header}</summary>
                    <div class="dd-detail">{detail_rows}</div>
                    </details></div>"""

            st.markdown(ana_html, unsafe_allow_html=True)
        else:
            st.markdown(
                '<span style="color:#94a3b8; font-size:0.82rem">本日のAI分析はありません</span>',
                unsafe_allow_html=True,
            )

    # 4c: 売買判断
    sig_cnt = pipeline["steps"]["signals"]["count"]
    with st.expander(f"Step 3. 売買判断 - {sig_cnt}件", expanded=False):
        today_sigs = _dm.get_todays_signals()
        if len(today_sigs) > 0:
            sig_html = ""
            for _, s in today_sigs.iterrows():
                sig_type = s["signal_type"]
                sig_label = "買い" if sig_type == "BUY" else "売り"
                sig_cls = "pill-green" if sig_type == "BUY" else "pill-red"
                conf = s.get("confidence", 0) or 0
                conv = s.get("conviction", 0) or 0
                price = s.get("price", 0) or 0
                status_s = s.get("status", "")
                status_label = {
                    "detected": "検出済",
                    "pending": "待機中",
                    "executed": "執行済",
                    "rejected": "見送り",
                    "cancelled": "取消",
                    "expired": "期限切れ",
                }.get(status_s, status_s)
                reasoning = s.get("reasoning", "") or ""
                df_raw = s.get("decision_factors_json", "") or ""
                target = s.get("target_price") or 0
                sl = s.get("stop_loss") or 0
                rsi = s.get("rsi")
                macd = s.get("macd")
                time_s = str(s.get("detected_at", ""))[:16].replace("T", " ")

                header = (
                    f'<span class="pill {sig_cls}" style="font-size:0.7rem">{sig_label}</span> '
                    f'<b style="margin-left:0.2rem">{s["ticker"]}</b> '
                    f'<span style="color:#64748b">@${price:.2f}</span> '
                    f'<span class="pill pill-blue" style="font-size:0.58rem; padding:0.03rem 0.25rem">{status_label}</span>'
                )

                detail_rows = ""
                detail_rows += f'<div class="dd-kv"><span class="dd-k">信頼度</span><span class="dd-v">{conf:.0%}</span></div>'
                if conv:
                    detail_rows += f'<div class="dd-kv"><span class="dd-k">確信度</span><span class="dd-v">{conv:.0f} / 10</span></div>'
                if target:
                    detail_rows += f'<div class="dd-kv"><span class="dd-k">目標価格</span><span class="dd-v">${target:.2f}</span></div>'
                if sl:
                    detail_rows += f'<div class="dd-kv"><span class="dd-k">損切ライン</span><span class="dd-v">${sl:.2f}</span></div>'
                if rsi is not None and pd.notna(rsi):
                    detail_rows += f'<div class="dd-kv"><span class="dd-k">RSI</span><span class="dd-v">{rsi:.1f}</span></div>'
                if macd is not None and pd.notna(macd):
                    detail_rows += f'<div class="dd-kv"><span class="dd-k">MACD</span><span class="dd-v">{macd:.4f}</span></div>'
                if reasoning:
                    detail_rows += f'<div class="dd-kv"><span class="dd-k">判断理由</span><span class="dd-v">{reasoning}</span></div>'

                # decision_factors
                try:
                    import json as _json

                    factors = _json.loads(df_raw) if df_raw else {}
                    if isinstance(factors, dict):
                        dr = factors.get("detailed_reason", "") or factors.get(
                            "reason", ""
                        )
                        chg = factors.get("change_pct")
                        if dr:
                            detail_rows += f'<div class="dd-kv"><span class="dd-k">詳細根拠</span><span class="dd-v">{dr}</span></div>'
                        if chg is not None:
                            detail_rows += f'<div class="dd-kv"><span class="dd-k">変動率</span><span class="dd-v">{chg:+.1f}%</span></div>'
                except Exception as e:
                    logger.warning(f"シグナル要因解析エラー: {e}")

                detail_rows += f'<div class="dd-kv"><span class="dd-k">検出時刻</span><span class="dd-v">{time_s}</span></div>'

                sig_html += f"""<div class="dd-item"><details>
                    <summary class="dd-summary">{header}</summary>
                    <div class="dd-detail">{detail_rows}</div>
                    </details></div>"""

            st.markdown(sig_html, unsafe_allow_html=True)
        else:
            st.markdown(
                '<span style="color:#94a3b8; font-size:0.82rem">本日の売買判断はありません</span>',
                unsafe_allow_html=True,
            )

    # 4d: 注文執行
    trade_cnt = pipeline["steps"]["trading"]["count"]
    with st.expander(f"Step 4. 注文執行 - {trade_cnt}件", expanded=False):
        today_trades = _dm.get_todays_trades()
        if len(today_trades) > 0:
            trade_html = ""
            for _, t in today_trades.iterrows():
                action = t["action"]
                a_label = "買い" if action == "BUY" else "売り"
                a_cls = "pill-green" if action == "BUY" else "pill-red"
                pnl_v = t.get("profit_loss") or 0
                pnl_c = "c-pos" if pnl_v >= 0 else "c-neg"
                pnl_s = "+" if pnl_v >= 0 else ""
                shares = int(t["shares"])
                entry_p = t["entry_price"]
                exit_p = t.get("exit_price")
                holding = t.get("holding_days")
                exit_reason = t.get("exit_reason", "") or ""
                entry_ts = str(t.get("entry_timestamp", ""))[:16].replace("T", " ")
                exit_ts = (
                    str(t.get("exit_timestamp", ""))[:16].replace("T", " ")
                    if t.get("exit_timestamp")
                    else ""
                )

                if t["status"] == "CLOSED":
                    pnl_txt = f'<span class="{pnl_c}" style="font-weight:600">{pnl_s}${pnl_v:,.2f}</span>'
                else:
                    pnl_txt = '<span class="pill pill-blue" style="font-size:0.6rem">保有中</span>'

                header = (
                    f'<span class="pill {a_cls}" style="font-size:0.7rem">{a_label}</span> '
                    f'<b style="margin-left:0.2rem">{t["ticker"]}</b> '
                    f'<span style="color:#64748b">{shares}株 @${entry_p:.2f}</span> '
                    f"{pnl_txt}"
                )

                detail_rows = ""
                detail_rows += f'<div class="dd-kv"><span class="dd-k">エントリー</span><span class="dd-v">${entry_p:.2f} ({entry_ts})</span></div>'
                if exit_p:
                    detail_rows += f'<div class="dd-kv"><span class="dd-k">エグジット</span><span class="dd-v">${exit_p:.2f} ({exit_ts})</span></div>'
                if t["status"] == "CLOSED":
                    pnl_pct = t.get("profit_loss_pct") or 0
                    detail_rows += f'<div class="dd-kv"><span class="dd-k">損益</span><span class="dd-v {pnl_c}">{pnl_s}${pnl_v:,.2f} ({pnl_s}{pnl_pct:.1f}%)</span></div>'
                if holding is not None and pd.notna(holding):
                    detail_rows += f'<div class="dd-kv"><span class="dd-k">保有日数</span><span class="dd-v">{int(holding)}日</span></div>'
                if exit_reason:
                    reason_label = {
                        "STOP_LOSS": "損切り",
                        "TAKE_PROFIT": "利確",
                        "SIGNAL": "シグナル",
                        "MANUAL": "手動",
                    }.get(exit_reason, exit_reason)
                    detail_rows += f'<div class="dd-kv"><span class="dd-k">決済理由</span><span class="dd-v">{reason_label}</span></div>'

                trade_html += f"""<div class="dd-item"><details>
                    <summary class="dd-summary">{header}</summary>
                    <div class="dd-detail">{detail_rows}</div>
                    </details></div>"""

            st.markdown(trade_html, unsafe_allow_html=True)
        else:
            st.markdown(
                '<span style="color:#94a3b8; font-size:0.82rem">本日の取引はありません</span>',
                unsafe_allow_html=True,
            )

    # 4e: 資産記録
    snap_cnt = pipeline["steps"]["portfolio"]["count"]
    with st.expander(f"Step 5. 資産記録 - {snap_cnt}件", expanded=False):
        if snap_cnt > 0:
            snap_time = pipeline["steps"]["portfolio"]["last_at"]
            st.markdown(
                f'<div style="font-size:0.82rem; color:#0f172a; padding:0.3rem 0">'
                f"本日 {snap_time} にポートフォリオスナップショットを{snap_cnt}件記録しました。"
                f"<br>最新の資産状況は Overview タブで確認できます。</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<span style="color:#94a3b8; font-size:0.82rem">本日のスナップショットはありません</span>',
                unsafe_allow_html=True,
            )

# ============================================================
# システム仕様 タブ
# ============================================================

with tab_spec:

    st.markdown(
        '<div class="spec-highlight">'
        "<b>システム仕様 — 設計と仕組みのリファレンス</b><br>"
        "このタブではAI投資システムの全体像・設計思想・設定値をまとめています。"
        "「投資プロセス」タブで見た実行結果が「なぜそうなったか」を理解するための参照資料です。"
        "</div>",
        unsafe_allow_html=True,
    )

    # ── 0. システム概要 ──

    st.markdown(
        f'<div class="sec-hdr">'
        f'<div class="bar" style="background:#0f172a"></div>'
        f'<div class="txt">システム概要</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#127919;</span>AI Investor とは</div>'
        '<div style="padding:0.5rem 1rem; font-size:0.76rem; color:#475569; line-height:1.8">'
        "米国株式市場を対象とした<b>完全自動AI投資システム</b>です。"
        "ニュース収集からAI分析、売買判断、注文執行、資産記録までを人間の介入なしに24時間稼働します。<br>"
        "テクニカル指標（定量）とGoogle Gemini LLMによる定性分析を組み合わせ、"
        "3つの売買戦略で米国株115銘柄（15テーマ）を監視・取引します。"
        "</div>"
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">対象市場</span><span class="spec-v">米国株式（NYSE / NASDAQ）</span></div>'
        '<div class="spec-row"><span class="spec-k">取引種別</span><span class="spec-v">現物ロングのみ（空売り・オプション非対応）</span></div>'
        '<div class="spec-row"><span class="spec-k">取引時間</span><span class="spec-v">通常取引時間のみ（9:30-16:00 ET）</span></div>'
        '<div class="spec-row"><span class="spec-k">人的介入</span><span class="spec-v">0%（完全自動）</span></div>'
        '<div class="spec-row"><span class="spec-k">実行環境</span><span class="spec-v">GCP VM（e2-micro / us-central1-a）</span></div>'
        '<div class="spec-row"><span class="spec-k">データベース</span><span class="spec-v">SQLite（16テーブル / ニュース30日保持）</span></div>'
        '<div class="spec-row"><span class="spec-k">月額コスト</span><span class="spec-v">約¥5,000（API利用料）</span></div>'
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128200;</span>現在のフェーズと目標</div>'
        '<div style="padding:0.5rem 1rem; font-size:0.76rem; color:#475569; line-height:1.8">'
        "<b>Phase 3: ペーパートレード検証</b>（2026年1月24日〜）<br>"
        "Alpacaのペーパートレード環境で実際の市場データを使い、"
        "初期資本 $100,000 で完全自動運用を行い、実取引移行の可否を判定します。"
        "</div>"
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">初期資本</span><span class="spec-v">$100,000（ペーパー）</span></div>'
        f'<div class="spec-row"><span class="spec-k">Go/No-Go判定</span><span class="spec-v">{_dm.GONOGO_DEADLINE}</span></div>'
        "</div>"
        '<div style="padding:0.5rem 1rem 0.2rem">'
        '<div style="font-size:0.72rem; font-weight:600; color:#64748b; margin-bottom:0.25rem">Go/No-Go 判定基準</div>'
        "</div>"
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">勝率</span><span class="spec-v">&ge; 55%（目標 60%）</span></div>'
        '<div class="spec-row"><span class="spec-k">累積リターン</span><span class="spec-v">&ge; +5%（3ヶ月間）</span></div>'
        '<div class="spec-row"><span class="spec-k">最大ドローダウン</span><span class="spec-v">&le; -15%</span></div>'
        '<div class="spec-row"><span class="spec-k">システム稼働率</span><span class="spec-v">&ge; 99%</span></div>'
        '<div class="spec-row"><span class="spec-k">注文成功率</span><span class="spec-v">&ge; 95%</span></div>'
        '<div class="spec-row"><span class="spec-k">人的介入率</span><span class="spec-v">0%</span></div>'
        "</div>"
        '<div class="spec-note">'
        "<b>Go:</b> 全基準達成 → Phase 4（実資金少額運用）に移行 / "
        "<b>条件付き:</b> 勝率55-60%＋改善傾向あり → Phase 3を3ヶ月延長 / "
        "<b>No-Go:</b> 勝率55%未満 or 重大問題 → Phase 2に差し戻し"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    # ── 1. スケジュール ──

    st.markdown(
        f'<div class="sec-hdr">'
        f'<div class="bar" style="background:{P}"></div>'
        f'<div class="txt">実行スケジュール</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128339;</span>日次スケジュール（米国東部時間）</div>'
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">プレマーケット分析</span><span class="spec-v">09:00 ET（毎日）</span></div>'
        '<div class="spec-row"><span class="spec-k">シグナル検出</span><span class="spec-v">9:30〜15:30 ET / 30分毎</span></div>'
        '<div class="spec-row"><span class="spec-k">日次サマリー</span><span class="spec-v">16:30 ET（市場終了後）</span></div>'
        '<div class="spec-row"><span class="spec-k">ニュース収集</span><span class="spec-v">9:15〜15:15 ET / 1時間毎</span></div>'
        '<div class="spec-row"><span class="spec-k">経済データ更新</span><span class="spec-v">08:00 ET（FRED）</span></div>'
        '<div class="spec-row"><span class="spec-k">日次シグナル回数</span><span class="spec-v">13回/日</span></div>'
        "</div>"
        '<div class="spec-note">土日・祝日は自動スキップ。全ての時刻はサマータイムに自動対応。</div>'
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#9881;</span>実行モード</div>'
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">定時分析（Full）</span><span class="spec-v">AI分析+ニュース+全指標</span></div>'
        '<div class="spec-row"><span class="spec-k">シグナル検出（Signal）</span><span class="spec-v">リアルタイム売買判断</span></div>'
        '<div class="spec-row"><span class="spec-k">日次サマリー</span><span class="spec-v">ポジション確認+通知</span></div>'
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    # ── 2. 情報収集の仕組み ──

    st.markdown(
        f'<div class="sec-hdr">'
        f'<div class="bar" style="background:#f59e0b"></div>'
        f'<div class="txt">情報収集の仕組み</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128225;</span>データソース</div>'
        '<div style="padding:0.4rem 1rem 0.3rem">'
        '<div style="font-size:0.72rem; font-weight:600; color:#64748b; margin-bottom:0.3rem">'
        '<span class="spec-badge spec-b1">Tier 1</span>公式データ（高信頼性）</div>'
        '<ul class="spec-list" style="margin:0 0 0.5rem; padding-left:1.5rem">'
        "<li>FRED - 米国経済指標（GDP, 雇用統計, CPI等）</li>"
        "<li>Alpha Vantage - 決算カレンダー</li>"
        "<li>Alpaca - 株価データ + 取引API</li>"
        "</ul>"
        '<div style="font-size:0.72rem; font-weight:600; color:#64748b; margin-bottom:0.3rem">'
        '<span class="spec-badge spec-b2">Tier 2</span>金融メディア</div>'
        '<ul class="spec-list" style="margin:0 0 0.5rem; padding-left:1.5rem">'
        "<li>Yahoo Finance / Google News RSS / NewsAPI</li>"
        "<li>Finnhub（60req/分）/ FMP（250req/日）</li>"
        "</ul>"
        '<div style="font-size:0.72rem; font-weight:600; color:#64748b; margin-bottom:0.3rem">'
        '<span class="spec-badge spec-b3">Tier 3</span>コミュニティ</div>'
        '<ul class="spec-list" style="margin:0 0 0.3rem; padding-left:1.5rem">'
        "<li>Reddit（wallstreetbets, stocks, investing）</li>"
        "</ul>"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128240;</span>RSSフィード（8+メディア）</div>'
        '<ul class="spec-list" style="padding-left:2rem">'
        "<li>MarketWatch Top Stories</li>"
        "<li>CNBC Finance / CNBC Top News</li>"
        "<li>Nasdaq RSS</li>"
        "<li>Seeking Alpha</li>"
        "<li>Yahoo Finance RSS</li>"
        "<li>Investing.com</li>"
        "<li>Benzinga</li>"
        "</ul>"
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">巡回間隔</span><span class="spec-v">15分</span></div>'
        '<div class="spec-row"><span class="spec-k">重複排除</span><span class="spec-v">URLベースUNIQUE制約</span></div>'
        '<div class="spec-row"><span class="spec-k">類似記事判定</span><span class="spec-v">85%以上で重複扱い</span></div>'
        '<div class="spec-row"><span class="spec-k">保存期間</span><span class="spec-v">30日間</span></div>'
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    # ニュースが投資判断に影響する流れ
    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128279;</span>ニュースが投資判断に影響する流れ</div>'
        '<div style="padding:0.5rem 1rem; font-size:0.74rem; color:#475569; line-height:1.7">'
        "収集されたニュースは以下の3段階で処理され、売買シグナルの確信度に反映されます:"
        "</div>"
        '<div style="padding:0 1rem 0.5rem; font-size:0.72rem; color:#64748b; line-height:1.7">'
        "<b>Step 1. イベント分類:</b> AIが各ニュースを9カテゴリ（決算・アナリスト・M&amp;A等）に分類し、"
        "影響の大きさ(0-1)とセンチメント(-1〜+1)を付与<br>"
        "<b>Step 2. 時間減衰:</b> イベントの種類ごとに半減期を設定（決算3日、M&amp;A 30日、一般2日等）。"
        "古いニュースの影響を指数関数的に減少<br>"
        "<b>Step 3. テーマ波及:</b> リーダー銘柄のニュースをフォロワー銘柄に0.7倍で波及。"
        "例: NVDAの好決算 → AMD・TSMに+0.56のスコアが波及<br>"
        "<b>Step 4. マクロ影響:</b> FRB金利・CPI等のマクロニュースは該当セクター全体に影響"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    # ── 3. AI分析の仕組み ──

    st.markdown(
        f'<div class="sec-hdr">'
        f'<div class="bar" style="background:#8b5cf6"></div>'
        f'<div class="txt">AI（LLM）による定性分析</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="spec-highlight">'
        "本システムでは、テクニカル指標（定量分析）だけでなく、"
        "Google Gemini LLMを活用した<b>6種類の定性分析</b>を組み合わせて投資判断を行います。"
        "LLMは「シニアアナリスト」「ヘッジファンドマネージャー」等の役割を与えられ、"
        "構造化されたプロンプトに基づき、ニュースの本質的な意味や市場の方向性を判断します。"
        "</div>",
        unsafe_allow_html=True,
    )

    # 3-1: AIモデル構成
    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#129302;</span>AIモデル構成</div>'
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">メインモデル</span><span class="spec-v">Gemini 3 Pro Preview</span></div>'
        '<div class="spec-row"><span class="spec-k">フォールバック</span><span class="spec-v">Gemini 2.5 Pro</span></div>'
        '<div class="spec-row"><span class="spec-k">軽量処理用</span><span class="spec-v">Gemini 2.5 Flash</span></div>'
        '<div class="spec-row"><span class="spec-k">最終手段</span><span class="spec-v">Deepseek（Gemini全障害時）</span></div>'
        '<div class="spec-row"><span class="spec-k">API制限</span><span class="spec-v">50リクエスト/日（動的スロットル）</span></div>'
        '<div class="spec-row"><span class="spec-k">キャッシュ</span><span class="spec-v">1時間TTL / 最大100件</span></div>'
        '<div class="spec-row"><span class="spec-k">リトライ</span><span class="spec-v">最大3回 / 指数バックオフ</span></div>'
        "</div>"
        '<div class="spec-note">重要な売買判断（テーマ分析・トレード戦略）にはProモデル、ニュース要約やセンチメント分類にはFlashモデルを使用。'
        "API使用量80%超で自動的に間隔を広げるスロットル機構付き。</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    # 3-2: 6種類のAI分析
    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128209;</span>LLM定性分析の6つのレイヤー</div>'
        '<div style="padding:0.5rem 1rem">'
        # -- 分析1: テーマ分析 --
        '<div style="margin-bottom:1rem; padding-bottom:0.8rem; border-bottom:1px solid #f1f5f9">'
        '<div style="font-size:0.82rem; font-weight:700; color:#1e40af; margin-bottom:0.3rem">'
        "1. テーマ分析（メガトレンド評価）</div>"
        '<div style="font-size:0.74rem; color:#475569; line-height:1.7">'
        "AIに「<b>シニアアナリスト（3-6ヶ月メガトレンド投資専門）</b>」の役割を与え、"
        "各投資テーマを包括的に評価させます。</div>"
        '<div style="font-size:0.72rem; color:#64748b; margin-top:0.3rem; line-height:1.6">'
        "<b>AIへの入力:</b> テーマ根拠 + マクロ環境（金利・インフレ）+ 市場データ（変動率・高安）"
        "+ テクニカル（RSI・MA50）+ ニュース上位3件<br>"
        "<b>AIの出力:</b> 現状分析(200字) / 3-6ヶ月見通し(250字) / メガトレンドスコア(0-100) / "
        "推奨保有期間 / 触媒リスト / リスク要因 / 信頼度(0-100) / セクターローテーション適合度<br>"
        "<b>判断基準:</b> 週次〜月次のトレンド重視。日次変動は無視。景気サイクルにおけるセクター位置を考慮。</div>"
        "</div>"
        # -- 分析2: ニュースセンチメント --
        '<div style="margin-bottom:1rem; padding-bottom:0.8rem; border-bottom:1px solid #f1f5f9">'
        '<div style="font-size:0.82rem; font-weight:700; color:#1e40af; margin-bottom:0.3rem">'
        "2. ニュースセンチメント分析（Chain-of-Thought）</div>"
        '<div style="font-size:0.74rem; color:#475569; line-height:1.7">'
        "AIに「<b>プロの投資アナリスト</b>」の役割を与え、段階的推論（Chain-of-Thought）で"
        "ニュースの投資への影響を評価させます。</div>"
        '<div style="font-size:0.72rem; color:#64748b; margin-top:0.3rem; line-height:1.6">'
        "<b>分析手順（Step by Step）:</b><br>"
        "&ensp;Step 1. 各ニュースの本質的な意味を理解<br>"
        "&ensp;Step 2. 短期(1-5日)と中期(1-4週間)の株価への影響を<b>別々に</b>評価<br>"
        "&ensp;Step 3. ポジティブ要因（触媒）とネガティブ要因（逆風）を列挙<br>"
        "&ensp;Step 4. 総合的な投資判断を導出<br>"
        "<b>AIの出力:</b> センチメントスコア(-1.0〜+1.0) / 短期・中期見通し / 触媒3件 / 逆風3件 / "
        "重要イベント3件 / 総合判断理由</div>"
        "</div>"
        # -- 分析3: イベント分類 --
        '<div style="margin-bottom:1rem; padding-bottom:0.8rem; border-bottom:1px solid #f1f5f9">'
        '<div style="font-size:0.82rem; font-weight:700; color:#1e40af; margin-bottom:0.3rem">'
        "3. イベント分類と影響度評価</div>"
        '<div style="font-size:0.74rem; color:#475569; line-height:1.7">'
        "各ニュースを9カテゴリに自動分類し、カテゴリごとに異なる<b>影響の持続期間</b>を適用します。</div>"
        '<div style="font-size:0.72rem; color:#64748b; margin-top:0.3rem; line-height:1.6">'
        "<b>分類カテゴリ:</b> 決算(半減期3日) / アナリスト評価(7日) / 新製品(14日) / M&amp;A(30日) / "
        "人事異動(7日) / 法規制(21日) / マクロ経済(14日) / セクター動向(7日) / 一般(2日)<br>"
        "<b>AIの判断:</b> カテゴリ + センチメント(-1〜+1) + 影響の大きさ(0〜1)<br>"
        "<b>時間減衰:</b> 古いニュースほど影響を指数関数的に減少させ、鮮度を重視。</div>"
        "</div>"
        # -- 分析4: ディープニュース分析 --
        '<div style="margin-bottom:1rem; padding-bottom:0.8rem; border-bottom:1px solid #f1f5f9">'
        '<div style="font-size:0.82rem; font-weight:700; color:#1e40af; margin-bottom:0.3rem">'
        "4. ディープニュース分析（2段階分析）</div>"
        '<div style="font-size:0.74rem; color:#475569; line-height:1.7">'
        "シグナル検出時に、その銘柄に関する全ニュースをAIが<b>深掘り分析</b>して確信度を調整します。</div>"
        '<div style="font-size:0.72rem; color:#64748b; margin-top:0.3rem; line-height:1.6">'
        "<b>Tier 1（背景蓄積）:</b> RSS・DB・Redditから記事を収集・蓄積。URLで重複排除。<br>"
        "<b>Tier 2（深層分析）:</b> Gemini Proに全記事のブリーフィングを渡し、以下を判断:<br>"
        "&ensp;- クロスソース合意度（複数メディアが同じ論調か？ 分散が小さい＝合意高い）<br>"
        "&ensp;- センチメント推移（直近3日 vs 4-7日前。±0.15以上の差で改善/悪化と判定）<br>"
        "&ensp;- 確信度調整（-3〜+3。AIの判断でシグナルの確信度を上下）<br>"
        "<b>推奨アクション:</b> confirm（そのまま） / increase（確信度UP） / decrease（DOWN） / reject（取消）<br>"
        "<b>フォールバック:</b> AI障害時はキーワードベース分析に自動切替。</div>"
        "</div>"
        # -- 分析5: メガトレンドスコアリング --
        '<div style="margin-bottom:1rem; padding-bottom:0.8rem; border-bottom:1px solid #f1f5f9">'
        '<div style="font-size:0.82rem; font-weight:700; color:#1e40af; margin-bottom:0.3rem">'
        "5. メガトレンドスコアリング（5軸×20点）</div>"
        '<div style="font-size:0.74rem; color:#475569; line-height:1.7">'
        "AIに「<b>ベテラン投資ストラテジスト</b>」の役割を与え、"
        "各テーマを5つの観点で定量スコアリングさせます。</div>"
        '<div style="font-size:0.72rem; color:#64748b; margin-top:0.3rem; line-height:1.6">'
        "<b>5つの評価軸（各0-20点、計100点満点）:</b><br>"
        "&ensp;1. <b>ニュース出現頻度</b> - 連日トップニュース=20点、ほぼ話題なし=0点<br>"
        "&ensp;2. <b>投資額（資金流入）</b> - 政府補助金+メガテック全力投資=20点、限定的=0点<br>"
        "&ensp;3. <b>技術成熟度</b> - 商用化・収益化済=20点、実験室レベル=0点（ガートナーハイプサイクル準拠）<br>"
        "&ensp;4. <b>市場予測</b> - CAGR 30%以上+巨大TAM=20点、成長鈍化=0点<br>"
        "&ensp;5. <b>企業決算での言及</b> - 主要企業の最重要トピック=20点、言及なし=0点<br>"
        "<b>ライフサイクル判定:</b> 0-39=萌芽期 / 40-69=成長期 / 70-85=成熟期 / 86-100=過熱期</div>"
        "</div>"
        # -- 分析6: トレード戦略生成 --
        "<div>"
        '<div style="font-size:0.82rem; font-weight:700; color:#1e40af; margin-bottom:0.3rem">'
        "6. トレード戦略生成（最終意思決定支援）</div>"
        '<div style="font-size:0.74rem; color:#475569; line-height:1.7">'
        "AIに「<b>ヘッジファンドのシニアポートフォリオマネージャー</b>」の役割を与え、"
        "具体的な売買プランを生成させます。</div>"
        '<div style="font-size:0.72rem; color:#64748b; margin-top:0.3rem; line-height:1.6">'
        "<b>AIへの入力:</b> 現在価格・変動率 + MA50/MA200/RSI/52週高安/出来高比 + 過去24hの重要ニュース + ポジション状況<br>"
        "<b>AIの出力:</b><br>"
        "&ensp;- 推奨アクション: BUY / SELL / HOLD / REDUCE / WATCH（5段階）<br>"
        "&ensp;- 確信度: 1-10（曖昧さ禁止、具体的な数値で理由付き）<br>"
        "&ensp;- エントリー戦略: 推奨価格 + 条件（例:「$XXX突破後、RSI 50以下で押し目」）<br>"
        "&ensp;- エグジット戦略: 利確2段階（第1・第2目標）+ 損切ライン + 各条件<br>"
        "&ensp;- リスクリワード比: 計算に基づく数値（BUYは2.5倍以上が必須）<br>"
        "&ensp;- 触媒: 日付付きのカタリスト一覧<br>"
        "&ensp;- リスク: 具体的なリスク要因と影響<br>"
        "&ensp;- アクションプラン: 「今日→今週→来月」の時系列行動計画<br>"
        "&ensp;- 代替シナリオ: 想定外の展開時の対応策</div>"
        "</div>"
        "</div>"  # padding div end
        "</div>",  # card end
        unsafe_allow_html=True,
    )

    # 3-3: 定量×定性の統合
    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128279;</span>定量×定性の統合（最終判断の仕組み）</div>'
        '<div style="padding:0.5rem 1rem; font-size:0.74rem; color:#475569; line-height:1.7">'
        "テクニカル指標（定量）とAI分析（定性）は以下の流れで統合されます:"
        "</div>"
        '<div style="padding:0 1rem 0.5rem">'
        # フロー図
        '<div style="display:flex; flex-direction:column; gap:0.3rem; font-size:0.72rem">'
        '<div style="display:flex; align-items:center; gap:0.5rem">'
        '<span style="background:#dbeafe; color:#1d4ed8; padding:0.2rem 0.5rem; border-radius:6px; font-weight:600; min-width:5rem; text-align:center">定量分析</span>'
        '<span style="color:#94a3b8">&rarr;</span>'
        '<span style="color:#475569">RSI・MACD・出来高等でベースのシグナルスコア(0-100)を算出</span>'
        "</div>"
        '<div style="display:flex; align-items:center; gap:0.5rem">'
        '<span style="background:#f3e8ff; color:#7c3aed; padding:0.2rem 0.5rem; border-radius:6px; font-weight:600; min-width:5rem; text-align:center">AI定性</span>'
        '<span style="color:#94a3b8">&rarr;</span>'
        '<span style="color:#475569">ニュースセンチメント・ディープ分析で確信度を -3〜+3 調整</span>'
        "</div>"
        '<div style="display:flex; align-items:center; gap:0.5rem">'
        '<span style="background:#ecfdf5; color:#059669; padding:0.2rem 0.5rem; border-radius:6px; font-weight:600; min-width:5rem; text-align:center">候補選定</span>'
        '<span style="color:#94a3b8">&rarr;</span>'
        '<span style="color:#475569">複合スコアでランク付け（下記配分）</span>'
        "</div>"
        '<div style="display:flex; align-items:center; gap:0.5rem">'
        '<span style="background:#fff7ed; color:#c2410c; padding:0.2rem 0.5rem; border-radius:6px; font-weight:600; min-width:5rem; text-align:center">最終判断</span>'
        '<span style="color:#94a3b8">&rarr;</span>'
        '<span style="color:#475569">リスク管理チェックを通過した候補のみ注文執行</span>'
        "</div>"
        "</div>"
        "</div>"
        # 複合スコア配分
        '<div style="padding:0.4rem 1rem 0.3rem">'
        '<div style="font-size:0.72rem; font-weight:600; color:#64748b; margin-bottom:0.25rem">候補選定の複合スコア配分</div>'
        "</div>"
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">確信度（Conviction）</span><span class="spec-v">20%</span></div>'
        '<div class="spec-row"><span class="spec-k">リスクリワード比</span><span class="spec-v">15%</span></div>'
        '<div class="spec-row"><span class="spec-k">セクターモメンタム</span><span class="spec-v">15%</span></div>'
        '<div class="spec-row"><span class="spec-k">相対強度（vs SPY・セクター）</span><span class="spec-v">15%</span></div>'
        '<div class="spec-row"><span class="spec-k">ニューススコア（AI定性）</span><span class="spec-v">15%</span></div>'
        '<div class="spec-row"><span class="spec-k">セクター分散ボーナス</span><span class="spec-v">10%</span></div>'
        '<div class="spec-row"><span class="spec-k">相関ペナルティ（低い方が有利）</span><span class="spec-v">10%</span></div>'
        "</div>"
        '<div class="spec-note">'
        "<b>ニュースによる確信度調整の例:</b> "
        "ニューススコア &gt; 0.5 → +2 / &gt; 0.3 → +1 / &lt; -0.3 → -1 / "
        "短期見通しが弱気 → -2。AIが「reject」を返した場合はシグナル自体を取消。"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    # ── 4. 売買判断の基準 ──

    st.markdown(
        f'<div class="sec-hdr">'
        f'<div class="bar" style="background:{W}"></div>'
        f'<div class="txt">売買判断の基準</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128200;</span>3つの売買戦略</div>'
        '<div style="padding:0.5rem 1rem">'
        # 戦略1
        '<div style="margin-bottom:1rem; padding-bottom:0.8rem; border-bottom:1px solid #f1f5f9">'
        '<div style="font-size:0.82rem; font-weight:700; color:#0f172a; margin-bottom:0.2rem">'
        "1. 押し目買い（Mean Reversion）</div>"
        '<div style="font-size:0.74rem; color:#475569; line-height:1.6; margin-bottom:0.3rem">'
        "RSIが40以下に下がった銘柄を「売られすぎ」と判断し買いシグナルを出す。"
        "相場の行き過ぎた下落からの反発を狙う戦略。</div>"
        '<div style="font-size:0.72rem; color:#64748b; line-height:1.6">'
        "<b>必須条件:</b> ADX&ge;20（レンジ相場を除外）+ MA200デッドゾーン外（&plusmn;0.5%以上離れていること）<br>"
        "<b>確信度加点:</b> MA200上=+2 / RSI 40-60=+2 / ゴールデンクロス=+2 / BB下限接近=+2 / 出来高急増=+1 / MACD&gt;Signal=+2 / ストキャスティクス&lt;20=+2<br>"
        "<b>追加検証（Tier 1のみ）:</b> 週足トレンド確認(+2/-5) / ファンダメンタル(&plusmn;2) / セクター相対強度(&plusmn;2)</div>"
        "</div>"
        # 戦略2
        '<div style="margin-bottom:1rem; padding-bottom:0.8rem; border-bottom:1px solid #f1f5f9">'
        '<div style="font-size:0.82rem; font-weight:700; color:#0f172a; margin-bottom:0.2rem">'
        "2. トレンド追従（Trend Following）</div>"
        '<div style="font-size:0.74rem; color:#475569; line-height:1.6; margin-bottom:0.3rem">'
        "MACD・ゴールデンクロス・出来高急増等で上昇トレンドの初動を検出。"
        "ADXが20以上で明確なトレンドがあることを確認して発出。</div>"
        '<div style="font-size:0.72rem; color:#64748b; line-height:1.6">'
        "<b>必須条件（全て満たす）:</b> MA20 &gt; MA50（短期上昇）+ 価格 &gt; 20日高値（ブレイクアウト）"
        "+ 出来高 &gt; 平均×1.5倍（勢い確認）+ RSI &gt; 50（過熱なし）<br>"
        "<b>ベース確信度:</b> 8（高い）+ Tier 1強化あり</div>"
        "</div>"
        # 戦略3
        "<div>"
        '<div style="font-size:0.82rem; font-weight:700; color:#0f172a; margin-bottom:0.2rem">'
        "3. VIX逆張り（VIX Contrarian）</div>"
        '<div style="font-size:0.74rem; color:#475569; line-height:1.6; margin-bottom:0.3rem">'
        "VIX（恐怖指数）が25以上に急騰した際、パニック売りからの反発を狙う。"
        "市場全体が過度に悲観的なときに買い向かう逆張り戦略。</div>"
        '<div style="font-size:0.72rem; color:#64748b; line-height:1.6">'
        "<b>発動条件:</b> VIX &ge; 25 または VIX前日比+15%以上<br>"
        "<b>必須条件:</b> RSI &le; 40（売られすぎ）+ MA200からの乖離 &ge; -10%（長期トレンド健全）<br>"
        "<b>確信度:</b> ベース5 + VIXスパイク加算(+2) + RSI加算(+3)</div>"
        "</div>"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    # 多カテゴリ検証
    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#9989;</span>シグナル発出の必須条件</div>'
        '<div style="padding:0.5rem 1rem; font-size:0.74rem; color:#475569; line-height:1.7">'
        "テクニカル指標は5カテゴリ（トレンド・モメンタム・出来高・ボラティリティ・MACD）に分類されます。"
        "シグナルが発出されるには、<b>2カテゴリ以上</b>が同じ方向を示していることが必須です。"
        "これにより「RSIだけ低いが他は全て正常」のような偽シグナルを排除します。"
        "</div>"
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">多カテゴリ検証</span><span class="spec-v">最低3カテゴリ一致（強カテゴリ含む場合2で可）</span></div>'
        '<div class="spec-row"><span class="spec-k">確信度の閾値</span><span class="spec-v">6以上（10点満点）で発出</span></div>'
        '<div class="spec-row"><span class="spec-k">シグナル有効期限</span><span class="spec-v">2営業日（価格乖離10%超で自動失効）</span></div>'
        '<div class="spec-row"><span class="spec-k">処理順序</span><span class="spec-v">確信度が高い順に優先処理</span></div>'
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#127919;</span>テクニカル指標と閾値</div>'
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">RSI（買いゾーン）</span><span class="spec-v">&le; 40（強い買い: &le; 30）</span></div>'
        '<div class="spec-row"><span class="spec-k">RSI（売りゾーン）</span><span class="spec-v">&ge; 70</span></div>'
        '<div class="spec-row"><span class="spec-k">MACD</span><span class="spec-v">12/26/9（Fast/Slow/Signal）</span></div>'
        '<div class="spec-row"><span class="spec-k">ボリンジャーバンド</span><span class="spec-v">20期間, 2&sigma;</span></div>'
        '<div class="spec-row"><span class="spec-k">ADX（トレンド強度）</span><span class="spec-v">&ge; 20 で有効</span></div>'
        '<div class="spec-row"><span class="spec-k">出来高スパイク</span><span class="spec-v">&ge; 1.5倍（強: &ge; 2.0倍）</span></div>'
        '<div class="spec-row"><span class="spec-k">VIX閾値</span><span class="spec-v">&ge; 25（極端: &ge; 35）</span></div>'
        '<div class="spec-row"><span class="spec-k">移動平均線</span><span class="spec-v">MA20 / MA50 / MA200</span></div>'
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#9878;</span>シグナル総合スコア（0〜100点）</div>'
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">RSI</span><span class="spec-v">最大 25点</span></div>'
        '<div class="spec-row"><span class="spec-k">MACD</span><span class="spec-v">最大 20点</span></div>'
        '<div class="spec-row"><span class="spec-k">ボリンジャーバンド</span><span class="spec-v">最大 15点</span></div>'
        '<div class="spec-row"><span class="spec-k">出来高</span><span class="spec-v">最大 15点</span></div>'
        '<div class="spec-row"><span class="spec-k">ストキャスティクス</span><span class="spec-v">最大 15点</span></div>'
        '<div class="spec-row"><span class="spec-k">ADX</span><span class="spec-v">最大 10点</span></div>'
        "</div>"
        '<div class="spec-note">確信度（Conviction）が6以上（10点満点中）のシグナルのみ発出。70点以上で注文執行対象。</div>'
        "</div>",
        unsafe_allow_html=True,
    )

    # ── 5. 注文執行とリスク管理 ──

    st.markdown(
        f'<div class="sec-hdr">'
        f'<div class="bar" style="background:{L}"></div>'
        f'<div class="txt">注文執行とリスク管理</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    # 注文前チェックフロー
    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128269;</span>注文前チェック（7段階ゲート）</div>'
        '<div style="padding:0.5rem 1rem; font-size:0.74rem; color:#475569; line-height:1.7; margin-bottom:0.3rem">'
        "シグナルが検出された後、以下の7つのチェックを<b>順番に</b>通過した場合のみ注文が執行されます。"
        "いずれか1つでも不合格なら注文は中止されます。"
        "</div>"
        '<div style="padding:0 1rem 0.5rem; font-size:0.72rem">'
        '<div style="display:flex; flex-direction:column; gap:0.25rem">'
        '<div style="display:flex; align-items:center; gap:0.4rem">'
        '<span style="background:#ecfdf5; color:#059669; padding:0.15rem 0.35rem; border-radius:4px; font-weight:700; font-size:0.65rem">1</span>'
        '<span style="color:#0f172a; font-weight:600">価格検証</span>'
        '<span style="color:#64748b">— Alpaca実勢価格との乖離20%未満か確認</span></div>'
        '<div style="display:flex; align-items:center; gap:0.4rem">'
        '<span style="background:#ecfdf5; color:#059669; padding:0.15rem 0.35rem; border-radius:4px; font-weight:700; font-size:0.65rem">2</span>'
        '<span style="color:#0f172a; font-weight:600">サーキットブレーカー</span>'
        '<span style="color:#64748b">— 連続損失・日次損失リミットに抵触していないか</span></div>'
        '<div style="display:flex; align-items:center; gap:0.4rem">'
        '<span style="background:#ecfdf5; color:#059669; padding:0.15rem 0.35rem; border-radius:4px; font-weight:700; font-size:0.65rem">3</span>'
        '<span style="color:#0f172a; font-weight:600">市場レジーム</span>'
        '<span style="color:#64748b">— VIX &lt; 30 かつ SPY 5日間リターン &gt; -3%</span></div>'
        '<div style="display:flex; align-items:center; gap:0.4rem">'
        '<span style="background:#ecfdf5; color:#059669; padding:0.15rem 0.35rem; border-radius:4px; font-weight:700; font-size:0.65rem">4</span>'
        '<span style="color:#0f172a; font-weight:600">重複チェック</span>'
        '<span style="color:#64748b">— 同銘柄のポジション・注文が既にないか</span></div>'
        '<div style="display:flex; align-items:center; gap:0.4rem">'
        '<span style="background:#ecfdf5; color:#059669; padding:0.15rem 0.35rem; border-radius:4px; font-weight:700; font-size:0.65rem">5</span>'
        '<span style="color:#0f172a; font-weight:600">決算ブラックアウト</span>'
        '<span style="color:#64748b">— 決算発表7日以内の銘柄は取引停止</span></div>'
        '<div style="display:flex; align-items:center; gap:0.4rem">'
        '<span style="background:#ecfdf5; color:#059669; padding:0.15rem 0.35rem; border-radius:4px; font-weight:700; font-size:0.65rem">6</span>'
        '<span style="color:#0f172a; font-weight:600">マクロ・セクター</span>'
        '<span style="color:#64748b">— FRB金利環境・CPI + セクター相対強度で確信度調整(&plusmn;2)</span></div>'
        '<div style="display:flex; align-items:center; gap:0.4rem">'
        '<span style="background:#ecfdf5; color:#059669; padding:0.15rem 0.35rem; border-radius:4px; font-weight:700; font-size:0.65rem">7</span>'
        '<span style="color:#0f172a; font-weight:600">相関チェック</span>'
        '<span style="color:#64748b">— 既存保有との60日間ピアソン相関が0.7未満か（超過時は株数半減）</span></div>'
        "</div>"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    # ポジション管理
    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128184;</span>ポジション管理</div>'
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">取引API</span><span class="spec-v">Alpaca（ペーパートレード）</span></div>'
        '<div class="spec-row"><span class="spec-k">1銘柄あたり上限</span><span class="spec-v">ポートフォリオの20%</span></div>'
        '<div class="spec-row"><span class="spec-k">同時保有上限</span><span class="spec-v">5銘柄</span></div>'
        '<div class="spec-row"><span class="spec-k">1サイクルの最大買い</span><span class="spec-v">3銘柄</span></div>'
        '<div class="spec-row"><span class="spec-k">同セクター上限</span><span class="spec-v">1銘柄/日</span></div>'
        '<div class="spec-row"><span class="spec-k">注文タイムアウト</span><span class="spec-v">300秒（5分）</span></div>'
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    # リスク管理（動的SL/TP追加）
    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128737;</span>リスク管理</div>'
        '<div style="padding:0.4rem 1rem 0.2rem">'
        '<div style="font-size:0.72rem; font-weight:600; color:#64748b; margin-bottom:0.25rem">固定パラメータ</div>'
        "</div>"
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">HARD STOP LOSS（絶対防衛）</span><span class="spec-v" style="color:#e11d48">-8%</span></div>'
        '<div class="spec-row"><span class="spec-k">最大利確目標</span><span class="spec-v" style="color:#059669">+20%</span></div>'
        '<div class="spec-row"><span class="spec-k">最低リスクリワード比</span><span class="spec-v">1.5倍</span></div>'
        '<div class="spec-row"><span class="spec-k">日次損失リミット</span><span class="spec-v" style="color:#e11d48">-5%</span></div>'
        "</div>"
        '<div class="spec-note">通常のSL/TPは下記の動的VIX連動値が適用されます。'
        "HARD STOP LOSSは全ての条件を無視して強制発動する最終防衛ラインです。</div>"
        '<div style="padding:0.5rem 1rem 0.2rem">'
        '<div style="font-size:0.72rem; font-weight:600; color:#64748b; margin-bottom:0.25rem">動的SL/TP（VIXレベルで自動調整）</div>'
        "</div>"
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">VIX &lt; 15（低ボラ）</span><span class="spec-v">SL 4% / TP 18%</span></div>'
        '<div class="spec-row"><span class="spec-k">VIX 15-20（通常）</span><span class="spec-v">SL 5% / TP 15%</span></div>'
        '<div class="spec-row"><span class="spec-k">VIX 20-30（やや高）</span><span class="spec-v">SL 6% / TP 12%</span></div>'
        '<div class="spec-row"><span class="spec-k">VIX &gt; 30（高ボラ）</span><span class="spec-v">SL 7% / TP 10%</span></div>'
        "</div>"
        '<div class="spec-note">ATR（14日間の平均変動幅）も考慮し、SL = max(2×ATR, VIXベースSL) で算出。'
        "VIXが高い局面ではSLを広めに取り、TPを控えめに設定する保守的な運用。</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    # 決済条件
    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128276;</span>決済（エグジット）条件</div>'
        '<div style="padding:0.5rem 1rem; font-size:0.74rem; color:#475569; line-height:1.7">'
        "以下のいずれかの条件を満たすと自動で売却シグナルが発出されます:"
        "</div>"
        '<div style="padding:0 1rem 0.5rem; font-size:0.72rem; color:#64748b; line-height:1.7">'
        "<b>1. ストップロス:</b> 損失が固定SL%またはATRベースSLに到達<br>"
        "<b>2. テイクプロフィット:</b> 利益が15%以上（無条件） / 10%以上かつRSI&gt;65 / 12%以上かつRSI&gt;70<br>"
        "<b>3. テクニカル悪化:</b> RSI &gt; 80（含み益があれば） / MACDデスクロス（損益&plusmn;3%圏内）<br>"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#9888;</span>サーキットブレーカー</div>'
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">発動条件</span><span class="spec-v">3回連続損失</span></div>'
        '<div class="spec-row"><span class="spec-k">効果</span><span class="spec-v">新規注文を一時停止</span></div>'
        '<div class="spec-row"><span class="spec-k">クールダウン</span><span class="spec-v">1日</span></div>'
        '<div class="spec-row"><span class="spec-k">自動解除</span><span class="spec-v">クールダウン後に復帰</span></div>'
        '<div class="spec-row"><span class="spec-k">通知</span><span class="spec-v">Discord（発動時/解除時）</span></div>'
        "</div>"
        '<div class="spec-note">サーキットブレーカーはシグナル検出には影響しません。注文執行のみを停止し、シグナル分析は継続します。</div>'
        "</div>",
        unsafe_allow_html=True,
    )

    # ── 6. ポートフォリオ構成 ──

    st.markdown(
        f'<div class="sec-hdr">'
        f'<div class="bar" style="background:#64748b"></div>'
        f'<div class="txt">ポートフォリオ構成</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#127919;</span>投資テーマ（15テーマ / 115銘柄）</div>'
        '<div style="padding:0.5rem 1rem">'
        # Tier 1
        '<div style="margin-bottom:0.6rem">'
        '<div style="font-size:0.72rem; font-weight:600; color:#64748b; margin-bottom:0.25rem">'
        '<span class="spec-badge spec-b1">Tier 1</span>コア（フル分析・全シグナル通知）</div>'
        '<div style="font-size:0.76rem; color:#0f172a; line-height:1.7">'
        "Market Index / Sector ETFs / AI Semiconductor / Cloud AI Infrastructure<br>"
        '<span style="color:#64748b; font-size:0.7rem">主要銘柄: NVDA, MSFT, GOOGL, AMZN, AAPL, META, TSM, ASML, CRWD, CCJ</span>'
        "</div></div>"
        # Tier 2
        '<div style="margin-bottom:0.6rem">'
        '<div style="font-size:0.72rem; font-weight:600; color:#64748b; margin-bottom:0.25rem">'
        '<span class="spec-badge spec-b2">Tier 2</span>ウォッチ（確信度80%以上のみ通知）</div>'
        '<div style="font-size:0.76rem; color:#0f172a; line-height:1.7">'
        "Cybersecurity / Energy Infrastructure / Defense Space / Bio Genomics"
        "</div></div>"
        # Tier 3
        "<div>"
        '<div style="font-size:0.72rem; font-weight:600; color:#64748b; margin-bottom:0.25rem">'
        '<span class="spec-badge spec-b3">Tier 3</span>アーカイブ（週次レポートのみ）</div>'
        '<div style="font-size:0.76rem; color:#0f172a; line-height:1.7">'
        "Robotics / Quantum / RareEarth / CleanEnergy / Fintech / Consumer Tech / Enterprise SaaS"
        "</div></div>"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128260;</span>テーマローテーション</div>'
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">最大同時投資テーマ</span><span class="spec-v">3テーマ</span></div>'
        '<div class="spec-row"><span class="spec-k">選定方法</span><span class="spec-v">モメンタムランキング</span></div>'
        '<div class="spec-row"><span class="spec-k">リバランス頻度</span><span class="spec-v">週次</span></div>'
        "</div>"
        '<div style="padding:0.3rem 1rem 0.5rem">'
        '<div style="font-size:0.72rem; font-weight:600; color:#64748b; margin-bottom:0.25rem">モメンタム配分</div>'
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">価格モメンタム（1M）</span><span class="spec-v">30%</span></div>'
        '<div class="spec-row"><span class="spec-k">価格モメンタム（3M）</span><span class="spec-v">20%</span></div>'
        '<div class="spec-row"><span class="spec-k">ニュースセンチメント</span><span class="spec-v">20%</span></div>'
        '<div class="spec-row"><span class="spec-k">セクターローテーション</span><span class="spec-v">15%</span></div>'
        '<div class="spec-row"><span class="spec-k">ファンダメンタル強度</span><span class="spec-v">15%</span></div>'
        "</div>"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    # ── 7. 障害対応とフォールバック ──

    st.markdown(
        f'<div class="sec-hdr">'
        f'<div class="bar" style="background:#f59e0b"></div>'
        f'<div class="txt">障害対応とフォールバック</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128260;</span>AI（Gemini）障害時</div>'
        '<div style="padding:0.5rem 1rem; font-size:0.74rem; color:#475569; line-height:1.7; margin-bottom:0.3rem">'
        "Gemini APIが応答しない場合、以下の順に自動フォールバックします:"
        "</div>"
        '<div style="padding:0 1rem 0.3rem; font-size:0.72rem">'
        '<div style="display:flex; flex-direction:column; gap:0.2rem">'
        '<div style="display:flex; align-items:center; gap:0.3rem">'
        '<span style="background:#dbeafe; color:#1d4ed8; padding:0.1rem 0.3rem; border-radius:4px; font-weight:700; font-size:0.6rem">1</span>'
        '<span style="color:#0f172a">Gemini 3 Pro Preview（メイン）</span></div>'
        '<div style="color:#94a3b8; font-size:0.65rem; padding-left:1.8rem">&darr; 障害時</div>'
        '<div style="display:flex; align-items:center; gap:0.3rem">'
        '<span style="background:#dbeafe; color:#1d4ed8; padding:0.1rem 0.3rem; border-radius:4px; font-weight:700; font-size:0.6rem">2</span>'
        '<span style="color:#0f172a">Gemini 2.5 Pro（フォールバック）</span></div>'
        '<div style="color:#94a3b8; font-size:0.65rem; padding-left:1.8rem">&darr; 障害時</div>'
        '<div style="display:flex; align-items:center; gap:0.3rem">'
        '<span style="background:#dbeafe; color:#1d4ed8; padding:0.1rem 0.3rem; border-radius:4px; font-weight:700; font-size:0.6rem">3</span>'
        '<span style="color:#0f172a">Gemini Flash（軽量モデル）</span></div>'
        '<div style="color:#94a3b8; font-size:0.65rem; padding-left:1.8rem">&darr; Gemini全障害時</div>'
        '<div style="display:flex; align-items:center; gap:0.3rem">'
        '<span style="background:#fff7ed; color:#c2410c; padding:0.1rem 0.3rem; border-radius:4px; font-weight:700; font-size:0.6rem">4</span>'
        '<span style="color:#0f172a">Deepseek API（最終手段）</span></div>'
        '<div style="color:#94a3b8; font-size:0.65rem; padding-left:1.8rem">&darr; 全AI障害時</div>'
        '<div style="display:flex; align-items:center; gap:0.3rem">'
        '<span style="background:#f1f5f9; color:#64748b; padding:0.1rem 0.3rem; border-radius:4px; font-weight:700; font-size:0.6rem">5</span>'
        '<span style="color:#64748b">キーワードベース分析（ルールベース）</span></div>'
        "</div>"
        "</div>"
        '<div class="spec-note">各リトライは最大3回・指数バックオフ(2秒→4秒→8秒)。1時間のキャッシュにより同一プロンプトの再呼び出しを回避。</div>'
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#9888;</span>その他の障害対応</div>'
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">Alpaca API障害</span><span class="spec-v">3回リトライ+指数バックオフ。失敗時はDiscord通知</span></div>'
        '<div class="spec-row"><span class="spec-k">ニュースソース障害</span><span class="spec-v">個別ソース障害は他ソースで継続。全障害時はDB蓄積分を使用</span></div>'
        '<div class="spec-row"><span class="spec-k">DB障害</span><span class="spec-v">SQLite UNIQUE制約でデータ整合性を保護。障害時はログに記録</span></div>'
        '<div class="spec-row"><span class="spec-k">スケジューラ停止</span><span class="spec-v">ハートビート監視（60分警告/120分重大 → Discord通知）</span></div>'
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    # ── 8. 通知とモニタリング ──

    st.markdown(
        f'<div class="sec-hdr">'
        f'<div class="bar" style="background:#8b5cf6"></div>'
        f'<div class="txt">通知とモニタリング</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128276;</span>Discord通知チャンネル</div>'
        '<div style="padding:0.5rem 1rem">'
        # 買いシグナル
        '<div style="display:flex; align-items:baseline; gap:0.5rem; padding:0.35rem 0; border-bottom:1px solid #f1f5f9; font-size:0.74rem">'
        '<span style="color:#059669; font-weight:700; min-width:8rem">買いシグナル</span>'
        '<span style="color:#475569">銘柄・価格・戦略・確信度・理由を即時通知</span>'
        "</div>"
        # 売りシグナル
        '<div style="display:flex; align-items:baseline; gap:0.5rem; padding:0.35rem 0; border-bottom:1px solid #f1f5f9; font-size:0.74rem">'
        '<span style="color:#e11d48; font-weight:700; min-width:8rem">売りシグナル</span>'
        '<span style="color:#475569">決済価格・損益・保有日数・決済理由を即時通知</span>'
        "</div>"
        # 日次サマリー
        '<div style="display:flex; align-items:baseline; gap:0.5rem; padding:0.35rem 0; border-bottom:1px solid #f1f5f9; font-size:0.74rem">'
        '<span style="color:#2563eb; font-weight:700; min-width:8rem">日次サマリー</span>'
        '<span style="color:#475569">本日の損益・取引・保有状況・累積成績（毎日16:30 ET）</span>'
        "</div>"
        # パフォーマンス
        '<div style="display:flex; align-items:baseline; gap:0.5rem; padding:0.35rem 0; border-bottom:1px solid #f1f5f9; font-size:0.74rem">'
        '<span style="color:#7c3aed; font-weight:700; min-width:8rem">パフォーマンス</span>'
        '<span style="color:#475569">週次・月次の成績レポート（勝率・リターン・セクター別）</span>'
        "</div>"
        # システム警告
        '<div style="display:flex; align-items:baseline; gap:0.5rem; padding:0.35rem 0; font-size:0.74rem">'
        '<span style="color:#f59e0b; font-weight:700; min-width:8rem">システム警告</span>'
        '<span style="color:#475569">エラー・API制限(80%超)・CB発動/解除・ハートビート異常</span>'
        "</div>"
        "</div>"
        '<div class="spec-note">シグナル通知は48時間のスライディングウィンドウで重複排除。エラー通知は1時間のクールダウン。</div>'
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128202;</span>ヘルスモニタリング</div>'
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">ハートビート</span><span class="spec-v">5分毎にJSONファイル更新</span></div>'
        '<div class="spec-row"><span class="spec-k">警告閾値</span><span class="spec-v">60分間更新なしで警告</span></div>'
        '<div class="spec-row"><span class="spec-k">重大閾値</span><span class="spec-v">120分間更新なしでクリティカル</span></div>'
        '<div class="spec-row"><span class="spec-k">ログ保存先</span><span class="spec-v">92_logs/（scheduler, trader, error）</span></div>'
        '<div class="spec-row"><span class="spec-k">API使用量監視</span><span class="spec-v">70-90%で段階的に警告</span></div>'
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    # ── 9. 自己改善の仕組み ──

    st.markdown(
        f'<div class="sec-hdr">'
        f'<div class="bar" style="background:{W}"></div>'
        f'<div class="txt">自己改善の仕組み</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128257;</span>PDCAサイクル</div>'
        '<div style="padding:0.5rem 1rem">'
        # 日次
        '<div style="margin-bottom:0.8rem; padding-bottom:0.6rem; border-bottom:1px solid #f1f5f9">'
        '<div style="font-size:0.78rem; font-weight:700; color:#0f172a; margin-bottom:0.2rem">日次レビュー（自動）</div>'
        '<div style="font-size:0.72rem; color:#64748b; line-height:1.6">'
        "毎日の取引結果を自動分析し、KPI進捗（勝率・リターン・ドローダウン）を追跡。"
        "7日間 vs 14日間のトレンド比較で改善/悪化を検出しDiscordに通知。</div>"
        "</div>"
        # 週次
        '<div style="margin-bottom:0.8rem; padding-bottom:0.6rem; border-bottom:1px solid #f1f5f9">'
        '<div style="font-size:0.78rem; font-weight:700; color:#0f172a; margin-bottom:0.2rem">週次レビュー（土曜日）</div>'
        '<div style="font-size:0.72rem; color:#64748b; line-height:1.6">'
        "損失取引（-5%以上）をAIが深掘り分析。原因分類（損切発動・シグナルロジック・市場変動）を行い、"
        "PDCA形式で改善提案を生成。パラメータ調整案やフィルター追加を提示。</div>"
        "</div>"
        # 改善実行
        "<div>"
        '<div style="font-size:0.78rem; font-weight:700; color:#0f172a; margin-bottom:0.2rem">改善の実行</div>'
        '<div style="font-size:0.72rem; color:#64748b; line-height:1.6">'
        "改善提案はバックテスト（過去データでの検証）を経て適用。"
        "現時点では人間の承認が必要（完全自動化はPhase 4以降に予定）。"
        "過去の教訓は38件が体系的に記録・分類されています。</div>"
        "</div>"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128218;</span>シグナル精度の追跡</div>'
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">シグナル記録</span><span class="spec-v">全シグナルをDBに保存（戦略・確信度・結果）</span></div>'
        '<div class="spec-row"><span class="spec-k">損益との紐付け</span><span class="spec-v">signal_id で取引と連結</span></div>'
        '<div class="spec-row"><span class="spec-k">戦略別成績</span><span class="spec-v">押し目・トレンド・VIX逆張りの個別分析</span></div>'
        '<div class="spec-row"><span class="spec-k">パターン検出</span><span class="spec-v">連続負け・セクター集中・早期損切の自動検出</span></div>'
        "</div>"
        '<div class="spec-note">現在は週次レポートで手動確認。リアルタイム精度トラッキングの自動化はPhase 4の改善項目。</div>'
        "</div>",
        unsafe_allow_html=True,
    )

    # ── 10. 現在の制約事項 ──

    st.markdown(
        f'<div class="sec-hdr">'
        f'<div class="bar" style="background:{L}"></div>'
        f'<div class="txt">現在の制約事項</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#9940;</span>対応していないこと</div>'
        '<div style="padding:0.5rem 1rem; font-size:0.74rem; color:#475569; line-height:1.8">'
        '<div style="display:grid; grid-template-columns:1fr 1fr; gap:0.2rem 1.5rem">'
        "<div>&#x2716; 空売り・オプション・先物</div>"
        "<div>&#x2716; 暗号資産</div>"
        "<div>&#x2716; 米国以外の市場</div>"
        "<div>&#x2716; プレマーケット / アフターアワーズ取引</div>"
        "<div>&#x2716; 高頻度トレード（ミリ秒単位）</div>"
        "<div>&#x2716; トレーリングストップ</div>"
        "<div>&#x2716; 自動リバランス（手動のみ）</div>"
        "<div>&#x2716; リアルタイムストリーミング（ポーリング方式）</div>"
        "</div>"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128295;</span>API制約とコスト</div>'
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">Alpaca</span><span class="spec-v">200 req/日（無料ペーパー）</span></div>'
        '<div class="spec-row"><span class="spec-k">Gemini</span><span class="spec-v">50 req/日（動的スロットル）</span></div>'
        '<div class="spec-row"><span class="spec-k">NewsAPI</span><span class="spec-v">100 req/日（無料枠）</span></div>'
        '<div class="spec-row"><span class="spec-k">Finnhub</span><span class="spec-v">60 req/分</span></div>'
        '<div class="spec-row"><span class="spec-k">yfinance</span><span class="spec-v">制限なし（429エラー頻発時あり）</span></div>'
        '<div class="spec-row"><span class="spec-k">月額予算</span><span class="spec-v">約¥5,000（API利用料合計）</span></div>'
        "</div>"
        '<div class="spec-note">API使用量が80%を超えるとDiscordに警告通知。Geminiは使用量80%超で呼び出し間隔を自動延長。</div>'
        "</div>",
        unsafe_allow_html=True,
    )

# ============================================================
# 詳細ログ タブ
# ============================================================

with tab_log:

    import json as _json

    st.markdown(
        '<div class="wf-intro">'
        "<b>詳細ログ — パイプライン実行の記録</b><br>"
        "日付を選んで、その日に収集されたニュース・AI分析・シグナル・取引の詳細を確認できます。"
        "各ステップで「何が入力され、どう判断されたか」を追跡するためのログビューです。"
        "</div>",
        unsafe_allow_html=True,
    )

    # 日付選択
    log_dates = _dm.get_available_log_dates(30)
    if log_dates:
        from datetime import date as _date

        date_options = [_date.fromisoformat(d) for d in log_dates]
        selected_date = st.date_input(
            "ログ日付",
            value=date_options[0],
            min_value=date_options[-1] if date_options else None,
            max_value=date_options[0] if date_options else None,
        )
        target = selected_date.isoformat()

        # 概要サマリー
        summary = _dm.get_log_day_summary(target)

        WEEKDAY_JP_LOG = ["月", "火", "水", "木", "金", "土", "日"]
        wd = WEEKDAY_JP_LOG[selected_date.weekday()]

        sum_cols = st.columns(5)
        sum_items = [
            ("ニュース", summary["news"], "📰"),
            ("AI分析", summary["analysis"], "🧠"),
            ("シグナル", summary["signals"], "🎯"),
            ("取引", summary["trades"], "💰"),
            ("実行", summary["runs"], "⚙️"),
        ]
        for col, (label, cnt, icon) in zip(sum_cols, sum_items):
            cnt_color = "#0f172a" if cnt > 0 else "#cbd5e1"
            with col:
                st.markdown(
                    f'<div class="card-sm" style="text-align:center; padding:0.6rem 0.3rem">'
                    f'<div style="font-size:1rem">{icon}</div>'
                    f'<div style="font-size:1.2rem; font-weight:700; color:{cnt_color}">{cnt}</div>'
                    f'<div style="font-size:0.65rem; color:#94a3b8">{label}</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )

        st.markdown(
            f'<div style="text-align:center; font-size:0.72rem; color:#64748b; margin:0.3rem 0 0.8rem">'
            f'{target} ({wd}) のパイプラインログ</div>',
            unsafe_allow_html=True,
        )

        # ── 1. システム実行ログ ──
        log_runs = _dm.get_log_system_runs(target)
        with st.expander(f"⚙️ システム実行ログ ({len(log_runs)}件)", expanded=len(log_runs) > 0):
            if len(log_runs) > 0:
                for _, run in log_runs.iterrows():
                    mode = run.get("run_mode", "")
                    status = run.get("status", "")
                    started = str(run.get("started_at", ""))[:19].replace("T", " ")
                    ended = str(run.get("ended_at", "") or "")[:19].replace("T", " ")
                    host = run.get("host_name", "") or ""
                    news_c = run.get("news_collected", 0) or 0
                    sig_d = run.get("signals_detected", 0) or 0
                    trd_e = run.get("trades_executed", 0) or 0
                    errs = run.get("errors_count", 0) or 0
                    err_msg = run.get("error_message", "") or ""
                    s_color = W if status == "completed" else (L if status == "failed" else "#f59e0b")
                    st.markdown(
                        f'<div class="dd-item"><details>'
                        f'<summary class="dd-summary">'
                        f'<span style="color:{s_color}; font-weight:600">{status}</span> '
                        f'<b>{mode}</b> '
                        f'<span style="color:#94a3b8">{started}</span>'
                        f'</summary>'
                        f'<div class="dd-detail">'
                        f'<div class="dd-kv"><span class="dd-k">開始</span><span class="dd-v">{started}</span></div>'
                        f'<div class="dd-kv"><span class="dd-k">終了</span><span class="dd-v">{ended}</span></div>'
                        f'<div class="dd-kv"><span class="dd-k">ホスト</span><span class="dd-v">{host}</span></div>'
                        f'<div class="dd-kv"><span class="dd-k">ニュース</span><span class="dd-v">{news_c}件</span></div>'
                        f'<div class="dd-kv"><span class="dd-k">シグナル</span><span class="dd-v">{sig_d}件</span></div>'
                        f'<div class="dd-kv"><span class="dd-k">取引</span><span class="dd-v">{trd_e}件</span></div>'
                        f'<div class="dd-kv"><span class="dd-k">エラー</span><span class="dd-v">{errs}件</span></div>'
                        + (f'<div class="dd-kv"><span class="dd-k">エラー内容</span><span class="dd-v" style="color:{L}">{err_msg}</span></div>' if err_msg else "")
                        + f"</div></details></div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown('<span style="color:#94a3b8; font-size:0.82rem">この日のシステム実行はありません</span>', unsafe_allow_html=True)

        # ── 2. ニュース収集ログ ──
        log_news = _dm.get_log_news(target)
        with st.expander(f"📰 ニュース収集ログ ({len(log_news)}件)", expanded=False):
            if len(log_news) > 0:
                # ソース別集計
                src_counts = log_news["source"].value_counts().head(10)
                src_pills = " ".join(
                    f'<span class="pill pill-blue" style="font-size:0.6rem; margin:0.1rem">{src} ({cnt})</span>'
                    for src, cnt in src_counts.items()
                )
                st.markdown(
                    f'<div style="margin-bottom:0.5rem; font-size:0.72rem; color:#64748b">'
                    f'ソース: {src_pills}</div>',
                    unsafe_allow_html=True,
                )

                # ティッカーフィルター
                all_tickers_set = set()
                for tj in log_news["tickers_json"].dropna():
                    try:
                        for t in _json.loads(tj):
                            all_tickers_set.add(t)
                    except Exception:
                        pass
                ticker_filter = st.selectbox(
                    "銘柄フィルター",
                    ["すべて"] + sorted(all_tickers_set),
                    key="news_ticker_filter",
                )

                filtered_news = log_news
                if ticker_filter != "すべて":
                    filtered_news = log_news[
                        log_news["tickers_json"].fillna("").str.contains(ticker_filter)
                    ]

                for _, n in filtered_news.head(50).iterrows():
                    title = n.get("title", "") or ""
                    source = n.get("source", "") or ""
                    content = n.get("content", "") or ""
                    theme = n.get("theme", "") or ""
                    tickers_raw = n.get("tickers_json", "") or ""
                    sent = n.get("sentiment_score")
                    quality = n.get("quality_score")
                    importance = n.get("importance", "") or ""
                    created = str(n.get("created_at", ""))[:19].replace("T", " ")
                    url = n.get("url", "") or ""

                    # ティッカーピル
                    tk_pills = ""
                    try:
                        tickers = _json.loads(tickers_raw) if tickers_raw else []
                        for tk in tickers[:8]:
                            tk_pills += f'<span style="font-size:0.6rem; color:{P}; margin-right:0.2rem">${tk}</span>'
                    except Exception:
                        pass

                    detail = ""
                    if content:
                        detail += f'<div class="dd-kv"><span class="dd-k">内容</span><span class="dd-v">{content[:500]}</span></div>'
                    if sent is not None and pd.notna(sent):
                        s_color = W if sent > 0 else (L if sent < 0 else "#94a3b8")
                        detail += f'<div class="dd-kv"><span class="dd-k">感情</span><span class="dd-v" style="color:{s_color}">{sent:+.2f}</span></div>'
                    if quality is not None and pd.notna(quality):
                        detail += f'<div class="dd-kv"><span class="dd-k">品質</span><span class="dd-v">{quality:.0f}/100</span></div>'
                    if importance:
                        detail += f'<div class="dd-kv"><span class="dd-k">重要度</span><span class="dd-v">{importance}</span></div>'
                    if theme:
                        detail += f'<div class="dd-kv"><span class="dd-k">テーマ</span><span class="dd-v">{theme}</span></div>'
                    if tk_pills:
                        detail += f'<div class="dd-kv"><span class="dd-k">関連銘柄</span><span class="dd-v">{tk_pills}</span></div>'
                    if url:
                        detail += f'<div class="dd-kv"><span class="dd-k">URL</span><span class="dd-v"><a href="{url}" target="_blank" style="color:{P}">{url[:80]}</a></span></div>'
                    detail += f'<div class="dd-kv"><span class="dd-k">取得時刻</span><span class="dd-v">{created}</span></div>'

                    st.markdown(
                        f'<div class="dd-item"><details>'
                        f'<summary class="dd-summary">{title}'
                        f'<span style="color:#94a3b8; font-size:0.68rem; margin-left:0.3rem">{source}</span>'
                        f'</summary>'
                        f'<div class="dd-detail">{detail}</div>'
                        f'</details></div>',
                        unsafe_allow_html=True,
                    )

                if len(filtered_news) > 50:
                    st.markdown(
                        f'<div style="color:#94a3b8; font-size:0.72rem; text-align:center; padding:0.5rem">'
                        f'他 {len(filtered_news) - 50}件は省略</div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown('<span style="color:#94a3b8; font-size:0.82rem">この日のニュースはありません</span>', unsafe_allow_html=True)

        # ── 3. AI分析ログ ──
        log_analyses = _dm.get_log_analyses(target)
        with st.expander(f"🧠 AI分析ログ ({len(log_analyses)}件)", expanded=False):
            if len(log_analyses) > 0:
                for _, a in log_analyses.iterrows():
                    theme = a.get("theme", "") or ""
                    ticker = a.get("ticker", "") or ""
                    a_type = a.get("analysis_type", "") or ""
                    score = a.get("score") or 0
                    direction = a.get("direction", "") or ""
                    summary_txt = a.get("summary", "") or ""
                    detailed = a.get("detailed_analysis", "") or ""
                    kp_raw = a.get("key_points_json", "") or ""
                    rec = a.get("recommendation", "") or ""
                    model = a.get("model_used", "") or ""
                    time_a = str(a.get("analyzed_at", ""))[:19].replace("T", " ")

                    dir_label = {"bullish": "強気", "bearish": "弱気", "neutral": "中立"}.get(direction, direction)
                    dir_color = W if direction == "bullish" else (L if direction == "bearish" else "#64748b")
                    type_label = {"theme_report": "テーマ", "ticker_analysis": "銘柄", "impact_analysis": "インパクト"}.get(a_type, a_type)

                    header = (
                        f'<span class="pill pill-blue" style="font-size:0.6rem; padding:0.03rem 0.25rem">{type_label}</span> '
                        f'<b>{theme}</b>'
                    )
                    if ticker:
                        header += f' <span style="color:{P}; font-weight:600">{ticker}</span>'
                    header += f' <span style="color:{dir_color}; font-weight:600">スコア{score:.0f} / {dir_label}</span>'

                    detail = ""
                    if rec:
                        detail += f'<div class="dd-kv"><span class="dd-k">推奨</span><span class="dd-v" style="font-weight:600">{rec}</span></div>'
                    if summary_txt:
                        detail += f'<div class="dd-kv"><span class="dd-k">要約</span><span class="dd-v">{summary_txt}</span></div>'
                    try:
                        kps = _json.loads(kp_raw) if kp_raw else []
                        if kps:
                            kp_list = "".join(f"<li>{kp}</li>" for kp in kps[:8])
                            detail += f'<div class="dd-kv"><span class="dd-k">注目点</span><span class="dd-v"><ul style="margin:0; padding-left:1.2rem">{kp_list}</ul></span></div>'
                    except Exception:
                        pass
                    if detailed:
                        detail += (
                            f'<div style="margin-top:0.4rem; padding-top:0.4rem; border-top:1px solid #e2e8f0">'
                            f'<span class="dd-k">詳細分析</span>'
                            f'<div style="margin-top:0.2rem; white-space:pre-wrap; font-size:0.72rem">{detailed[:1200]}</div></div>'
                        )
                    detail += f'<div class="dd-kv" style="margin-top:0.3rem"><span class="dd-k">モデル</span><span class="dd-v">{model} / {time_a}</span></div>'

                    st.markdown(
                        f'<div class="dd-item"><details>'
                        f'<summary class="dd-summary">{header}</summary>'
                        f'<div class="dd-detail">{detail}</div>'
                        f'</details></div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown('<span style="color:#94a3b8; font-size:0.82rem">この日のAI分析はありません</span>', unsafe_allow_html=True)

        # ── 4. シグナルログ ──
        log_signals = _dm.get_log_signals(target)
        with st.expander(f"🎯 シグナルログ ({len(log_signals)}件)", expanded=len(log_signals) > 0):
            if len(log_signals) > 0:
                for _, s in log_signals.iterrows():
                    sig_type = s["signal_type"]
                    sig_label = "買い" if sig_type == "BUY" else "売り"
                    sig_cls = "pill-green" if sig_type == "BUY" else "pill-red"
                    ticker = s["ticker"]
                    price = s.get("price", 0) or 0
                    conv = s.get("conviction") or 0
                    conf = s.get("confidence") or 0
                    status_s = s.get("status", "")
                    rsi = s.get("rsi")
                    macd = s.get("macd")
                    ma200 = s.get("ma200")
                    vol_ratio = s.get("volume_ratio")
                    target_p = s.get("target_price")
                    sl = s.get("stop_loss")
                    reasoning = s.get("reasoning", "") or ""
                    df_raw = s.get("decision_factors_json", "") or ""
                    time_s = str(s.get("detected_at", ""))[:19].replace("T", " ")

                    status_label = {
                        "pending": "待機中", "executed": "執行済", "rejected": "見送り",
                        "cancelled": "取消", "expired": "期限切れ",
                    }.get(status_s, status_s)

                    header = (
                        f'<span class="pill {sig_cls}" style="font-size:0.7rem">{sig_label}</span> '
                        f'<b>{ticker}</b> '
                        f'<span style="color:#64748b">@${price:.2f}</span> '
                        f'<span class="pill pill-blue" style="font-size:0.58rem; padding:0.03rem 0.25rem">{status_label}</span>'
                    )
                    if conv:
                        header += f' <span style="color:#64748b; font-size:0.72rem">確信度 {conv}/10</span>'

                    detail = ""
                    detail += f'<div class="dd-kv"><span class="dd-k">検出時刻</span><span class="dd-v">{time_s}</span></div>'
                    if conv:
                        detail += f'<div class="dd-kv"><span class="dd-k">確信度</span><span class="dd-v">{conv} / 10</span></div>'
                    if conf:
                        detail += f'<div class="dd-kv"><span class="dd-k">信頼度</span><span class="dd-v">{conf:.0%}</span></div>'
                    if rsi is not None and pd.notna(rsi):
                        rsi_color = L if rsi > 70 else (W if rsi < 30 else "#0f172a")
                        detail += f'<div class="dd-kv"><span class="dd-k">RSI</span><span class="dd-v" style="color:{rsi_color}">{rsi:.1f}</span></div>'
                    if macd is not None and pd.notna(macd):
                        detail += f'<div class="dd-kv"><span class="dd-k">MACD</span><span class="dd-v">{macd:.4f}</span></div>'
                    if ma200 is not None and pd.notna(ma200):
                        above = price > ma200 if price and ma200 else False
                        ma_label = f"${ma200:.2f}" + (" (上)" if above else " (下)")
                        detail += f'<div class="dd-kv"><span class="dd-k">200日MA</span><span class="dd-v">{ma_label}</span></div>'
                    if vol_ratio is not None and pd.notna(vol_ratio):
                        detail += f'<div class="dd-kv"><span class="dd-k">出来高比</span><span class="dd-v">{vol_ratio:.2f}x</span></div>'
                    if target_p:
                        detail += f'<div class="dd-kv"><span class="dd-k">目標価格</span><span class="dd-v">${target_p:.2f}</span></div>'
                    if sl:
                        detail += f'<div class="dd-kv"><span class="dd-k">損切ライン</span><span class="dd-v">${sl:.2f}</span></div>'
                    if reasoning:
                        detail += (
                            f'<div style="margin-top:0.4rem; padding-top:0.4rem; border-top:1px solid #e2e8f0">'
                            f'<span class="dd-k">判断理由</span>'
                            f'<div style="margin-top:0.2rem; white-space:pre-wrap; font-size:0.72rem">{reasoning}</div></div>'
                        )

                    # decision_factors 詳細展開
                    if df_raw:
                        try:
                            factors = _json.loads(df_raw)
                            if isinstance(factors, dict):
                                factor_detail = ""
                                # ニュース関連
                                ns = factors.get("news_score")
                                nr = factors.get("news_reason", "")
                                if ns is not None:
                                    ns_color = W if ns > 0 else (L if ns < 0 else "#94a3b8")
                                    factor_detail += f'<div class="dd-kv"><span class="dd-k">ニューススコア</span><span class="dd-v" style="color:{ns_color}">{ns:+.2f}</span></div>'
                                if nr:
                                    factor_detail += f'<div class="dd-kv"><span class="dd-k">ニュース理由</span><span class="dd-v">{nr}</span></div>'
                                # テクニカル
                                tr = factors.get("technical_reason", "")
                                if tr:
                                    factor_detail += f'<div class="dd-kv"><span class="dd-k">テクニカル</span><span class="dd-v">{tr}</span></div>'
                                fr = factors.get("fundamental_reason", "")
                                if fr:
                                    factor_detail += f'<div class="dd-kv"><span class="dd-k">ファンダ</span><span class="dd-v">{fr}</span></div>'
                                # 戦略/カテゴリ
                                strat = factors.get("strategy_type", "")
                                cats = factors.get("categories", [])
                                if strat:
                                    factor_detail += f'<div class="dd-kv"><span class="dd-k">戦略</span><span class="dd-v">{strat}</span></div>'
                                if cats:
                                    factor_detail += f'<div class="dd-kv"><span class="dd-k">カテゴリ</span><span class="dd-v">{", ".join(cats)}</span></div>'
                                # SELL詳細
                                dr = factors.get("detailed_reason", "")
                                chg = factors.get("change_pct")
                                if dr:
                                    factor_detail += f'<div class="dd-kv"><span class="dd-k">詳細根拠</span><span class="dd-v">{dr}</span></div>'
                                if chg is not None:
                                    chg_color = W if chg > 0 else L
                                    factor_detail += f'<div class="dd-kv"><span class="dd-k">変動率</span><span class="dd-v" style="color:{chg_color}">{chg:+.1f}%</span></div>'

                                if factor_detail:
                                    detail += (
                                        f'<div style="margin-top:0.4rem; padding-top:0.4rem; border-top:1px solid #e2e8f0">'
                                        f'<span class="dd-k" style="font-weight:600">判断要因</span>'
                                        f'{factor_detail}</div>'
                                    )
                        except Exception:
                            pass

                    st.markdown(
                        f'<div class="dd-item"><details open>'
                        f'<summary class="dd-summary">{header}</summary>'
                        f'<div class="dd-detail">{detail}</div>'
                        f'</details></div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown('<span style="color:#94a3b8; font-size:0.82rem">この日のシグナルはありません</span>', unsafe_allow_html=True)

        # ── 5. 取引ログ ──
        log_trades = _dm.get_log_trades(target)
        with st.expander(f"💰 取引ログ ({len(log_trades)}件)", expanded=len(log_trades) > 0):
            if len(log_trades) > 0:
                for _, t in log_trades.iterrows():
                    action = t["action"]
                    a_label = "買い" if action == "BUY" else "売り"
                    a_cls = "pill-green" if action == "BUY" else "pill-red"
                    ticker = t["ticker"]
                    entry_p = t["entry_price"]
                    exit_p = t.get("exit_price")
                    shares = int(t["shares"])
                    pnl = t.get("profit_loss") or 0
                    pnl_pct = t.get("profit_loss_pct") or 0
                    status_t = t.get("status", "")
                    exit_reason = t.get("exit_reason", "") or ""
                    strategy = t.get("strategy_used", "") or ""
                    notes = t.get("notes", "") or ""
                    entry_ts = str(t.get("entry_timestamp", ""))[:19].replace("T", " ")
                    exit_ts = str(t.get("exit_timestamp", "") or "")[:19].replace("T", " ")
                    holding = t.get("holding_days")

                    pnl_c = "c-pos" if pnl >= 0 else "c-neg"
                    pnl_s = "+" if pnl >= 0 else ""

                    if status_t == "CLOSED":
                        pnl_txt = f'<span class="{pnl_c}" style="font-weight:600">{pnl_s}${pnl:,.2f} ({pnl_s}{pnl_pct:.1f}%)</span>'
                    else:
                        pnl_txt = '<span class="pill pill-blue" style="font-size:0.6rem">保有中</span>'

                    header = (
                        f'<span class="pill {a_cls}" style="font-size:0.7rem">{a_label}</span> '
                        f'<b>{ticker}</b> '
                        f'<span style="color:#64748b">{shares}株 @${entry_p:.2f}</span> {pnl_txt}'
                    )

                    detail = ""
                    detail += f'<div class="dd-kv"><span class="dd-k">エントリー</span><span class="dd-v">${entry_p:.2f} ({entry_ts})</span></div>'
                    if exit_p and pd.notna(exit_p):
                        detail += f'<div class="dd-kv"><span class="dd-k">エグジット</span><span class="dd-v">${exit_p:.2f} ({exit_ts})</span></div>'
                    if holding is not None and pd.notna(holding):
                        detail += f'<div class="dd-kv"><span class="dd-k">保有日数</span><span class="dd-v">{int(holding)}日</span></div>'
                    if exit_reason:
                        reason_label = {"STOP_LOSS": "損切り", "TAKE_PROFIT": "利確", "SIGNAL": "シグナル", "MANUAL": "手動"}.get(exit_reason, exit_reason)
                        detail += f'<div class="dd-kv"><span class="dd-k">決済理由</span><span class="dd-v">{reason_label}</span></div>'
                    if strategy:
                        detail += f'<div class="dd-kv"><span class="dd-k">戦略</span><span class="dd-v">{strategy}</span></div>'
                    if notes:
                        detail += f'<div class="dd-kv"><span class="dd-k">メモ</span><span class="dd-v">{notes}</span></div>'

                    st.markdown(
                        f'<div class="dd-item"><details>'
                        f'<summary class="dd-summary">{header}</summary>'
                        f'<div class="dd-detail">{detail}</div>'
                        f'</details></div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown('<span style="color:#94a3b8; font-size:0.82rem">この日の取引はありません</span>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div style="color:#94a3b8; text-align:center; padding:2rem; font-size:0.82rem">'
            "直近30日間のログデータがありません</div>",
            unsafe_allow_html=True,
        )
