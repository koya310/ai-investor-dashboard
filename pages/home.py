"""Home -- ポートフォリオ概要"""

import logging
from datetime import datetime

import dashboard_data as _dm
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.shared import P, W, L, load_common_data

logger = logging.getLogger(__name__)

# ── データ読み込み ──
d = load_common_data()
start = d["start"]
daily = d["daily"]
spy = d["spy"]
trades = d["trades"]
kpi = d["kpi"]
verdict = d["verdict"]
capital = d["capital"]
alpaca_pf = d["alpaca_pf"]
alpaca_positions = d["alpaca_positions"]


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
        for theme, tdata in sorted(by_theme.items(), key=lambda x: x[1]["total_pnl"]):
            c = "c-pos" if tdata["total_pnl"] >= 0 else "c-neg"
            sign = "+" if tdata["total_pnl"] >= 0 else ""
            html += (
                f'<div class="dlg-row">'
                f'<span class="dlg-key">{theme} ({tdata["trades"]}回, '
                f'勝率{tdata["win_rate"]}%)</span>'
                f'<span class="{c}" style="font-weight:600">'
                f'{sign}${tdata["total_pnl"]:.0f}</span></div>'
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
# 1. ポートフォリオ総額 + 保有銘柄
# ============================================================

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

# ============================================================
# 2. 資産推移チャート
# ============================================================

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

    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 3. 実取引チェックリスト
# ============================================================

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
    if st.button("詳細分析", type="secondary", use_container_width=True):
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
    vt = f"<b>GO</b> -- 全{total}項目を達成。Phase 4（実取引）へ移行可能です。"
elif v == "CONDITIONAL_GO":
    vc = "v-cond"
    recs = " / ".join(verdict["recommendations"][:2])
    vt = (
        f"<b>条件付き</b> -- {passed}/{total}項目を達成。"
        f"<br><span style='font-size:0.78rem'>{recs}</span>"
    )
else:
    vc = "v-ng"
    vt = f"<b>未達</b> -- {passed}/{total}項目のみ達成。残り{days_left}日で改善が必要です。"

st.markdown(
    f'<div class="verdict {vc}">{vt}</div>',
    unsafe_allow_html=True,
)

# ============================================================
# 4. 取引履歴
# ============================================================

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
